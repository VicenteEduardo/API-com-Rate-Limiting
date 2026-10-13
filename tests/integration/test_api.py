"""Integração: auth JWT, perfis e rate limiting por HTTP."""

from app.application.use_cases import ChangeUserRoleUseCase
from app.domain.entities import User


def register(client, name="Ada Lovelace", email="ada@example.com", password="segredo123"):
    return client.post("/api/v1/auth/register", json={"name": name, "email": email, "password": password})


def login(client, email="ada@example.com", password="segredo123"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def auth_headers(client, email="ada@example.com", password="segredo123"):
    token = login(client, email, password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def make_admin(repo, user_id):
    user = repo.get_by_id(user_id)
    assert user is not None
    admin_actor = User(name="Root", email="root@x.com", role="admin")
    ChangeUserRoleUseCase(repo).execute(user_id, "admin", admin_actor)
    assert repo.get_by_id(user_id).is_admin


def test_health_isento_e_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_login_me(client):
    r = register(client)
    assert r.status_code == 201, r.text
    assert r.json()["role"] == "user"
    assert "password" not in r.text and "password_hash" not in r.text

    r = register(client)  # duplicado
    assert r.status_code == 409

    r = login(client)
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"

    r = login(client, password="errada123")
    assert r.status_code == 401

    r = client.get("/api/v1/auth/me", headers=auth_headers(client))
    assert r.status_code == 200
    assert r.json()["email"] == "ada@example.com"

    r = client.get("/api/v1/auth/me")  # sem token
    assert r.status_code == 401


def test_perfis_admin_e_user(client, repo):
    ada_id = register(client).json()["id"]
    register(client, name="Grace", email="grace@example.com")
    make_admin(repo, ada_id)

    admin_h = auth_headers(client)
    user_h = auth_headers(client, email="grace@example.com")

    # listar: só admin
    assert client.get("/api/v1/users", headers=user_h).status_code == 403
    r = client.get("/api/v1/users", headers=admin_h)
    assert r.status_code == 200
    assert r.json()["total"] == 2

    # ver outro: user comum não pode, admin pode
    grace_id = login(client, email="grace@example.com").json()["user_id"]
    assert client.get(f"/api/v1/users/{grace_id}", headers=user_h).status_code == 200
    assert client.get(f"/api/v1/users/{ada_id}", headers=user_h).status_code == 403
    assert client.get(f"/api/v1/users/{grace_id}", headers=admin_h).status_code == 200

    # promover: só admin
    r = client.patch(f"/api/v1/users/{grace_id}/role", json={"role": "admin"}, headers=user_h)
    assert r.status_code == 403
    r = client.patch(f"/api/v1/users/{grace_id}/role", json={"role": "admin"}, headers=admin_h)
    assert r.status_code == 200
    assert r.json()["role"] == "admin"

    # apagar a si próprio
    r = client.delete(f"/api/v1/users/{grace_id}", headers=auth_headers(client, email="grace@example.com"))
    assert r.status_code == 204


def test_rate_limit_bloqueia_429(client):
    from app.presentation.dependencies import get_rate_limiter

    limiter = get_rate_limiter()
    limiter.reset_all()
    limiter.limit = 3
    try:
        for i in range(3):
            r = register(client, email=f"u{i}@x.com")
            assert r.status_code in (201, 409), r.text
        r = register(client, email="novo@novo.com")
        assert r.status_code == 429
        assert r.headers.get("Retry-After")
        assert r.json()["code"] == "rate_limit_exceeded"
    finally:
        limiter.reset_all()
        limiter.limit = 60


def test_openapi_exposto(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/users" in paths
