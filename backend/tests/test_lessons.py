"""Tests de la API de lecciones con una base de datos SQLite en memoria."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import seed


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # la misma conexión en memoria para todo el test
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)

    with testing_session() as db:
        seed(db)

    def override_get_db():
        with testing_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        test_client.engine = engine
        yield test_client
    app.dependency_overrides.clear()


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


def test_unknown_lesson_returns_404(client):
    response = client.get("/api/lessons/no-existe")
    assert response.status_code == 404


def test_seed_is_idempotent(client):
    with sessionmaker(bind=client.engine)() as db:
        seed(db)  # segunda ejecución: no debe duplicar nada
    modules = client.get("/api/modules").json()
    assert sum(len(m["lessons"]) for m in modules) == 15
