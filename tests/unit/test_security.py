"""Unidade: senhas e JWT."""

import time

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_e_verify():
    h = hash_password("segredo123")
    assert h != "segredo123"
    assert verify_password("segredo123", h) is True
    assert verify_password("outra-senha", h) is False


def test_hash_rejeita_senha_curta():
    with pytest.raises(ValueError):
        hash_password("curta")


def test_verify_formato_desconhecido_recusa():
    assert verify_password("x", "lixo-sem-formato") is False
    assert verify_password("x", "") is False


def test_jwt_roundtrip():
    token = create_access_token("uid-1", "admin", "segredo", 60)
    payload = decode_access_token(token, "segredo")
    assert payload["sub"] == "uid-1"
    assert payload["role"] == "admin"


def test_jwt_adulterado_ou_outra_chave():
    token = create_access_token("uid-1", "user", "segredo", 60)
    with pytest.raises(ValueError):
        decode_access_token(token + "x", "segredo")
    with pytest.raises(ValueError):
        decode_access_token(token, "outra-chave")


def test_jwt_expirado():
    token = create_access_token("uid-1", "user", "segredo", -1)
    time.sleep(0.01)
    with pytest.raises(ValueError):
        decode_access_token(token, "segredo")
