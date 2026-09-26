"""Punto de entrada de la API.

Arrancar en local (desde la carpeta backend):
    uvicorn app.main:app --reload
Documentación interactiva: http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import lessons


@asynccontextmanager
async def lifespan(_: FastAPI):
    # MVP: crea las tablas si no existen. Cuando el esquema cambie, pasaremos a Alembic.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Python Learning Dashboard API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(lessons.router)


@app.get("/api/health", tags=["sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}
