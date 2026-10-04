"""Estado de los cursos de DAW de la app Android: /api/course-state/{curso} (ADR-0018)."""

from app.schemas import MAX_PCAP_STATE_BYTES


def test_requires_login(client):
    assert client.get("/api/course-state/sql").status_code == 401
    assert client.put("/api/course-state/sql", json={"data": {}}).status_code == 401


def test_unknown_course_is_404(client, auth_headers):
    assert client.get("/api/course-state/cobol", headers=auth_headers).status_code == 404
    assert (
        client.put("/api/course-state/cobol", json={"data": {}}, headers=auth_headers).status_code
        == 404
    )


def test_each_course_is_a_separate_document(client, auth_headers):
    assert client.get("/api/course-state/java", headers=auth_headers).json() == {
        "data": {},
        "updated_at": None,
    }
    java = {"answers": {"java-01": [False, True]}}
    saved = client.put("/api/course-state/java", json={"data": java}, headers=auth_headers)
    assert saved.status_code == 200 and saved.json()["updated_at"]
    client.put("/api/course-state/sql", json={"data": {"answers": {}}}, headers=auth_headers)

    java["answers"]["java-02"] = [True]
    client.put("/api/course-state/java", json={"data": java}, headers=auth_headers)
    got = client.get("/api/course-state/java", headers=auth_headers).json()["data"]
    assert got["answers"] == {"java-01": [False, True], "java-02": [True]}
    assert client.get("/api/course-state/sql", headers=auth_headers).json()["data"] == {
        "answers": {}
    }


def test_rejects_oversized_state(client, auth_headers):
    huge = {"answers": {"x": ["a" * MAX_PCAP_STATE_BYTES]}}
    response = client.put("/api/course-state/js", json={"data": huge}, headers=auth_headers)
    assert response.status_code == 422


def test_export_and_delete_include_course_states(client, auth_headers):
    assert client.get("/api/users/me/export", headers=auth_headers).json()["courses"] == {}
    client.put("/api/course-state/js", json={"data": {"bestCombo": 3}}, headers=auth_headers)
    exported = client.get("/api/users/me/export", headers=auth_headers).json()
    assert exported["courses"] == {"js": {"bestCombo": 3}}


def test_learning_progress_is_saved_and_exported(client, auth_headers):
    """El progreso por conceptos (ADR-0031) usa el mismo mecanismo, con el id «learn»."""
    learn = {
        "v": 1,
        "ex": {"buc-01": {"h": [False, True], "last": "2026-10-04T10:00:00.000Z", "n": 2}},
        "errors": {"bucles.range-fin": {"n": 1, "last": "2026-10-04T09:00:00.000Z", "streak": 1}},
    }
    saved = client.put("/api/course-state/learn", json={"data": learn}, headers=auth_headers)
    assert saved.status_code == 200
    assert client.get("/api/course-state/learn", headers=auth_headers).json()["data"] == learn
    exported = client.get("/api/users/me/export", headers=auth_headers).json()
    assert exported["courses"]["learn"] == learn
