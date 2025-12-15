# app/schemas/errors.py (NUEVO ARCHIVO)

from pydantic import BaseModel
from typing import Optional, List, Any, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """Detalle de un error"""
    code: str  # "QUOTA_EXCEEDED", "INVALID_FILE", "LLM_ERROR"
    message: str
    field: Optional[str] = None  # Campo que causó el error
    details: Optional[dict] = None


class APIError(BaseModel):
    """Error response estándar"""
    error: str  # Tipo de error general
    message: str  # Mensaje user-friendly
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None  # Para tracking
    documentation_url: Optional[str] = None  # Link a docs
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Invalid input data",
                "details": [
                    {
                        "code": "MISSING_FIELD",
                        "message": "Field 'product_name' is required",
                        "field": "product_name"
                    }
                ],
                "timestamp": "2024-12-15T10:30:00Z",
                "request_id": "req_abc123",
                "documentation_url": "https://docs.example.com/errors/validation"
            }
        }


class QuotaExceededError(APIError):
    """Error específico de quota"""
    current_usage: int
    limit: int
    reset_at: datetime
    upgrade_url: str


class RateLimitError(APIError):
    """Error de rate limiting"""
    retry_after: int  # Segundos
    limit: str  # "10 requests per minute"