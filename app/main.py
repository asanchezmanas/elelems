# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.services.embedding_service import EmbeddingService
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
    **RAG Ecommerce API** - Sistema de generación de contenido con RAG
    
    Características:
    - 📄 Parsing de documentos (PDF, DOCX, PPTX, etc.)
    - 🧠 Embeddings locales (gratis, privado)
    - 🔍 Búsqueda semántica en documentos
    - ✨ Generación de contenido con prompts dinámicos
    - 💾 Persistencia de documentos originales
    - 🚀 Stack 100% gratuito hasta escala media
    
    **Stack técnico:**
    - FastAPI + Supabase (Storage + pgvector)
    - Docling (parsing) + sentence-transformers (embeddings)
    - Groq API (LLM gratuito) o OpenAI (backup)
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """
    Inicialización al arrancar
    - Precarga modelo de embeddings
    """
    logger.info(f"Starting {settings.PROJECT_NAME}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    
    # Precargar modelo de embeddings (evita latencia en primera request)
    logger.info("Warming up embedding model...")
    EmbeddingService.warmup()
    logger.info("Embedding model ready")
    
    logger.info(f"{settings.PROJECT_NAME} started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar"""
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check general"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_model": settings.EMBEDDING_MODEL
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )