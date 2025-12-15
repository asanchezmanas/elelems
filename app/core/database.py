# app/core/database.py
from supabase import create_client, Client
from app.core.config import settings


class SupabaseClient:
    """Cliente Supabase singleton"""
    
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Obtiene o crea el cliente de Supabase"""
        if cls._instance is None:
            cls._instance = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY
            )
        return cls._instance


# Helper para obtener el cliente fácilmente
def get_supabase() -> Client:
    """Dependencia FastAPI para inyectar cliente Supabase"""
    return SupabaseClient.get_client()