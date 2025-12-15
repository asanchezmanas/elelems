# app/providers/llm/groq_provider.py
from groq import AsyncGroq
from app.providers.llm.base import BaseLLMProvider
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """
    Provider para Groq API
    - Gratis (6000 requests/día)
    - Muy rápido
    - Llama 3.1 70B disponible
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile"
    ):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Groq provider with model: {model}")
    
    async def generate(
        self,
        prompt: str,
        context: List[str] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Genera texto con Groq"""
        
        # Construir mensajes
        messages = []
        
        # System message (si existe)
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Contexto de RAG (si existe)
        if context and len(context) > 0:
            context_str = "\n\n---\n\n".join(context)
            messages.append({
                "role": "system",
                "content": f"Contexto relevante para tu respuesta:\n\n{context_str}"
            })
        
        # Prompt del usuario
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Llamar a Groq API
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_text = response.choices[0].message.content
            
            logger.info(f"Generated {len(generated_text)} characters")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model

