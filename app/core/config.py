"""Config centralizada (12-factor). SRP: so leitura de env."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DDD API com Rate Limiting"
    app_version: str = "1.0.0"
    env: str = "dev"

    # Rate limiting — sliding window em memoria (troque por Redis em prod)
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10  # reservado p/ token bucket futuro
    rate_limit_enabled: bool = True
    # rotas isentas (health/docs nunca bloqueiam)
    rate_limit_exempt_paths: str = "/health,/docs,/redoc,/openapi.json"

    cors_origins: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def exempt_paths(self) -> List[str]:
        return [p.strip() for p in self.rate_limit_exempt_paths.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
