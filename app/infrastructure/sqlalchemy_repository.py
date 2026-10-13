"""Repositório Postgres via SQLAlchemy — cumpre o mesmo IUserRepository.

Trocar de memória para Postgres não toca em nenhum caso de uso: a fábrica em
`dependencies.py` decide qual implementação entregar a partir de DATABASE_URL.
Sessão curta por operação (abre, usa, fecha): simples, previsível e sem fugas.
"""

from __future__ import annotations

from datetime import timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.domain.entities import User
from app.domain.repositories import IUserRepository
from app.domain.value_objects import Email
from app.infrastructure.db import UserModel


def _to_entity(m: UserModel) -> User:
    created = m.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return User(name=m.name, email=Email(m.email), id=m.id, created_at=created)


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, sessions: sessionmaker):
        self._sessions = sessions

    def save(self, user: User) -> User:
        with self._sessions() as s:
            existing = s.get(UserModel, user.id)
            if existing is None:
                s.add(
                    UserModel(
                        id=user.id, name=user.name,
                        email=str(user.email), created_at=user.created_at,
                    )
                )
            else:
                existing.name = user.name
                existing.email = str(user.email)
            s.commit()
            return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._sessions() as s:
            m = s.get(UserModel, user_id)
            return _to_entity(m) if m else None

    def get_by_email(self, email: str) -> Optional[User]:
        with self._sessions() as s:
            m = s.scalars(
                select(UserModel).where(func.lower(UserModel.email) == email.strip().lower())
            ).first()
            return _to_entity(m) if m else None

    def list(self, limit: int = 20, offset: int = 0) -> List[User]:
        with self._sessions() as s:
            rows = s.scalars(
                select(UserModel).order_by(UserModel.created_at).limit(limit).offset(offset)
            ).all()
            return [_to_entity(m) for m in rows]

    def delete(self, user_id: str) -> bool:
        with self._sessions() as s:
            m = s.get(UserModel, user_id)
            if m is None:
                return False
            s.delete(m)
            s.commit()
            return True

    def count(self) -> int:
        with self._sessions() as s:
            return s.scalar(select(func.count()).select_from(UserModel)) or 0
