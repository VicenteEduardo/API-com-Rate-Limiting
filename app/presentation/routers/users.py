"""Gestão de utilizadores — agora com autorização.

- Listar e promover: só admin (403 caso contrário).
- Ver e apagar: o próprio ou um admin (`User.can_manage` decide).
- Criar conta: rota pública em `/auth/register` (registo entra como `user`).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dtos import ListUsersInput
from app.application.use_cases import (
    ChangeUserRoleUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
)
from app.domain.entities import User
from app.domain.exceptions import ForbiddenError, UserNotFoundError
from app.domain.repositories import IUserRepository
from app.presentation.auth import get_current_user, require_admin
from app.presentation.dependencies import get_repository
from app.presentation.schemas import ChangeRoleRequest, UserListResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


def _to_resp(o) -> UserResponse:
    return UserResponse(id=o.id, name=o.name, email=o.email, role=o.role, created_at=o.created_at)


def _ensure_can_manage(actor: User, target_id: str, repo: IUserRepository) -> None:
    if actor.is_admin:
        return
    if actor.id != target_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="so pode gerir a si proprio")


@router.get("", response_model=UserListResponse, summary="Listar usuarios (admin)",
            description="Apenas admins. 403 para users comuns.",
            responses={403: {"description": "Apenas admins"}})
def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: IUserRepository = Depends(get_repository),
    _: User = Depends(require_admin),
):
    items = ListUsersUseCase(repo).execute(ListUsersInput(limit=limit, offset=offset))
    return UserListResponse(
        items=[_to_resp(o) for o in items], total=repo.count(), limit=limit, offset=offset
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Buscar usuario por id",
            description="O próprio ou um admin.",
            responses={403: {"description": "Sem permissao"}, 404: {"description": "Usuario nao encontrado"}})
def get_user(
    user_id: str,
    repo: IUserRepository = Depends(get_repository),
    actor: User = Depends(get_current_user),
):
    _ensure_can_manage(actor, user_id, repo)
    try:
        return _to_resp(GetUserUseCase(repo).execute(user_id))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover usuario",
               description="O próprio ou um admin.",
               responses={403: {"description": "Sem permissao"}, 404: {"description": "Usuario nao encontrado"}})
def delete_user(
    user_id: str,
    repo: IUserRepository = Depends(get_repository),
    actor: User = Depends(get_current_user),
):
    _ensure_can_manage(actor, user_id, repo)
    try:
        DeleteUserUseCase(repo).execute(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return None


@router.patch("/{user_id}/role", response_model=UserResponse, summary="Alterar papel (admin)",
              description="Promove/des-promove entre `admin` e `user`.",
              responses={403: {"description": "Apenas admins"}})
def change_role(
    user_id: str,
    payload: ChangeRoleRequest,
    repo: IUserRepository = Depends(get_repository),
    actor: User = Depends(require_admin),
):
    try:
        return _to_resp(ChangeUserRoleUseCase(repo).execute(user_id, payload.role, actor))
    except (UserNotFoundError, ForbiddenError) as e:
        code = 404 if isinstance(e, UserNotFoundError) else 403
        raise HTTPException(status_code=code, detail=str(e))
