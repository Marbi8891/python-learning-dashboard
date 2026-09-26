"""Tests de la API de lecciones con una base de datos SQLite en memoria."""

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from app.seed import seed


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_modules_are_ordered_with_lessons(client):
    modules = client.get("/api/modules").json()
    assert [m["slug"] for m in modules] == [
        "fundamentos",
        "intermedio",
        "avanzado",
        "especializacion",
    ]
    assert [lesson["slug"] for lesson in modules[0]["lessons"]] == [
        "variables",
        "tipos",
        "operadores",
        "input",
    ]


def test_modules_endpoint_avoids_n_plus_one(client):
    queries = []
    event.listen(client.engine, "before_cursor_execute", lambda *args: queries.append(args[2]))
    client.get("/api/modules")
    assert len(queries) == 2  # módulos + lecciones, sin importar cuántos módulos haya


def test_lesson_detail(client):
    lesson = client.get("/api/lessons/variables").json()
    assert lesson["title"] == "Variables y print()"
    assert lesson["module_slug"] == "fundamentos"
    assert "print(" in lesson["example_code"]
    assert len(lesson["quiz"]) == 3 and lesson["quiz"][0]["options"]
    assert lesson["challenge"]["title"] == "Tarjeta de presentación"


def test_every_lesson_has_content_and_sources(client):
    modules = client.get("/api/modules").json()
    for module in modules:
        for summary in module["lessons"]:
            lesson = client.get(f"/api/lessons/{summary['slug']}").json()
            assert lesson["theory"] and lesson["example_code"] and lesson["exercise"]
            assert lesson["sources"], f"{summary['slug']} no cita ninguna fuente"
            assert all(s["url"].startswith("https://") for s in lesson["sources"])
            assert lesson["starter"] and lesson["checks"], (
                f"{summary['slug']} sin ejercicio corregible"
            )
            assert lesson["assistant"]["hint"] and len(lesson["assistant"]["faq"]) >= 2


def test_unknown_lesson_returns_404(client):
    response = client.get("/api/lessons/no-existe")
    assert response.status_code == 404


def test_seed_is_idempotent(client):
    with sessionmaker(bind=client.engine)() as db:
        seed(db)  # segunda ejecución: no debe duplicar nada
    modules = client.get("/api/modules").json()
    assert sum(len(m["lessons"]) for m in modules) == 15
