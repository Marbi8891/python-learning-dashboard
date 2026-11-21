"""Control de versiones de los documentos de progreso: dos pestañas no se pisan (409)."""

import logging

import pytest

PATHS = ["/api/v1/pcap-state", "/api/v1/course-state/sql"]


@pytest.mark.parametrize("path", PATHS)
def test_version_starts_at_zero_and_grows(client, auth_headers, path):
    assert client.get(path, headers=auth_headers).json()["version"] == 0
    first = client.put(path, json={"data": {"a": 1}, "version": 0}, headers=auth_headers)
    assert first.status_code == 200 and first.json()["version"] == 1
    second = client.put(path, json={"data": {"a": 2}, "version": 1}, headers=auth_headers)
    assert second.json()["version"] == 2
    assert client.get(path, headers=auth_headers).json() | {"updated_at": None} == {
        "data": {"a": 2},
        "version": 2,
        "updated_at": None,
    }


@pytest.mark.parametrize("path", PATHS)
def test_stale_version_gets_409_and_keeps_the_other_tab(client, auth_headers, path):
    """Pestaña A y B leen la versión 0; A guarda; B (con la versión vieja) no puede pisarlo."""
    client.put(path, json={"data": {"tab": "A"}, "version": 0}, headers=auth_headers)
    stale = client.put(path, json={"data": {"tab": "B"}, "version": 0}, headers=auth_headers)
    assert stale.status_code == 409
    assert "otra pestaña" in stale.json()["detail"]
    current = client.get(path, headers=auth_headers).json()
    assert current["data"] == {"tab": "A"} and current["version"] == 1
    # B vuelve a leer, fusiona y guarda con la versión nueva
    merged = client.put(
        path, json={"data": {"tab": "A+B"}, "version": current["version"]}, headers=auth_headers
    )
    assert merged.status_code == 200 and merged.json()["version"] == 2


@pytest.mark.parametrize("path", PATHS)
def test_version_of_a_document_that_does_not_exist_is_a_conflict(client, auth_headers, path):
    response = client.put(path, json={"data": {}, "version": 3}, headers=auth_headers)
    assert response.status_code == 409
    assert client.get(path, headers=auth_headers).json()["version"] == 0


@pytest.mark.parametrize("path", PATHS)
def test_without_version_it_can_still_create_the_document(client, auth_headers, path):
    """Un cliente antiguo (sin `version`) puede crear el documento: no hay nada que pisar."""
    created = client.put(path, json={"data": {"v": 1}}, headers=auth_headers)
    assert created.status_code == 200 and created.json()["version"] == 1


@pytest.mark.parametrize("path", PATHS)
def test_without_version_an_existing_document_is_not_overwritten(
    client, auth_headers, path, caplog
):
    """PLD-003: sin `version` no se sobrescribe en silencio lo guardado desde otro dispositivo."""
    client.put(path, json={"data": {"de": "movil"}, "version": 0}, headers=auth_headers)
    legacy = client.put(path, json={"data": {"de": "pestaña antigua"}}, headers=auth_headers)
    assert legacy.status_code == 428
    assert "vuelve a leer la cuenta" in legacy.json()["detail"]
    current = client.get(path, headers=auth_headers).json()
    assert current["data"] == {"de": "movil"} and current["version"] == 1
    assert any("sync.version_missing" in r.getMessage() for r in caplog.records)
    # Tras releer (como hace la web al recargar), guarda con la versión y funciona
    merged = {"data": {"de": "movil+antigua"}, "version": current["version"]}
    assert client.put(path, json=merged, headers=auth_headers).json()["version"] == 2


@pytest.mark.parametrize("path", PATHS)
def test_explicit_null_version_is_the_same_as_missing(client, auth_headers, path):
    client.put(path, json={"data": {"a": 1}, "version": 0}, headers=auth_headers)
    response = client.put(path, json={"data": {}, "version": None}, headers=auth_headers)
    assert response.status_code == 428


@pytest.mark.parametrize("path", PATHS)
def test_version_from_the_future_is_a_conflict(client, auth_headers, path):
    client.put(path, json={"data": {"a": 1}, "version": 0}, headers=auth_headers)
    response = client.put(path, json={"data": {"a": 2}, "version": 7}, headers=auth_headers)
    assert response.status_code == 409
    assert client.get(path, headers=auth_headers).json() | {"updated_at": None} == {
        "data": {"a": 1},
        "version": 1,
        "updated_at": None,
    }


@pytest.mark.parametrize("path", PATHS)
def test_version_zero_on_an_existing_document_is_a_conflict(client, auth_headers, path):
    """Una pestaña que leyó «vacío» antes de que otra creara el documento no lo pisa."""
    client.put(path, json={"data": {"tab": "A"}, "version": 0}, headers=auth_headers)
    stale = client.put(path, json={"data": {}, "version": 0}, headers=auth_headers)
    assert stale.status_code == 409


@pytest.mark.parametrize("path", PATHS)
def test_conflict_is_logged_without_progress_data(client, auth_headers, path, caplog):
    caplog.set_level(logging.INFO, logger="pld.sync")
    client.put(path, json={"data": {"secreto": "respuesta"}, "version": 0}, headers=auth_headers)
    caplog.clear()
    client.put(path, json={"data": {"x": 1}, "version": 0}, headers=auth_headers)
    lines = [r.getMessage() for r in caplog.records if r.name == "pld.sync"]
    assert len(lines) == 1 and "sync.conflict" in lines[0] and "leida=0" in lines[0]
    assert "respuesta" not in lines[0] and "secreto" not in lines[0]


@pytest.mark.parametrize("path", PATHS)
def test_retrying_the_same_save_after_it_succeeded_is_a_conflict_not_a_duplicate(
    client, auth_headers, path
):
    """Si la respuesta se perdió y la app repite el PUT con la misma versión, no se aplica dos
    veces: recibe 409, relee (ve que ya está guardado) y sigue."""
    body = {"data": {"n": 1}, "version": 0}
    assert client.put(path, json=body, headers=auth_headers).status_code == 200
    assert client.put(path, json=body, headers=auth_headers).status_code == 409
    assert client.get(path, headers=auth_headers).json()["version"] == 1


def test_documents_of_other_users_and_courses_are_not_affected_by_a_conflict(client, auth_headers):
    client.put("/api/v1/course-state/sql", json={"data": {}, "version": 0}, headers=auth_headers)
    client.put("/api/v1/course-state/sql", json={"data": {}, "version": 0}, headers=auth_headers)
    java = client.put(
        "/api/v1/course-state/java", json={"data": {}, "version": 0}, headers=auth_headers
    )
    assert java.status_code == 200


def test_negative_version_is_rejected(client, auth_headers):
    response = client.put(
        "/api/v1/pcap-state", json={"data": {}, "version": -1}, headers=auth_headers
    )
    assert response.status_code == 422


def test_versions_are_per_user_and_per_course(client, auth_headers):
    client.put("/api/v1/course-state/sql", json={"data": {}, "version": 0}, headers=auth_headers)
    java = client.put(
        "/api/v1/course-state/java", json={"data": {}, "version": 0}, headers=auth_headers
    )
    assert java.status_code == 200 and java.json()["version"] == 1


def test_two_first_saves_at_the_same_time_only_one_creates_it(client, auth_headers, monkeypatch):
    """Dos pestañas crean el documento a la vez: la segunda no lo ve al leer y choca al insertar."""
    from sqlalchemy.orm import Session

    from app.models import PcapState

    path = "/api/v1/pcap-state"
    client.put(path, json={"data": {"tab": "A"}, "version": 0}, headers=auth_headers)
    real_get = Session.get

    def get_before_the_other_tab_committed(self, model, *args, **kwargs):
        return None if model is PcapState else real_get(self, model, *args, **kwargs)

    monkeypatch.setattr(Session, "get", get_before_the_other_tab_committed)
    late = client.put(path, json={"data": {"tab": "B"}, "version": 0}, headers=auth_headers)
    assert late.status_code == 409
    monkeypatch.undo()
    current = client.get(path, headers=auth_headers).json()
    assert current["data"] == {"tab": "A"} and current["version"] == 1
