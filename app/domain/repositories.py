"""Portas (interfaces) do dominio. ISP + DIP: interfaces pequenas, dominio nao conhece infra."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import User


class IUserRepository(ABC):
    """Porta de persistencia de User."""

    @abstractmethod
    def save(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def list(self, limit: int = 20, offset: int = 0) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        raise NotImplementedError


class IRateLimiter(ABC):
    """Porta de rate limiting. Infra implementa (memoria, Redis...). LSP: qualquer impl. e substituivel."""

    @abstractmethod
    def is_allowed(self, key: str) -> tuple:
        """Retorna (allowed: bool, info: dict com limit/remaining/reset)."""
        raise NotImplementedError

    @abstractmethod
    def reset(self, key: str) -> None:
        raise NotImplementedError
