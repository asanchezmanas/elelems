# app/api/v1/endpoints/generate.py
from fastapi import APIRouter, Depends
from app.services.generation_service import GenerationService
from app.schemas.generation import GenerateRequest, GenerateResponse

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    gen_service: GenerationService = Depends()
):
    """
    Endpoint universal de generación
    
    Ejemplos:
    - prompt_name: "product_description"
    - prompt_name: "email_order_confirmation"
    - prompt_name: "support_response"
    """
    result = await gen_service.generate(
        prompt_name=request.prompt_name,
        variables=request.variables,
        use_rag=request.use_rag,
        rag_query=request.rag_query
    )
    
    return GenerateResponse(
        prompt_name=request.prompt_name,
        content=result,
        tokens_used=len(result.split())  # Estimación
    )

# Ejemplo de uso
"""
POST /api/v1/generate

{
  "prompt_name": "product_description",
  "variables": {
    "product_name": "Zapatillas Running Pro",
    "category": "Deportes",
    "features": "Suela de gel, transpirables, ligeras",
    "price": "89.99€",
    "target_audience": "Runners amateur",
    "tone": "deportivo y motivador",
    "brand_context": ""  # Se llena automático con RAG
  },
  "use_rag": true,
  "rag_query": "estilo de marca zapatillas"
}
"""