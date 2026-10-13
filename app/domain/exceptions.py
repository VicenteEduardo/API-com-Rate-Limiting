"""Erros que o domínio reconhece — com nomes que dizem o que aconteceu.

A camada HTTP traduz cada um para o status certo (409, 404, 429...), mas aqui
em baixo falamos a língua do negócio: "utilizador já existe", "não encontrado".
"""

class DomainError(Exception):
    """Base para todos os erros de negócio deste sistema."""


class UserAlreadyExistsError(DomainError):
    """O e-mail já pertence a outro utilizador."""


class UserNotFoundError(DomainError):
    """Não há nenhum utilizador com esse identificador."""


class RateLimitExceededError(DomainError):
    """O cliente fez pedidos depressa demais — precisa esperar um pouco."""

    def __init__(self, message: str = "rate limit excedido", retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after
