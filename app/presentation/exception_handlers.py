"""Tradução central de erros de negócio para HTTP (um único lugar).

Antes cada rota fazia o seu try/except; agora as rotas deixam a exceção subir
e estes handlers decidem o status. Adicionar um erro novo = registar aqui,
sem tocar nas rotas existentes.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.domain.exceptions import (
    ForbiddenError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

log = get_logger("app.errors")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFoundError)
    async def not_found(_: Request, exc: UserNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc), "code": "user_not_found"})

    @app.exception_handler(UserAlreadyExistsError)
    async def conflict(_: Request, exc: UserAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc), "code": "user_already_exists"})

    @app.exception_handler(InvalidCredentialsError)
    async def unauthorized(_: Request, exc: InvalidCredentialsError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc), "code": "invalid_credentials"})

    @app.exception_handler(ForbiddenError)
    async def forbidden(_: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc), "code": "forbidden"})

    @app.exception_handler(ValueError)
    async def unprocessable(_: Request, exc: ValueError) -> JSONResponse:
        log.warning("validacao falhou: %s", exc)
        return JSONResponse(status_code=422, content={"detail": str(exc), "code": "validation_error"})
