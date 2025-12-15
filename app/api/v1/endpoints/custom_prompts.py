# app/api/v1/endpoints/custom_prompts.py
from fastapi import APIRouter, Depends
from app.schemas.custom_prompt import CustomPromptCreate
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/custom-prompts")
async def create_custom_prompt(
    prompt: CustomPromptCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crea prompt personalizado del usuario"""
    # Guardar en DB
    # Validar template
    # Cargar dinámicamente en PromptLoader