# app/schemas/document.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
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