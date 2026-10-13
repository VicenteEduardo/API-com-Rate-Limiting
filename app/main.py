"""Ponto de entrada: monta o FastAPI e liga todas as peças.

Aqui não há regra de negócio — só composição: middlewares, handlers de erro
e rotas. Juntar uma funcionalidade nova é registar um router; o núcleo não muda.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.presentation.dependencies import get_rate_limiter
from app.presentation.exception_handlers import register_exception_handlers
from app.presentation.middlewares import RateLimitMiddleware
from app.presentation.routers import health, users

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API de exemplo com **DDD + SOLID + TDD**, "
        "**Rate Limiting (sliding window)** e **Swagger (OpenAPI)** automatico. "
        "Camadas: domain (entidades/VOs) -> application (use cases/DTOs) -> "
        "infrastructure (repositorios/rate limiter) -> presentation (routers/schemas/middlewares)."
    ),
    docs_url="/docs",   # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, limiter=get_rate_limiter(), settings=settings)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(users.router, prefix="/api/v1")


@app.get("/", tags=["root"], summary="Raiz")
def root():
    return {"message": f"{settings.app_name} — docs em /docs", "version": settings.app_version}
