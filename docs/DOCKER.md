# Entorno local con Docker

Este entorno permite ejecutar localmente el frontend, la API FastAPI y PostgreSQL sin cambiar el despliegue existente en GitHub Pages y Render.

## Requisitos

- Docker Desktop actualizado (Windows/macOS) o Docker Engine con Docker Compose v2.
- Puertos locales 5500 y 8000 disponibles.

## Preparación (Windows PowerShell)

Desde la raíz del repositorio:

```powershell
Copy-Item .env.docker.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Edita `.env` y sustituye `POSTGRES_PASSWORD` y `JWT_SECRET` por valores aleatorios propios. El secreto JWT debe tener al menos 32 caracteres. No compartas ni subas `.env`.

## Iniciar

```powershell
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs -f api
```

Abre:

- Frontend: http://localhost:5500
- Salud de la API: http://localhost:8000/api/health
- Documentación de la API (solo entorno local): http://localhost:8000/docs

El frontend usa la configuración local de `frontend/config.js` y llama a la API en localhost. Los servicios solo publican puertos en la interfaz loopback del ordenador. PostgreSQL no se publica al host y queda aislado en la red interna de backend.

## Detener y recuperar

```powershell
docker compose down
```

El volumen `db-data` conserva PostgreSQL al detener y recrear contenedores. No ejecutes `docker compose down -v` salvo que quieras borrar deliberadamente todos los datos de la base local.

Para ver errores:

```powershell
docker compose logs --tail=200 api db web
```

## Validación básica

```powershell
Invoke-RestMethod http://localhost:8000/api/health
Invoke-WebRequest -UseBasicParsing http://localhost:5500/
```

Para validar que la base de datos mantiene los datos tras reiniciar:

1. Crea una cuenta de prueba o genera datos locales no sensibles.
2. Ejecuta `docker compose restart db api`.
3. Vuelve a comprobar el acceso y que los datos siguen disponibles.

## Arquitectura y límites

- `api` se construye desde `backend/Dockerfile`, usando la raíz del repositorio como contexto porque el backend copia los contenidos compartidos de `frontend/data/`.
- `web` sirve los archivos del frontend en modo solo lectura.
- `db` utiliza PostgreSQL 16 y el volumen nombrado `db-data`.
- Las migraciones Alembic y la carga idempotente de lecciones se ejecutan al iniciar el contenedor API, como establece el Dockerfile existente.
- La base de datos aquí es local para desarrollo; no la uses como reemplazo automático de Neon en producción.
- Esta configuración no despliega nada en Internet y no modifica Render ni GitHub Pages.
