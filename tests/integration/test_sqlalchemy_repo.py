"""Mesmo contrato, outra infraestrutura (prova do L de SOLID).

Corre o repositório SQLAlchemy sobre SQLite em memória e repete o essencial
do ciclo de vida. Se esta implementação passa, a do Postgres — mesma classe,
outro driver — comporta-se igual perante os casos de uso.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application.dtos import CreateUserInput
from app.application.use_cases import CreateUserUseCase, GetUserUseCase
from app.domain.exceptions import UserAlreadyExistsError
from app.infrastructure.db import Base
from app.infrastructure.sqlalchemy_repository import SQLAlchemyUserRepository

import pytest


@pytest.fixture
def repo():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return SQLAlchemyUserRepository(sessionmaker(bind=engine, expire_on_commit=False))


def test_sql_repo_crud(repo):
    out = CreateUserUseCase(repo).execute(CreateUserInput(name="Ada", email="ada@example.com"))
    assert GetUserUseCase(repo).execute(out.id).email == "ada@example.com"
    assert repo.count() == 1
    assert len(repo.list(limit=10, offset=0)) == 1
    assert repo.delete(out.id) is True
    assert repo.count() == 0


def test_sql_repo_duplicado(repo):
    CreateUserUseCase(repo).execute(CreateUserInput(name="Ada", email="ada@example.com"))
    with pytest.raises(UserAlreadyExistsError):
        CreateUserUseCase(repo).execute(CreateUserInput(name="Outra", email="ada@example.com"))
