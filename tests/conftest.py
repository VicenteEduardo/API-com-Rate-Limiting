"""Fixtures partilhadas pelos testes de integração.

Cada teste recebe um repositório e um limite de requisições isolados, para
correrem em qualquer ordem sem interferência entre si.
"""

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.repositories import InMemoryUserRepository
from app.main import app
from app.presentation.dependencies import get_rate_limiter, get_repository


@pytest.fixture
def repo():
    return InMemoryUserRepository()


@pytest.fixture
def client():
    test_repo = InMemoryUserRepository()
    app.dependency_overrides[get_repository] = lambda: test_repo
    limiter = get_rate_limiter()
    limiter.reset_all()
    limiter.limit = 60
    yield TestClient(app)
    app.dependency_overrides.clear()
    limiter.reset_all()
    limiter.limit = 60
