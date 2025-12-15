# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import documents, generation

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

api_router.include_router(
    generation.router,
    prefix="/generation",
    tags=["Generation"]
)