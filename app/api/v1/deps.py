# ============================================
# app/api/v1/deps.py (CORREGIDO)
# ============================================

from typing import Optional
from app.core.database import get_supabase
from app.services.llamaindex_rag_service import LlamaIndexRAGService
from app.services.generation_service import GenerationService
from app.providers.llm.factory import get_llm_provider
from app.prompts.loader import get_prompt_loader
import logging

logger = logging.getLogger(__name__)

# ✅ Singletons thread-safe
_rag_service: Optional[LlamaIndexRAGService] = None
_generation_service: Optional[GenerationService] = None
_service_lock = None  # Importar threading.Lock si es necesario

def get_rag_service() -> LlamaIndexRAGService:
    """
    Dependencia para inyectar RAGService mejorado
    Thread-safe singleton
    """
    global _rag_service, _service_lock
    
    if _service_lock is None:
        import threading
        _service_lock = threading.Lock()
    
    if _rag_service is None:
        with _service_lock:
            # Double-check locking
            if _rag_service is None:
                logger.info("Initializing LlamaIndexRAGService singleton")
                _rag_service = LlamaIndexRAGService()
    
    return _rag_service


def get_generation_service() -> GenerationService:
    """
    Dependencia para inyectar GenerationService
    Thread-safe singleton
    """
    global _generation_service, _service_lock
    
    if _service_lock is None:
        import threading
        _service_lock = threading.Lock()
    
    if _generation_service is None:
        with _service_lock:
            if _generation_service is None:
                logger.info("Initializing GenerationService singleton")
                _generation_service = GenerationService(
                    llm_provider=get_llm_provider(),
                    rag_service=get_rag_service(),
                    prompt_loader=get_prompt_loader()
                )
    
    return _generation_service

