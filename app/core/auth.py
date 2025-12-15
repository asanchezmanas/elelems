# ============================================
# app/core/auth.py (CORREGIDO)
# ============================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import jwt
from app.core.database import get_supabase
from app.core.config import settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> dict:
    """
    Valida JWT token de Supabase Auth
    
    ✅ CORREGIDO: Usa verificación correcta de JWT
    """
    try:
        token = credentials.credentials
        
        # ✅ Método correcto: Verificar JWT directamente
        # El token de Supabase es un JWT estándar
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,  # ✅ Añadir a settings
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # ✅ Opcionalmente, verificar con Supabase
        # user_response = supabase.auth.admin.get_user_by_id(user_id)
        
        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated")
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
