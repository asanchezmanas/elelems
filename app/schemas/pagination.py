# app/schemas/pagination.py (NUEVO ARCHIVO)

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional
from app.schemas.document import DocumentResponse
from app.schemas.search import SearchResult

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parámetros de paginación reutilizables"""
    page: int = Field(default=1, ge=1, description="Número de página")
    page_size: int = Field(default=20, ge=1, le=100, description="Items por página")
    sort_by: Optional[str] = Field(None, description="Campo para ordenar")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel, Generic[T]):
    """Response genérica paginada"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ):
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


# Ejemplo de uso:
class DocumentListResponsePaginated(PaginatedResponse[DocumentResponse]):
    """Lista de documentos paginada"""
    pass


class SearchResultsPaginated(PaginatedResponse[SearchResult]):
    """Resultados de búsqueda paginados"""
    pass