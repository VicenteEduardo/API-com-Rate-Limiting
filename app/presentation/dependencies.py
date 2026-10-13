"""Quem monta quem (composition root da injeção de dependência).

A fábrica `get_repository` é o único ponto que escolhe a infraestrutura:
sem DATABASE_URL, memória (ideal para dev e testes); com DATABASE_URL,
Postgres via SQLAlchemy. As rotas e os casos de uso nunca sabem a diferença.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.domain.repositories import IUserRepository
from app.infrastructure.rate_limiter import InMemorySlidingWindowRateLimiter
from app.infrastructure.repositories import InMemoryUserRepository


@lru_cache
def get_repository() -> IUserRepository:
    settings: Settings = get_settings()
    if settings.database_url:
        from app.infrastructure.db import make_session_factory
        from app.infrastructure.sqlalchemy_repository import SQLAlchemyUserRepository

        return SQLAlchemyUserRepository(make_session_factory(settings.database_url))
    return InMemoryUserRepository()


@lru_cache
def get_rate_limiter() -> InMemorySlidingWindowRateLimiter:
    s: Settings = get_settings()
    return InMemorySlidingWindowRateLimiter(limit_per_minute=s.rate_limit_per_minute)
