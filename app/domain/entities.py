"""Domain entities. Camada mais interna do DDD. Sem dependencias externas (DIP)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.domain.value_objects import Email


@dataclass
class User:
    """Entidade User. Identidade por `id`. SRP: so representa o usuario."""

    name: str
    email: Email
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        name = (self.name or "").strip()
        if len(name) < 2:
            raise ValueError("name deve ter ao menos 2 caracteres")
        if len(name) > 120:
            raise ValueError("name deve ter no maximo 120 caracteres")
        self.name = name

    def rename(self, new_name: str) -> None:
        tmp = User(name=new_name, email=self.email, id=self.id, created_at=self.created_at)
        self.name = tmp.name

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": str(self.email),
            "created_at": self.created_at.isoformat(),
        }
