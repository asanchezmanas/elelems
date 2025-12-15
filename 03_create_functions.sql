-- ============================================
-- 03_create_functions.sql
-- Funciones para búsqueda vectorial
-- ============================================

-- Función principal de búsqueda por similitud
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding VECTOR(384),
    match_count INT DEFAULT 5,
    filter_doc_type TEXT DEFAULT NULL,
    similarity_threshold FLOAT DEFAULT 0.0
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    content TEXT,
    section_title TEXT,
    filename TEXT,
    doc_type TEXT,
    chunk_index INTEGER,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id AS chunk_id,
        dc.document_id,
        dc.content,
        dc.section_title,
        d.filename,
        d.doc_type,
        dc.chunk_index,
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 
        -- Solo documentos indexados exitosamente
        d.status = 'indexed'
        -- Filtro opcional por tipo de documento
        AND (filter_doc_type IS NULL OR d.doc_type = filter_doc_type)
        -- Filtro por umbral de similitud
        AND (1 - (dc.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Función para búsqueda híbrida (texto + vector)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding VECTOR(384),
    match_count INT DEFAULT 5,
    text_weight FLOAT DEFAULT 0.3,
    vector_weight FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    chunk_id UUID,
    content TEXT,
    filename TEXT,
    combined_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id AS chunk_id,
        dc.content,
        d.filename,
        (
            -- Puntuación vectorial
            (1 - (dc.embedding <=> query_embedding)) * vector_weight
            +
            -- Puntuación de texto (BM25 aproximado con ts_rank)
            ts_rank(to_tsvector('spanish', dc.content), plainto_tsquery('spanish', query_text)) * text_weight
        ) AS combined_score
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 
        d.status = 'indexed'
        AND (
            -- Coincidencia de texto O similitud vectorial
            to_tsvector('spanish', dc.content) @@ plainto_tsquery('spanish', query_text)
            OR (1 - (dc.embedding <=> query_embedding)) > 0.5
        )
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- Función para obtener chunks de un documento específico (para debugging)
CREATE OR REPLACE FUNCTION get_document_chunks(
    doc_id UUID
)
RETURNS TABLE (
    chunk_id UUID,
    content TEXT,
    section_title TEXT,
    chunk_index INTEGER,
    token_count INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id AS chunk_id,
        dc.content,
        dc.section_title,
        dc.chunk_index,
        dc.token_count
    FROM document_chunks dc
    WHERE dc.document_id = doc_id
    ORDER BY dc.chunk_index;
END;
$$;

-- Función para estadísticas de documentos
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents BIGINT,
    total_chunks BIGINT,
    total_size_mb NUMERIC,
    avg_chunks_per_doc NUMERIC,
    doc_types JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT d.id) AS total_documents,
        COUNT(dc.id) AS total_chunks,
        ROUND(SUM(d.file_size_bytes)::NUMERIC / 1024 / 1024, 2) AS total_size_mb,
        ROUND(AVG(d.total_chunks), 2) AS avg_chunks_per_doc,
        jsonb_object_agg(d.doc_type, count_per_type) AS doc_types
    FROM documents d
    LEFT JOIN document_chunks dc ON d.id = dc.document_id
    LEFT JOIN (
        SELECT doc_type, COUNT(*) as count_per_type
        FROM documents
        GROUP BY doc_type
    ) type_counts ON d.doc_type = type_counts.doc_type
    WHERE d.status = 'indexed'
    GROUP BY type_counts.count_per_type;
END;
$$;

-- ============================================
-- Verificar creación de funciones
-- ============================================

SELECT 
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN (
    'match_document_chunks',
    'hybrid_search',
    'get_document_chunks',
    'get_document_stats'
);