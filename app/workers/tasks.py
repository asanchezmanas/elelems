# app/workers/tasks.py
from celery import Celery

celery_app = Celery(
    "rag_ecommerce",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task
def process_document_async(
    file_path: str,
    doc_type: str,
    user_id: str
):
    """Procesa documento en background"""
    # Parsing, chunking, embedding puede tomar minutos
    # No bloquear el endpoint
    
@celery_app.task
def batch_generate_descriptions(
    product_ids: List[str]
):
    """Genera descripciones en batch (noche)"""

# En endpoint:
@router.post("/upload")
async def upload_document(...):
    # Subir a storage
    # Crear registro "processing"
    
    # ✅ Procesar async
    process_document_async.delay(file_path, doc_type, user_id)
    
    return {"status": "processing", "job_id": "..."}