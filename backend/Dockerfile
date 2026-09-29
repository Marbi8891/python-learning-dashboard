# Imagen del backend. Se construye desde la RAÍZ del repositorio,
# porque necesita el contenido compartido de frontend/data:
#   docker build -f backend/Dockerfile -t pld-api .
#   docker run -p 8000:8000 --env-file backend/.env pld-api
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY frontend/data/lessons.json /app/frontend/data/lessons.json

# Usuario sin privilegios y sin permiso de escritura sobre el código (la base de datos es externa)
RUN useradd --create-home --uid 1000 app
USER app

EXPOSE 8000

# Detrás del proxy de Render: la IP real del cliente es la última de X-Forwarded-For (ADR-0022).
# No se usa --proxy-headers con --forwarded-allow-ips='*': uvicorn tomaría la PRIMERA IP de la
# cabecera, que la escribe el propio cliente, y el límite de intentos se podría saltar.
ENV TRUSTED_PROXY_HOPS=1

# Migra, sincroniza lecciones (idempotente) y arranca.
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
