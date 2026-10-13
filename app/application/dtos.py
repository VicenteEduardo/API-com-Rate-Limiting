"""Objetos que atravessam a fronteira da aplicação.

Os DTOs desacoplam o mundo lá de fora do domínio: a rota HTTP monta um Input,
o caso de uso devolve um Output, e ninguém precisa conhecer a entidade User
para conversar com a aplicação. São congelados (frozen) porque dados de
entrada/saída não devem ser alterados a meio do caminho.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateUserInput:
    """O que precisamos para criar alguém: nome e e-mail em bruto."""

    name: str
    email: str


@dataclass(frozen=True)
class CreateUserOutput:
    """O que devolvemos depois de criar (ou buscar): tudo pronto para o HTTP."""

    id: str
    name: str
    email: str
    role: str
    created_at: str


@dataclass(frozen=True)
class ListUsersInput:
    """Paginação com limites saudáveis: protege a API de pedidos absurdos."""

    limit: int = 20
    offset: int = 0

    def __post_init__(self) -> None:
        if self.limit < 1 or self.limit > 100:
            raise ValueError("limit deve estar entre 1 e 100")
        if self.offset < 0:
            raise ValueError("offset deve ser >= 0")


@dataclass(frozen=True)
class RegisterUserInput:
    """Registo público: entra sempre como `user` (promoção é ato de admin)."""

    name: str
    email: str
    password: str


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str


@dataclass(frozen=True)
class TokenOutput:
    access_token: str
    token_type: str = "bearer"
    user_id: str = ""
    role: str = ""
