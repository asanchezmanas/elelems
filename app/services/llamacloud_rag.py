# app/services/llamacloud_rag.py
from llama_cloud import LlamaCloud
from typing import List

class LlamaCloudRAG:
    """
    Wrapper de LlamaCloud para RAG avanzado
    - Maneja chunking automático
    - RAPTOR (clustering jerárquico)
    - Parsing de docs (PDF, DOCX, etc.)
    """
    
    def __init__(self, api_key: str):
        self.client = LlamaCloud(api_key=api_key)
        self.index_id = None  # Se crea al subir primer doc
    
    async def upload_document(
        self,
        file_path: str,
        metadata: dict = None
    ) -> str:
        """
        Sube y procesa documento
        LlamaCloud hace automáticamente:
        - Parsing (PDF, DOCX, HTML, etc.)
        - Chunking inteligente
        - Embeddings
        - Indexación RAPTOR
        """
        doc = await self.client.upload(
            file_path=file_path,
            metadata=metadata or {}
        )
        
        if not self.index_id:
            # Crear índice en primer upload
            self.index_id = await self.client.create_index(
                name="ecommerce_knowledge",
                index_type="raptor"  # Clustering jerárquico
            )
        
        await self.client.add_to_index(
            index_id=self.index_id,
            document_ids=[doc.id]
        )
        
        return doc.id
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict = None
    ) -> List[dict]:
        """
        Búsqueda semántica con RAPTOR
        - Busca en chunks individuales
        - Y en resúmenes jerárquicos
        """
        results = await self.client.query(
            index_id=self.index_id,
            query=query,
            top_k=top_k,
            filters=filters
        )
        
        return [
            {
                "content": r.text,
                "score": r.score,
                "metadata": r.metadata,
                "source": r.source_file
            }
            for r in results
        ]
    
    async def delete_document(self, doc_id: str):
        """Elimina documento del índice"""
        await self.client.delete_document(doc_id)
