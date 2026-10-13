"""Schemas HTTP (Pydantic): validação na fronteira da API.

Convertem e validam o JSON de entrada antes de chegar aos casos de uso, e
definem o formato exato das respostas documentadas no Swagger. O domínio
nunca vê estes objetos — e não precisa.
"""

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
    role: str
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


class RegisterRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"name": "Ada Lovelace", "email": "ada@example.com", "password": "segredo123"}})

    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class ChangeRoleRequest(BaseModel):
    role: str = Field(pattern="^(admin|user)$")
