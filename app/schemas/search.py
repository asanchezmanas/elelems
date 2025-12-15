# app/schemas/search.py
from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.document import DocType


class SearchRequest(BaseModel):
    """Request para búsqueda semántica"""
    query: str = Field(..., min_length=3, description="Consulta de búsqueda")
    top_k: int = Field(default=5, ge=1, le=20, description="Número de resultados")
    doc_type: Optional[DocType] = Field(None, description="Filtrar por tipo de documento")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "política de devoluciones y reembolsos",
                "top_k": 5,
                "doc_type": "policy",
                "similarity_threshold": 0.75
            }
        }


class SearchResult(BaseModel):
    """Resultado individual de búsqueda"""
    chunk_id: str
    document_id: str
    content: str
    section_title: Optional[str]
    filename: str
    doc_type: str
    similarity: float
    chunk_index: int
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    """Respuesta de búsqueda semántica"""
    results: List[SearchResult]
    total: int
    query: str


class PromptListResponse(BaseModel):
    """Lista de prompts disponibles"""
    prompts: List[dict]
    total: int
