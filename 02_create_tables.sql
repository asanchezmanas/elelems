-- ============================================
-- 02_create_tables.sql (CORREGIDO)
-- ============================================

-- Tabla de documentos (metadata y referencia a Storage)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- ✅ Movido aquí desde ALTER TABLE
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    file_size_bytes INTEGER,
    mime_type TEXT,
    
    -- Metadata del parsing
    total_pages INTEGER,
    total_chunks INTEGER DEFAULT 0,
    
    -- Status del procesamiento
    status TEXT DEFAULT 'pending',
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
    
    -- Vector embedding (dimensión 384 para MiniLM)
    embedding VECTOR(384),
    
    -- Metadata del chunk
    chunk_index INTEGER NOT NULL,
    token_count INTEGER,
    page_number INTEGER,
    
    -- Metadata adicional (JSON flexible)
    metadata JSONB,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_chunk_per_doc UNIQUE (document_id, chunk_index)
);

-- ✅ AÑADIDO: Tablas de suscripciones y uso
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE,
    tier TEXT NOT NULL DEFAULT 'free',
    stripe_subscription_id TEXT,
    stripe_customer_id TEXT,
    status TEXT DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_tier CHECK (tier IN ('free', 'starter', 'pro', 'business', 'enterprise')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'canceled', 'past_due', 'incomplete'))
);

CREATE TABLE IF NOT EXISTS usage_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    month TEXT NOT NULL,
    documents_stored INT DEFAULT 0,
    generations_count INT DEFAULT 0,
    api_calls INT DEFAULT 0,
    storage_used_mb FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, month)
);

CREATE TABLE IF NOT EXISTS user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE,
    groq_api_key_encrypted TEXT,
    openai_api_key_encrypted TEXT,
    anthropic_api_key_encrypted TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ÍNDICES para performance
-- ============================================

-- Documents
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_filename ON documents(filename);
CREATE INDEX idx_documents_doc_type ON documents(doc_type);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- Chunks
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_chunk_index ON document_chunks(document_id, chunk_index);

-- ⚡ Índice IVFFlat para búsqueda vectorial
CREATE INDEX idx_chunks_embedding ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ✅ CORREGIDO: Índice trigram para búsqueda de texto
CREATE INDEX idx_chunks_content_trgm ON document_chunks 
USING gin (content gin_trgm_ops);

-- Subscriptions
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_tier ON user_subscriptions(tier);

-- Usage
CREATE INDEX idx_usage_stats_user_month ON usage_stats(user_id, month);

-- API Keys
CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);

-- ============================================
-- RLS (Row Level Security) - COMPLETO
-- ============================================

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;

-- ✅ Documents: Policies completas
CREATE POLICY "Users can select their own documents"
ON documents FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own documents"
ON documents FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own documents"
ON documents FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own documents"
ON documents FOR DELETE
USING (auth.uid() = user_id);

-- ✅ Document Chunks: Solo ver chunks de sus documentos
CREATE POLICY "Users can select chunks of their documents"
ON document_chunks FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_chunks.document_id 
    AND documents.user_id = auth.uid()
  )
);

CREATE POLICY "Users can insert chunks to their documents"
ON document_chunks FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_chunks.document_id 
    AND documents.user_id = auth.uid()
  )
);

CREATE POLICY "Users can delete chunks of their documents"
ON document_chunks FOR DELETE
USING (
  EXISTS (
    SELECT 1 FROM documents 
    WHERE documents.id = document_chunks.document_id 
    AND documents.user_id = auth.uid()
  )
);

-- ✅ Subscriptions: Solo ver su propia suscripción
CREATE POLICY "Users can view their subscription"
ON user_subscriptions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can update their subscription"
ON user_subscriptions FOR UPDATE
USING (auth.uid() = user_id);

-- ✅ Usage stats
CREATE POLICY "Users can view their usage"
ON usage_stats FOR SELECT
USING (auth.uid() = user_id);

-- ✅ API Keys
CREATE POLICY "Users can manage their API keys"
ON user_api_keys FOR ALL
USING (auth.uid() = user_id);

-- ============================================
-- TRIGGERS para updated_at
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

CREATE TRIGGER update_user_subscriptions_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usage_stats_updated_at
    BEFORE UPDATE ON usage_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_api_keys_updated_at
    BEFORE UPDATE ON user_api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Verificar creación
-- ============================================

SELECT 
    tablename, 
    schemaname 
FROM pg_tables 
WHERE tablename IN (
    'documents', 
    'document_chunks',
    'user_subscriptions',
    'usage_stats',
    'user_api_keys'
);