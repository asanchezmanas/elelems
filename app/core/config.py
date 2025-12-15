# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación"""
    
    # API
    PROJECT_NAME: str = "RAG Ecommerce"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: Optional[str] = None  # Para operaciones admin
    
    # LLM Provider
    LLM_PROVIDER: str = "groq"  # groq, openai
    
    # Groq
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    
    # OpenAI (backup)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Embeddings (local con sentence-transformers)
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384  # MiniLM-L12
    
    # RAG Configuration
    CHUNK_SIZE: int = 512  # tokens
    CHUNK_OVERLAP: int = 50
    DEFAULT_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Storage
    STORAGE_BUCKET: str = "documents"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".pptx", ".txt", ".md", ".html"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton global
settings = Settings()