# app/providers/llm/openai_provider.py (opcional, backup)
from openai import AsyncOpenAI
from app.providers.llm.base import BaseLLMProvider
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """Provider para OpenAI API (backup)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini"
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI provider with model: {model}")
    
    async def generate(
        self,
        prompt: str,
        context: List[str] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Genera texto con OpenAI"""
        
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        if context and len(context) > 0:
            context_str = "\n\n---\n\n".join(context)
            messages.append({
                "role": "system",
                "content": f"Contexto relevante:\n\n{context_str}"
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model

