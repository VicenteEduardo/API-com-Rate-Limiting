"""Configuração centralizada (12-factor): tudo vem do ambiente, com defeitos sensatos."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DDD API com Rate Limiting"
    app_version: str = "1.0.0"
    env: str = "dev"

    # Rate limiting — janela deslizante em memória (evoluir para Redis em produção)
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10  # reservado para futura estratégia token bucket
    rate_limit_enabled: bool = True
    # Rotas isentas: monitorização e documentação nunca devem ser bloqueadas
    rate_limit_exempt_paths: str = "/health,/docs,/redoc,/openapi.json"

    cors_origins: str = "*"

    # Base de dados. SQLite local por defeito; Postgres via env.
    # Ex.: postgresql+psycopg2://user:pass@db:5432/api
    database_url: str = "sqlite:///./data/app.db"

    # Auth (JWT). Em produção, definir SECRET_KEY forte via ambiente.
    secret_key: str = "dev-secret-key-mudar-em-producao"
    access_token_expire_minutes: int = 60
    # Seed do primeiro admin no arranque (vazio = sem seed)
    admin_email: str = ""
    admin_password: str = ""
    admin_name: str = "Admin"

    @property
    def exempt_paths(self) -> List[str]:
        return [p.strip() for p in self.rate_limit_exempt_paths.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
