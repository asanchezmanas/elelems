# app/schemas/custom_prompt.py

from pydantic import BaseModel
from typing import List
class CustomPromptCreate(BaseModel):
    name: str
    description: str
    template: str
    variables: List[str]
    temperature: float = 0.7
    max_tokens: int = 1000
    is_public: bool = False  # ¿Compartir con comunidad?

