# app/repositories/document_repository.py
from supabase import Client
from typing import List, Optional
from datetime import datetime
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentStatus


class DocumentRepository:
    """
    Maneja la metadata de documentos en PostgreSQL
    """
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "documents"
    
    async def create(self, document: DocumentCreate) -> str:
        """
        Crea registro de documento
        
        Returns:
            ID del documento creado
        """
        data = document.model_dump()
        result = self.client.table(self.table).insert(data).execute()
        return result.data[0]["id"]
    
    async def get_by_id(self, document_id: str) -> Optional[DocumentResponse]:
        """Obtiene documento por ID"""
        result = self.client.table(self.table)\
            .select("*")\
            .eq("id", document_id)\
            .execute()
        
        if not result.data:
            return None
        
        return DocumentResponse(**result.data[0])
    
    async def get_by_filename(self, filename: str) -> Optional[DocumentResponse]:
        """Obtiene documento por filename único"""
        result = self.client.table(self.table)\
            .select("*")\
            .eq("filename", filename)\
            .execute()
        
        if not result.data:
            return None
        
        return DocumentResponse(**result.data[0])
    
    async def list_documents(
        self,
        doc_type: Optional[str] = None,
        status: Optional[DocumentStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[DocumentResponse], int]:
        """
        Lista documentos con filtros y paginación
        
        Returns:
            tuple[documentos, total_count]
        """
        query = self.client.table(self.table).select("*", count="exact")
        
        # Aplicar filtros
        if doc_type:
            query = query.eq("doc_type", doc_type)
        if status:
            query = query.eq("status", status.value)
        
        # Paginación y orden
        result = query\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        documents = [DocumentResponse(**doc) for doc in result.data]
        total = result.count if result.count else 0
        
        return documents, total
    
    async def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        total_chunks: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Actualiza estado de procesamiento"""
        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if total_chunks is not None:
            update_data["total_chunks"] = total_chunks
        
        if error_message:
            update_data["error_message"] = error_message
        
        self.client.table(self.table)\
            .update(update_data)\
            .eq("id", document_id)\
            .execute()
    
    async def delete(self, document_id: str):
        """
        Elimina documento (cascade eliminará chunks automáticamente)
        """
        self.client.table(self.table)\
            .delete()\
            .eq("id", document_id)\
            .execute()
    
    async def get_stats(self) -> dict:
        """Obtiene estadísticas de documentos"""
        result = self.client.rpc("get_document_stats").execute()
        
        if result.data:
            return result.data[0]
        
        return {
            "total_documents": 0,
            "total_chunks": 0,
            "total_size_mb": 0,
            "avg_chunks_per_doc": 0,
            "doc_types": {}
        }