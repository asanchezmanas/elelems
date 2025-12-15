# app/prompts/loader.py
from typing import Dict, List
from app.prompts.base import PromptTemplate
from app.prompts.templates import product, support
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    Carga y gestiona prompts dinámicamente
    Permite añadir prompts custom en runtime
    """
    
    def __init__(self):
        self._prompts: Dict[str, PromptTemplate] = {}
        self._load_default_prompts()
    
    def _load_default_prompts(self):
        """Carga todos los prompts disponibles por defecto"""
        
        # Productos
        self._prompts["product_description"] = product.PRODUCT_DESCRIPTION
        self._prompts["product_categorization"] = product.PRODUCT_CATEGORIZATION
        self._prompts["meta_tags_generator"] = product.META_TAGS_GENERATOR
        
        # Soporte
        self._prompts["support_response"] = support.SUPPORT_RESPONSE
        self._prompts["faq_generator"] = support.FAQ_GENERATOR
        self._prompts["complaint_response"] = support.COMPLAINT_RESPONSE
        
        # Emails (importar cuando se creen)
        try:
            from app.prompts.templates import email
            self._prompts["email_order_confirmation"] = email.EMAIL_ORDER_CONFIRMATION
            self._prompts["email_shipping_notification"] = email.EMAIL_SHIPPING_NOTIFICATION
            self._prompts["email_abandoned_cart"] = email.EMAIL_ABANDONED_CART
        except ImportError:
            logger.warning("Email templates not found, skipping")
        
        logger.info(f"Loaded {len(self._prompts)} default prompts")
    
    def get(self, prompt_name: str) -> PromptTemplate:
        """
        Obtiene un prompt por nombre
        
        Raises:
            ValueError: Si el prompt no existe
        """
        if prompt_name not in self._prompts:
            available = ", ".join(self._prompts.keys())
            raise ValueError(
                f"Prompt '{prompt_name}' no encontrado. "
                f"Disponibles: {available}"
            )
        return self._prompts[prompt_name]
    
    def list_available(self) -> List[dict]:
        """
        Lista todos los prompts disponibles con metadata
        
        Returns:
            Lista de dicts con info de cada prompt
        """
        return [
            {
                "name": name,
                "variables": prompt.variables,
                "system_message": prompt.system_message[:100] + "..." if prompt.system_message else None,
                "temperature": prompt.temperature,
                "max_tokens": prompt.max_tokens
            }
            for name, prompt in self._prompts.items()
        ]
    
    def add_custom(self, prompt: PromptTemplate):
        """
        Añade un prompt personalizado en runtime
        Útil para A/B testing o personalizaciones por cliente
        """
        if prompt.name in self._prompts:
            logger.warning(f"Overwriting existing prompt: {prompt.name}")
        
        self._prompts[prompt.name] = prompt
        logger.info(f"Added custom prompt: {prompt.name}")
    
    def remove(self, prompt_name: str):
        """Elimina un prompt"""
        if prompt_name in self._prompts:
            del self._prompts[prompt_name]
            logger.info(f"Removed prompt: {prompt_name}")
    
    def reload(self):
        """Recarga todos los prompts desde archivos"""
        self._prompts.clear()
        self._load_default_prompts()
        logger.info("Reloaded all prompts")


# Singleton global
prompt_loader = PromptLoader()


def get_prompt_loader() -> PromptLoader:
    """Dependencia FastAPI"""
    return prompt_loader