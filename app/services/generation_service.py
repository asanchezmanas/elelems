# app/services/generation_service.py
from app.providers.llm.base import BaseLLMProvider
from app.services.rag_service import RAGService
from app.prompts.loader import PromptLoader
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class GenerationService:
    """
    Servicio de generación unificado
    Combina: Prompts dinámicos + LLM + RAG opcional
    """
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        rag_service: RAGService,
        prompt_loader: PromptLoader
    ):
        self.llm = llm_provider
        self.rag = rag_service
        self.prompts = prompt_loader
    
    async def generate(
        self,
        prompt_name: str,
        variables: Dict[str, str],
        use_rag: bool = False,
        rag_query: Optional[str] = None,
        doc_type_filter: Optional[str] = None,
        top_k: int = 5
    ) -> tuple[str, List[str]]:
        """
        Método universal de generación
        
        Args:
            prompt_name: Nombre del template
            variables: Variables para rellenar template
            use_rag: Si debe buscar contexto en documentos
            rag_query: Query custom para RAG (si no, usa variables)
            doc_type_filter: Filtrar por tipo de documento
            top_k: Cuántos documentos recuperar
        
        Returns:
            tuple[contenido_generado, lista_de_fuentes]
        """
        
        # 1. Cargar template
        template = self.prompts.get(prompt_name)
        
        logger.info(f"Generating with prompt: {prompt_name}")
        
        # 2. Validar variables
        missing = template.get_missing_variables(**variables)
        if missing:
            raise ValueError(
                f"Faltan variables requeridas: {missing}. "
                f"Necesarias: {template.variables}"
            )
        
        # 3. Obtener contexto RAG si es necesario
        context_docs = []
        sources = []
        
        if use_rag:
            # Determinar query para RAG
            if rag_query:
                query = rag_query
            else:
                # Usar alguna variable relevante como query
                query = self._extract_rag_query(variables)
            
            logger.info(f"Searching RAG with query: {query[:50]}...")
            
            # Buscar contexto relevante
            results = await self.rag.search(
                query=query,
                top_k=top_k,
                doc_type=doc_type_filter
            )
            
            context_docs = [r.content for r in results]
            sources = list(set([r.filename for r in results]))
            
            logger.info(f"Found {len(results)} relevant chunks from {len(sources)} documents")
            
            # Añadir contexto a variables si hay placeholder
            if "brand_context" in variables and context_docs:
                variables["brand_context"] = "\n\n".join(context_docs[:3])
            elif "{knowledge_base_context}" in template.template and context_docs:
                variables["knowledge_base_context"] = "\n\n".join(context_docs)
        
        # 4. Formatear prompt
        user_prompt = template.format(**variables)
        
        # 5. Generar con LLM
        logger.info(f"Calling LLM: {self.llm.get_model_name()}")
        
        generated_content = await self.llm.generate(
            prompt=user_prompt,
            context=context_docs if use_rag else None,
            system_message=template.system_message,
            temperature=template.temperature,
            max_tokens=template.max_tokens
        )
        
        logger.info(f"Generated {len(generated_content)} characters")
        
        return generated_content, sources
    
    def _extract_rag_query(self, variables: Dict[str, str]) -> str:
        """
        Extrae una query inteligente de las variables
        Prioriza ciertas variables que suelen ser más descriptivas
        """
        priority_keys = [
            "product_name",
            "customer_query",
            "recurring_question",
            "complaint",
            "topic",
            "description"
        ]
        
        # Buscar primera variable de prioridad
        for key in priority_keys:
            if key in variables and variables[key]:
                return variables[key]
        
        # Fallback: concatenar primeras variables
        relevant_vars = []
        for key, value in list(variables.items())[:3]:
            if value and len(value) < 200:  # Evitar textos muy largos
                relevant_vars.append(value)
        
        return " ".join(relevant_vars) if relevant_vars else "información general"
    
    def list_available_prompts(self) -> List[dict]:
        """Lista todos los prompts disponibles"""
        return self.prompts.list_available()