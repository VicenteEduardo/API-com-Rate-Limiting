"""TDD — Entidade User."""

import pytest

from app.domain.entities import User
from app.domain.value_objects import Email


def test_cria_usuario_valido():
    u = User(name="Ada Lovelace", email=Email("ada@example.com"))
    assert u.id
    assert u.name == "Ada Lovelace"
    assert str(u.email) == "ada@example.com"
    assert u.created_at


def test_nome_curto_levanta():
    with pytest.raises(ValueError):
        User(name="A", email=Email("a@b.com"))


def test_rename():
    u = User(name="Ada", email=Email("ada@example.com"))
    u.rename("Grace Hopper")
    assert u.name == "Grace Hopper"
