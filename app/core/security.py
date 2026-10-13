"""Autenticação: hashing de senhas e tokens JWT.

Senhas com PBKDF2-HMAC-SHA256 da stdlib (200k iterações + salt aleatório):
sem dependências nativas, sem surpresas entre plataformas. Tokens JWT (HS256)
assinados com a SECRET_KEY — stateless, com expiração curta por defeito.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """Gera `pbkdf2$iteracoes$salt$hash` a partir da senha em claro."""
    if len(password) < 8:
        raise ValueError("password deve ter ao menos 8 caracteres")
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS)
    return f"pbkdf2${_ITERATIONS}${salt}${dk.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Compara em tempo constante; formato desconhecido = recusa segura."""
    try:
        algo, iters, salt, expected = password_hash.split("$")
        if algo != "pbkdf2":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iters))
        return secrets.compare_digest(dk.hex(), expected)
    except (ValueError, AttributeError):
        return False


def create_access_token(user_id: str, role: str, secret: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str, secret: str) -> dict:
    """Devolve o payload ou levanta ValueError (expirado, assinatura inválida...)."""
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError as e:
        raise ValueError(f"token invalido: {e}")
