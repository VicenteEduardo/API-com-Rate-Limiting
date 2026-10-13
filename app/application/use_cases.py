"""Casos de uso: as coisas que o sistema sabe fazer.

Cada classe resolve um único problema (o S de SOLID) e só conversa com o
domínio através das interfaces — nunca com o banco diretamente (o D de
SOLID). Repara que não há nenhum import de FastAPI aqui: estes casos de uso
funcionariam igual numa CLI, num worker ou em qualquer outra porta de entrada.
"""

from __future__ import annotations

from typing import List

from app.application.dtos import CreateUserInput, CreateUserOutput, ListUsersInput
from app.domain.entities import User
from app.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.repositories import IUserRepository
from app.domain.value_objects import Email


def _to_output(user: User) -> CreateUserOutput:
    """Converte a entidade interna no formato que sai do caso de uso."""
    return CreateUserOutput(
        id=user.id, name=user.name, email=str(user.email), created_at=user.created_at.isoformat()
    )


class CreateUserUseCase:
    """Cria um utilizador, recusando e-mails duplicados ou inválidos."""

    def __init__(self, repo: IUserRepository):
        self._repo = repo

    def execute(self, data: CreateUserInput) -> CreateUserOutput:
        email = Email(data.email)  # valida primeiro: falha rápido, sem efeitos colaterais
        if self._repo.get_by_email(str(email)) is not None:
            raise UserAlreadyExistsError(f"email {email} ja cadastrado")
        user = User(name=data.name, email=email)
        saved = self._repo.save(user)
        return _to_output(saved)


class GetUserUseCase:
    """Vai buscar um utilizador pelo id — ou explica que ele não existe."""

    def __init__(self, repo: IUserRepository):
        self._repo = repo

    def execute(self, user_id: str) -> CreateUserOutput:
        user = self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"user {user_id} nao encontrado")
        return _to_output(user)


class ListUsersUseCase:
    """Lista utilizadores com paginação (para nunca despejar a base inteira)."""

    def __init__(self, repo: IUserRepository):
        self._repo = repo

    def execute(self, data: ListUsersInput) -> List[CreateUserOutput]:
        return [_to_output(u) for u in self._repo.list(limit=data.limit, offset=data.offset)]


class DeleteUserUseCase:
    """Apaga um utilizador. Apagar o que não existe também é erro (404)."""

    def __init__(self, repo: IUserRepository):
        self._repo = repo

    def execute(self, user_id: str) -> None:
        if not self._repo.delete(user_id):
            raise UserNotFoundError(f"user {user_id} nao encontrado")
