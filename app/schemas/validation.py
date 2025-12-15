# app/schemas/validation.py (NUEVO ARCHIVO)

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class FileValidationResult(BaseModel):
    """Resultado de validación de archivo antes de procesar"""
    is_valid: bool
    filename: str
    file_size_mb: float
    mime_type: str
    extension: str
    errors: List[str] = []
    warnings: List[str] = []
    
    @property
    def can_process(self) -> bool:
        return self.is_valid and len(self.errors) == 0


class PromptValidationResult(BaseModel):
    """Validación de prompt antes de generar"""
    is_valid: bool
    prompt_name: str
    missing_variables: List[str] = []
    extra_variables: List[str] = []
    variable_types_correct: bool = True
    estimated_tokens: int = 0
    estimated_cost_usd: float = 0.0
    warnings: List[str] = []


class BulkOperationRequest(BaseModel):
    """Request para operaciones en batch"""
    operation: str = Field(..., description="upload, delete, reprocess")
    document_ids: Optional[List[str]] = None
    filters: Optional[dict] = None  # {"doc_type": "policy", "status": "failed"}
    dry_run: bool = False  # Preview sin ejecutar
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v):
        allowed = ['upload', 'delete', 'reprocess', 'export']
        if v not in allowed:
            raise ValueError(f"Operation must be one of: {allowed}")
        return v


class BulkOperationResponse(BaseModel):
    """Response de operación bulk"""
    operation: str
    total_items: int
    successful: int
    failed: int
    skipped: int
    errors: List[dict] = []  # [{"item": "doc-123", "error": "..."}]
    execution_time_seconds: float