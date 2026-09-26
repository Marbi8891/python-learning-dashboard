# Imagen del backend. Se construye desde la RAÍZ del repositorio,
# porque necesita el contenido compartido de frontend/data:
#   docker build -f backend/Dockerfile -t pld-api .
#   docker run -p 8000:8000 --env-file backend/.env pld-api
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY frontend/data/lessons.json /app/frontend/data/lessons.json

RUN useradd --create-home --uid 1000 app && chown -R app /app/backend
USER app

EXPOSE 8000

# Migra, sincroniza lecciones (idempotente) y arranca.
# --proxy-headers: detrás de un proxy (Render, Nginx) la IP real llega en X-Forwarded-For,
# necesaria para que el límite de intentos de login funcione por usuario.
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
