# Línea base de seguridad

Estado de partida comprobado al crear el equipo AppSec, contra el que se miden las revisiones
incrementales. Si cambia algo de esta página (stack, controles, herramientas), security-lead la actualiza.

- **Commit revisado**: `708431f` (`main`, «feat: panel integral del alumno», 19/10/2026)
- **Entorno**: contenedor Linux, Python 3.13, Node 22, Claude Code 2.1.303. La CI usa Python 3.12.

## 1. Stack real

| Capa | Tecnología | Dónde |
|---|---|---|
| Web | HTML + CSS + módulos ES sin framework ni build, PWA (`sw.js`) | `frontend/`, publicada en GitHub Pages por `.github/workflows/pages.yml` en cada push a `main` |
| Python del alumno | Pyodide 314.0.7 desde jsDelivr en un Web Worker | `frontend/js/pyodide-worker.js` |
| API | FastAPI + Pydantic 2 + SQLAlchemy 2 + Alembic, Docker en Render | `backend/app/`, `backend/migrations/`, `render.yaml` |
| Base de datos | PostgreSQL (Neon) en producción, SQLite en tests y en local | `backend/app/database.py` |
| Identidad | Email + contraseña (Argon2id) y Google Sign-In (`google-auth`) | `backend/app/routers/auth.py` |
| Sesión | JWT HS256 de 30 min; cookie `__Host-pld_session` con `X-PLD-Session` (web) o Bearer (Android) | `backend/app/security.py`, `session_cookie.py` |
| Tutor IA | A2A 1.0 (`a2a-sdk`), Ollama local por defecto, simulado en tests | `backend/app/a2a/` |
| Android | Kotlin + Compose, misma API (`/api` sin versión) | `android/` |

## 2. Controles existentes (comprobados en el código)

- Autorización: todas las rutas con datos personales dependen de `CurrentUser`
  (`backend/app/deps.py:22`) y filtran por `user.id`. Ninguna acepta un id de usuario.
  **Comprobado** con `backend/tests/test_security_isolation.py` (nuevo) y `test_dashboard.py`.
- Invalidación: `token_version` comparado en cada petición (`deps.py:40`).
- CSRF: la cookie solo cuenta con la cabecera `X-PLD-Session` (`session_cookie.py:31`).
- CORS: lista explícita `cors_origins` (`backend/app/config.py:20`) con credenciales.
- Cabeceras en `/api/`, `/a2a/` y la Agent Card (`backend/app/main.py`, `API_SECURITY_HEADERS`).
- Límite de cuerpo 300 KB contando bytes reales (`BodySizeLimit`, `main.py`).
- Límites de intentos por IP y por cuenta, en memoria (`backend/app/rate_limit.py`).
- Eventos `pld.security` con MITRE ATT&CK y seudónimos HMAC (`backend/app/security_events.py`).
- CSP en `<meta>` (`frontend/index.html:8`), sin scripts en línea ni `unsafe-eval`.
- Detalle y riesgos aceptados: [`/SECURITY.md`](../../SECURITY.md), [`revision-2026-10.md`](revision-2026-10.md),
  [`mitre-attack.md`](mitre-attack.md), [`../auth.md`](../auth.md).

## 3. Resultado de las comprobaciones (ejecutadas el 19/10/2026)

| Comprobación | Resultado real |
|---|---|
| `pytest` backend con cobertura | 638 pasan, 1 saltado (Ollama real), 100 % de cobertura (incluye 4 tests nuevos de aislamiento) |
| `npm run test:unit` | 78 pasan (incluye 6 nuevos del guardián y de los agentes) |
| `ruff check` / `ruff format --check` | Sin errores |
| `pip-audit -r backend/requirements.txt` (2.10.1) | 0 vulnerabilidades conocidas |
| `npm audit --audit-level=high` | 0 vulnerabilidades |
| Bandit 1.9.4 `-r backend/app` | 0 de severidad media o alta tras revisar; 4 bajas falsas positivas (ver `SECURITY_FINDINGS.md`) |
| Semgrep 1.181.0, reglas propias `.semgrep/` | 0 hallazgos. Cada regla se probó con código vulnerable de ejemplo y salta |
| Semgrep, conjuntos públicos (`p/python`…) | **No ejecutado en local**: el entorno no llega a `semgrep.dev`. Lo ejecuta la CI (informativo) |
| Gitleaks 8.28.0 historia (90 commits) y árbol | 1 falso positivo (contraseña ficticia de un test), ignorado por huella |
| `npm run test:e2e` | No ejecutado en local en esta revisión; lo ejecuta la CI |
| Android | No ejecutado (sin SDK); lo ejecuta la CI |

## 4. Herramientas disponibles

Gratuitas y sin cuenta: pip-audit, npm audit, Bandit, Semgrep (CLI, `--metrics=off`), Gitleaks.
Cómo instalarlas, ejecutarlas e interpretarlas: [`SECURITY_TESTING.md`](SECURITY_TESTING.md).
CodeQL y Dependabot alerts dependen de ajustes de GitHub (gratuitos en repositorios públicos), §6 de ese documento.
