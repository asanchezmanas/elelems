# app/providers/llm/base.py
from abc import ABC, abstractmethod
from typing import List, Optional


class BaseLLMProvider(ABC):
    """Interface abstracta para providers de LLM"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: List[str] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Genera texto usando el LLM
        
        Args:
            prompt: Prompt del usuario
            context: Contexto adicional (de RAG)
            system_message: Mensaje de sistema
            temperature: Creatividad (0-1)
            max_tokens: Tokens máximos de respuesta
        
        Returns:
            Texto generado
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Retorna nombre del modelo usado"""
        pass
