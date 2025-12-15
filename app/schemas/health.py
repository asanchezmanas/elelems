# app/schemas/health.py (NUEVO ARCHIVO)

from pydantic import BaseModel
from typing import Dict, Optional, Field
from datetime import datetime
from enum import Enum


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health de un componente individual"""
    status: ServiceStatus
    response_time_ms: Optional[int] = None
    last_check: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    metadata: Optional[dict] = None


class HealthCheckResponse(BaseModel):
    """Response completo de health check"""
    status: ServiceStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime_seconds: int
    
    components: Dict[str, ComponentHealth] = {
        "database": ComponentHealth(status=ServiceStatus.HEALTHY),
        "storage": ComponentHealth(status=ServiceStatus.HEALTHY),
        "embedding_service": ComponentHealth(status=ServiceStatus.HEALTHY),
        "llm_provider": ComponentHealth(status=ServiceStatus.HEALTHY)
    }
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-12-15T10:30:00Z",
                "version": "1.0.0",
                "uptime_seconds": 86400,
                "components": {
                    "database": {
                        "status": "healthy",
                        "response_time_ms": 12
                    },
                    "llm_provider": {
                        "status": "healthy",
                        "response_time_ms": 450,
                        "metadata": {"model": "llama-3.1-70b"}
                    }
                }
            }
        }