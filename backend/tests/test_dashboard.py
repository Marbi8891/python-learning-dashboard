"""Panel del alumno: /api/v1/dashboard y /api/v1/dashboard/activity (ADR-0035)."""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ExerciseAttempt, Lesson, LessonProgress, User
from app.rate_limit import auth_limiter
from app.routers import dashboard
from tests.conftest import login, register
from tests.test_google_auth import configure_google

DASHBOARD = "/api/v1/dashboard"
ACTIVITY = "/api/v1/dashboard/activity"


def headers_for(client, email, name):
    assert register(client, email=email, name=name).status_code == 201
    token = login(client, email=email).json()["access_token"]
    auth_limiter.reset()
    return {"Authorization": f"Bearer {token}"}


def test_requires_login(client):
    for path in (DASHBOARD, ACTIVITY):
        response = client.get(path)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
    forged = {"Authorization": "Bearer no-es-un-token"}
    assert client.get(DASHBOARD, headers=forged).status_code == 401


def test_new_student_gets_an_empty_dashboard(client, auth_headers):
    data = client.get(DASHBOARD, headers=auth_headers).json()
    assert data["user"]["display_name"] == "Ana"
    assert data["user"]["email"] == "ana@example.com"
    assert data["user"]["sign_in_method"] == "password"
    assert "password_hash" not in data["user"] and "token_version" not in data["user"]
    lessons = data["lessons"]
    assert lessons["completed"] == 0 and lessons["total"] == 27
    assert lessons["last_completed_at"] is None
    assert lessons["next_lesson"]["slug"] == "variables"
    assert [m["completed"] for m in lessons["modules"]] == [0] * len(lessons["modules"])
    assert sum(m["total"] for m in lessons["modules"]) == 27
    assert data["exercises"] == {
        "attempts": 0,
        "passed": 0,
        "lessons_tried": 0,
        "lessons_passed": 0,
        "last_attempt_at": None,
    }
    assert data["daily"] == [] and data["synced"] == []
    assert client.get(ACTIVITY, headers=auth_headers).json() == {
        "items": [],
        "total": 0,
        "limit": 20,
        "offset": 0,
    }


def test_dashboard_reflects_progress_attempts_and_synced_states(client, auth_headers):
    client.post(
        "/api/lessons/variables/attempts",
        json={"code": "x = 1", "passed": False},
        headers=auth_headers,
    )
    client.post(
        "/api/lessons/variables/attempts",
        json={"code": "x = 2", "passed": True},  # aprobar completa la lección
        headers=auth_headers,
    )
    client.put("/api/progress/tipos", headers=auth_headers)
    client.put("/api/pcap-state", json={"data": {"bestCombo": 2}}, headers=auth_headers)
    client.put("/api/course-state/learn", json={"data": {"v": 1}}, headers=auth_headers)

    data = client.get(DASHBOARD, headers=auth_headers).json()
    assert data["lessons"]["completed"] == 2
    assert data["lessons"]["next_lesson"]["slug"] not in {"variables", "tipos"}
    assert data["lessons"]["modules"][0]["completed"] == 2
    assert data["lessons"]["last_completed_at"]
    assert data["exercises"]["attempts"] == 2
    assert data["exercises"]["passed"] == 1
    assert data["exercises"]["lessons_tried"] == 1
    assert data["exercises"]["lessons_passed"] == 1
    assert data["exercises"]["last_attempt_at"]
    assert [s["key"] for s in data["synced"]] == ["pcap", "learn"]
    today = data["daily"][-1]
    assert today["lessons_completed"] == 2 and today["attempts"] == 2 and today["passed"] == 1

    # Completar una actividad más se refleja al volver a pedir el panel
    client.put("/api/progress/operadores", headers=auth_headers)
    again = client.get(DASHBOARD, headers=auth_headers).json()
    assert again["lessons"]["completed"] == 3


def test_activity_is_paginated_newest_first(client, auth_headers):
    for code in ("a", "b", "c"):
        client.post(
            "/api/lessons/variables/attempts",
            json={"code": code, "passed": False},
            headers=auth_headers,
        )
    client.put("/api/progress/tipos", headers=auth_headers)
    first = client.get(ACTIVITY, params={"limit": 3}, headers=auth_headers).json()
    assert first["total"] == 4 and first["limit"] == 3 and len(first["items"]) == 3
    second = client.get(ACTIVITY, params={"limit": 3, "offset": 3}, headers=auth_headers).json()
    assert len(second["items"]) == 1
    items = first["items"] + second["items"]
    moments = [item["at"] for item in items]
    assert moments == sorted(moments, reverse=True)
    kinds = {item["kind"] for item in items}
    assert kinds == {"attempt", "lesson_completed"}
    completed = next(item for item in items if item["kind"] == "lesson_completed")
    assert completed["lesson_slug"] == "tipos" and completed["passed"] is None
    assert completed["lesson_title"]
    attempt = next(item for item in items if item["kind"] == "attempt")
    assert attempt["passed"] is False and "code" not in attempt  # el código no sale en el historial


def test_rejects_invalid_parameters(client, auth_headers):
    for params in ({"limit": 0}, {"limit": 51}, {"offset": -1}, {"limit": "diez"}):
        assert client.get(ACTIVITY, params=params, headers=auth_headers).status_code == 422
    for offset in (-721, 841, "x"):
        params = {"utc_offset_minutes": offset}
        assert client.get(DASHBOARD, params=params, headers=auth_headers).status_code == 422


def test_a_student_cannot_see_another_students_data(client):
    ana = headers_for(client, "ana@example.com", "Ana")
    luis = headers_for(client, "luis@example.com", "Luis")
    client.put("/api/progress/variables", headers=ana)
    client.post(
        "/api/lessons/variables/attempts",
        json={"code": "secreto = 'de Ana'", "passed": True},
        headers=ana,
    )
    with Session(client.engine) as db:
        ana_id = db.scalar(select(User.id).where(User.email == "ana@example.com"))

    # Luis solo ve lo suyo, aunque intente pedir los datos de Ana con un id en la URL
    for params in ({}, {"user_id": ana_id}, {"user": "ana@example.com"}):
        data = client.get(DASHBOARD, params=params, headers=luis).json()
        assert data["user"]["email"] == "luis@example.com"
        assert data["lessons"]["completed"] == 0
        assert data["exercises"]["attempts"] == 0
        feed = client.get(ACTIVITY, params=params, headers=luis).json()
        assert feed["total"] == 0 and feed["items"] == []

    assert client.get(ACTIVITY, headers=ana).json()["total"] == 2


def test_sign_in_method_follows_the_last_login(client, monkeypatch):
    headers = headers_for(client, "google@example.com", "Ana")
    assert client.get(DASHBOARD, headers=headers).json()["user"]["sign_in_method"] == "password"
    configure_google(
        monkeypatch,
        {"email": "google@example.com", "email_verified": True, "name": "Ana"},
    )
    response = client.post("/api/auth/google", json={"credential": "x" * 40})
    google = {"Authorization": f"Bearer {response.json()['access_token']}"}
    assert client.get(DASHBOARD, headers=google).json()["user"]["sign_in_method"] == "google"
    events = client.get("/api/users/me/activity", headers=google).json()
    assert events[0]["kind"] == "login_google"


def test_daily_uses_the_students_local_day(client, auth_headers):
    now = datetime(2026, 10, 19, 23, 30, tzinfo=UTC)
    with Session(client.engine) as db:
        user_id = db.scalar(select(User.id).where(User.email == "ana@example.com"))
        lesson_id = db.scalar(select(Lesson.id).where(Lesson.slug == "variables"))
        late = datetime(2026, 10, 19, 22, 30)  # sin zona, como lo devuelve SQLite
        db.add(LessonProgress(user_id=user_id, lesson_id=lesson_id, completed_at=late))
        old = now - timedelta(days=dashboard.DAILY_DAYS + 1)
        for moment, ok in ((late, True), (old, False)):
            db.add(
                ExerciseAttempt(
                    user_id=user_id, lesson_id=lesson_id, code="", passed=ok, created_at=moment
                )
            )
        db.commit()

        utc = dashboard._daily(db, user_id, now, 0)
        madrid = dashboard._daily(db, user_id, now, 120)  # 00:30 del día siguiente en Madrid
    assert [d.day for d in utc] == [date(2026, 10, 19)]
    assert [d.day for d in madrid] == [date(2026, 10, 20)]
    assert (utc[0].lessons_completed, utc[0].attempts, utc[0].passed) == (1, 1, 1)
