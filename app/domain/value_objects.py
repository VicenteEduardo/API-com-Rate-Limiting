"""Objetos de valor do domínio.

Um Value Object não tem identidade própria: dois e-mails iguais são o mesmo
e-mail. Por isso são imutáveis na prática e validam-se a si mesmos — se um
Email existe, é porque é válido. Ninguém precisa validar depois.
"""

from __future__ import annotations

import re

# Expressão simples mas honesta: garante "algo@algo.algo" sem espaços.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Email:
    """Um endereço de e-mail válido.

    Normaliza (minúsculas, sem espaços nas bordas) logo na criação, para que
    "ADA@Exemplo.com" e "ada@exemplo.com" sejam tratados como o mesmo e-mail
    em todo o sistema — sem surpresas nas pesquisas por duplicados.
    """

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
