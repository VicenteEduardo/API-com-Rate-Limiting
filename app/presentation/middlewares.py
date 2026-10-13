"""Middleware de rate limiting: protege todas as rotas (exceto as isentas).

Funciona por cliente (IP, respeitando `X-Forwarded-For` atrás de proxies) e
informa sempre o estado do limite nos cabeçalhos `X-RateLimit-*`, seguindo a
convenção da indústria. Recebe as dependências prontas — nunca as cria.
"""

from __future__ import annotations

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.core.logging import get_logger
from app.infrastructure.rate_limiter import InMemorySlidingWindowRateLimiter

log = get_logger("app.ratelimit")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "anonymous"


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limiter: InMemorySlidingWindowRateLimiter,
        settings: Settings,
    ):
        super().__init__(app)
        self.limiter = limiter
        self.settings = settings

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.settings.rate_limit_enabled:
            return await call_next(request)
        if request.url.path in self.settings.exempt_paths:
            return await call_next(request)

        key = f"ip:{_client_ip(request)}"
        allowed, info = self.limiter.is_allowed(key)
        if not allowed:
            log.warning("rate limit excedido para %s em %s", key, request.url.path)
            response: Response = JSONResponse(
                status_code=429,
                content={"detail": "rate limit excedido. Tente novamente em instantes.", "code": "rate_limit_exceeded"},
            )
        else:
            response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        if not allowed:
            response.headers["Retry-After"] = str(info["retry_after"])
        return response
