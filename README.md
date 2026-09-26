# Python Learning Dashboard

[![CI](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/ci.yml)
[![Deploy frontend](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml/badge.svg)](https://github.com/Marbi8891/python-learning-dashboard/actions/workflows/pages.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Dashboard interactivo para aprender Python, de principiante a avanzado: ruta de aprendizaje con progreso, teoría con ejemplos, ejercicios y consola para ejecutar código.

**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Arquitectura

| Parte | Tecnología | Despliegue |
|---|---|---|
| `frontend/` | HTML, CSS y JavaScript (sin framework) | GitHub Pages (GitHub Actions) |
| `backend/` | FastAPI, SQLAlchemy 2, SQLite/PostgreSQL | Pendiente (ver ADR) |

Las decisiones de arquitectura y el plan por fases están en [docs/adr/0001-arquitectura.md](docs/adr/0001-arquitectura.md).

```
├── frontend/              Interfaz (se publica en Pages)
├── backend/
│   ├── app/               API: config, modelos, esquemas, routers
│   ├── data/lessons.json  Contenido de las lecciones
│   └── tests/
├── docs/adr/              Registro de decisiones de arquitectura
├── .github/               CI, despliegue, Dependabot y plantillas
└── deploy.ps1             Publicación en un comando (Windows)
```

## Desarrollo local

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # Linux/Mac: cp .env.example .env
python -m app.seed                # carga las lecciones
uvicorn app.main:app --reload
```

- Documentación interactiva: http://127.0.0.1:8000/docs
- Calidad: `ruff check . && ruff format --check . && python -m pytest -q`

### Frontend

```bash
cd frontend
python -m http.server 5500        # http://localhost:5500 (permitido en CORS)
```

## API (v0.1)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/health` | Estado del servicio |
| GET | `/api/modules` | Módulos con sus lecciones (resumen) |
| GET | `/api/lessons/{slug}` | Detalle de una lección |

## Publicar

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy.ps1 -Message "feat: ..."
```

El script crea el repositorio si no existe, activa GitHub Pages y sube el código. Después, GitHub Actions publica `frontend/` y la CI comprueba el backend.

## Roadmap

- [x] Barra lateral y API de lecciones
- [ ] Panel de contenido con pestañas y resaltado de sintaxis
- [ ] Consola interactiva con Pyodide
- [ ] Usuarios y login
- [ ] Progreso por usuario
- [ ] Corrección de ejercicios

## Contribuir y licencia

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) y [SECURITY.md](SECURITY.md). Licencia [MIT](LICENSE).
