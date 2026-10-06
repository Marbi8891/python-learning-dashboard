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
from app.security_events import Event, record
from app.session_cookie import MODE_HEADER

logging.basicConfig(level=logging.INFO)

# Versión del protocolo que manda un cliente A2A (ADR-0034); la web la necesita en CORS
A2A_VERSION_HEADER = "A2A-Version"


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_jwt_secret()  # falla al arrancar si falta JWT_SECRET, no en el primer login
    yield


_docs = get_settings().enable_docs
app = FastAPI(
    title="Python Learning Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
    # En producción no se publica el mapa de la API (ENABLE_DOCS=true para verla en local)
    docs_url="/docs" if _docs else None,
    redoc_url="/redoc" if _docs else None,
    openapi_url="/openapi.json" if _docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", MODE_HEADER, A2A_VERSION_HEADER],
    # La web envía la cookie de sesión HttpOnly a la API, que está en otro dominio (ADR-0033)
    allow_credentials=True,
)

# Cabeceras de seguridad solo en la API: la web local (serve_frontend) sirve HTML y Pyodide,
# y una política más estricta la rompería.
API_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    # El API solo devuelve JSON; no necesita ejecutar recursos ni poder incrustarse.
    "Content-Security-Policy": (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    ),
    # Respuestas con datos personales (sesión, progreso, exportación): nunca en cachés intermedias
    "Cache-Control": "no-store",
}


# Rutas de la API: la REST y las de los agentes A2A (ADR-0034)
API_PATHS = ("/api/", "/a2a/", "/.well-known/agent-card.json")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(API_PATHS):
        for name, value in API_SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
    return response


def _log_too_large(scope) -> None:
    record(Event.BODY_TOO_LARGE, Request(scope))


class BodySizeLimit:
    """Rechaza con 413 los cuerpos mayores que MAX_BODY_BYTES, contando lo que llega realmente
    (también sin Content-Length), antes de que nadie lo lea entero en memoria (ADR-0022)."""

    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None and declared.isdigit() and int(declared) > self.max_bytes:
            _log_too_large(scope)
            await self._too_large(send)
            return
        received = 0
        responded = False

        async def limited_receive():
            nonlocal received, responded
            message = await receive()
            received += len(message.get("body", b""))
            if received > self.max_bytes and not responded:
                # Se responde 413 ya; lo que intente enviar la app después se descarta
                responded = True
                _log_too_large(scope)
                await self._too_large(send)
                raise _BodyTooLarge
            return message

        async def guarded_send(message):
            if not responded:
                await send(message)

        try:
            await self.app(scope, limited_receive, guarded_send)
        except _BodyTooLarge:
            pass

    @staticmethod
    async def _too_large(send) -> None:
        body = b'{"detail":"La peticion es demasiado grande"}'
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", b"%d" % len(body)),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


class _BodyTooLarge(Exception):
    pass


app.add_middleware(BodySizeLimit, max_bytes=get_settings().max_body_bytes)


API_V1_PREFIX = "/api/v1"
LEGACY_API_PREFIX = "/api"

# API pública versionada. Es la superficie que debe consumir el frontend y cualquier cliente nuevo.
for router in (
    lessons.router,
    auth.router,
    account.router,
    progress.router,
    attempts.router,
    pcap.router,
    course_state.router,
):
    app.include_router(router, prefix=API_V1_PREFIX)

# Compatibilidad con clientes existentes (incluida la app Android). Estas rutas no aparecen
# en OpenAPI y quedan marcadas como deprecated para no convertir la migración en un corte brusco.
for router in (
    lessons.router,
    auth.router,
    account.router,
    progress.router,
    attempts.router,
    pcap.router,
    course_state.router,
):
    app.include_router(
        router,
        prefix=LEGACY_API_PREFIX,
        deprecated=True,
        include_in_schema=False,
    )


@app.get("/api/v1/health", tags=["sistema"])
@app.get("/api/health", tags=["sistema"], include_in_schema=False)
def health() -> dict[str, str | bool]:
    # "email": el frontend solo ofrece la recuperación por email si hay SMTP configurado
    return {"status": "ok", "email": bool(get_settings().smtp_host)}


# Agentes A2A: una capacidad más junto a la API REST, no un sustituto (ADR-0034).
# El SDK solo se importa si se activa: sin A2A, la API no gasta memoria en él.
if get_settings().a2a_enabled:
    from app.a2a.server import mount_a2a

    mount_a2a(app, get_settings())

if get_settings().serve_frontend:
    mount_frontend(app, get_settings().frontend_dir)
