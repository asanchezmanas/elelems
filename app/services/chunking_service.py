# app/services/chunking_service.py
import tiktoken
from typing import List, Dict
from app.core.config import settings
import re
import logging

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Chunking inteligente para RAG
    - Respeta límites de oraciones
    - Mantiene contexto con overlap
    - Preserva estructura de secciones
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        # Tokenizer para contar tokens
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def chunk_document(
        self,
        parsed_doc: Dict,
        preserve_sections: bool = True
    ) -> List[Dict]:
        """
        Divide documento en chunks optimizados para RAG
        
        Args:
            parsed_doc: Documento parseado por DocumentParser
            preserve_sections: Si debe mantener secciones intactas
        
        Returns:
            Lista de chunks con metadata
        """
        chunks = []
        
        if preserve_sections and parsed_doc.get("sections"):
            # Chunking por secciones (mejor para docs estructurados)
            chunks = self._chunk_by_sections(parsed_doc)
        else:
            # Chunking por tamaño (mejor para texto continuo)
            chunks = self._chunk_by_size(parsed_doc["text"], parsed_doc["metadata"])
        
        # Añadir metadata común
        for i, chunk in enumerate(chunks):
            chunk["chunk_index"] = i
            chunk["metadata"] = {
                **parsed_doc.get("metadata", {}),
                **chunk.get("metadata", {})
            }
            
            # Calcular token count
            chunk["token_count"] = len(self.tokenizer.encode(chunk["content"]))
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def _chunk_by_sections(self, parsed_doc: Dict) -> List[Dict]:
        """Chunking respetando estructura de secciones"""
        chunks = []
        current_section = None
        current_content = []
        current_tokens = 0
        current_page = None
        
        for item in parsed_doc["sections"]:
            if item["type"] == "heading":
                # Guardar sección anterior si existe
                if current_content:
                    chunks.append({
                        "content": "\n\n".join(current_content),
                        "section_title": current_section,
                        "metadata": {"page_number": current_page}
                    })
                    current_content = []
                    current_tokens = 0
                
                # Empezar nueva sección
                current_section = item["title"]
                current_page = item.get("page")
                current_content.append(f"## {item['title']}")
                current_tokens += len(self.tokenizer.encode(item["title"]))
            
            elif item["type"] == "paragraph":
                text = item["content"]
                tokens = len(self.tokenizer.encode(text))
                
                # Si supera el límite, crear nuevo chunk
                if current_tokens + tokens > self.chunk_size and current_content:
                    chunks.append({
                        "content": "\n\n".join(current_content),
                        "section_title": current_section,
                        "metadata": {"page_number": current_page}
                    })
                    
                    # Overlap: mantener título de sección + última parte
                    overlap_content = []
                    if current_section:
                        overlap_content.append(f"## {current_section}")
                    
                    if len(current_content) > 1:
                        # Mantener último párrafo para contexto
                        last_para = current_content[-1]
                        sentences = self._split_sentences(last_para)
                        if len(sentences) > 1:
                            overlap = ". ".join(sentences[-2:])
                            overlap_content.append(overlap)
                    
                    current_content = overlap_content
                    current_tokens = sum(len(self.tokenizer.encode(c)) for c in overlap_content)
                
                current_content.append(text)
                current_tokens += tokens
                
                # Actualizar página si está disponible
                if item.get("page"):
                    current_page = item["page"]
        
        # Guardar último chunk
        if current_content:
            chunks.append({
                "content": "\n\n".join(current_content),
                "section_title": current_section,
                "metadata": {"page_number": current_page}
            })
        
        return chunks
    
    def _chunk_by_size(self, text: str, metadata: Dict) -> List[Dict]:
        """Chunking simple por tamaño con overlap"""
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            tokens = len(self.tokenizer.encode(sentence))
            
            if current_tokens + tokens > self.chunk_size and current_chunk:
                # Guardar chunk actual
                chunks.append({
                    "content": " ".join(current_chunk),
                    "section_title": None,
                    "metadata": metadata
                })
                
                # Overlap: mantener últimas oraciones
                overlap_sentences = []
                overlap_tokens = 0
                for s in reversed(current_chunk):
                    s_tokens = len(self.tokenizer.encode(s))
                    if overlap_tokens + s_tokens <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_tokens = overlap_tokens
            
            current_chunk.append(sentence)
            current_tokens += tokens
        
        # Último chunk
        if current_chunk:
            chunks.append({
                "content": " ".join(current_chunk),
                "section_title": None,
                "metadata": metadata
            })
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split en oraciones (español e inglés)
        Mejora: usar spacy para splitting más preciso
        """
        # Regex para español: respeta abreviaciones comunes
        pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]