"""Excecoes de dominio. Camada de apresentacao traduz para HTTP."""


class DomainError(Exception):
    pass


class UserAlreadyExistsError(DomainError):
    pass


class UserNotFoundError(DomainError):
    pass


class RateLimitExceededError(DomainError):
    def __init__(self, message: str = "rate limit excedido", retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after
