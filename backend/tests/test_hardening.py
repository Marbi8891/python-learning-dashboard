"""Endurecimiento de seguridad (ADR-0022): IP real, bloqueos, sesiones, tamaños y datos."""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher

from app.config import get_settings
from app.rate_limit import auth_limiter, login_failures
from app.security import ALGORITHM, decode_access_token, get_jwt_secret
from tests.conftest import PASSWORD, login, register


def test_forged_forwarded_for_does_not_bypass_ip_limit(client, monkeypatch):
    # Detrás de un proxy (Render), la IP real es la que el proxy añade al final
    monkeypatch.setattr(get_settings(), "trusted_proxy_hops", 1)
    codes = []
    for n in range(7):
        response = client.post(
            "/api/auth/login",
            data={"username": "x@example.com", "password": "nope"},
            headers={
                "X-Forwarded-For": f"10.0.0.{n}, 203.0.113.7"
            },  # la primera la inventa el cliente
        )
        codes.append(response.status_code)
    assert codes.count(429) >= 2  # límite de 5 por minuto para la IP 203.0.113.7


def test_without_trusted_proxy_the_header_is_ignored(client):
    for n in range(5):
        client.post(
            "/api/auth/login",
            data={"username": "x@example.com", "password": "nope"},
            headers={"X-Forwarded-For": f"10.0.0.{n}"},
        )
    assert login(client).status_code == 429  # misma IP de conexión: sigue limitada


def test_account_is_locked_after_repeated_failures_from_many_ips(client, monkeypatch):
    register(client)
    monkeypatch.setattr(login_failures, "max_calls", 3)
    for _ in range(3):
        auth_limiter.reset()  # simula que cada intento llega desde una IP distinta
        assert login(client, password="incorrecta-000").status_code == 401
    auth_limiter.reset()
    assert login(client).status_code == 429  # ni con la contraseña buena, durante el bloqueo


def test_successful_login_clears_the_failure_count(client, monkeypatch):
    register(client)
    monkeypatch.setattr(login_failures, "max_calls", 3)
    login(client, password="incorrecta-000")
    auth_limiter.reset()
    assert login(client).status_code == 200
    assert not login_failures.blocked("ana@example.com")


def test_old_password_hashes_are_upgraded_on_login(client):
    register(client)
    strong_old = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4).hash(PASSWORD)
    with client.engine.begin() as conn:
        conn.exec_driver_sql("UPDATE users SET password_hash = ?", (strong_old,))
    auth_limiter.reset()
    assert login(client).status_code == 200
    with client.engine.connect() as conn:
        new_hash = conn.exec_driver_sql("SELECT password_hash FROM users").scalar_one()
    assert new_hash != strong_old and "m=19456,t=2,p=1" in new_hash


def test_logout_all_invalidates_every_session(client, auth_headers):
    other = {"Authorization": f"Bearer {login(client).json()['access_token']}"}
    assert client.post("/api/auth/logout-all", headers=auth_headers).status_code == 204
    assert client.get("/api/users/me", headers=auth_headers).status_code == 401
    assert client.get("/api/users/me", headers=other).status_code == 401
    auth_limiter.reset()
    assert login(client).status_code == 200  # se puede volver a entrar


def test_tokens_without_expiry_are_rejected(client):
    token = jwt.encode({"sub": "1", "ver": 0}, get_jwt_secret(), algorithm=ALGORITHM)
    assert decode_access_token(token) is None
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        get_jwt_secret(),
        algorithm=ALGORITHM,
    )
    assert decode_access_token(expired) is None


def test_oversized_bodies_are_rejected_before_parsing(client, auth_headers):
    huge = b'{"data": {"x": "' + b"a" * (get_settings().max_body_bytes + 10) + b'"}}'
    declared = client.put(
        "/api/pcap-state",
        content=huge,
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    assert declared.status_code == 413

    def chunks():  # sin Content-Length: se cuenta lo que llega
        for _ in range(40):
            yield b"a" * 10_000

    streamed = client.put(
        "/api/pcap-state",
        content=chunks(),
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    assert streamed.status_code == 413


def test_small_bodies_still_work(client, auth_headers):
    response = client.put("/api/pcap-state", json={"data": {"answers": {}}}, headers=auth_headers)
    assert response.status_code == 200


def test_personal_data_is_never_cached(client, auth_headers):
    response = client.get("/api/users/me/export", headers=auth_headers)
    assert response.headers["Cache-Control"] == "no-store"


def test_api_map_is_not_published_by_default(client):
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_reset_emails_are_limited_per_account(client, monkeypatch):
    register(client)
    sent = []
    monkeypatch.setattr("app.routers.auth.send_email", lambda to, subject, body: sent.append(to))
    for _ in range(5):
        auth_limiter.reset()
        response = client.post(
            "/api/auth/password-reset/request", json={"email": "ana@example.com"}
        )
        assert response.status_code == 202  # la respuesta no cambia
    assert len(sent) == 3


def test_only_recent_attempts_are_kept(client, auth_headers, monkeypatch):
    monkeypatch.setattr(get_settings(), "attempts_kept_per_lesson", 3)
    url = "/api/lessons/variables/attempts"
    for n in range(5):
        client.post(url, json={"code": f"print({n})", "passed": False}, headers=auth_headers)
    with client.engine.connect() as conn:
        codes = [
            row[0] for row in conn.exec_driver_sql("SELECT code FROM exercise_attempts ORDER BY id")
        ]
    assert codes == ["print(2)", "print(3)", "print(4)"]
    assert len(client.get(url, headers=auth_headers).json()) == 3


def test_rate_limiter_forgets_expired_keys(monkeypatch):
    from app.rate_limit import RateLimiter

    limiter = RateLimiter(1, window_seconds=10)
    now = [0.0]
    monkeypatch.setattr("app.rate_limit.time.monotonic", lambda: now[0])
    monkeypatch.setattr("app.rate_limit._SWEEP_ABOVE", 2)
    for key in ("a", "b", "c"):
        limiter.record(key)
    now[0] = 100.0
    limiter.record("d")  # con más de 2 claves, se purgan las caducadas
    assert set(limiter._hits) == {"d"}


def test_body_limit_also_protects_apps_that_do_not_catch_errors():
    import asyncio

    from app.main import BodySizeLimit

    async def reader(scope, receive, send):  # lee el cuerpo sin capturar excepciones
        while (await receive()).get("more_body"):
            pass
        await send({"type": "http.response.start", "status": 200, "headers": []})

    chunks = iter([{"type": "http.request", "body": b"x" * 60, "more_body": True}] * 3)
    sent = []

    async def receive():
        return next(chunks)

    async def send(message):
        sent.append(message)

    guarded = BodySizeLimit(reader, max_bytes=100)
    asyncio.run(guarded({"type": "http", "headers": []}, receive, send))
    assert [m.get("status") for m in sent if m["type"] == "http.response.start"] == [413]
