"""DI (composition root). SRP: so monta dependencias. Singleton p/ repo+limiter."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.infrastructure.rate_limiter import InMemorySlidingWindowRateLimiter
from app.infrastructure.repositories import InMemoryUserRepository


@lru_cache
def get_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@lru_cache
def get_rate_limiter() -> InMemorySlidingWindowRateLimiter:
    s: Settings = get_settings()
    return InMemorySlidingWindowRateLimiter(limit_per_minute=s.rate_limit_per_minute)
