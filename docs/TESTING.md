# Pruebas: cómo ejecutarlas

> Documento de la **Fase 1**. Recoge las pruebas que **ya existen**. Comandos desde la raíz del
> repositorio salvo que se indique otra carpeta.

## 1. Resumen

| Suite | Comando | Qué cubre | Resultado el 5/10/2026 |
|---|---|---|---|
| Lint y formato (Python) | `cd backend && ruff check . ../e2e ../scripts && ruff format --check . ../e2e ../scripts` | PEP 8 y formato de backend, e2e y scripts | ✅ sin errores |
| Backend | `cd backend && python -m pytest -q --cov=app --cov-fail-under=100` | API, seguridad, RGPD, contenido de `lessons.json`, banco PCAP (cada respuesta se ejecuta) | ✅ 470 tests, 100 % de cobertura |
| Núcleo educativo | `python scripts/learning/build_learning.py --check` | `learning.json` al día y cada salida, corrección y solución comprobadas con `runner.py` | ✅ 22 conceptos, 128 ejercicios |
| Unitarios del frontend | `npm run test:unit` | `tests/unit/*.test.mjs` con `node --test`: dominio, repaso, recomendación, sesiones, simulacros, Markdown seguro | ✅ 54 tests |
| Cursos de DAW | `python scripts/courses/<curso>_course.py --check` (`sql`, `js`, `java`, `entornos`, `programacion`) | Cada respuesta de código se ejecuta (SQLite, Node, Java, Python) | No ejecutado en la auditoría (necesita Java); lo pasa la CI de Android |
| End-to-end + WCAG | `npm ci && npx playwright install chromium && npm run test:e2e` | La web completa con el backend real, la consola Python y axe-core en tema claro y oscuro | No ejecutado en la auditoría; lo pasa la CI |
| Android | `cd android && ./gradlew testDebugUnitTest lintDebug` | Lógica en Kotlin y lint | No ejecutado (sin SDK); lo pasa la CI |
| Migraciones en PostgreSQL | `MIGRATION_TEST_DATABASE_URL=postgresql://… python -m pytest -q tests/test_migrations.py` (en `backend/`) | Migraciones sobre BD vacía y con datos | Lo pasa la CI |
| Dependencias | `pip-audit -r backend/requirements.txt` y `npm audit --audit-level=high` | Vulnerabilidades conocidas | Lo pasa la CI |

## 2. Preparar el entorno (una vez)

```bash
# Python 3.11 o superior (la CI usa 3.12)
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r backend/requirements-dev.txt

# Node 22 (solo para los tests del frontend)
npm ci
npx playwright install chromium        # solo para e2e
```

Los e2e arrancan solos el frontend (`python -m http.server 5500`) y el backend
(`e2e/start_backend.py`, con SQLite temporal); ver `playwright.config.js`.

## 3. Qué ejecutar según lo que cambies

| Si cambias… | Ejecuta como mínimo |
|---|---|
| `frontend/js/learn/*` (lógica) | `npm run test:unit` y, si toca vistas, `npm run test:e2e` |
| Vistas, HTML o CSS | `npm run test:e2e` (incluye la auditoría WCAG) |
| `frontend/data/lessons.json` o `pcap.json` | `cd backend && python -m pytest -q tests/test_content.py tests/test_pcap.py` |
| `scripts/learning/**` | `python scripts/learning/build_learning.py` y después `--check`, más `npm run test:unit` |
| `scripts/courses/**` | `python scripts/courses/<curso>_course.py --check` |
| `frontend/py/runner.py` | Backend completo + `build_learning.py --check` + e2e de consola |
| `backend/**` | Lint, formato y pytest con cobertura del 100 % |
| `frontend/js/learn/*` **y** existe el equivalente en `android/` | Lo anterior + `./gradlew testDebugUnitTest` |
| Dependencias | `pip-audit` y `npm audit` |

## 4. Dónde están las pruebas

```
backend/tests/       pytest (API, seguridad, contenido, PCAP, migraciones)
tests/unit/          node --test (lógica pura del frontend)
e2e/                 Playwright + axe-core (14 especificaciones)
android/app/src/test JUnit en la JVM
scripts/**/--check   comprobación del contenido generado ejecutando cada respuesta
```

## 5. Huecos detectados

- La plantilla de PR (`.github/pull_request_template.md`) y `CONTRIBUTING.md` no piden `npm run test:unit`
  ni `build_learning.py --check`.
- No hay pruebas manuales de accesibilidad documentadas (lector de pantalla, solo teclado, zoom al 200 %).
- No hay pruebas del service worker (modo sin conexión) ni de rendimiento (tamaño de carga inicial).
- No hay prueba que compruebe que la lógica en JavaScript y en Kotlin dan el mismo resultado con los mismos datos.

## 6. Reglas para los agentes

- Una tarea no está terminada hasta que pasan las suites de la sección 3 que le tocan.
- **Prohibido** borrar, saltar (`skip`) o debilitar un test para que pase; si un test parece mal,
  se explica y decide el autor.
- Si no se puede ejecutar una suite (falta Java, SDK o navegador), se dice explícitamente y se confía
  en la CI, nunca se da por buena en silencio.
