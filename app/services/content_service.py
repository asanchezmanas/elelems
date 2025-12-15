# app/services/content_service.py
from app.prompts.loader import prompt_loader
from app.providers.llm.base import BaseLLMProvider
from app.services.rag_service import RAGService

class ContentService:
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        rag_service: RAGService
    ):
        self.llm = llm_provider
        self.rag = rag_service
    
    async def generate_blog_post(
        self,
        topic: str,
        keywords: list[str],
        tone: str,
        length: str
    ) -> BlogPost:
        # 1. Buscar contexto relevante (posts anteriores, guías de estilo)
        context = await self.rag.search_relevant_docs(
            query=f"{topic} {' '.join(keywords)}",
            doc_types=["blog_post", "style_guide", "brand_voice"]
        )
        
        # 2. Construir prompt
        prompt = self._build_blog_prompt(topic, keywords, tone, length)
        
        # 3. Generar con LLM
        content = await self.llm.generate(prompt, context)
        
        # 4. Post-procesamiento
        return self._parse_blog_post(content)
    
    def _build_blog_prompt(self, topic, keywords, tone, length):
        word_counts = {"short": 500, "medium": 1000, "long": 1500}
        
        return f"""Escribe un artículo de blog sobre: {topic}

Instrucciones:
- Tono: {tone}
- Palabras clave SEO: {', '.join(keywords)}
- Longitud aproximada: {word_counts[length]} palabras
- Incluye: introducción, 3-5 secciones, conclusión
- Formato: Markdown con headers (##, ###)

Artículo:"""