# app/schemas/webhooks.py (NUEVO ARCHIVO)

from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal, List, Field
from datetime import datetime


class WebhookConfig(BaseModel):
    """Configuración de webhook"""
    url: HttpUrl
    events: List[str]  # ["document.indexed", "generation.completed"]
    secret: Optional[str] = None  # Para verificar firma
    enabled: bool = True


class WebhookEvent(BaseModel):
    """Evento de webhook"""
    id: str
    event: str  # "document.indexed"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt_abc123",
                "event": "document.indexed",
                "timestamp": "2024-12-15T10:30:00Z",
                "data": {
                    "document_id": "doc-uuid",
                    "filename": "brand_guide.pdf",
                    "total_chunks": 15,
                    "status": "indexed"
                }
            }
        }


class WebhookDelivery(BaseModel):
    """Estado de entrega de webhook"""
    webhook_id: str
    event_id: str
    status: Literal["pending", "delivered", "failed"]
    attempts: int
    last_attempt: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None