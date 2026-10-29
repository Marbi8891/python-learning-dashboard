# Pruebas

Los comandos se ejecutan desde la raíz del repositorio, salvo que se indique otra carpeta.

## Preparar el entorno

```bash
# Python 3.11 o superior (la CI usa 3.12)
python -m venv .venv
.venv\Scripts\activate                 # Linux/Mac: source .venv/bin/activate
pip install -r backend/requirements-dev.txt

# Node 22 (solo para las pruebas del frontend)
npm ci
npx playwright install chromium        # solo para las e2e
```

Las e2e arrancan solas el frontend (`e2e/serve_frontend.py`, un `http.server` con HTTP/1.1) y el backend (`e2e/start_backend.py`, con una SQLite temporal). Está en `playwright.config.js`.

## Qué hay

| Tipo | Comando | Qué prueba |
|---|---|---|
| Lint y formato | `cd backend && ruff check . ../e2e ../scripts && ruff format --check . ../e2e ../scripts` | Estilo PEP 8 |
| Backend | `cd backend && python -m pytest -q --cov=app --cov-fail-under=100` | API, autenticación, RGPD, contenido y banco del PCAP |
| Núcleo por conceptos | `python scripts/learning/build_learning.py --check` | `learning.json` al día y cada respuesta comprobada |
| Currículo de DAW | `python scripts/curriculum/build_curriculum.py --check` | Catálogo al día; las pruebas están en `test_curriculum.py` |
| Cursos de DAW | `python scripts/courses/<curso>_course.py --check` (`sql`, `js`, `java`, `entornos`, `programacion`) | Cada respuesta de código se ejecuta (SQLite, Node, Java y Python) |
| Frontend | `npm run test:unit` | Lógica del aprendizaje, repaso, recomendación, panel y Markdown seguro |
| End-to-end y WCAG | `npm run test:e2e` | La web entera con el backend real y auditoría de accesibilidad |
| Migraciones en PostgreSQL | `MIGRATION_TEST_DATABASE_URL=postgresql://… python -m pytest -q tests/test_migrations.py` (en `backend/`) | Migraciones sobre una BD vacía y con datos |
| Dependencias | `pip-audit -r backend/requirements.txt` y `npm audit --audit-level=high` | Vulnerabilidades conocidas |

GitHub Actions (`ci.yml`) lo pasa todo en cada push y pull request.

En un portátil, las e2e en paralelo pueden agotar el tiempo de espera, porque cada navegador descarga Pyodide (unos 10 MB) a la vez. Si pasa, ejecútalas en serie: `npx playwright test --workers=1`.

## Qué ejecutar según lo que cambies

| Si cambias… | Ejecuta |
|---|---|
| `frontend/js/learn/*` | `npm run test:unit` y, si cambian vistas, `npm run test:e2e` |
| HTML o CSS | `npm run test:e2e` |
| `frontend/data/lessons.json` o `pcap.json` | `cd backend && python -m pytest -q tests/test_content.py tests/test_pcap.py` |
| `scripts/learning/**` | `python scripts/learning/build_learning.py` y después `--check` |
| `scripts/courses/**` | `python scripts/courses/<curso>_course.py --check` |
| `backend/**` | Lint, formato y pytest con cobertura |
| `scripts/curriculum/**` | `python scripts/curriculum/build_curriculum.py --check` y `cd backend && python -m pytest -q tests/test_curriculum.py` |
| `docs/memoria/img/*.dot` | `dot -Tpng <archivo>.dot -o <archivo>.png` (Graphviz) para regenerar el diagrama |

## Lo que falta

- Pruebas manuales de accesibilidad (lector de pantalla, solo teclado, zoom al 200 %).
- Pruebas en un móvil real y medición de rendimiento con Lighthouse (memoria, 6.3 y 6.5).
- El modo sin conexión tiene una prueba automática (`e2e/study.spec.js`, «PWA») que recarga «¿Qué estudio ahora?» sin red, pero no cubre abrir una lección que no se había visitado antes.
