# app/api/v1/endpoints/documents.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.services.rag_service import RAGService
from app.schemas.document import DocumentResponse, SearchRequest, SearchResponse
from app.services.generation_service import GenerationService
from app.schemas.generation import GenerateRequest, GenerateResponse

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(..., description="policy, faq, product_guide, brand_guide"),
    preserve_sections: bool = Form(True),
    rag_service: RAGService = Depends()
):
    """
    Sube documento para RAG
    
    - Docling parsea automáticamente PDF, DOCX, etc.
    - Chunking inteligente respetando estructura
    - Embeddings locales (gratis)
    - Storage en Supabase pgvector
    """
    # Validar tipo archivo
    allowed = [".pdf", ".docx", ".pptx", ".txt", ".md", ".html"]
    if not any(file.filename.endswith(ext) for ext in allowed):
        raise HTTPException(400, f"Formato no soportado. Use: {allowed}")
    
    # Leer contenido
    content = await file.read()
    
    # Procesar
    result = await rag_service.ingest_document(
        file_bytes=content,
        filename=file.filename,
        doc_type=doc_type,
        preserve_sections=preserve_sections
    )
    
    return DocumentResponse(**result)

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    rag_service: RAGService = Depends()
):
    """
    Búsqueda semántica en documentos
    """
    results = await rag_service.search(
        query=request.query,
        top_k=request.top_k,
        doc_type=request.doc_type
    )
    
    return SearchResponse(results=results)

@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    rag_service: RAGService = Depends()
):
    """Elimina documento y todos sus chunks"""
    await rag_service.delete_document(filename)
    return {"message": f"Documento {filename} eliminado"}

# app/api/v1/endpoints/generate.py
@router.post("/generate", response_model=GenerateResponse)
async def generate_with_rag(
    request: GenerateRequest,
    gen_service: GenerationService = Depends(),
    rag_service: RAGService = Depends()
):
    """
    Genera contenido con RAG gratuito
    """
    # 1. Buscar contexto relevante
    context_docs = []
    if request.use_rag:
        rag_query = request.rag_query or request.variables.get("product_name", "")
        results = await rag_service.search(
            query=rag_query,
            top_k=3,
            doc_type=request.doc_type_filter
        )
        context_docs = [r["content"] for r in results]
    
    # 2. Añadir contexto a variables
    if context_docs:
        request.variables["brand_context"] = "\n\n".join(context_docs)
    
    # 3. Generar
    result = await gen_service.generate(
        prompt_name=request.prompt_name,
        variables=request.variables
    )
    
    return GenerateResponse(
        content=result,
        sources=[r["filename"] for r in results] if context_docs else []
    )