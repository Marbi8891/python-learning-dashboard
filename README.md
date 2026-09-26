# Python Learning Dashboard

[![CI](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml)
[![Deploy frontend](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml)
![Cobertura backend](https://img.shields.io/badge/cobertura%20backend-100%25-brightgreen)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Dashboard interactivo para aprender Python de principiante a avanzado: 15 lecciones con teoría propia y fuentes enlazadas, **consola de Python en el navegador**, **ejercicios corregidos automáticamente**, asistente por lección y cuenta opcional para sincronizar el progreso.

**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Funcionalidades

- **Ruta de aprendizaje:** 4 módulos y 15 lecciones, con progreso por módulo y un orden recomendado.
- **Teoría y ejemplos:** explicaciones propias, código con resaltado de sintaxis y botones «Copiar», «Probar en la consola» y «Abrir en PyCharm» (copia el código, guía los pasos y permite descargar el `.py`).
- **Consola interactiva:** Python 3.14 real ([Pyodide](https://pyodide.org)) en un Web Worker. Admite `input()`, muestra los errores con la línea exacta y corta los bucles infinitos a los 10 s.
- **Ejercicios corregidos:** cada lección tiene plantilla y tests. Superarlos completa la lección.
- **Asistente:** preguntas frecuentes, pista del ejercicio y «Siguiente tema», adaptados a cada lección.
- **Mini-quiz:** 3 preguntas por lección (45 en total) que explican por qué cada respuesta es correcta o no.
- **Retos extra:** uno por lección, de ★ a ★★★ (FizzBuzz, carrito de la compra, renombrador de fotos…), con tests automáticos.
- **XP, niveles y racha:** 7 niveles de «Novato/a» a «Leyenda de Python», bonus por acertar a la primera, 13 logros con su vitrina y confeti (desactivado si el sistema pide reducir el movimiento).
- **Cuenta (opcional):** registro, login, progreso sincronizado entre dispositivos, recuperación de contraseña y RGPD (descargar los datos y borrar la cuenta).
- **Estética de academia:** diseño editorial (tinta, marfil y dorado, titulares en serif), portada con la ficha del curso y temario, y página «Mi aprendizaje» con cifras, actividad, logros e historial.
- **Pensado para el alumno:** portada con «Continuar donde lo dejaste», guía Aprende → Practica → Comprueba en cada lección, consola al lado en pantallas anchas y errores de Python explicados en español.
- **Tema y letra:** claro, oscuro o automático, y tres tamaños de letra.
- **Accesible y adaptable:** WCAG 2.1 AA verificado automáticamente en los dos temas, navegable con teclado y con menú móvil.

## Usarlo en tu PC (Windows)

Doble clic en **`Iniciar-Dashboard.bat`**. La primera vez instala lo necesario y después abre la app en el navegador, solo accesible desde tu ordenador. Requiere Python 3.11 o superior. Guía y solución de problemas: [docs/EJECUTAR-EN-WINDOWS.md](docs/EJECUTAR-EN-WINDOWS.md).

En Linux o macOS: `pip install -r backend/requirements.txt && python scripts/run_local.py`.

## Arquitectura

| Parte | Tecnología | Despliegue |
|---|---|---|
| `frontend/` | HTML, CSS y JavaScript (módulos ES, sin framework), Pyodide | GitHub Pages |
| `backend/` | FastAPI, SQLAlchemy 2, Alembic, PostgreSQL/SQLite, JWT + Argon2 | Docker: Render, Oracle Cloud… |

Decisiones documentadas:
- [ADR-0001 Arquitectura](docs/adr/0001-arquitectura.md)
- [ADR-0002 Contenido](docs/adr/0002-contenido-de-lecciones.md)
- [ADR-0003 Autenticación y ejercicios](docs/adr/0003-autenticacion-y-ejercicios.md)
- [ADR-0004 Consola, corrección y privacidad](docs/adr/0004-consola-ejercicios-y-privacidad.md)
- [ADR-0005 Gamificación](docs/adr/0005-gamificacion.md)
- [ADR-0006 Experiencia del alumno](docs/adr/0006-experiencia-del-alumno.md)
- [ADR-0007 Estética editorial](docs/adr/0007-estetica-editorial.md)
- [ADR-0008 Backend en Render y base de datos en Neon](docs/adr/0008-backend-render-neon.md)

```
├── frontend/
│   ├── data/lessons.json   Contenido: teoría, ejemplos, ejercicios, quiz, retos y asistente (fuente única)
│   ├── py/runner.py        Motor que ejecuta y corrige el código (navegador y CI)
│   ├── js/                 app, consola, Worker de Pyodide, quiz, juego, asistente, cuenta, API
│   ├── css/  fonts/  vendor/
│   ├── config.js           URL de la API (vacía = modo sin cuenta)
│   └── privacidad.html
├── backend/
│   ├── app/                API: config, seguridad, modelos, routers, email
│   ├── migrations/         Alembic
│   ├── tests/              pytest (100 % de cobertura)
│   └── Dockerfile
├── e2e/                    Playwright: app completa + auditoría WCAG
├── docs/                   ADR y guía de despliegue
├── render.yaml             Blueprint de Render (backend + PostgreSQL)
├── docker-compose.yml      Todo en local con PostgreSQL
├── deploy.ps1              Publicación en GitHub Pages (Windows)
├── scripts/run_local.py    Versión de escritorio: web + API en 127.0.0.1
└── Iniciar-Dashboard.bat   Lanzador para Windows (doble clic)
```

## Desarrollo local

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
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
python -m http.server 5500        # http://localhost:5500 (usa la API local automáticamente)
```

### Todo con Docker

```bash
JWT_SECRET=<valor> docker compose up --build
```

## Tests

| Suite | Comando | Qué cubre |
|---|---|---|
| Backend | `cd backend && python -m pytest --cov=app` | API, seguridad, RGPD, migraciones y contenido (100 % de cobertura) |
| End-to-end | `npm ci && npx playwright install chromium && npm run test:e2e` | La app completa con el backend real, la consola Python y la auditoría WCAG |
| Calidad | `cd backend && ruff check . ../e2e && ruff format --check . ../e2e` | Estilo PEP 8 y formato |

La CI ejecuta todo en cada push, incluidas las migraciones contra PostgreSQL 16.

## API

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/health` | | Estado del servicio |
| GET | `/api/modules` | | Módulos con sus lecciones |
| GET | `/api/lessons/{slug}` | | Lección completa (teoría, ejemplo, ejercicio, tests y asistente) |
| POST | `/api/auth/register` | | Crear cuenta (requiere `accept_privacy: true`) |
| POST | `/api/auth/login` | | Formulario OAuth2 (`username` = email) → token |
| POST | `/api/auth/password-reset/request` | | Enviar enlace de recuperación |
| POST | `/api/auth/password-reset/confirm` | | Nueva contraseña (cierra todas las sesiones) |
| GET | `/api/users/me` | ✔ | Usuario actual |
| GET | `/api/users/me/export` | ✔ | Todos mis datos en JSON (RGPD) |
| POST | `/api/users/me/delete` | ✔ | Borrar la cuenta y sus datos (pide la contraseña) |
| GET | `/api/progress` | ✔ | Lecciones completadas |
| PUT / DELETE | `/api/progress/{slug}` | ✔ | Marcar o desmarcar |
| POST | `/api/progress/import` | ✔ | Fusionar el progreso del navegador |
| POST / GET | `/api/lessons/{slug}/attempts` | ✔ | Registrar un intento o ver los últimos 20 |

## Publicar

Guía completa en **[docs/DEPLOY.md](docs/DEPLOY.md)**: GitHub Pages, backend en Render, conexión entre ambos, SMTP y la lista de comprobación del RGPD.

## Contribuir y licencia

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) y [SECURITY.md](SECURITY.md). Licencia [MIT](LICENSE). Las fuentes tipográficas (Inter, JetBrains Mono y Fraunces, OFL) y highlight.js incluyen sus propias licencias en `frontend/fonts/` y `frontend/vendor/`.
