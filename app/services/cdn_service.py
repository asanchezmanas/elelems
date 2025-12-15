# Mover archivos grandes a CDN
# app/services/cdn_service.py
class CDNService:
    """
    Sube archivos procesados a Cloudflare R2 / AWS S3
    
    - Documentos originales en Supabase Storage (privado)
    - PDFs generados, imágenes, exports en CDN (público con firma)
    """
    
    async def upload_to_cdn(
        self,
        file_bytes: bytes,
        path: str,
        content_type: str
    ) -> str:
        """Sube a CDN y retorna URL pública"""