"""TDD — Casos de uso."""

import pytest

from app.application.dtos import CreateUserInput, ListUsersInput
from app.application.use_cases import CreateUserUseCase, DeleteUserUseCase, GetUserUseCase, ListUsersUseCase
from app.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.infrastructure.repositories import InMemoryUserRepository


@pytest.fixture
def repo():
    return InMemoryUserRepository()


def test_create_user_ok(repo):
    out = CreateUserUseCase(repo).execute(CreateUserInput(name="Ada", email="ada@example.com"))
    assert out.name == "Ada"
    assert repo.count() == 1


def test_create_user_duplicado(repo):
    CreateUserUseCase(repo).execute(CreateUserInput(name="Ada", email="ada@example.com"))
    with pytest.raises(UserAlreadyExistsError):
        CreateUserUseCase(repo).execute(CreateUserInput(name="Outra", email="ADA@example.com"))


def test_create_user_email_invalido(repo):
    with pytest.raises(ValueError):
        CreateUserUseCase(repo).execute(CreateUserInput(name="Ada", email="invalido"))


def test_get_list_delete(repo):
    created = CreateUserUseCase(repo).execute(CreateUserInput(name="Ada", email="ada@example.com"))
    assert GetUserUseCase(repo).execute(created.id).email == "ada@example.com"
    items = ListUsersUseCase(repo).execute(ListUsersInput(limit=10, offset=0))
    assert len(items) == 1
    DeleteUserUseCase(repo).execute(created.id)
    assert repo.count() == 0
    with pytest.raises(UserNotFoundError):
        GetUserUseCase(repo).execute(created.id)


def test_list_input_invalido():
    with pytest.raises(ValueError):
        ListUsersInput(limit=0)
    with pytest.raises(ValueError):
        ListUsersInput(limit=101)
