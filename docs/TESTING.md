# Pruebas: cómo ejecutarlas

> Escrito en la Fase 1 y **actualizado el 21/10/2026** con la auditoría integral ([`AUDIT.md`](AUDIT.md)).
> Comandos desde la raíz del repositorio salvo que se indique otra carpeta.

## 0. Estrategia

| Nivel | Herramienta | Qué se prueba ahí |
|---|---|---|
| Unitario (Python) | pytest | API, seguridad, contenido, motor `runner.py`, scripts (`check_site.py`, `production_csp.py`) |
| Unitario (JavaScript) | `node --test`, sin dependencias | Solo **lógica pura** sin DOM: dominio, repaso, plan, simulacros, Markdown seguro, logros, copia del progreso, buscador, `PythonRunner` con un Worker falso |
| Contenido | `build_learning.py --check`, `<curso>_course.py --check` | Cada respuesta de cada ejercicio se **ejecuta** |
| Integración + end-to-end | Playwright con el backend real (SQLite temporal) | Flujos completos en Chromium: consola, ejercicios, progreso, cuentas, importación, navegación, móvil |
| Accesibilidad | axe-core dentro de Playwright | WCAG 2.1 AA automático en tema claro y oscuro; lo manual va en §5 |
| Sitio publicado | `scripts/check_site.py` | Rutas relativas, archivos e imports existentes, sintaxis JS, JSON válidos (CI y antes de publicar) |
| Seguridad | Bandit, Semgrep, Gitleaks, pip-audit, npm audit | Ver [`security/SECURITY_TESTING.md`](security/SECURITY_TESTING.md) |

Regla: una regla de negocio nueva va en un módulo puro con test unitario; la vista se cubre con un e2e.

## 1. Resumen

| Suite | Comando | Qué cubre | Resultado el 21/10/2026 |
|---|---|---|---|
| Lint y formato (Python) | `cd backend && ruff check . ../e2e ../scripts && ruff format --check . ../e2e ../scripts` | PEP 8 y formato de backend, e2e y scripts | ✅ sin errores |
| Backend | `cd backend && python -m pytest -q --cov=app --cov-fail-under=100` | API, seguridad, RGPD, contenido de `lessons.json`, banco PCAP (cada respuesta se ejecuta), `check_site.py` | ✅ 791 passed, 1 skipped, 100 % de cobertura |
| Núcleo educativo | `python scripts/learning/build_learning.py --check` | `learning.json` al día y cada salida, corrección y solución comprobadas con `runner.py` | ✅ 22 conceptos, 131 ejercicios |
| Unitarios del frontend | `npm run test:unit` | `tests/unit/*.test.mjs` con `node --test`: dominio, repaso, recomendación, sesiones, simulacros, Markdown seguro, logros, copia del progreso, buscador, `PythonRunner` | ✅ 94 tests |
| Sitio estático | `python scripts/check_site.py` | Lo que se publica en Pages: rutas relativas, archivos e imports, sintaxis JS (`node --check`), JSON | ✅ correcto |
| Cursos de DAW | `python scripts/courses/<curso>_course.py --check` (`sql`, `js`, `java`, `entornos`, `programacion`) | Cada respuesta de código se ejecuta (SQLite, Node, Java, Python) | No ejecutado en la auditoría (necesita Java); lo pasa la CI de Android |
| End-to-end + WCAG | `npm ci && npx playwright install chromium && npm run test:e2e` | La web completa con el backend real, la consola Python y axe-core en tema claro y oscuro (20 especificaciones) | ✅ 153 passed (con Pyodide servido en local, ver §2) |
| Android | `cd android && ./gradlew testDebugUnitTest lintDebug` | Lógica en Kotlin y lint | No ejecutado (sin SDK); lo pasa la CI |
| Migraciones en PostgreSQL | `MIGRATION_TEST_DATABASE_URL=postgresql://… python -m pytest -q tests/test_migrations.py` (en `backend/`) | Migraciones sobre BD vacía y con datos | Lo pasa la CI |
| Dependencias | `pip-audit -r backend/requirements.txt` y `npm audit --audit-level=high` | Vulnerabilidades conocidas | ✅ sin vulnerabilidades conocidas |
| Seguridad (Bandit, Semgrep, Gitleaks…) | `python scripts/security/run_checks.py` | Análisis estático, reglas propias y secretos; ver [`security/SECURITY_TESTING.md`](security/SECURITY_TESTING.md) | Lo pasa la CI (`security.yml`) |

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

**Sin acceso a jsDelivr** (redes que lo bloquean): los e2e de la consola necesitan Pyodide. Se puede
servir en local sin commitearlo:

```bash
npm pack pyodide@314.0.7 && tar xzf pyodide-314.0.7.tgz && mv package frontend/pyodide-local
PYODIDE_URL=http://localhost:5500/pyodide-local/ npm run test:e2e
```

## 3. Qué ejecutar según lo que cambies

| Si cambias… | Ejecuta como mínimo |
|---|---|
| `frontend/js/learn/*` (lógica) | `npm run test:unit` y, si toca vistas, `npm run test:e2e` |
| Vistas, HTML o CSS | `python scripts/check_site.py` y `npm run test:e2e` (incluye la auditoría WCAG) |
| `frontend/js/**` (cualquier módulo) | `python scripts/check_site.py` y `npm run test:unit` |
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
e2e/                 Playwright + axe-core (20 especificaciones)
scripts/check_site.py  prueba de humo del sitio estático (CI y pages.yml)
android/app/src/test JUnit en la JVM
scripts/**/--check   comprobación del contenido generado ejecutando cada respuesta
```

## 5. Huecos detectados

- ~~La plantilla de PR no pide `npm run test:unit` ni `build_learning.py --check`~~ Corregido el 21/10.
- No hay pruebas manuales de accesibilidad documentadas. Lista pendiente de pasar (ROADMAP R4):
  - [ ] Solo teclado: todas las rutas del menú, la consola (Tab sale del editor tras Escape), el simulacro y los diálogos.
  - [ ] Lector de pantalla (NVDA + Firefox o VoiceOver + Safari): lección, consola, resultado de un ejercicio, buscador de lecciones, importación.
  - [ ] Zoom del navegador al 200 % y 400 % (reflujo, 1.4.10) en escritorio y móvil.
  - [ ] Tamaño de letra grande del sistema y «Letra grande» de la app.
  - [ ] WCAG 2.2: foco no oculto (2.4.11) con el menú móvil abierto y tamaño de objetivo mínimo (2.5.8) en los chips y botones pequeños.
- No hay pruebas del service worker (modo sin conexión) ni de rendimiento (tamaño de carga inicial).
- No hay prueba que compruebe que la lógica en JavaScript y en Kotlin dan el mismo resultado con los mismos datos.

## 6. Reglas para los agentes

- Una tarea no está terminada hasta que pasan las suites de la sección 3 que le tocan.
- **Prohibido** borrar, saltar (`skip`) o debilitar un test para que pase; si un test parece mal,
  se explica y decide el autor.
- Si no se puede ejecutar una suite (falta Java, SDK o navegador), se dice explícitamente y se confía
  en la CI, nunca se da por buena en silencio.
