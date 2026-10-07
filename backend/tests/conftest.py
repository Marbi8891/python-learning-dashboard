"""Fixtures compartidas. Cada test usa una base de datos SQLite en memoria nueva."""

import os

# Debe definirse antes de importar la app (la configuración se lee una sola vez)
os.environ.setdefault("JWT_SECRET", "secreto-solo-para-tests-" + "x" * 32)
# Agentes A2A con el modelo simulado (ADR-0034): se prueban junto al resto de la API
os.environ.setdefault("A2A_ENABLED", "true")
os.environ.setdefault("A2A_MOCK_MODEL", "true")
# Los tests nunca usan una API key real (los del proveedor simulan la API de Anthropic)
os.environ.pop("ANTHROPIC_API_KEY", None)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.rate_limit import auth_limiter, login_failures, reset_requests  # noqa: E402
from app.seed import seed  # noqa: E402

PASSWORD = "contraseña-segura-123"


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
    a2a_limiters = (
        app.state.a2a_limiter,
        app.state.a2a_budget.per_user,
        app.state.a2a_budget.overall,
    )
    for limiter in (auth_limiter, login_failures, reset_requests, *a2a_limiters):
        limiter.reset()
    with TestClient(app) as test_client:
        test_client.engine = engine
        yield test_client
    app.dependency_overrides.clear()
    for limiter in (auth_limiter, login_failures, reset_requests):
        limiter.reset()


def register(client, email="ana@example.com", password=PASSWORD, name="Ana"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "display_name": name, "accept_privacy": True},
    )


def login(client, email="ana@example.com", password=PASSWORD):
    return client.post("/api/auth/login", data={"username": email, "password": password})


@pytest.fixture
def auth_headers(client):
    register(client)
    token = login(client).json()["access_token"]
    for limiter in (auth_limiter, login_failures, reset_requests):
        limiter.reset()  # que el registro y el login de la fixture no consuman el límite
    return {"Authorization": f"Bearer {token}"}
