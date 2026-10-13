"""Schemas HTTP (Pydantic). Validacao de borda. Nao vazar entidades de dominio."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUserRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"name": "Ada Lovelace", "email": "ada@example.com"}})

    name: str = Field(min_length=2, max_length=120)
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    env: str
