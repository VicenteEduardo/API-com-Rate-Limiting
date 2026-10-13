"""Testes de integracao da API (inclui rate limiting via HTTP)."""


def test_health_isento_e_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_crud_usuario(client):
    r = client.post("/api/v1/users", json={"name": "Ada Lovelace", "email": "ada@example.com"})
    assert r.status_code == 201, r.text
    uid = r.json()["id"]
    assert "X-RateLimit-Limit" in r.headers
    assert "X-RateLimit-Remaining" in r.headers

    r = client.get(f"/api/v1/users/{uid}")
    assert r.status_code == 200

    r = client.get("/api/v1/users?limit=10&offset=0")
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    # duplicado -> 409
    r = client.post("/api/v1/users", json={"name": "Outra", "email": "ada@example.com"})
    assert r.status_code == 409

    r = client.delete(f"/api/v1/users/{uid}")
    assert r.status_code == 204

    r = client.get(f"/api/v1/users/{uid}")
    assert r.status_code == 404


def test_rate_limit_bloqueia_429(client):
    from app.main import app
    from app.presentation.dependencies import get_rate_limiter

    limiter = get_rate_limiter()
    limiter.reset_all()
    limiter.limit = 3
    try:
        for _ in range(3):
            r = client.post("/api/v1/users", json={"name": "Ab", "email": "x@y.com"})
            # pode ser 201 ou 409 (duplicado), mas nao 429 ainda
            assert r.status_code in (201, 409), r.text
        r = client.post("/api/v1/users", json={"name": "Ab", "email": "novo@novo.com"})
        assert r.status_code == 429
        assert r.headers.get("Retry-After")
        assert r.json()["code"] == "rate_limit_exceeded"
    finally:
        limiter.reset_all()
        limiter.limit = 60


def test_openapi_exposto(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "paths" in r.json()
