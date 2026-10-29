# Python Learning Dashboard

[![CI](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Proyecto de 2º de DAW: una web para **aprender Python entendiendo lo que haces** y preparar el examen **PCAP** y los módulos de programación del ciclo.

**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Qué tiene

- **Teoría y ejercicios por conceptos:** 22 conceptos con explicación, ejemplo línea a línea y 131 ejercicios. Cuando fallas, te explica el error típico y te pone otro ejercicio parecido.
- **Consola de Python en el navegador** con [Pyodide](https://pyodide.org). No hay que instalar nada. Admite `input()` y corta los bucles infinitos a los 10 segundos.
- **Curso del PCAP:** 27 lecciones, mini-quiz en cada una, retos y un simulacro de 40 preguntas en 65 minutos con el reparto oficial del examen. 126 preguntas en español o inglés.
- **Cursos de DAW:** Programación, Bases de datos, Entornos de desarrollo, JavaScript y Java.
- **Currículo oficial de DAW en Castilla y León** (`#/daw/curriculo`): los 17 módulos de la Orden EDU/1311/2024 y los resultados de aprendizaje y criterios de evaluación literales del Real Decreto 405/2023. Se genera con `scripts/curriculum/` (ver [docs/PLAN-CURRICULO-DAW.md](docs/PLAN-CURRICULO-DAW.md)). En «Mi panel › Mi progreso» se ve cuántas preguntas de cada módulo has practicado y cuántas dominas.
- **Repaso espaciado** y plan de estudio según la fecha del examen.
- **XP, niveles, racha y logros.**
- **Cuenta opcional:** registro con email o con Google, recuperación de contraseña y panel del alumno. Puedes descargar tus datos o borrar la cuenta (RGPD).
- **PWA:** se puede instalar y funciona sin conexión después de la primera visita.
- **Tema claro y oscuro** y accesibilidad WCAG 2.1 AA.

Todo el temario se genera con los scripts de `scripts/`, que ejecutan el código de cada pregunta para comprobar que la respuesta es correcta.

## Tecnologías

| Parte | Tecnología |
|---|---|
| Frontend | HTML, CSS y JavaScript (módulos ES, sin framework), Pyodide, highlight.js |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, PyJWT, Argon2 |
| Base de datos | PostgreSQL (Neon) en producción y SQLite en local |
| Pruebas | pytest, Ruff, node --test, Playwright, axe-core |
| Despliegue | GitHub Pages (web), Render con Docker (API), GitHub Actions |

## Estructura

```
frontend/   la web (HTML, CSS, JS) y el temario en frontend/data/
backend/    la API en FastAPI, migraciones y pruebas
scripts/    generan y comprueban el temario; run_local.py arranca todo en local
e2e/        pruebas end-to-end con Playwright
tests/unit/ pruebas unitarias del JavaScript
docs/       memoria, despliegue, API y pruebas
```

## Cómo funciona

```
Navegador ──► GitHub Pages (HTML, CSS, JS y el temario en JSON)
   │
   ├─► Web Worker con Pyodide ──► jsDelivr (solo la primera vez, para descargar Python)
   │
   └─► API FastAPI en Render (/api/v1) ──► PostgreSQL en Neon
        (solo si el alumno inicia sesión)
```

- **Sin cuenta** todo funciona en el navegador y el progreso se guarda en `localStorage`.
- **Con cuenta** el frontend llama a la API con `fetch` (`frontend/js/api.js`). La sesión va en una cookie `HttpOnly` y las peticiones llevan la cabecera `X-PLD-Session` para evitar CSRF.
- La URL del backend sale de `frontend/config.js`: en `localhost` usa `http://127.0.0.1:8000` y en GitHub Pages la API de Render. GitHub Pages solo sirve archivos estáticos; FastAPI se despliega aparte.

### Python en el navegador (Pyodide y Web Workers)

`frontend/js/python-runner.js` crea un Web Worker (`pyodide-worker.js`) que carga Pyodide, es decir, Python compilado a WebAssembly. Al worker se le manda el código con `postMessage` y él devuelve la salida o el error.

- La página no se bloquea mientras se ejecuta el código del alumno, porque corre en otro hilo.
- Si un programa tarda más de 10 segundos, se termina el worker (`terminate()`) y se crea otro nuevo.
- Después de cargar Python, el worker desactiva `fetch`, `XMLHttpRequest`, `WebSocket` y similares, así el código del alumno no puede enviar datos a otros servidores.
- La corrección usa `frontend/py/runner.py`, el mismo archivo que usan las pruebas del backend para comprobar los ejemplos.

Un Web Worker no es un aislamiento de seguridad completo: el código se ejecuta en el mismo origen que la web. Para este proyecto basta, porque cada alumno solo ejecuta su propio código en su navegador.

## Variables de entorno del backend

Se copian de `backend/.env.example` a `backend/.env` (que no se sube al repositorio).

| Variable | Para qué | Obligatoria |
|---|---|---|
| `JWT_SECRET` | Firmar las sesiones (32 caracteres o más) | Sí |
| `DATABASE_URL` | Base de datos (por defecto SQLite `dev.db`) | No |
| `CORS_ORIGINS` | Orígenes del frontend que pueden llamar a la API | No |
| `FRONTEND_URL` | Para construir el enlace de recuperación de contraseña | No |
| `GOOGLE_CLIENT_ID` | Activar «Continuar con Google» | No |
| `BREVO_API_KEY` o `SMTP_*` | Enviar los emails de recuperación | No |
| `ENABLE_DOCS` | Ver la documentación de la API en `/docs` | No |

## Usarlo en tu PC (Windows)

Doble clic en **`Iniciar-Dashboard.bat`**. La primera vez instala lo necesario y luego abre la web en el navegador. Hace falta Python 3.11 o superior. Más detalles en [docs/EJECUTAR-EN-WINDOWS.md](docs/EJECUTAR-EN-WINDOWS.md).

En Linux o macOS: `pip install -r backend/requirements.txt && python scripts/run_local.py`.

## Desarrollo

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # Linux/Mac: cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # pégalo en JWT_SECRET del .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload     # http://127.0.0.1:8000
```

La documentación de la API (`/docs`) solo se ve con `ENABLE_DOCS=true`.

### Frontend

```bash
cd frontend
python -m http.server 5500        # http://localhost:5500
```

### Con Docker

Consulta la [guía de Docker](docs/DOCKER.md). Incluye la preparación de variables de entorno, el inicio de servicios, verificaciones y cómo detener el entorno sin borrar datos.

En Windows PowerShell, desde la raíz del proyecto:

```powershell
Copy-Item .env.docker.example .env
# Edita .env y define una contraseña PostgreSQL única y JWT_SECRET.
docker compose config
docker compose up --build -d
docker compose ps
```

Frontend: http://localhost:5500 · Salud de la API: http://localhost:8000/api/health · Docs locales: http://localhost:8000/docs

No subas el archivo `.env` con secretos. Para conservar los datos, usa `docker compose down`; evita `docker compose down -v`, que elimina el volumen de la base de datos.

## Pruebas

```bash
cd backend && python -m pytest --cov=app        # backend
npm ci && npm run test:unit                     # lógica del frontend
npx playwright install chromium && npm run test:e2e   # web completa
```

Todas las pruebas y qué ejecutar según lo que cambies: [docs/TESTING.md](docs/TESTING.md).

## Limitaciones conocidas

- El backend está en el plan gratuito de Render: si nadie lo usa durante un rato se apaga, y la primera petición tarda.
- Los límites de intentos de login se guardan en memoria: funcionan con un solo servidor.
- El progreso y la XP los calcula el navegador; el servidor los guarda, pero no comprueba que sean ciertos.
- En la consola no hay red (por seguridad), así que los ejemplos con `requests`, Flask o pytest se ejecutan en el ordenador (PyCharm), no en el navegador.
- Falta revisar la accesibilidad a mano con un lector de pantalla; ahora solo se comprueba con axe-core.

## Documentación

- [Memoria del proyecto](docs/memoria/memoria.md)
- [Guion de la defensa](docs/DEMO-Y-DEFENSA.md)
- [API](docs/API.md)
- [Recuperación de contraseña y login con Google](docs/auth.md)
- [Despliegue](docs/DEPLOY.md)
- [Docker local](docs/DOCKER.md)
- [Pruebas](docs/TESTING.md)
- [Ejecutar en Windows](docs/EJECUTAR-EN-WINDOWS.md)
- [Plan del currículo oficial de DAW](docs/PLAN-CURRICULO-DAW.md)
- [Auditoría y licencias de fuentes](docs/AUDITORIA-Y-LICENCIAS.md)
- [Seguridad](SECURITY.md)

## Licencia

MIT. Autor: Mrabeh Fathi Boussayff.
