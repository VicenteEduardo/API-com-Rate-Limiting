"""Fixtures compartilhadas (TDD)."""

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.rate_limiter import InMemorySlidingWindowRateLimiter
from app.infrastructure.repositories import InMemoryUserRepository
from app.main import app
from app.presentation.dependencies import get_rate_limiter, get_repository


@pytest.fixture
def repo():
    return InMemoryUserRepository()


@pytest.fixture
def client():
    # isola cada teste de integracao: repo+limiter frescos
    test_repo = InMemoryUserRepository()
    test_limiter = InMemorySlidingWindowRateLimiter(limit_per_minute=60)
    app.dependency_overrides[get_repository] = lambda: test_repo
    # o middleware capturou a instancia original no startup; troca o objeto interno
    import app.main as main_mod
    from app.presentation.middlewares import RateLimitMiddleware

    for m in app.user_middleware:
        pass
    # abordagem simples: limpa limiter global e injeta limite alto
    limiter = get_rate_limiter()
    limiter.reset_all()
    limiter.limit = 60
    yield TestClient(app)
    app.dependency_overrides.clear()
    limiter.reset_all()
    limiter.limit = 60
