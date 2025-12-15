# app/services/rag_service.py
from app.services.document_parser import DocumentParser
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.schemas.repositories.storage_repository import StorageRepository
from app.schemas.repositories.document_repository import DocumentRepository
from app.schemas.repositories.vector_repository import VectorRepository
from app.schemas.document import DocumentCreate, DocumentStatus, DocumentProcessingResult
from app.schemas.search import SearchResult
from typing import List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGService:
    """
    Servicio RAG completo y gratuito
    
    Pipeline:
    1. Upload → Supabase Storage (documento original)
    2. Parse → Docling (extrae contenido)
    3. Chunk → Chunking inteligente
    4. Embed → sentence-transformers (local)
    5. Store → Supabase pgvector (vectores + metadata)
    """
    
    def __init__(
        self,
        parser: DocumentParser,
        chunker: ChunkingService,
        embedder: EmbeddingService,
        storage_repo: StorageRepository,
        doc_repo: DocumentRepository,
        vector_repo: VectorRepository
    ):
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.storage = storage_repo
        self.doc_repo = doc_repo
        self.vector_repo = vector_repo
    
    async def ingest_document(
        self,
        file_bytes: bytes,
        filename: str,
        doc_type: str,
        preserve_sections: bool = True
    ) -> DocumentProcessingResult:
        """
        Pipeline completo de ingesta de documento
        
        Args:
            file_bytes: Contenido del archivo
            filename: Nombre original
            doc_type: Tipo de documento (policy, faq, etc.)
            preserve_sections: Mantener estructura de secciones
        
        Returns:
            Resultado del procesamiento con ID y metadata
        """
        try:
            logger.info(f"Starting ingestion: {filename}")
            
            # 1. Subir documento original a Storage
            storage_path, unique_filename = await self.storage.upload_document(
                file_bytes=file_bytes,
                filename=filename,
                doc_type=doc_type
            )
            
            logger.info(f"Uploaded to storage: {storage_path}")
            
            # 2. Crear registro en DB
            doc_create = DocumentCreate(
                filename=unique_filename,
                original_filename=filename,
                doc_type=doc_type,
                storage_path=storage_path,
                file_size_bytes=len(file_bytes),
                mime_type=self._get_mime_type(filename)
            )
            
            document_id = await self.doc_repo.create(doc_create)
            
            # Actualizar a "processing"
            await self.doc_repo.update_status(
                document_id=document_id,
                status=DocumentStatus.PROCESSING
            )
            
            logger.info(f"Document created: {document_id}")
            
            # 3. Parse documento
            parsed = await self.parser.parse_document(file_bytes, filename)
            
            # 4. Chunk inteligente
            chunks = self.chunker.chunk_document(parsed, preserve_sections)
            
            logger.info(f"Generated {len(chunks)} chunks")
            
            # 5. Generate embeddings (batch para eficiencia)
            texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embedder.embed_batch(texts)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # 6. Store chunks + vectores
            chunk_ids = await self.vector_repo.insert_chunks(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document_id
            )
            
            logger.info(f"Stored {len(chunk_ids)} chunks in vector DB")
            
            # 7. Actualizar a "indexed"
            await self.doc_repo.update_status(
                document_id=document_id,
                status=DocumentStatus.INDEXED,
                total_chunks=len(chunks)
            )
            
            # 8. Generar URL de descarga (válida 1 hora)
            download_url = await self.storage.get_public_url(storage_path)
            
            logger.info(f"Successfully indexed: {filename}")
            
            return DocumentProcessingResult(
                document_id=document_id,
                filename=filename,
                doc_type=doc_type,
                total_chunks=len(chunks),
                status=DocumentStatus.INDEXED,
                message=f"Documento procesado exitosamente: {len(chunks)} chunks creados",
                download_url=download_url
            )
        
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)
            
            # Actualizar a "failed" si existe document_id
            if 'document_id' in locals():
                await self.doc_repo.update_status(
                    document_id=document_id,
                    status=DocumentStatus.FAILED,
                    error_message=str(e)
                )
            
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        doc_type: Optional[str] = None,
        threshold: float = None
    ) -> List[SearchResult]:
        """
        Búsqueda semántica en documentos indexados
        
        Args:
            query: Consulta en lenguaje natural
            top_k: Número de resultados
            doc_type: Filtrar por tipo de documento
            threshold: Umbral de similitud (0-1)
        
        Returns:
            Lista de chunks relevantes ordenados por similitud
        """
        # 1. Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # 2. Search en vector DB
        results = await self.vector_repo.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            doc_type=doc_type,
            threshold=threshold or 0.7
        )
        
        logger.info(f"Found {len(results)} results for query: '{query[:50]}...'")
        return results
    
    async def delete_document(self, document_id: str):
        """
        Elimina documento completo (Storage + DB + Vectores)
        """
        # 1. Obtener info del documento
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise ValueError(f"Document not found: {document_id}")
        
        # 2. Eliminar de Storage
        await self.storage.delete_document(doc.storage_path)
        
        # 3. Eliminar de DB (CASCADE eliminará chunks automáticamente)
        await self.doc_repo.delete(document_id)
        
        logger.info(f"Deleted document: {doc.filename}")
    
    async def get_document_download_url(
        self,
        document_id: str,
        expires_in: int = 3600
    ) -> str:
        """
        Genera URL temporal para descargar documento original
        
        Args:
            document_id: ID del documento
            expires_in: Segundos hasta expiración
        
        Returns:
            URL firmada temporalmente
        """
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise ValueError(f"Document not found: {document_id}")
        
        return await self.storage.get_public_url(
            storage_path=doc.storage_path,
            expires_in=expires_in
        )
    
    def _get_mime_type(self, filename: str) -> str:
        """Determina MIME type por extensión"""
        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".html": "text/html"
        }
        ext = Path(filename).suffix.lower()
        return mime_types.get(ext, "application/octet-stream")