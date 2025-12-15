# app/services/user_api_keys.py
"""
Gestión segura de API keys de usuarios (BYOK - Bring Your Own Keys)
Permite a usuarios usar sus propias keys de Groq/OpenAI
"""
from cryptography.fernet import Fernet
from typing import Optional
from pydantic import BaseModel
import base64
import os


class UserAPIKeysConfig(BaseModel):
    """Configuración de API keys de un usuario"""
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


class UserAPIKeysService:
    """
    Servicio para gestionar API keys encriptadas de usuarios
    
    Security:
    - Keys se almacenan encriptadas en DB
    - Encryption key en variable de entorno
    - Keys nunca se exponen en logs
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Args:
            encryption_key: Fernet key (32 bytes base64)
                           Si None, se genera una nueva (solo para dev)
        """
        if encryption_key is None:
            # ⚠️ Solo para desarrollo - en producción usar env var
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️  Generated encryption key: {encryption_key}")
            print("   Add to .env as: API_KEYS_ENCRYPTION_KEY=...")
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt_key(self, api_key: str) -> str:
        """
        Encripta una API key
        
        Args:
            api_key: API key en texto plano
        
        Returns:
            API key encriptada (base64)
        """
        if not api_key:
            return ""
        
        encrypted = self.cipher.encrypt(api_key.encode())
        return encrypted.decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """
        Desencripta una API key
        
        Args:
            encrypted_key: API key encriptada
        
        Returns:
            API key en texto plano
        """
        if not encrypted_key:
            return ""
        
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {str(e)}")
    
    def encrypt_config(self, config: UserAPIKeysConfig) -> dict:
        """
        Encripta todas las keys en una config
        
        Args:
            config: Config con keys en texto plano
        
        Returns:
            Dict con keys encriptadas para guardar en DB
        """
        return {
            "groq_api_key_encrypted": self.encrypt_key(config.groq_api_key) if config.groq_api_key else None,
            "openai_api_key_encrypted": self.encrypt_key(config.openai_api_key) if config.openai_api_key else None,
            "anthropic_api_key_encrypted": self.encrypt_key(config.anthropic_api_key) if config.anthropic_api_key else None
        }
    
    def decrypt_config(self, encrypted_data: dict) -> UserAPIKeysConfig:
        """
        Desencripta config desde DB
        
        Args:
            encrypted_data: Dict con keys encriptadas
        
        Returns:
            UserAPIKeysConfig con keys desencriptadas
        """
        return UserAPIKeysConfig(
            groq_api_key=self.decrypt_key(encrypted_data.get("groq_api_key_encrypted", "")) or None,
            openai_api_key=self.decrypt_key(encrypted_data.get("openai_api_key_encrypted", "")) or None,
            anthropic_api_key=self.decrypt_key(encrypted_data.get("anthropic_api_key_encrypted", "")) or None
        )
    
    def validate_groq_key(self, api_key: str) -> bool:
        """
        Valida que una Groq API key sea válida
        
        Args:
            api_key: Groq API key
        
        Returns:
            True si es válida
        """
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            # Test simple
            client.models.list()
            return True
        except Exception:
            return False
    
    def validate_openai_key(self, api_key: str) -> bool:
        """Valida OpenAI API key"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            client.models.list()
            return True
        except Exception:
            return False


# app/repositories/user_keys_repository.py
"""Repository para gestionar API keys en Supabase"""
from supabase import Client
from typing import Optional


class UserKeysRepository:
    """Gestiona API keys de usuarios en DB"""
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.table = "user_api_keys"
    
    async def get_user_keys(self, user_id: str) -> Optional[dict]:
        """
        Obtiene keys encriptadas de usuario
        
        Returns:
            Dict con keys encriptadas o None si no existen
        """
        result = self.client.table(self.table)\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        if result.data:
            return result.data[0]
        return None
    
    async def save_user_keys(
        self,
        user_id: str,
        encrypted_keys: dict
    ):
        """
        Guarda o actualiza keys de usuario
        
        Args:
            user_id: ID del usuario
            encrypted_keys: Dict con keys encriptadas
        """
        # Upsert (insert or update)
        data = {
            "user_id": user_id,
            **encrypted_keys,
            "updated_at": "now()"
        }
        
        self.client.table(self.table)\
            .upsert(data)\
            .execute()
    
    async def delete_user_keys(self, user_id: str):
        """Elimina todas las keys de un usuario"""
        self.client.table(self.table)\
            .delete()\
            .eq("user_id", user_id)\
            .execute()


# app/api/v1/endpoints/user_settings.py
"""Endpoints para gestión de API keys de usuario"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.user_api_keys import UserAPIKeysService, UserAPIKeysConfig
from app.repositories.user_keys_repository import UserKeysRepository
from app.core.database import get_supabase
from app.core.config import settings

router = APIRouter()


class SaveAPIKeysRequest(BaseModel):
    """Request para guardar API keys"""
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    validate: bool = True  # Si debe validar keys antes de guardar


class APIKeysResponse(BaseModel):
    """Response con status de API keys (sin exponer las keys)"""
    has_groq_key: bool
    has_openai_key: bool
    groq_key_valid: Optional[bool] = None
    openai_key_valid: Optional[bool] = None


# Singleton de servicio
_keys_service = None

def get_keys_service() -> UserAPIKeysService:
    global _keys_service
    if _keys_service is None:
        encryption_key = getattr(settings, 'API_KEYS_ENCRYPTION_KEY', None)
        _keys_service = UserAPIKeysService(encryption_key)
    return _keys_service


@router.post("/api-keys", response_model=APIKeysResponse)
async def save_api_keys(
    request: SaveAPIKeysRequest,
    user_id: str,  # TODO: Obtener de auth token
    keys_service: UserAPIKeysService = Depends(get_keys_service),
    supabase: Client = Depends(get_supabase)
):
    """
    Guarda API keys del usuario (encriptadas)
    
    **BYOK (Bring Your Own Keys)**
    - Usuario puede usar sus propias keys de Groq/OpenAI
    - Keys se almacenan encriptadas
    - Opcionalmente se validan antes de guardar
    """
    
    # Validar keys si se solicita
    if request.validate:
        if request.groq_api_key:
            if not keys_service.validate_groq_key(request.groq_api_key):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Groq API key"
                )
        
        if request.openai_api_key:
            if not keys_service.validate_openai_key(request.openai_api_key):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid OpenAI API key"
                )
    
    # Encriptar y guardar
    config = UserAPIKeysConfig(
        groq_api_key=request.groq_api_key,
        openai_api_key=request.openai_api_key
    )
    
    encrypted = keys_service.encrypt_config(config)
    
    repo = UserKeysRepository(supabase)
    await repo.save_user_keys(user_id, encrypted)
    
    return APIKeysResponse(
        has_groq_key=bool(request.groq_api_key),
        has_openai_key=bool(request.openai_api_key),
        groq_key_valid=True if request.groq_api_key and request.validate else None,
        openai_key_valid=True if request.openai_api_key and request.validate else None
    )


@router.get("/api-keys", response_model=APIKeysResponse)
async def get_api_keys_status(
    user_id: str,  # TODO: Obtener de auth token
    supabase: Client = Depends(get_supabase),
    keys_service: UserAPIKeysService = Depends(get_keys_service)
):
    """
    Obtiene status de API keys (sin exponer las keys reales)
    
    Retorna si el usuario tiene keys configuradas
    """
    repo = UserKeysRepository(supabase)
    encrypted_data = await repo.get_user_keys(user_id)
    
    if not encrypted_data:
        return APIKeysResponse(
            has_groq_key=False,
            has_openai_key=False
        )
    
    # Desencriptar para verificar
    config = keys_service.decrypt_config(encrypted_data)
    
    return APIKeysResponse(
        has_groq_key=bool(config.groq_api_key),
        has_openai_key=bool(config.openai_api_key)
    )


@router.delete("/api-keys")
async def delete_api_keys(
    user_id: str,  # TODO: Obtener de auth token
    supabase: Client = Depends(get_supabase)
):
    """Elimina todas las API keys del usuario"""
    repo = UserKeysRepository(supabase)
    await repo.delete_user_keys(user_id)
    
    return {"message": "API keys deleted successfully"}


# SQL para crear tabla (ejecutar en Supabase)
"""
-- Tabla para almacenar API keys encriptadas de usuarios
CREATE TABLE IF NOT EXISTS user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE,
    groq_api_key_encrypted TEXT,
    openai_api_key_encrypted TEXT,
    anthropic_api_key_encrypted TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Foreign key si tienes tabla de users
    -- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Índice para búsquedas rápidas
CREATE INDEX idx_user_api_keys_user_id ON user_api_keys(user_id);

-- Trigger para updated_at
CREATE TRIGGER update_user_api_keys_updated_at
    BEFORE UPDATE ON user_api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""