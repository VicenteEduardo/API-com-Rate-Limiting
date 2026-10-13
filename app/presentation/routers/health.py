"""Rota de saúde — propositadamente isenta do rate limit.

Se o balanceador de carga não consegue cá chegar, nada mais interessa:
por isso responde rápido, sem autenticação e sem contar para o limite.
"""

from fastapi import APIRouter

from app.core.config import get_settings
from app.presentation.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health():
    s = get_settings()
    return HealthResponse(status="ok", version=s.app_version, env=s.env)
