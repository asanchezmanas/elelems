# app/services/document_parser.py
from docling.document_converter import DocumentConverter
from pathlib import Path
import tempfile
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Parser universal de documentos usando Docling
    Soporta: PDF, DOCX, PPTX, HTML, MD, TXT
    """
    
    def __init__(self):
        self.converter = DocumentConverter()
    
    async def parse_document(
        self,
        file_bytes: bytes,
        filename: str
    ) -> Dict:
        """
        Parsea documento y extrae contenido estructurado
        
        Args:
            file_bytes: Contenido del archivo
            filename: Nombre del archivo (para determinar tipo)
        
        Returns:
            {
                "text": str,  # Contenido completo
                "sections": List[dict],  # Secciones estructuradas
                "tables": List[dict],  # Tablas extraídas
                "metadata": dict  # Info del documento
            }
        """
        # Guardar temporalmente para Docling
        suffix = Path(filename).suffix
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        
        try:
            logger.info(f"Parsing document: {filename}")
            
            # Docling convierte automáticamente
            result = self.converter.convert(tmp_path)
            
            # Extraer contenido estructurado
            parsed = {
                "text": result.document.export_to_text(),
                "sections": self._extract_sections(result),
                "tables": self._extract_tables(result),
                "metadata": {
                    "filename": filename,
                    "pages": self._get_page_count(result),
                    "format": suffix,
                    "has_tables": len(self._extract_tables(result)) > 0
                }
            }
            
            logger.info(f"Successfully parsed: {filename} ({len(parsed['sections'])} sections)")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing {filename}: {str(e)}")
            raise
        finally:
            # Limpiar archivo temporal
            Path(tmp_path).unlink(missing_ok=True)
    
    def _extract_sections(self, result) -> List[dict]:
        """
        Extrae secciones con estructura jerárquica
        
        Returns:
            Lista de secciones con tipo, contenido y metadata
        """
        sections = []
        
        for item in result.document.iterate_items():
            item_type = item.self_ref.split("/")[1] if "/" in item.self_ref else "unknown"
            
            if item_type == "texts":
                # Párrafo/texto normal
                sections.append({
                    "type": "paragraph",
                    "content": item.text,
                    "page": self._get_item_page(item)
                })
            
            elif item_type.startswith("heading"):
                # Encabezado (h1, h2, etc.)
                level = getattr(item, "level", 1)
                sections.append({
                    "type": "heading",
                    "title": item.text,
                    "level": level,
                    "page": self._get_item_page(item)
                })
        
        return sections
    
    def _extract_tables(self, result) -> List[dict]:
        """
        Extrae tablas en formato markdown
        """
        tables = []
        
        for item in result.document.iterate_items():
            if item.self_ref.startswith("#/tables/"):
                tables.append({
                    "markdown": item.export_to_markdown(),
                    "page": self._get_item_page(item)
                })
        
        return tables
    
    def _get_page_count(self, result) -> Optional[int]:
        """Intenta obtener número de páginas"""
        try:
            return getattr(result.document, 'num_pages', None)
        except:
            return None
    
    def _get_item_page(self, item) -> Optional[int]:
        """Obtiene número de página de un item"""
        try:
            prov = getattr(item, 'prov', [])
            if prov and len(prov) > 0:
                return prov[0].get('page')
        except:
            pass
        return None