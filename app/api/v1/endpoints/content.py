# app/api/v1/endpoints/content.py
from fastapi import APIRouter, Depends
from app.services.content_service import ContentService
from app.schemas.content import BlogPostRequest, BlogPostResponse

router = APIRouter()

@router.post("/blog/generate", response_model=BlogPostResponse)
async def generate_blog_post(
    request: BlogPostRequest,
    content_service: ContentService = Depends()
):
    """
    Genera un artículo de blog usando RAG
    
    - Busca documentos relevantes (políticas, posts anteriores)
    - Genera contenido coherente con tu brand voice
    """
    article = await content_service.generate_blog_post(
        topic=request.topic,
        keywords=request.keywords,
        tone=request.tone,  # profesional, casual, técnico
        length=request.length  # short, medium, long
    )
    
    return BlogPostResponse(
        title=article.title,
        content=article.content,
        meta_description=article.meta_description,
        seo_score=article.seo_score
    )