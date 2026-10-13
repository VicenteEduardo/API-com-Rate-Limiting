"""Health check — isento de rate limit."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.presentation.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health():
    s = get_settings()
    return HealthResponse(status="ok", version=s.app_version, env=s.env)
