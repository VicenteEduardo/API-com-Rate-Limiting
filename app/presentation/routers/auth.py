"""Registo, login e perfil próprio. Registo é público; o resto exige JWT."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.application.dtos import LoginInput, RegisterUserInput
from app.application.use_cases import AuthenticateUserUseCase
from app.application.use_cases import RegisterUserUseCase
from app.core.config import get_settings
from app.domain.entities import User
from app.domain.repositories import IUserRepository
from app.presentation.auth import get_current_user
from app.presentation.dependencies import get_repository
from app.presentation.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_resp(o) -> UserResponse:
    return UserResponse(id=o.id, name=o.name, email=o.email, role=o.role, created_at=o.created_at)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Registar utilizador",
             description="Registo público. Cria sempre com papel `user`. 409 se e-mail duplicado.")
def register(payload: RegisterRequest, repo: IUserRepository = Depends(get_repository)):
    out = RegisterUserUseCase(repo).execute(
        RegisterUserInput(name=payload.name, email=str(payload.email), password=payload.password)
    )
    return _to_resp(out)


@router.post("/login", response_model=TokenResponse, summary="Iniciar sessão",
             description="Devolve o JWT (Bearer) para usar nas rotas protegidas. 401 se credenciais invalidas.",
             responses={401: {"description": "Credenciais invalidas"}})
def login(payload: LoginRequest, repo: IUserRepository = Depends(get_repository)):
    s = get_settings()
    out = AuthenticateUserUseCase(repo, s.secret_key, s.access_token_expire_minutes).execute(
        LoginInput(email=str(payload.email), password=payload.password)
    )
    return TokenResponse(
        access_token=out.access_token, token_type=out.token_type,
        user_id=out.user_id, role=out.role,
    )


@router.get("/me", response_model=UserResponse, summary="O meu perfil")
def me(current: User = Depends(get_current_user)):
    return UserResponse(
        id=current.id, name=current.name, email=str(current.email),
        role=current.role, created_at=current.created_at.isoformat(),
    )
