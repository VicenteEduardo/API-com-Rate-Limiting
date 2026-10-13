"""Base SQLAlchemy e modelo relacional.

A tabela espelha a entidade User: e-mail único com índice (a pesquisa quente
da verificação de duplicados) e papel para autorização. O SQLite local serve
o desenvolvimento sem dependências; o Postgres entra só com DATABASE_URL.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def make_session_factory(database_url: str):
    """Cria engine + tabelas (create_all; para migrações formais, evoluir para Alembic)."""
    kwargs: dict = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        path = database_url.split("sqlite:///")[-1].split("?")[0]
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(database_url, **kwargs)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
