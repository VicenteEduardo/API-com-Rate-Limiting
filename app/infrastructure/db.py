"""Base SQLAlchemy e modelo relacional.

Só é importado quando há DATABASE_URL configurada, por isso o Hinterland
em memória continua a funcionar sem Postgres instalado. A tabela espelha a
entidade User 1:1 — e-mail único com índice, porque é a pesquisa quente
(verificação de duplicados a cada criação).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def make_session_factory(database_url: str):
    """Cria engine + tabelas (create_all; para migrações formais, evoluir para Alembic)."""
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
