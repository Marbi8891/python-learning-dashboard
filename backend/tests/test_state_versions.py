"""Control de versiones de los documentos de progreso: dos pestañas no se pisan (409)."""

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
def test_without_version_it_still_saves_like_older_apps(client, auth_headers, path):
    """Una pestaña con la versión anterior de la web (sin `version`) sigue pudiendo guardar."""
    client.put(path, json={"data": {"v": 1}, "version": 0}, headers=auth_headers)
    legacy = client.put(path, json={"data": {"v": "antigua"}}, headers=auth_headers)
    assert legacy.status_code == 200 and legacy.json()["version"] == 2


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
