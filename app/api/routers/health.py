"""Health check router."""
from __future__ import annotations

from fastapi import APIRouter

from api.schemas import HealthResponseSchema
from config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponseSchema)
async def health_check() -> HealthResponseSchema:
    """Health check endpoint for container orchestration."""
    return HealthResponseSchema(
        status="ok",
        version="1.0.0",
        environment=settings.app_env,
    )
