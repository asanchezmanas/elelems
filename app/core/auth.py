# app/core/auth.py
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import jwt

from app.core.supabase_client import get_supabase
from app.services.rag_service import RAGService, get_rag_service

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> dict:
    """Valida JWT token de Supabase Auth"""
    try:
        token = credentials.credentials
        
        # Verificar con Supabase
        user = supabase.auth.get_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        return user.user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

# Uso en endpoints:
@router.post("/upload")
async def upload_document(
    file: UploadFile,
    current_user: dict = Depends(get_current_user),  # ✅ Proteger endpoint
    rag_service: RAGService = Depends(get_rag_service)
):
    user_id = current_user["id"]
    # Ahora todos los docs tienen user_id