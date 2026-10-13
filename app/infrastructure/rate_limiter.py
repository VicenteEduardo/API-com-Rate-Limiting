"""Limitador de requisições: janela deslizante em memória.

A ideia é intuitiva: para cada cliente guardamos *quando* cada pedido chegou
nos últimos 60 segundos. Se já houver pedidos demais nessa janela, o novo
pedido espera — devolvemos 429 e dizemos em quanto tempo pode tentar de novo.

Para produção com várias instâncias, a evolução natural é um irmão gémeo desta
classe a falar com Redis. A interface é a mesma, por isso nada mais muda.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict


class InMemorySlidingWindowRateLimiter:
    """Seguro entre threads; uma fila de instantes por chave (ex.: por IP)."""

    def __init__(self, limit_per_minute: int = 60, window_seconds: int = 60):
        if limit_per_minute < 1:
            raise ValueError("limit_per_minute deve ser >= 1")
        self.limit = limit_per_minute
        self.window = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> tuple:
        """Decide e já contabiliza: cada chamada é um pedido a registar."""
        now = time.monotonic()
        cutoff = now - self.window
        with self._lock:
            q = self._hits[key]
            # Esquece o que já saiu da janela — o passado distante não conta.
            while q and q[0] <= cutoff:
                q.popleft()
            if len(q) >= self.limit:
                retry_after = int(q[0] + self.window - now) + 1
                return False, {
                    "limit": self.limit,
                    "remaining": 0,
                    "reset": retry_after,
                    "retry_after": retry_after,
                }
            q.append(now)
            remaining = self.limit - len(q)
            reset = int(q[0] + self.window - now) + 1 if q else self.window
            return True, {"limit": self.limit, "remaining": remaining, "reset": reset, "retry_after": 0}

    def reset(self, key: str) -> None:
        """Perdoa um cliente específico (útil em testes e em suporte)."""
        with self._lock:
            self._hits.pop(key, None)

    def reset_all(self) -> None:
        """Limpa o quadro geral — os testes agradecem entre um caso e outro."""
        with self._lock:
            self._hits.clear()
