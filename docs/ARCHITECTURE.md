# Arquitectura actual

> Documento de la **Fase 1 (auditoría)**. Describe el proyecto **tal como está** en `main`
> (commit `9d35ee6`, 5 de octubre de 2026). No propone cambios: los problemas detectados se
> listan al final y los cambios futuros se deciden fase a fase.

## 1. Visión general

Python Learning Dashboard tiene **cuatro piezas** que comparten el mismo contenido:

```
                  frontend/data/*.json  (contenido: fuente única)
                    ▲            ▲              ▲
   genera y comprueba│            │ lee          │ lee (copiado en la imagen Docker)
                    │            │              │
 scripts/ (Python)  │   frontend/ (web)    backend/ (API FastAPI)      android/ (Kotlin)
 learning/, courses/│   GitHub Pages  ───HTTPS──►  Render + Neon   ◄──HTTPS── app nativa
                         Pyodide en un Worker        PostgreSQL
```

| Pieza | Tecnología | Dónde se ejecuta | Despliegue |
|---|---|---|---|
| `frontend/` | HTML, CSS y JavaScript con **módulos ES, sin framework ni build** | Navegador | GitHub Pages (`.github/workflows/pages.yml`) |
| `backend/` | FastAPI, SQLAlchemy 2, Alembic, Pydantic Settings, PyJWT, Argon2 | Contenedor Docker | Render (`render.yaml`), base de datos en Neon |
| `android/` | Kotlin + Jetpack Compose | Móvil | APK desde GitHub Actions (`android.yml`) |
| `scripts/` | Python (solo biblioteca estándar + SQLite/Node/Java para comprobar) | PC del autor y CI | Genera `frontend/data/**` |

Decisiones ya documentadas: 32 ADR en [`docs/adr/`](adr/). Este documento no las sustituye; las resume.

## 2. Frontend (`frontend/`)

### 2.1 Punto de entrada

`index.html` es la única página de la app (SPA con rutas `#/…`). Orden de carga:

1. `<meta http-equiv="Content-Security-Policy">` (GitHub Pages no permite cabeceras propias).
2. 13 hojas de estilo en cascada (`base.css` → … → `pro.css` → `learn.css`).
3. `js/theme-init.js` (script clásico, síncrono): tema, tamaño de letra y defensa anti-marcos.
4. `config.js` (script clásico): `window.PLD_CONFIG` (URL de la API, email de contacto, PWA, analítica).
5. `js/analytics.js` (`defer`): GoatCounter, **desactivado** (`goatcounter: ""`).
6. `js/app.js` (`type="module"`): importa estáticamente el resto de módulos.

Otras páginas estáticas: `privacidad.html`, `aviso-legal.html`, `404.html`.

### 2.2 Rutas (hash)

Definidas en `js/app.js` y `js/learn/learn-app.js`:

| Ruta | Vista | Módulo |
|---|---|---|
| `#/aprender` (principal) | «¿Qué estudio ahora?» | `js/learn/learn-app.js` |
| `#/teoria`, `#/practicar`, `#/progreso` | Núcleo educativo por conceptos (ADR-0031) | `js/learn/*` |
| `#/daw` | Preparación DAW y cursos de DAW | `js/daw.js`, `js/learn/daw-prep.js` |
| `#/bienvenida` | Mapa de bienvenida (primera visita) | `js/learn/welcome.js` |
| `#/inicio`, `#/leccion/<slug>` | Curso PCAP (27 lecciones) | `js/app.js`, `home.js`, `console.js`, `quiz.js`, `assistant.js` |
| `#/pcap` | Zona de examen PCAP | `js/pcap.js`, `pcap-store.js` |
| `#/perfil`, `#/certificado` | Perfil, logros y certificado | `profile.js`, `certificate.js` |
| `#/cuenta`, `#/restablecer` | Cuenta y recuperación de contraseña | `account.js`, `private.js` |

### 2.3 Módulos JavaScript

| Grupo | Archivos | Qué hacen |
|---|---|---|
| Coordinación | `app.js` (768 líneas) | Carga `data/lessons.json`, pinta barra lateral y lecciones, enruta, registra el service worker |
| Núcleo educativo (lógica pura) | `learn/mastery.js`, `recommend.js`, `session.js`, `exam.js`, `answers.js` | Dominio por concepto, repaso espaciado, plan de hoy, sesiones, simulacros. **No tocan el DOM**: se prueban con `node --test` |
| Núcleo educativo (vistas) | `learn/learn-app.js`, `session-view.js`, `ui.js`, `welcome.js`, `daw-prep.js` | Pintan HTML con plantillas de texto |
| Persistencia | `store.js`, `game.js`, `pcap-store.js`, `course-store.js`, `learn/learn-store.js`, `prefs.js` | Leen/escriben `localStorage` y sincronizan con la API |
| Validación de datos externos | `progress-guard.js` (`cleanProgress`), `learn/mastery.js` (`cleanLearning`) | Filtran lo que llega de `localStorage` o de la cuenta |
| Seguridad del HTML | `markdown.js` | `escapeHtml`, `safeUrl`, Markdown mínimo que siempre escapa |
| Python | `python-runner.js`, `pyodide-worker.js`, `console.js` | Consola y corrección de ejercicios |
| API | `api.js` | Cliente HTTP, token en memoria, prefijo `/api/v1` |
| Otros | `quiz.js`, `assistant.js`, `tour.js`, `celebrate.js`, `certificate.js`, `profile.js`, `home.js`, `daw.js`, `pcap.js`, `pcap-sync.js` | Funcionalidades concretas |

Librerías de terceros: **solo** `vendor/highlight/` (highlight.js copiado en el repo) y Pyodide (CDN).
No hay `node_modules` en producción ni paso de *build*.

### 2.4 Ejecución de Python (Pyodide)

```
console.js / session-view.js
   └─ PythonRunner (python-runner.js)        ← hilo principal
        └─ new Worker("pyodide-worker.js", {type: "module"})
             ├─ import("https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs")
             └─ ejecuta frontend/py/runner.py  (run_for_js / check_for_js)
```

- Pyodide se carga **solo la primera vez que se ejecuta código** (perezoso).
- Límite de 10 s: si se supera, se destruye el Worker y se crea otro.
- `py/runner.py` es el **mismo motor** que usan los tests de CPython (`backend/tests`, `scripts/learning`).
- Al pegar código que toca `js`, `fetch`, `localStorage`… la consola avisa (`console.js`, `RISKY_PASTE`).

### 2.5 PWA

- `manifest.webmanifest` (nombre «Prepara el PCAP», `start_url: ./#/inicio`).
- `sw.js` (versión `v5`, se cambia a mano):
  - web propia: *network first* con copia en caché `pld-site-v5`;
  - Pyodide: *cache first* en `pld-pyodide`;
  - API: nunca se guarda en caché.
- Se registra en `app.js` solo si `PLD_CONFIG.serviceWorker` (desactivado en localhost).

### 2.6 Dónde se guarda el progreso

| Clave `localStorage` | Contenido | Módulo | Sincroniza con |
|---|---|---|---|
| `pld:completed` | Lecciones PCAP completadas | `store.js` | `/api/v1/progress` |
| `pld:game` | XP, racha, logros | `game.js` | — (solo local) |
| `pld:pcap` | Preparación del examen PCAP | `pcap-store.js` | `/api/v1/pcap-state` |
| `pld:course:<id>` | Cursos de DAW (sql, js, java, entornos, programacion) | `course-store.js` | `/api/v1/course-state/<id>` |
| `pld:learn` | Progreso por conceptos (núcleo educativo) | `learn/learn-store.js` | `/api/v1/course-state/learn` |
| `pld:draft:<slug>` | Borrador del editor por lección | `console.js` | — |
| `pld:prefs` | Tema y tamaño de letra | `prefs.js` | — |
| `pld:cert-name`, `pld:welcome-seen` | Nombre del certificado, bienvenida vista | `certificate.js`, `learn-store.js` | — |
| `sessionStorage pld:flash` | Mensaje tras borrar la cuenta | `account.js` | — |

El **token de sesión** (JWT) vive solo en una variable de `api.js` (ADR-0032). Al cerrar sesión
se borran todas las claves `pld:*` salvo `pld:prefs`.

### 2.7 Contenido (`frontend/data/`)

| Archivo | Tamaño | Qué contiene | Cómo se genera |
|---|---|---|---|
| `lessons.json` | 225 KB | Curso PCAP: 27 lecciones con teoría, ejemplo, ejercicio, tests, quiz, reto y asistente | A mano (lo valida `backend/tests/test_content.py`) |
| `pcap.json` | 177 KB | 126 preguntas ES/EN, 48 fichas, formato del examen | A mano (lo valida `backend/tests/test_pcap.py`) |
| `learning.json` | 158 KB | 22 conceptos, errores típicos, 128 ejercicios | `scripts/learning/build_learning.py` |
| `courses/<id>/lessons.json` y `bank.json` | 20–130 KB | Cursos de DAW: programacion, sql, entornos, js, java | `scripts/courses/<id>_course.py` |

Regla del proyecto: **los JSON generados no se editan a mano**; se cambia el script y se regenera.

## 3. Backend (`backend/`)

### 3.1 Estructura

| Archivo | Responsabilidad |
|---|---|
| `app/main.py` | App FastAPI, CORS, cabeceras de seguridad, límite de 300 KB por petición, routers en `/api/v1` y rutas antiguas `/api` (*deprecated*) |
| `app/config.py` | Variables de entorno (`.env`): BD, `JWT_SECRET`, CORS, SMTP, límites |
| `app/security.py` | Argon2id, JWT HS256 (30 min, con `token_version`), tokens de recuperación (SHA-256) |
| `app/deps.py` | `get_current_user` (valida token y versión) |
| `app/rate_limit.py` | Límites en memoria por IP y por cuenta |
| `app/password_policy.py` | Contraseñas comunes o con el email/nombre: rechazadas |
| `app/security_events.py` | Log JSON `pld.security` con técnica MITRE ATT&CK, IP y email seudonimizados |
| `app/routers/` | `auth`, `account`, `lessons`, `progress`, `attempts`, `pcap`, `course_state` |
| `app/models.py`, `schemas.py` | Modelos SQLAlchemy y esquemas Pydantic |
| `app/mailer.py` | SMTP (si no hay, el enlace va al log en desarrollo) |
| `app/local_site.py` | Modo escritorio: la API sirve también la web (`Iniciar-Dashboard.bat`) |
| `migrations/` | Alembic (6 migraciones en `versions/`) |
| `tests/` | pytest, **470 tests, 100 % de cobertura** (comprobado el 5/10/2026) |

### 3.2 Autenticación

- Registro con aceptación de privacidad; login OAuth2 *password flow* (`username` = email).
- Respuesta: JWT de 30 min. La web lo guarda **en memoria**; al recargar, se pierde la sesión.
- `token_version` en el usuario: cambiar contraseña o «cerrar sesión en todos» invalida tokens.
- Bloqueo por cuenta (10 fallos → 15 min) y por IP (5/min), recuperación por email (3 cada 15 min).
- No hay roles ni administración: cada usuario solo accede a sus datos (el id sale del token).

### 3.3 API

Documentada en [`docs/API.md`](API.md) y en la tabla del `README.md`. Superficie: salud, lecciones,
auth, cuenta (export/borrado RGPD), progreso, intentos, estado PCAP y estado de cursos.

## 4. App Android (`android/`)

Kotlin + Compose, ~5 800 líneas en `pld/learn`, `pld/pcap` y `pld/ui`. Lee los mismos JSON de
`frontend/data/` (copiados en la compilación) y **reimplementa en Kotlin** la lógica del núcleo
educativo (`Learning.kt` ≈ `learn/mastery.js` + `recommend.js` + `session.js`). Sincroniza con las
rutas antiguas `/api/...` (`pcap/Sync.kt`). Pide permiso de internet solo para la cuenta y la sincronización; el contenido funciona sin conexión (ADR-0014, ADR-0026).

## 5. Servicios externos

| Servicio | Para qué | Dónde se configura |
|---|---|---|
| GitHub Pages | Web pública | `pages.yml` |
| GitHub Actions | CI, APK, despliegue | `.github/workflows/` |
| Render (plan gratuito, Frankfurt) | API | `render.yaml`, `backend/Dockerfile` |
| Neon (PostgreSQL, UE) | Base de datos | Variable `DATABASE_URL` en Render |
| jsDelivr | Pyodide 314.0.7 | `python-runner.js`, CSP |
| SMTP (opcional) | Recuperación de contraseña | Variables `SMTP_*` en Render |
| GoatCounter (opcional, desactivado) | Analítica sin cookies | `config.js` |
| Dependabot | Actualizaciones de dependencias | `.github/dependabot.yml` |

**No hay ninguna integración de IA** dentro de la aplicación. El «Asistente» de cada lección
(`js/assistant.js`) muestra respuestas preparadas en `lessons.json`.

## 6. Dependencias

| Ecosistema | Archivo | Dependencias |
|---|---|---|
| pip (backend) | `backend/requirements.txt` | fastapi, uvicorn, sqlalchemy, alembic, pydantic-settings, email-validator, python-multipart, pyjwt, argon2-cffi, psycopg (rangos de versión, sin *lockfile*) |
| pip (desarrollo) | `backend/requirements-dev.txt` | pytest, httpx, ruff, pytest-cov |
| npm (solo tests) | `package.json` + `package-lock.json` | `@playwright/test` 1.56.0, `@axe-core/playwright` 4.10.2 (versiones exactas) |
| Frontend | `frontend/vendor/` | highlight.js (copiado) |
| CDN | — | Pyodide 314.0.7 |
| Gradle | `android/` | Compose y dependencias de Android |

## 7. Integración continua

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `ci.yml` → `backend` | push a `main` y PR | ruff, `pip-audit`, pytest 100 %, `build_learning.py --check`, migraciones en PostgreSQL 16 |
| `ci.yml` → `e2e` | push a `main` y PR | `npm run test:unit`, `npm audit`, Playwright + axe |
| `android.yml` | cambios en `android/`, `frontend/data/`, `scripts/courses/` | Comprueba cursos, tests JVM, lint, APK |
| `pages.yml` | push a `main` que toca `frontend/` | **Publica** la web |

Todos los workflows usan `permissions: contents: read` (salvo Pages) y `persist-credentials: false`.

## 8. Problemas detectados en la auditoría

Resumen. El detalle de seguridad está en [`SECURITY.md`](SECURITY.md) y el de pruebas en [`TESTING.md`](TESTING.md).
Las afirmaciones marcadas con *(inferido)* no se han comprobado con una prueba.

### Seguridad
1. El Worker de Pyodide **no recibe la CSP** de `<meta>` *(inferido de la especificación CSP)*: el código Python del alumno podría usar `import js` para hacer peticiones a cualquier origen. No tiene acceso al token, al DOM ni a `localStorage`.
2. Pyodide se carga del CDN **sin SRI** (riesgo ya documentado en `docs/security/revision-2026-10.md`).
3. `style-src 'unsafe-inline'` y CSP en `<meta>` (ya documentados).
4. `app.js` (barra lateral) inserta `module.slug` y `lesson.slug` en atributos HTML **sin escapar**. El dato viene del propio JSON, así que el riesgo es bajo, pero rompe la regla «todo se escapa».
5. `game.js` mezcla `pld:game` de `localStorage` sin validarlo (los demás almacenes usan `cleanProgress`/`cleanLearning`). Hoy no llega a HTML sin escapar, pero es una inconsistencia.
6. La CSP de producción permite `connect-src http://127.0.0.1:8000 http://localhost:8000`.
7. `python-multipart` y `argon2-cffi` sin límite superior de versión; el backend no tiene *lockfile* con *hashes*.
8. `deploy.ps1` hace commit **y push a `main`**: ningún agente debe ejecutarlo.

### Accesibilidad
9. axe-core pasa (WCAG 2.1 AA) en las vistas auditadas, pero **no hay pruebas manuales documentadas** (lector de pantalla, solo teclado, zoom al 200 %).
10. 120 declaraciones `font-size` en `px`. El tamaño de letra propio usa `--ui-zoom`; la preferencia de tamaño de letra del navegador no afecta al texto en `px`.

### Rendimiento
11. 13 CSS bloqueantes (≈113 KB) y ≈325 KB de JS sin minificar, todos importados al arrancar desde `app.js`.
12. `data/lessons.json` (225 KB) se descarga al arrancar aunque la portada sea `#/aprender`, y se pide dos veces (`app.js` y `learn-app.js`).
13. El service worker precachea solo 6 archivos: sin conexión solo funciona lo ya visitado. La versión `v5` se cambia a mano.

### Duplicación y archivos grandes
14. La lógica del núcleo educativo está **duplicada** en JavaScript y en Kotlin (hay que cambiar las dos).
15. Capas de CSS superpuestas de varios rediseños: `base.css`, `academy.css`, `pro.css` y `learn.css` redefinen estilos; `pro.css` redefine los colores de `base.css`.
16. Archivos muy grandes: `scripts/courses/programacion_course.py` (3 199 líneas), `scripts/learning/exercises.py` (2 926), `sql_course.py` (2 517), `learn.css` (1 267), `pcap.js` (774), `app.js` (768).

### Deuda técnica
17. `manifest.webmanifest` sigue presentando la app como «Prepara el PCAP» con `start_url #/inicio`, pero la portada es ahora `#/aprender`.
18. La plantilla de PR y `CONTRIBUTING.md` no mencionan `npm run test:unit` ni `build_learning.py --check`.
19. Rutas antiguas `/api/...` mantenidas por la app Android publicada (ya documentado).
20. Los tests e2e y Android no se pudieron ejecutar en esta auditoría (sin navegador del proyecto instalado ni SDK de Android); se confía en la CI.
