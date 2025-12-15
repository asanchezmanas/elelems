# app/api/v1/deps.py
from app.core.database import get_supabase
from app.services.document_parser import DocumentParser
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import get_embedding_service
from app.services.rag_service import RAGService
from app.services.generation_service import GenerationService
from app.repositories.storage_repository import StorageRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.vector_repository import VectorRepository
from app.providers.llm.groq_provider import get_llm_provider
from app.prompts.loader import get_prompt_loader


# Singletons para servicios pesados
_rag_service = None
_generation_service = None


def get_rag_service() -> RAGService:
    """
    Dependencia para inyectar RAGService
    Crea una instancia singleton para reutilizar
    """
    global _rag_service
    
    if _rag_service is None:
        supabase = get_supabase()
        
        _rag_service = RAGService(
            parser=DocumentParser(),
            chunker=ChunkingService(),
            embedder=get_embedding_service(),
            storage_repo=StorageRepository(supabase),
            doc_repo=DocumentRepository(supabase),
            vector_repo=VectorRepository(supabase)
        )
    
    return _rag_service


def get_generation_service() -> GenerationService:
    """
    Dependencia para inyectar GenerationService
    """
    global _generation_service
    
    if _generation_service is None:
        _generation_service = GenerationService(
            llm_provider=get_llm_provider(),
            rag_service=get_rag_service(),
            prompt_loader=get_prompt_loader()
        )
    
    return _generation_service