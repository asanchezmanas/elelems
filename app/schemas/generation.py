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

class PromptInfo(BaseModel):
    """Info detallada de un prompt"""
    name: str
    description: Optional[str] = None
    variables: List[str]
    required_variables: List[str]
    optional_variables: List[str] = []
    system_message: Optional[str] = None
    temperature: float
    max_tokens: int
    supports_rag: bool = True
    example_usage: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "product_description",
                "variables": ["product_name", "category", "features", "price"],
                "required_variables": ["product_name", "features"],
                "temperature": 0.8,
                "supports_rag": True
            }
        }


class GenerateResponseDetailed(GenerateResponse):
    """Response extendida con metadata útil"""
    generation_time_ms: int  # Tiempo que tomó generar
    prompt_tokens: int  # Tokens del prompt
    completion_tokens: int  # Tokens de la respuesta
    total_tokens: int
    estimated_cost_usd: float  # Costo aproximado
    rag_chunks_used: int = 0  # Cuántos chunks se usaron
    confidence_score: Optional[float] = None  # Si el modelo lo provee
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Descripción generada...",
                "prompt_name": "product_description",
                "generation_time_ms": 1234,
                "prompt_tokens": 450,
                "completion_tokens": 320,
                "total_tokens": 770,
                "estimated_cost_usd": 0.00154,
                "rag_chunks_used": 3,
                "sources": ["brand_guide.pdf"]
            }
        }


class GenerateError(BaseModel):
    """Error detallado cuando falla generación"""
    error_code: str  # "quota_exceeded", "invalid_prompt", "llm_error"
    message: str
    details: Optional[dict] = None
    retry_after: Optional[int] = None  # Segundos hasta poder reintentar