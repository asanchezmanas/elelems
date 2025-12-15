# app/services/usage_tracking.py
"""
Sistema de tracking de uso y enforcement de quotas por tier
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from supabase import Client


class SubscriptionTier(str, Enum):
    """Tiers de suscripción"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class TierLimits(BaseModel):
    """Límites por tier"""
    max_documents: int
    max_generations_per_month: int
    max_users: int
    max_file_size_mb: int
    has_priority_support: bool
    includes_api_keys: bool  # Si incluye APIs o es BYOK


# Configuración de límites por tier
TIER_LIMITS = {
    SubscriptionTier.FREE: TierLimits(
        max_documents=25,
        max_generations_per_month=100,
        max_users=1,
        max_file_size_mb=5,
        has_priority_support=False,
        includes_api_keys=False  # BYOK
    ),
    SubscriptionTier.STARTER: TierLimits(
        max_documents=200,
        max_generations_per_month=500,
        max_users=3,
        max_file_size_mb=10,
        has_priority_support=False,
        includes_api_keys=False  # BYOK
    ),
    SubscriptionTier.PRO: TierLimits(
        max_documents=1000,
        max_generations_per_month=3000,
        max_users=10,
        max_file_size_mb=25,
        has_priority_support=True,
        includes_api_keys=True  # APIs incluidas
    ),
    SubscriptionTier.BUSINESS: TierLimits(
        max_documents=10000,
        max_generations_per_month=10000,
        max_users=25,
        max_file_size_mb=50,
        has_priority_support=True,
        includes_api_keys=True
    ),
    SubscriptionTier.ENTERPRISE: TierLimits(
        max_documents=999999,  # "Unlimited"
        max_generations_per_month=999999,
        max_users=999999,
        max_file_size_mb=100,
        has_priority_support=True,
        includes_api_keys=True
    )
}


class UsageStats(BaseModel):
    """Estadísticas de uso de un usuario en un mes"""
    user_id: str
    month: str  # "2024-12"
    documents_stored: int = 0
    generations_count: int = 0
    api_calls: int = 0
    storage_used_mb: float = 0.0
    tier: SubscriptionTier


class QuotaExceededError(Exception):
    """Error cuando se excede quota"""
    def __init__(self, message: str, upgrade_url: str = None):
        self.message = message
        self.upgrade_url = upgrade_url
        super().__init__(self.message)


class UsageTrackingService:
    """
    Servicio para tracking de uso y enforcement de quotas
    """
    
    def __init__(self, supabase: Client):
        self.client = supabase
        self.usage_table = "usage_stats"
        self.subscriptions_table = "user_subscriptions"
    
    async def get_user_tier(self, user_id: str) -> SubscriptionTier:
        """
        Obtiene tier de suscripción del usuario
        
        Returns:
            SubscriptionTier del usuario
        """
        result = self.client.table(self.subscriptions_table)\
            .select("tier")\
            .eq("user_id", user_id)\
            .execute()
        
        if result.data:
            return SubscriptionTier(result.data[0]["tier"])
        
        # Default a FREE si no tiene suscripción
        return SubscriptionTier.FREE
    
    async def get_current_usage(
        self,
        user_id: str,
        month: Optional[str] = None
    ) -> UsageStats:
        """
        Obtiene uso actual del usuario en el mes
        
        Args:
            user_id: ID del usuario
            month: Mes en formato "YYYY-MM" (default: mes actual)
        
        Returns:
            UsageStats con uso actual
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        
        result = self.client.table(self.usage_table)\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("month", month)\
            .execute()
        
        if result.data:
            tier = await self.get_user_tier(user_id)
            return UsageStats(**result.data[0], tier=tier)
        
        # Crear registro si no existe
        tier = await self.get_user_tier(user_id)
        return UsageStats(
            user_id=user_id,
            month=month,
            tier=tier
        )
    
    async def check_quota(
        self,
        user_id: str,
        resource: str,  # "documents", "generations", "storage"
        amount: int = 1
    ) -> bool:
        """
        Verifica si usuario puede usar un recurso
        
        Args:
            user_id: ID del usuario
            resource: Tipo de recurso a verificar
            amount: Cantidad a consumir
        
        Returns:
            True si está dentro de quota
        
        Raises:
            QuotaExceededError si excede quota
        """
        tier = await self.get_user_tier(user_id)
        limits = TIER_LIMITS[tier]
        usage = await self.get_current_usage(user_id)
        
        if resource == "documents":
            current = usage.documents_stored
            limit = limits.max_documents
            
            if current + amount > limit:
                raise QuotaExceededError(
                    f"Document limit exceeded. Current: {current}/{limit}. "
                    f"Upgrade to store more documents.",
                    upgrade_url="/upgrade"
                )
        
        elif resource == "generations":
            current = usage.generations_count
            limit = limits.max_generations_per_month
            
            if current + amount > limit:
                raise QuotaExceededError(
                    f"Generation limit exceeded. Used: {current}/{limit} this month. "
                    f"Resets on {self._get_reset_date()}. Upgrade for more.",
                    upgrade_url="/upgrade"
                )
        
        elif resource == "storage":
            current = usage.storage_used_mb
            limit = limits.max_file_size_mb
            
            if amount > limit:
                raise QuotaExceededError(
                    f"File too large. Max size for {tier.value}: {limit}MB. "
                    f"Upgrade for larger files.",
                    upgrade_url="/upgrade"
                )
        
        return True
    
    async def increment_usage(
        self,
        user_id: str,
        resource: str,
        amount: int = 1
    ):
        """
        Incrementa contador de uso
        
        Args:
            user_id: ID del usuario
            resource: Tipo de recurso ("documents", "generations", etc.)
            amount: Cantidad a incrementar
        """
        month = datetime.now().strftime("%Y-%m")
        
        # Verificar si existe registro
        usage = await self.get_current_usage(user_id, month)
        
        # Preparar update
        updates = {"month": month, "user_id": user_id}
        
        if resource == "documents":
            updates["documents_stored"] = usage.documents_stored + amount
        elif resource == "generations":
            updates["generations_count"] = usage.generations_count + amount
        elif resource == "api_calls":
            updates["api_calls"] = usage.api_calls + amount
        
        # Upsert
        self.client.table(self.usage_table)\
            .upsert(updates)\
            .execute()
    
    async def get_usage_percentage(
        self,
        user_id: str,
        resource: str
    ) -> float:
        """
        Obtiene porcentaje de uso de un recurso
        
        Returns:
            Porcentaje de 0-100
        """
        tier = await self.get_user_tier(user_id)
        limits = TIER_LIMITS[tier]
        usage = await self.get_current_usage(user_id)
        
        if resource == "documents":
            return (usage.documents_stored / limits.max_documents) * 100
        elif resource == "generations":
            return (usage.generations_count / limits.max_generations_per_month) * 100
        
        return 0.0
    
    def _get_reset_date(self) -> str:
        """Retorna fecha de reset del mes (1er día del próximo mes)"""
        now = datetime.now()
        next_month = now.month + 1 if now.month < 12 else 1
        year = now.year if now.month < 12 else now.year + 1
        return f"{year}-{next_month:02d}-01"


# app/middleware/quota_middleware.py
"""
Middleware para verificar quotas automáticamente
"""
from fastapi import Request, HTTPException
from app.services.usage_tracking import UsageTrackingService, QuotaExceededError


async def check_quota_middleware(
    request: Request,
    user_id: str,
    resource: str,
    amount: int = 1
):
    """
    Middleware helper para verificar quotas
    
    Usage en endpoints:
        await check_quota_middleware(request, user_id, "generations")
    """
    usage_service = UsageTrackingService(request.app.state.supabase)
    
    try:
        await usage_service.check_quota(user_id, resource, amount)
    except QuotaExceededError as e:
        raise HTTPException(
            status_code=429,  # Too Many Requests
            detail={
                "error": "quota_exceeded",
                "message": e.message,
                "upgrade_url": e.upgrade_url
            }
        )


# app/api/v1/endpoints/usage.py
"""
Endpoints para consultar uso y quotas
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.usage_tracking import UsageTrackingService, SubscriptionTier, TIER_LIMITS
from app.core.database import get_supabase

router = APIRouter()


class UsageResponse(BaseModel):
    """Response con info de uso"""
    tier: SubscriptionTier
    current_usage: dict
    limits: dict
    usage_percentages: dict
    reset_date: str


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    user_id: str,  # TODO: Obtener de auth token
    supabase = Depends(get_supabase)
):
    """
    Obtiene uso actual y límites del usuario
    
    **Útil para:**
    - Mostrar barras de progreso en UI
    - Avisar cuando se acerque al límite
    - Mostrar cuándo resetea
    """
    service = UsageTrackingService(supabase)
    
    tier = await service.get_user_tier(user_id)
    usage = await service.get_current_usage(user_id)
    limits = TIER_LIMITS[tier]
    
    # Calcular porcentajes
    doc_percentage = await service.get_usage_percentage(user_id, "documents")
    gen_percentage = await service.get_usage_percentage(user_id, "generations")
    
    return UsageResponse(
        tier=tier,
        current_usage={
            "documents": usage.documents_stored,
            "generations": usage.generations_count,
            "api_calls": usage.api_calls
        },
        limits={
            "documents": limits.max_documents,
            "generations": limits.max_generations_per_month,
            "users": limits.max_users,
            "file_size_mb": limits.max_file_size_mb
        },
        usage_percentages={
            "documents": round(doc_percentage, 1),
            "generations": round(gen_percentage, 1)
        },
        reset_date=service._get_reset_date()
    )


# SQL para crear tablas (ejecutar en Supabase)
"""
-- Tabla de suscripciones de usuarios
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE,
    tier TEXT NOT NULL DEFAULT 'free',
    stripe_subscription_id TEXT,
    stripe_customer_id TEXT,
    status TEXT DEFAULT 'active',  -- active, canceled, past_due
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_tier CHECK (tier IN ('free', 'starter', 'pro', 'business', 'enterprise')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'canceled', 'past_due', 'incomplete'))
);

-- Tabla de estadísticas de uso
CREATE TABLE IF NOT EXISTS usage_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    month TEXT NOT NULL,  -- "2024-12"
    documents_stored INT DEFAULT 0,
    generations_count INT DEFAULT 0,
    api_calls INT DEFAULT 0,
    storage_used_mb FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, month)
);

-- Índices
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_usage_stats_user_month ON usage_stats(user_id, month);
CREATE INDEX idx_user_subscriptions_tier ON user_subscriptions(tier);

-- Trigger para updated_at
CREATE TRIGGER update_user_subscriptions_updated_at
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usage_stats_updated_at
    BEFORE UPDATE ON usage_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""