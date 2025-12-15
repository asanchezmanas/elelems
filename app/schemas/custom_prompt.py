
# app/schemas/custom_prompt.py
class CustomPromptCreate(BaseModel):
    name: str
    description: str
    template: str
    variables: List[str]
    temperature: float = 0.7
    max_tokens: int = 1000
    is_public: bool = False  # ¿Compartir con comunidad?

# app/api/v1/endpoints/custom_prompts.py
@router.post("/custom-prompts")
async def create_custom_prompt(
    prompt: CustomPromptCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crea prompt personalizado del usuario"""
    # Guardar en DB
    # Validar template
    # Cargar dinámicamente en PromptLoader