"""Health endpoints."""
from fastapi import APIRouter
from smart_search.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()

@router.get("/")
async def root():
    """API root."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running"
    }

@router.get("/ping")
async def ping():
    """Ping."""
    return {"status": "pong"}
