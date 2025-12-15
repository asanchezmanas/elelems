# app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
from typing import List
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embeddings locales con sentence-transformers
    100% gratis y privado
    """
    
    _instance: SentenceTransformer = None
    
    def __init__(self, model_name: str = None):
        """
        Args:
            model_name: Nombre del modelo de sentence-transformers
                - paraphrase-multilingual-MiniLM-L12-v2 (español, dim=384)
                - all-MiniLM-L6-v2 (inglés, más rápido, dim=384)
                - paraphrase-multilingual-mpnet-base-v2 (mejor calidad, dim=768)
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        
        # Cargar modelo (se hace una sola vez y se cachea)
        if EmbeddingService._instance is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            EmbeddingService._instance = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully (dim={self.get_dimension()})")
        
        self.model = EmbeddingService._instance
    
    def embed_text(self, text: str) -> List[float]:
        """
        Genera embedding de un texto
        
        Args:
            text: Texto a embedear
        
        Returns:
            Vector de dimensión self.get_dimension()
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Genera embeddings de múltiples textos (más eficiente)
        
        Args:
            texts: Lista de textos
            batch_size: Tamaño del batch para procesamiento
        
        Returns:
            Lista de vectores
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10,
            batch_size=batch_size
        )
        
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """
        Retorna dimensión del vector
        Importante: debe coincidir con VECTOR(dimension) en PostgreSQL
        """
        return self.model.get_sentence_embedding_dimension()
    
    @classmethod
    def warmup(cls):
        """
        Precarga el modelo (llamar en startup)
        Evita latencia en primera request
        """
        service = cls()
        service.embed_text("warmup")
        logger.info("Embedding model warmed up")


# Singleton global para inyección de dependencias
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Dependencia FastAPI"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service