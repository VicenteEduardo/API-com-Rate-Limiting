"""TDD — Value Object Email (primeiro a ser escrito no ciclo red-green-refactor)."""

import pytest

from app.domain.value_objects import Email


def test_email_valido_normaliza():
    assert str(Email("  Ada@Example.COM ")) == "ada@example.com"


def test_email_invalido_levanta():
    for bad in ["", "sem-arroba", "a@b", "@x.com", "a b@c.com"]:
        with pytest.raises(ValueError):
            Email(bad)


def test_email_igualdade():
    assert Email("a@b.com") == Email("A@B.COM")
    assert Email("a@b.com") == "a@b.com"
    assert hash(Email("a@b.com")) == hash(Email("a@b.com"))
