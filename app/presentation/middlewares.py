"""Middleware de Rate Limiting. SRP: so limita. DIP: recebe limiter + settings."""

from __future__ import annotations

from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.infrastructure.rate_limiter import InMemorySlidingWindowRateLimiter


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
        response: Response
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={"detail": "rate limit excedido. Tente novamente em instantes.", "code": "rate_limit_exceeded"},
            )
        else:
            response = await call_next(request)

        # Headers padrao (IETF + X-RateLimit) — observabilidade
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        if not allowed:
            response.headers["Retry-After"] = str(info["retry_after"])
        return response
