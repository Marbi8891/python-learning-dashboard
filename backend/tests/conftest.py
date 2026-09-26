"""Fixtures compartidas. Cada test usa una base de datos SQLite en memoria nueva."""

import os

# Debe definirse antes de importar la app (la configuración se lee una sola vez)
os.environ.setdefault("JWT_SECRET", "secreto-solo-para-tests-" + "x" * 32)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.rate_limit import auth_limiter  # noqa: E402
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
    auth_limiter.reset()
    with TestClient(app) as test_client:
        test_client.engine = engine
        yield test_client
    app.dependency_overrides.clear()
    auth_limiter.reset()


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
    auth_limiter.reset()  # que el registro y el login de la fixture no consuman el límite
    return {"Authorization": f"Bearer {token}"}
