-- ============================================
-- 02_create_tables.sql
-- Ejecutar en Supabase SQL Editor
-- ============================================

-- Tabla de documentos (metadata y referencia a Storage)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    doc_type TEXT NOT NULL, -- 'policy', 'faq', 'product_guide', 'brand_guide'
    storage_path TEXT NOT NULL, -- Path en Supabase Storage
    file_size_bytes INTEGER,
    mime_type TEXT,
    
    -- Metadata del parsing
    total_pages INTEGER,
    total_chunks INTEGER DEFAULT 0,
    
    -- Status del procesamiento
    status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'indexed', 'failed'
    error_message TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_doc_type CHECK (doc_type IN ('policy', 'faq', 'product_guide', 'brand_guide', 'other')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'indexed', 'failed'))
);

-- Tabla de chunks con vectores
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Contenido
    content TEXT NOT NULL,
    section_title TEXT,
    
    -- Vector embedding (dimensión 384 para MiniLM, cambiar si usas otro modelo)
    embedding VECTOR(384),
    
    -- Metadata del chunk
    chunk_index INTEGER NOT NULL, -- Posición en el documento
    token_count INTEGER,
    page_number INTEGER,
    
    -- Metadata adicional (JSON flexible)
    metadata JSONB,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_chunk_per_doc UNIQUE (document_id, chunk_index)
);

-- ============================================
-- ÍNDICES para performance
-- ============================================

-- Índice para búsqueda por filename
CREATE INDEX idx_documents_filename ON documents(filename);

-- Índice para filtrar por tipo de documento
CREATE INDEX idx_documents_doc_type ON documents(doc_type);

-- Índice para status
CREATE INDEX idx_documents_status ON documents(status);

-- Índice para búsqueda temporal
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- Índice de relación FK
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);

-- Índice de orden de chunks
CREATE INDEX idx_chunks_chunk_index ON document_chunks(document_id, chunk_index);

-- ⚡ CRÍTICO: Índice IVFFlat para búsqueda vectorial rápida
-- 'lists' debería ser ~sqrt(total_rows), ajustar según crezca la DB
CREATE INDEX idx_chunks_embedding ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Para búsquedas híbridas (texto + vector)
CREATE INDEX idx_chunks_content_trgm ON document_chunks USING gin (content gin_trgm_ops);

-- ============================================
-- TRIGGER para updated_at automático
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Verificar creación
-- ============================================

SELECT 
    tablename, 
    schemaname 
FROM pg_tables 
WHERE tablename IN ('documents', 'document_chunks');