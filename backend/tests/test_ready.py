"""/api/v1/ready: la base de datos responde y el esquema está en la última migración (#111)."""

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app import readiness
from app.database import get_db
from app.main import app


def stamp(client, revision):
    with client.engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32))"))
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(text("INSERT INTO alembic_version VALUES (:r)"), {"r": revision})


def test_ready_when_database_answers_and_schema_is_current(client):
    stamp(client, readiness.expected_revision())
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["migrations"] == "ok"
    assert isinstance(body["database_ms"], int)
    assert response.headers["cache-control"] == "no-store"


def test_expected_revision_is_the_latest_migration_file():
    # El nombre de cada archivo de migración lleva su revisión: la última es la de cabeza
    revision = readiness.expected_revision()
    assert revision
    versions = readiness.ALEMBIC_INI.parent / "migrations" / "versions"
    assert any(revision in p.name for p in versions.glob("*.py"))


def test_not_ready_when_a_migration_is_missing(client):
    stamp(client, "revision-antigua")
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "database": "ok",
        "migrations": "pending",
        "database_ms": response.json()["database_ms"],
    }


def test_not_ready_when_schema_was_never_versioned(client):
    # Sin tabla alembic_version (base creada a mano): no se sabe en qué versión está
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json()["migrations"] == "pending"


def test_not_ready_when_database_does_not_answer_and_no_detail_leaks(client, caplog):
    class Broken:
        def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, Exception("password=secreta host=neon"))

    app.dependency_overrides[get_db] = lambda: Broken()
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "error", "migrations": "unknown"}
    assert "secreta" not in response.text
    assert "la base de datos no responde" in caplog.text  # el detalle va al log, no al cliente


def test_health_stays_independent_of_the_database(client):
    # Render reinicia el servicio si /api/health falla: no debe depender de que Neon despierte
    class Broken:
        def execute(self, *args, **kwargs):
            raise AssertionError("health no debe tocar la base de datos")

    app.dependency_overrides[get_db] = lambda: Broken()
    assert client.get("/api/health").json()["status"] == "ok"
