"""Tests de la API de lecciones con una base de datos SQLite en memoria."""

import json

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.seed import seed


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "email": False}


def test_health_reports_email_when_smtp_is_configured(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "smtp_host", "smtp.example.com")
    assert client.get("/api/health").json()["email"] is True


def test_modules_are_ordered_with_lessons(client):
    modules = client.get("/api/modules").json()
    # Temario organizado por los bloques del examen PCAP (ver ADR-0009)
    assert [m["slug"] for m in modules] == [
        "fundamentos",
        "modulos",
        "excepciones",
        "strings",
        "poo",
        "miscelanea",
        "especializacion",
    ]
    assert [lesson["slug"] for lesson in modules[0]["lessons"]][:4] == [
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
    assert sum(len(m["lessons"]) for m in modules) == 27


def test_seed_moves_lessons_and_removes_empty_modules(client, tmp_path):
    """Reorganizar el temario conserva las lecciones (y su progreso) y borra los módulos vacíos."""
    data = {
        "modules": [
            {
                "slug": "nuevo",
                "title": "Nuevo",
                "lessons": [
                    {"slug": slug, "title": slug}
                    for slug in ("variables", "pytest", "automatizacion", "flask")
                ],
            },
        ]
    }
    path = tmp_path / "lessons.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with sessionmaker(bind=client.engine)() as db:
        seed(db, path)
    modules = client.get("/api/modules").json()
    slugs = {m["slug"] for m in modules}
    assert "nuevo" in slugs and "fundamentos" in slugs  # fundamentos aún tiene otras lecciones
    assert client.get("/api/lessons/variables").json()["module_slug"] == "nuevo"
    assert "especializacion" not in slugs  # se quedó sin lecciones
