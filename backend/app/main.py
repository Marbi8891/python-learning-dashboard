"""Punto de entrada de la API.

Arrancar en local (desde la carpeta backend):
    alembic upgrade head      # crea o actualiza las tablas
    python -m app.seed        # carga las lecciones
    uvicorn app.main:app --reload
Documentación interactiva: http://127.0.0.1:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.local_site import mount_frontend
from app.routers import account, attempts, auth, course_state, lessons, pcap, progress
from app.security import get_jwt_secret

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_jwt_secret()  # falla al arrancar si falta JWT_SECRET, no en el primer login
    yield


app = FastAPI(title="Python Learning Dashboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Cabeceras de seguridad solo en la API: la web local (serve_frontend) sirve HTML y Pyodide,
# y una política más estricta la rompería.
API_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        for name, value in API_SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
    return response


for router in (
    lessons.router,
    auth.router,
    account.router,
    progress.router,
    attempts.router,
    pcap.router,
    course_state.router,
):
    app.include_router(router)


@app.get("/api/health", tags=["sistema"])
def health() -> dict[str, str | bool]:
    # "email": el frontend solo ofrece la recuperación por email si hay SMTP configurado
    return {"status": "ok", "email": bool(get_settings().smtp_host)}


if get_settings().serve_frontend:
    mount_frontend(app, get_settings().frontend_dir)
