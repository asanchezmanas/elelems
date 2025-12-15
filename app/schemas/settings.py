# app/schemas/settings.py (NUEVO ARCHIVO)

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserPreferences(BaseModel):
    """Preferencias del usuario"""
    default_doc_type: Optional[str] = None
    default_prompt_temperature: float = 0.7
    default_rag_top_k: int = 5
    preferred_model: Optional[str] = None
    auto_save_generations: bool = True
    email_notifications: bool = True
    language: str = "es"


class WorkspaceSettings(BaseModel):
    """Settings de workspace/equipo"""
    name: str
    default_tone: str = "professional"
    brand_keywords: List[str] = []
    custom_instructions: Optional[str] = None
    allowed_doc_types: List[str] = ["policy", "faq", "product_guide", "brand_guide"]
    max_file_size_mb: int = 10


class APIKeySettings(BaseModel):
    """Settings de API keys (sin exponer keys reales)"""
    has_groq_key: bool = False
    has_openai_key: bool = False
    has_anthropic_key: bool = False
    groq_key_valid: Optional[bool] = None
    openai_key_valid: Optional[bool] = None
    last_validated: Optional[datetime] = None