"""Aislamiento entre cuentas (OWASP API1 BOLA): un alumno nunca llega a los datos de otro.

Ana guarda datos en cada ruta privada; Luis, con su propia sesión válida, intenta leerlos,
sobrescribirlos y borrarlos.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CourseState, ExerciseAttempt, LessonProgress, PcapState, User
from app.rate_limit import auth_limiter, login_failures
from tests.conftest import PASSWORD, login, register

V1 = "/api/v1"
SECRET_CODE = "secreto = 'solo de Ana'"


def session_for(client, email, name):
    assert register(client, email=email, name=name).status_code == 201
    token = login(client, email=email).json()["access_token"]
    auth_limiter.reset()
    login_failures.reset()
    return {"Authorization": f"Bearer {token}"}


def ana_saves_everything(client, ana):
    assert client.put(f"{V1}/progress/variables", headers=ana).status_code == 200
    attempt = client.post(
        f"{V1}/lessons/variables/attempts",
        json={"code": SECRET_CODE, "passed": True},
        headers=ana,
    )
    assert attempt.status_code == 201
    course = client.put(f"{V1}/course-state/sql", json={"data": {"de": "Ana"}}, headers=ana)
    assert course.status_code == 200
    assert (
        client.put(f"{V1}/pcap-state", json={"data": {"de": "Ana"}}, headers=ana).status_code == 200
    )


def count_rows(client, model, email):
    with Session(client.engine) as db:
        user_id = db.scalar(select(User.id).where(User.email == email))
        return db.scalar(select(func.count()).select_from(model).where(model.user_id == user_id))


def test_another_student_cannot_read_any_private_data(client):
    ana = session_for(client, "ana@example.com", "Ana")
    luis = session_for(client, "luis@example.com", "Luis")
    ana_saves_everything(client, ana)

    assert client.get(f"{V1}/progress", headers=luis).json() == []
    assert client.get(f"{V1}/lessons/variables/attempts", headers=luis).json() == []
    assert client.get(f"{V1}/course-state/sql", headers=luis).json()["data"] == {}
    assert client.get(f"{V1}/pcap-state", headers=luis).json()["data"] == {}
    assert client.get(f"{V1}/users/me", headers=luis).json()["email"] == "luis@example.com"

    exported = client.get(f"{V1}/users/me/export", headers=luis)
    assert exported.status_code == 200
    assert "ana@example.com" not in exported.text and SECRET_CODE not in exported.text
    activity = client.get(f"{V1}/users/me/activity", headers=luis).text
    assert "ana@example.com" not in activity


def test_ids_or_emails_in_the_request_are_ignored(client):
    ana = session_for(client, "ana@example.com", "Ana")
    luis = session_for(client, "luis@example.com", "Luis")
    ana_saves_everything(client, ana)
    with Session(client.engine) as db:
        ana_id = db.scalar(select(User.id).where(User.email == "ana@example.com"))

    for params in ({"user_id": ana_id}, {"user": "ana@example.com"}, {"id": ana_id}):
        assert client.get(f"{V1}/progress", params=params, headers=luis).json() == []
        assert client.get(f"{V1}/pcap-state", params=params, headers=luis).json()["data"] == {}
        me = client.get(f"{V1}/users/me", params=params, headers=luis).json()
        assert me["email"] == "luis@example.com"

    # Un campo de propietario en el cuerpo no cambia de cuenta
    body = {"data": {"de": "Luis"}, "user_id": ana_id}
    client.put(f"{V1}/course-state/sql", json=body, headers=luis)
    assert client.get(f"{V1}/course-state/sql", headers=ana).json()["data"] == {"de": "Ana"}


def test_another_student_cannot_overwrite_or_delete_data(client):
    ana = session_for(client, "ana@example.com", "Ana")
    luis = session_for(client, "luis@example.com", "Luis")
    ana_saves_everything(client, ana)

    # Las escrituras de Luis van a su propia cuenta
    client.put(f"{V1}/course-state/sql", json={"data": {"de": "Luis"}}, headers=luis)
    client.put(f"{V1}/pcap-state", json={"data": {"de": "Luis"}}, headers=luis)
    client.delete(f"{V1}/progress/variables", headers=luis)
    client.patch(f"{V1}/users/me", json={"display_name": "Cambiado"}, headers=luis)

    assert client.get(f"{V1}/course-state/sql", headers=ana).json()["data"] == {"de": "Ana"}
    assert client.get(f"{V1}/pcap-state", headers=ana).json()["data"] == {"de": "Ana"}
    assert [p["lesson_slug"] for p in client.get(f"{V1}/progress", headers=ana).json()] == [
        "variables"
    ]
    assert client.get(f"{V1}/users/me", headers=ana).json()["display_name"] == "Ana"

    # Borrar la cuenta de Luis no toca ni una fila de Ana
    deleted = client.post(f"{V1}/users/me/delete", json={"password": PASSWORD}, headers=luis)
    assert deleted.status_code == 204
    for model in (LessonProgress, ExerciseAttempt, CourseState, PcapState):
        assert count_rows(client, model, "ana@example.com") == 1, model.__name__
    assert client.get(f"{V1}/users/me", headers=ana).status_code == 200
    assert client.get(f"{V1}/users/me", headers=luis).status_code == 401


def test_private_routes_require_a_session(client):
    private = [
        ("get", f"{V1}/progress"),
        ("put", f"{V1}/progress/variables"),
        ("get", f"{V1}/lessons/variables/attempts"),
        ("get", f"{V1}/course-state/sql"),
        ("get", f"{V1}/pcap-state"),
        ("get", f"{V1}/users/me"),
        ("get", f"{V1}/users/me/export"),
        ("get", f"{V1}/users/me/activity"),
        ("get", f"{V1}/dashboard"),
        ("get", f"{V1}/dashboard/activity"),
    ]
    for method, path in private:
        for headers in ({}, {"Authorization": "Bearer no-es-un-token"}):
            response = getattr(client, method)(path, headers=headers)
            assert response.status_code == 401, (method, path, headers)
