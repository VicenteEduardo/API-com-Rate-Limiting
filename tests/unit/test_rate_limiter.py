"""TDD — Rate limiter sliding window."""

from app.infrastructure.rate_limiter import InMemorySlidingWindowRateLimiter


def test_permite_ate_limite():
    rl = InMemorySlidingWindowRateLimiter(limit_per_minute=3)
    assert rl.is_allowed("k")[0] is True
    assert rl.is_allowed("k")[0] is True
    assert rl.is_allowed("k")[0] is True
    allowed, info = rl.is_allowed("k")
    assert allowed is False
    assert info["remaining"] == 0
    assert info["retry_after"] >= 1


def test_chaves_isoladas():
    rl = InMemorySlidingWindowRateLimiter(limit_per_minute=1)
    assert rl.is_allowed("a")[0] is True
    assert rl.is_allowed("a")[0] is False
    assert rl.is_allowed("b")[0] is True


def test_reset():
    rl = InMemorySlidingWindowRateLimiter(limit_per_minute=1)
    rl.is_allowed("k")
    assert rl.is_allowed("k")[0] is False
    rl.reset("k")
    assert rl.is_allowed("k")[0] is True


def test_headers_info():
    rl = InMemorySlidingWindowRateLimiter(limit_per_minute=10)
    allowed, info = rl.is_allowed("k")
    assert allowed is True
    assert info["limit"] == 10
    assert info["remaining"] == 9
