"""Value Objects do dominio. Imutaveis e auto-validados."""

from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Email:
    """VO de e-mail. OCP: validacao encapsulada, extensivel sem alterar User."""

    __slots__ = ("_value",)

    def __init__(self, value: str):
        v = (value or "").strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError(f"email invalido: {value!r}")
        if len(v) > 254:
            raise ValueError("email deve ter no maximo 254 caracteres")
        self._value = v

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Email):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other.strip().lower()
        return NotImplemented  # type: ignore[return-value]

    def __hash__(self) -> int:
        return hash(self._value)
