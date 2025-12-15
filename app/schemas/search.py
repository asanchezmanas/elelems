# app/schemas/search.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
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

class SearchFilters(BaseModel):
    """Filtros avanzados para búsqueda"""
    doc_type: Optional[DocType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)
    exclude_document_ids: List[str] = []
    only_document_ids: Optional[List[str]] = None
    has_section_title: Optional[bool] = None
    page_number: Optional[int] = None


class SearchRequest(BaseModel):
    """Request mejorado"""
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[SearchFilters] = None
    rerank: bool = False  # Re-ranking con modelo más potente
    include_metadata: bool = True
    highlight_matches: bool = False  # Resaltar coincidencias


class SearchResultWithHighlight(SearchResult):
    """Resultado con highlights"""
    highlighted_content: Optional[str] = None  # Con <mark>tags</mark>
    match_score_breakdown: Optional[dict] = None  # {"semantic": 0.85, "keyword": 0.65}