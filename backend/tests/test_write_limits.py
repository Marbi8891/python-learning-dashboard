"""AUD-009: límite de guardados de progreso por usuario (la BD gratuita tiene poco espacio)."""

import pytest

from app.rate_limit import write_limiter
from tests.conftest import login, register


@pytest.fixture
def small_limit(monkeypatch):
    monkeypatch.setattr(write_limiter, "max_calls", 3)


def _headers(client, email):
    register(client, email=email)
    return {"Authorization": f"Bearer {login(client, email=email).json()['access_token']}"}


def test_default_limit_leaves_room_for_real_use():
    assert write_limiter.max_calls >= 60  # la web guarda como mucho cada 1,5 s por almacén


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("put", "/api/v1/pcap-state", {"data": {}}),
        ("put", "/api/v1/course-state/sql", {"data": {}}),
        ("post", "/api/v1/progress/import", {"lesson_slugs": []}),
        ("put", "/api/v1/progress/variables", None),
        ("post", "/api/v1/lessons/variables/attempts", {"code": "print(1)", "passed": False}),
    ],
)
def test_writes_are_limited_per_user(client, auth_headers, small_limit, method, path, body):
    send = getattr(client, method)
    kwargs = {"headers": auth_headers}
    if body is not None:
        kwargs["json"] = body
    # Sin versión, el estado se sobrescribe: no hay 409 entre un guardado y el siguiente
    codes = [send(path, **kwargs).status_code for _ in range(4)]
    assert all(code < 400 for code in codes[:3]), codes
    assert codes[3] == 429
    assert "Tu progreso sigue en este navegador" in send(path, **kwargs).json()["detail"]


def _save(client, headers):
    return client.put("/api/v1/pcap-state", headers=headers, json={"data": {}}).status_code


def test_limit_is_per_user_and_reads_are_free(client, auth_headers, small_limit):
    assert [_save(client, auth_headers) for _ in range(4)] == [200, 200, 200, 429]
    # Leer no cuenta
    assert client.get("/api/v1/pcap-state", headers=auth_headers).status_code == 200
    # Otro usuario no se ve afectado
    other = _headers(client, "otra@example.com")
    assert _save(client, other) == 200


def test_rate_limited_write_is_logged(client, auth_headers, small_limit, caplog):
    for _ in range(4):
        client.put("/api/v1/pcap-state", headers=auth_headers, json={"data": {}})
    assert any('"progress.rate_limited"' in record.getMessage() for record in caplog.records)
