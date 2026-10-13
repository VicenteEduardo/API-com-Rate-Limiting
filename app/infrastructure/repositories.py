"""Guarda de utilizadores em memória — simples, rápida e segura entre threads.

Serve para desenvolvimento e testes. Quando chegar a hora do Postgres, basta
criar uma nova classe que cumpra o mesmo `IUserRepository`: os casos de uso
nem vão reparar na troca. É o O de SOLID — extensão sem modificação.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from app.domain.entities import User
from app.domain.repositories import IUserRepository


class InMemoryUserRepository(IUserRepository):
    """Dicionários protegidos por lock: dois índices (por id e por e-mail)."""

    def __init__(self) -> None:
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, str] = {}  # e-mail normalizado -> id
        self._lock = threading.Lock()

    def save(self, user: User) -> User:
        with self._lock:
            self._by_id[user.id] = user
            self._by_email[str(user.email)] = user.id
            return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._by_id.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        with self._lock:
            uid = self._by_email.get(email.strip().lower())
            return self._by_id.get(uid) if uid else None

    def list(self, limit: int = 20, offset: int = 0) -> List[User]:
        with self._lock:
            # Ordem de chegada: os mais antigos primeiro, como uma fila justa.
            users = sorted(self._by_id.values(), key=lambda u: u.created_at)
            return users[offset : offset + limit]

    def delete(self, user_id: str) -> bool:
        with self._lock:
            user = self._by_id.pop(user_id, None)
            if user is None:
                return False
            self._by_email.pop(str(user.email), None)
            return True

    def count(self) -> int:
        with self._lock:
            return len(self._by_id)

    def clear(self) -> None:
        """Esvazia tudo — feita à medida dos testes, que gostam de recomeçar do zero."""
        with self._lock:
            self._by_id.clear()
            self._by_email.clear()
