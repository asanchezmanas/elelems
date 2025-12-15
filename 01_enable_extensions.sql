-- ============================================
-- 01_enable_extensions.sql
-- Ejecutar en Supabase SQL Editor
-- ============================================

-- Habilitar extensión pgvector para almacenar embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Habilitar UUID para IDs únicos
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verificar instalación
SELECT * FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');