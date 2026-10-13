"""Entidades do domínio — o coração do sistema.

Repara que este ficheiro não importa nada de frameworks: nem FastAPI, nem
banco de dados, nem HTTP. É Python puro, de propósito. A regra de negócio
vive aqui e não depende de como a API é exposta lá fora — é isso que o DDD
quer dizer com "camada mais interna".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.value_objects import Email


@dataclass
class User:
    """Um utilizador do sistema.

    A identidade é o `id`: dois utilizadores com o mesmo nome e e-mail
    continuam a ser pessoas diferentes se os ids divergirem. O `rename`
    existe para que a mudança de nome passe sempre pela mesma validação
    da criação — uma única regra, um único lugar.
    """

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
        # Reaproveita a validação do construtor em vez de duplicá-la aqui.
        tmp = User(name=new_name, email=self.email, id=self.id, created_at=self.created_at)
        self.name = tmp.name

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": str(self.email),
            "created_at": self.created_at.isoformat(),
        }
