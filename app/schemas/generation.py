# app/schemas/generation.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class GenerateRequest(BaseModel):
    """Request para generar contenido"""
    prompt_name: str = Field(..., description="Nombre del prompt template a usar")
    variables: Dict[str, str] = Field(..., description="Variables para el template")
    use_rag: bool = Field(default=False, description="Si debe usar RAG para contexto")
    rag_query: Optional[str] = Field(None, description="Query custom para RAG")
    doc_type_filter: Optional[str] = Field(None, description="Filtrar por tipo de documento")
    top_k: int = Field(default=5, description="Número de documentos a recuperar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt_name": "product_description",
                "variables": {
                    "product_name": "Zapatillas Running Pro",
                    "category": "Deportes",
                    "features": "Suela de gel, transpirables",
                    "price": "89.99€",
                    "target_audience": "Runners amateur",
                    "tone": "deportivo y motivador"
                },
                "use_rag": True,
                "doc_type_filter": "brand_guide",
                "top_k": 3
            }
        }


class GenerateResponse(BaseModel):
    """Respuesta con contenido generado"""
    content: str
    prompt_name: str
    tokens_used: Optional[int] = None
    sources: List[str] = Field(default_factory=list, description="Archivos usados como contexto")
    model_used: Optional[str] = None

