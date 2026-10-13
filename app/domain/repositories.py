"""As "portas" do domínio: contratos, não implementações.

Estas interfaces dizem *o que* o sistema precisa (guardar utilizadores,
verificar o limite de requisições) sem dizer *como*. A infraestrutura —
banco em memória hoje, Postgres ou Redis amanhã — é que cumpre o contrato.

É o D de SOLID (Dependency Inversion) na prática: o domínio manda, a
infraestrutura obedece. E são interfaces pequenas de propósito (o I de
SOLID): ninguém é obrigado a implementar o que não usa.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities import User


class IUserRepository(ABC):
    """Tudo o que os casos de uso precisam para lidar com utilizadores."""

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
    """Contrato do limitador de requisições.

    Qualquer implementação — memória, Redis, a que inventares — pode ser
    ligada sem tocar no resto do código (o L de SOLID: substituível sem
    sustos). Devolve se o pedido passa e os números para os cabeçalhos HTTP.
    """

    @abstractmethod
    def is_allowed(self, key: str) -> tuple:
        """Devolve (allowed, info) onde info traz limit/remaining/reset."""
        raise NotImplementedError

    @abstractmethod
    def reset(self, key: str) -> None:
        raise NotImplementedError
