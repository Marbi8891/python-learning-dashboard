"""Punto de entrada de la API.

Arrancar en local (desde la carpeta backend):
    alembic upgrade head      # crea o actualiza las tablas
    python -m app.seed        # carga las lecciones
    uvicorn app.main:app --reload
Documentación interactiva: http://127.0.0.1:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.local_site import mount_frontend
from app.routers import account, attempts, auth, lessons, progress
from app.security import get_jwt_secret

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_jwt_secret()  # falla al arrancar si falta JWT_SECRET, no en el primer login
    yield


app = FastAPI(title="Python Learning Dashboard API", version="0.6.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

for router in (lessons.router, auth.router, account.router, progress.router, attempts.router):
    app.include_router(router)


@app.get("/api/health", tags=["sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}


if get_settings().serve_frontend:
    mount_frontend(app, get_settings().frontend_dir)
