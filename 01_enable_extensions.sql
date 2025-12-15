-- ============================================
-- 01_enable_extensions.sql (CORREGIDO)
-- ============================================

-- Habilitar extensión pgvector para almacenar embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Habilitar UUID para IDs únicos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ✅ AÑADIDO: pg_trgm para búsquedas de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verificar instalación
SELECT * FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp', 'pg_trgm');
