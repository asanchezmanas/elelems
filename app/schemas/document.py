# app/schemas/document.py
from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class DocType(str, Enum):
    """Tipos de documentos permitidos"""
    POLICY = "policy"
    FAQ = "faq"
    PRODUCT_GUIDE = "product_guide"
    BRAND_GUIDE = "brand_guide"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Estados del procesamiento de documentos"""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentUploadRequest(BaseModel):
    """Request para subir documento"""
    doc_type: DocType
    preserve_sections: bool = True


class DocumentChunkMetadata(BaseModel):
    """Metadata de un chunk"""
    page_number: Optional[int] = None
    section_level: Optional[int] = None
    has_tables: bool = False


class DocumentChunk(BaseModel):
    """Chunk de documento con su vector"""
    id: str
    document_id: str
    content: str
    section_title: Optional[str] = None
    chunk_index: int
    token_count: Optional[int] = None
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """Base para documento"""
    filename: str
    doc_type: DocType


class DocumentCreate(DocumentBase):
    """Crear documento"""
    original_filename: str
    storage_path: str
    file_size_bytes: int
    mime_type: str
    total_pages: Optional[int] = None


class DocumentResponse(DocumentBase):
    """Respuesta con info de documento"""
    id: str
    original_filename: str
    storage_path: str
    file_size_bytes: int
    mime_type: str
    total_pages: Optional[int] = None
    total_chunks: int
    status: DocumentStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentProcessingResult(BaseModel):
    """Resultado del procesamiento de documento"""
    document_id: str
    filename: str
    doc_type: DocType
    total_chunks: int
    status: DocumentStatus
    message: str
    download_url: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Lista de documentos con paginación"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentDeleteResponse(BaseModel):
    """Respuesta al eliminar documento"""
    success: bool
    message: str
    document_id: str

class DocumentUploadResponse(BaseModel):
    """Response inmediata al subir (antes de procesar)"""
    document_id: str
    filename: str
    status: DocumentStatus  # "pending" o "processing"
    message: str
    storage_path: str
    estimated_processing_time_seconds: int  # Estimación según tamaño
    webhook_url: Optional[str] = None  # Para notificar cuando termine


class DocumentChunkResponse(BaseModel):
    """Response al consultar chunks de un documento"""
    document_id: str
    filename: str
    total_chunks: int
    chunks: List[DocumentChunk]
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "uuid-xxx",
                "filename": "brand_guide.pdf",
                "total_chunks": 15,
                "chunks": [
                    {
                        "id": "chunk-uuid-1",
                        "content": "Nuestra marca se define por...",
                        "section_title": "Identidad de Marca",
                        "chunk_index": 0,
                        "token_count": 150
                    }
                ]
            }
        }


class DocumentDownloadResponse(BaseModel):
    """Response al solicitar descarga"""
    document_id: str
    filename: str
    download_url: str
    expires_at: datetime
    expires_in_seconds: int
    file_size_mb: float


class DocumentStatsResponse(BaseModel):
    """Stats detalladas de documentos"""
    total_documents: int
    total_chunks: int
    total_size_mb: float
    avg_chunks_per_doc: float
    by_type: Dict[str, int]  # {"policy": 10, "faq": 5}
    by_status: Dict[str, int]  # {"indexed": 40, "failed": 2}
    oldest_document: Optional[datetime]
    newest_document: Optional[datetime]
    most_referenced_document: Optional[str]  # Doc más usado en RAG


class DocumentReprocessRequest(BaseModel):
    """Request para reprocesar documento (si falló)"""
    document_id: str
    force: bool = False  # Forzar incluso si está indexed
    preserve_sections: bool = True
class DocumentUploadRequest(BaseModel):
    doc_type: DocType
    preserve_sections: bool = True
    
    # ✅ AÑADIR:
    custom_metadata: Optional[dict] = None
    webhook_url: Optional[HttpUrl] = None  # Notificar cuando termine
    priority: int = Field(default=5, ge=1, le=10)  # Para queue
    
    @field_validator('custom_metadata')
    @classmethod
    def validate_metadata(cls, v):
        if v and len(v) > 20:
            raise ValueError("Maximum 20 custom metadata fields")
        return v


class DocumentFilter(BaseModel):
    """Filtros para listar documentos"""
    doc_type: Optional[DocType] = None
    status: Optional[DocumentStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    filename_contains: Optional[str] = None
    min_chunks: Optional[int] = None
    max_chunks: Optional[int] = None