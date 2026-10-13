"""Router de Users. Camada fina: traduz HTTP <-> use cases. Sem regra de negocio aqui."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos import CreateUserInput, ListUsersInput
from app.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
)
from app.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.infrastructure.repositories import InMemoryUserRepository
from app.presentation.dependencies import get_repository
from app.presentation.schemas import CreateUserRequest, UserListResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


def _to_resp(o) -> UserResponse:
    return UserResponse(id=o.id, name=o.name, email=o.email, created_at=o.created_at)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Criar usuario", description="Cria usuario. 409 se e-mail duplicado. 429 se rate limit.")
def create_user(payload: CreateUserRequest, repo: InMemoryUserRepository = Depends(get_repository)):
    try:
        out = CreateUserUseCase(repo).execute(CreateUserInput(name=payload.name, email=str(payload.email)))
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(e))
    except UserAlreadyExistsError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=str(e))
    return _to_resp(out)


@router.get("", response_model=UserListResponse, summary="Listar usuarios com paginacao")
def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: InMemoryUserRepository = Depends(get_repository),
):
    try:
        items = ListUsersUseCase(repo).execute(ListUsersInput(limit=limit, offset=offset))
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(e))
    return UserListResponse(
        items=[_to_resp(o) for o in items], total=repo.count(), limit=limit, offset=offset
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Buscar usuario por id")
def get_user(user_id: str, repo: InMemoryUserRepository = Depends(get_repository)):
    try:
        return _to_resp(GetUserUseCase(repo).execute(user_id))
    except UserNotFoundError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover usuario")
def delete_user(user_id: str, repo: InMemoryUserRepository = Depends(get_repository)):
    try:
        DeleteUserUseCase(repo).execute(user_id)
    except UserNotFoundError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))
    return None
