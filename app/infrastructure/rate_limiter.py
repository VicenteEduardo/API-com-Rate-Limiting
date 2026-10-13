"""Rate limiter: sliding window log em memoria. Thread-safe.

Algoritmo: guarda timestamps dos ultimos 60s por chave (IP).
Se len(janela) >= limit -> bloqueia (429).
OCP: para Redis/prod, crie RedisRateLimiter implementando IRateLimiter.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict


class InMemorySlidingWindowRateLimiter:
    def __init__(self, limit_per_minute: int = 60, window_seconds: int = 60):
        if limit_per_minute < 1:
            raise ValueError("limit_per_minute deve ser >= 1")
        self.limit = limit_per_minute
        self.window = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> tuple:
        now = time.monotonic()
        cutoff = now - self.window
        with self._lock:
            q = self._hits[key]
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
        with self._lock:
            self._hits.pop(key, None)

    def reset_all(self) -> None:
        with self._lock:
            self._hits.clear()
