# app/core/config.py
from pydantic_settings import BaseSettings, field_validator, HttpUrl
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
    
    # ✅ AÑADIDOS: Para Supabase connection string
    SUPABASE_HOST: str = ""
    SUPABASE_PORT: int = 5432
    SUPABASE_DB: str = "postgres"
    SUPABASE_USER: str = "postgres"
    SUPABASE_PASSWORD: str = ""
    
    # ✅ AÑADIDO: Encryption key para API keys
    API_KEYS_ENCRYPTION_KEY: Optional[str] = None
    
    # ✅ AÑADIDO: Frontend URL para CORS
    FRONTEND_URL: HttpUrl = "http://localhost:3000"
    
    # ✅ AÑADIDO: Redis para cache (opcional)
    REDIS_URL: Optional[str] = None
    
    # ✅ VALIDADORES
    @field_validator('SUPABASE_URL')
    @classmethod
    def validate_supabase_url(cls, v):
        if not v or not v.startswith('https://'):
            raise ValueError("Invalid Supabase URL")
        return v
    
    @field_validator('GROQ_API_KEY', 'OPENAI_API_KEY')
    @classmethod
    def validate_api_keys(cls, v, info):
        field_name = info.field_name
        llm_provider = info.data.get('LLM_PROVIDER', 'groq')
        
        # Validar que existe la key del provider configurado
        if llm_provider == 'groq' and field_name == 'GROQ_API_KEY':
            if not v:
                raise ValueError("GROQ_API_KEY required when LLM_PROVIDER=groq")
        elif llm_provider == 'openai' and field_name == 'OPENAI_API_KEY':
            if not v:
                raise ValueError("OPENAI_API_KEY required when LLM_PROVIDER=openai")
        
        return v
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton global
settings = Settings()