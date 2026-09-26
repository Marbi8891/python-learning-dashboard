"""Progreso por usuario e intentos de ejercicios."""

from tests.conftest import login, register


def test_progress_requires_auth(client):
    assert client.get("/api/progress").status_code == 401
    assert client.put("/api/progress/variables").status_code == 401


def test_complete_is_idempotent_and_listed(client, auth_headers):
    first = client.put("/api/progress/variables", headers=auth_headers)
    second = client.put("/api/progress/variables", headers=auth_headers)
    assert first.status_code == second.status_code == 200
    assert first.json()["completed_at"] == second.json()["completed_at"]

    progress = client.get("/api/progress", headers=auth_headers).json()
    assert [p["lesson_slug"] for p in progress] == ["variables"]


def test_uncomplete(client, auth_headers):
    client.put("/api/progress/tipos", headers=auth_headers)
    assert client.delete("/api/progress/tipos", headers=auth_headers).status_code == 204
    assert client.get("/api/progress", headers=auth_headers).json() == []


def test_unknown_lesson_404(client, auth_headers):
    assert client.put("/api/progress/no-existe", headers=auth_headers).status_code == 404


def test_import_merges_and_ignores_unknown(client, auth_headers):
    client.put("/api/progress/variables", headers=auth_headers)
    response = client.post(
        "/api/progress/import",
        json={"lesson_slugs": ["variables", "tipos", "no-existe", "tipos"]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert sorted(p["lesson_slug"] for p in response.json()) == ["tipos", "variables"]


def test_progress_is_private_per_user(client, auth_headers):
    client.put("/api/progress/variables", headers=auth_headers)
    register(client, email="luis@example.com", name="Luis")
    token = login(client, email="luis@example.com").json()["access_token"]
    other = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/progress", headers=other).json() == []


def test_failed_attempt_is_stored_but_does_not_complete(client, auth_headers):
    url = "/api/lessons/variables/attempts"
    response = client.post(url, json={"code": "print(1)", "passed": False}, headers=auth_headers)
    assert response.status_code == 201
    assert client.get("/api/progress", headers=auth_headers).json() == []


def test_passed_attempt_completes_lesson(client, auth_headers):
    url = "/api/lessons/funciones/attempts"
    client.post(url, json={"code": "v1", "passed": False}, headers=auth_headers)
    client.post(url, json={"code": "v2", "passed": True}, headers=auth_headers)

    history = client.get(url, headers=auth_headers).json()
    assert [a["code"] for a in history] == ["v2", "v1"]  # más reciente primero
    progress = client.get("/api/progress", headers=auth_headers).json()
    assert [p["lesson_slug"] for p in progress] == ["funciones"]


def test_attempt_code_size_limited(client, auth_headers):
    url = "/api/lessons/variables/attempts"
    response = client.post(url, json={"code": "x" * 20_001, "passed": True}, headers=auth_headers)
    assert response.status_code == 422


def test_progress_list_uses_single_query(client, auth_headers):
    from sqlalchemy import event

    for slug in ("variables", "tipos", "operadores"):
        client.put(f"/api/progress/{slug}", headers=auth_headers)
    queries = []
    event.listen(client.engine, "before_cursor_execute", lambda *a: queries.append(a[2]))
    client.get("/api/progress", headers=auth_headers)
    assert len(queries) == 2  # usuario del token + progreso (JOIN), sin N+1
