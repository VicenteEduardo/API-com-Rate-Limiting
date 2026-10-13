"""Rotas de utilizadores — camada fina, sem regra de negócio.

Cada rota faz três coisas e só três: valida a entrada (Pydantic), chama o
caso de uso certo e devolve a resposta. Erros de negócio sobem até aos
handlers centrais (`exception_handlers.py`), que definem o status HTTP.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos import CreateUserInput, ListUsersInput
from app.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
)
from app.domain.repositories import IUserRepository
from app.presentation.dependencies import get_repository
from app.presentation.schemas import CreateUserRequest, UserListResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


def _to_resp(o) -> UserResponse:
    return UserResponse(id=o.id, name=o.name, email=o.email, created_at=o.created_at)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Criar usuario",
             description="Cria usuario. 409 se e-mail duplicado. 429 se rate limit.",
             responses={409: {"description": "E-mail ja cadastrado"}, 429: {"description": "Rate limit excedido"}})
def create_user(payload: CreateUserRequest, repo: IUserRepository = Depends(get_repository)):
    out = CreateUserUseCase(repo).execute(CreateUserInput(name=payload.name, email=str(payload.email)))
    return _to_resp(out)


@router.get("", response_model=UserListResponse, summary="Listar usuarios com paginacao")
def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: IUserRepository = Depends(get_repository),
):
    items = ListUsersUseCase(repo).execute(ListUsersInput(limit=limit, offset=offset))
    return UserListResponse(
        items=[_to_resp(o) for o in items], total=repo.count(), limit=limit, offset=offset
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Buscar usuario por id",
            responses={404: {"description": "Usuario nao encontrado"}})
def get_user(user_id: str, repo: IUserRepository = Depends(get_repository)):
    return _to_resp(GetUserUseCase(repo).execute(user_id))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover usuario",
               responses={404: {"description": "Usuario nao encontrado"}})
def delete_user(user_id: str, repo: IUserRepository = Depends(get_repository)):
    DeleteUserUseCase(repo).execute(user_id)
    return None
