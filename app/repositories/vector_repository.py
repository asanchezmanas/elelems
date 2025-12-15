# app/repositories/vector_repository.py
from supabase import Client
from typing import List, Optional
from app.schemas.search import SearchResult


class VectorRepository:
    """
    Maneja chunks de documentos con embeddings vectoriales
    """
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "document_chunks"
    
    async def insert_chunks(
        self,
        chunks: List[dict],
        embeddings: List[List[float]],
        document_id: str
    ) -> List[str]:
        """
        Inserta chunks con sus embeddings
        
        Args:
            chunks: Lista de chunks parseados
            embeddings: Embeddings correspondientes
            document_id: ID del documento padre
        
        Returns:
            Lista de IDs de chunks insertados
        """
        records = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            records.append({
                "document_id": document_id,
                "content": chunk["content"],
                "section_title": chunk.get("section_title"),
                "embedding": embedding,
                "chunk_index": i,
                "token_count": chunk.get("token_count"),
                "page_number": chunk.get("metadata", {}).get("page_number"),
                "metadata": chunk.get("metadata", {})
            })
        
        result = self.client.table(self.table).insert(records).execute()
        return [record["id"] for record in result.data]
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        doc_type: Optional[str] = None,
        threshold: float = 0.7
    ) -> List[SearchResult]:
        """
        Búsqueda por similitud semántica usando pgvector
        
        Args:
            query_embedding: Vector de la consulta
            top_k: Número de resultados
            doc_type: Filtrar por tipo de documento
            threshold: Umbral de similitud (0-1)
        
        Returns:
            Lista de resultados ordenados por similitud
        """
        result = self.client.rpc(
            "match_document_chunks",
            {
                "query_embedding": query_embedding,
                "match_count": top_k,
                "filter_doc_type": doc_type,
                "similarity_threshold": threshold
            }
        ).execute()
        
        return [
            SearchResult(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                content=r["content"],
                section_title=r["section_title"],
                filename=r["filename"],
                doc_type=r["doc_type"],
                similarity=r["similarity"],
                chunk_index=r["chunk_index"],
                metadata=r["metadata"]
            )
            for r in result.data
        ]
    
    async def get_document_chunks(
        self,
        document_id: str
    ) -> List[dict]:
        """
        Obtiene todos los chunks de un documento (para debugging)
        """
        result = self.client.rpc(
            "get_document_chunks",
            {"doc_id": document_id}
        ).execute()
        
        return result.data
    
    async def delete_by_document(self, document_id: str):
        """
        Elimina todos los chunks de un documento
        (normalmente manejado por CASCADE, pero útil para cleanup manual)
        """
        self.client.table(self.table)\
            .delete()\
            .eq("document_id", document_id)\
            .execute()