"""Quem é você, e o que pode fazer: autenticação e autorização.

`get_current_user` valida o Bearer JWT e carrega o utilizador; `require_admin`
exige o papel admin. As rotas declaram o que precisam via `Depends` — a regra
"admin gere todos, user gere só a si" vive na entidade (`User.can_manage`),
não espalhada pelas rotas.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.domain.entities import User
from app.domain.repositories import IUserRepository
from app.presentation.dependencies import get_repository

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    repo: IUserRepository = Depends(get_repository),
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token em falta")
    try:
        payload = decode_access_token(creds.credentials, get_settings().secret_key)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    user = repo.get_by_id(str(payload.get("sub", "")))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="utilizador do token nao existe")
    return user


def require_admin(current: User = Depends(get_current_user)) -> User:
    if not current.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="apenas admins")
    return current
