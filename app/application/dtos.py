"""DTOs da camada de aplicacao. Desacoplam dominio do HTTP (DIP)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CreateUserInput:
    name: str
    email: str


@dataclass(frozen=True)
class CreateUserOutput:
    id: str
    name: str
    email: str
    created_at: str


@dataclass(frozen=True)
class ListUsersInput:
    limit: int = 20
    offset: int = 0

    def __post_init__(self) -> None:
        if self.limit < 1 or self.limit > 100:
            raise ValueError("limit deve estar entre 1 e 100")
        if self.offset < 0:
            raise ValueError("offset deve ser >= 0")
