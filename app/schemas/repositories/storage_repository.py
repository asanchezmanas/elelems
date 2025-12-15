# app/repositories/storage_repository.py
from supabase import Client
from typing import Optional
from pathlib import Path
import uuid
from app.core.config import settings


class StorageRepository:
    """
    Maneja el almacenamiento de documentos originales en Supabase Storage
    """
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.bucket = settings.STORAGE_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Crea el bucket si no existe"""
        try:
            # Intentar crear bucket (falla si ya existe, pero es OK)
            self.client.storage.create_bucket(
                self.bucket,
                options={"public": False}  # Privado por defecto
            )
        except Exception:
            # Bucket ya existe
            pass
    
    async def upload_document(
        self,
        file_bytes: bytes,
        filename: str,
        doc_type: str
    ) -> tuple[str, str]:
        """
        Sube documento a Supabase Storage
        
        Args:
            file_bytes: Contenido del archivo
            filename: Nombre original del archivo
            doc_type: Tipo de documento
        
        Returns:
            tuple[storage_path, unique_filename]
        """
        # Generar nombre único
        file_extension = Path(filename).suffix
        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}{file_extension}"
        
        # Path organizado por tipo de documento
        storage_path = f"{doc_type}/{unique_filename}"
        
        # Subir archivo
        self.client.storage.from_(self.bucket).upload(
            path=storage_path,
            file=file_bytes,
            file_options={
                "content-type": self._get_mime_type(file_extension),
                "x-upsert": "false"  # No sobrescribir
            }
        )
        
        return storage_path, unique_filename
    
    async def download_document(self, storage_path: str) -> bytes:
        """
        Descarga documento desde Storage
        
        Returns:
            Contenido del archivo en bytes
        """
        response = self.client.storage.from_(self.bucket).download(storage_path)
        return response
    
    async def get_public_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Genera URL temporal para descargar documento
        
        Args:
            storage_path: Path del documento en Storage
            expires_in: Segundos hasta que expire (default 1 hora)
        
        Returns:
            URL firmada temporalmente
        """
        response = self.client.storage.from_(self.bucket).create_signed_url(
            path=storage_path,
            expires_in=expires_in
        )
        return response["signedURL"]
    
    async def delete_document(self, storage_path: str):
        """Elimina documento de Storage"""
        self.client.storage.from_(self.bucket).remove([storage_path])
    
    def _get_mime_type(self, extension: str) -> str:
        """Determina MIME type por extensión"""
        mime_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".html": "text/html"
        }
        return mime_types.get(extension.lower(), "application/octet-stream")