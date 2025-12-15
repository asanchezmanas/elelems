# app/providers/llm/factory.py
from app.providers.llm.base import BaseLLMProvider
from app.providers.llm.groq_provider import GroqProvider
from app.providers.llm.openai_provider import OpenAIProvider
from app.core.config import settings


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory pattern para obtener el provider configurado
    Cambia provider editando .env (LLM_PROVIDER=groq|openai)
    """
    
    if settings.LLM_PROVIDER == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        
        return GroqProvider(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL
        )
    
    elif settings.LLM_PROVIDER == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
    
    else:
        raise ValueError(
            f"Unknown LLM provider: {settings.LLM_PROVIDER}. "
            "Use 'groq' or 'openai'"
        )