# Plan de mejora

Auditoría técnica inicial (Fase 0) del 2026-11-01 sobre `main` en el commit `f6a475b`.
Este documento es la fuente de verdad del estado real: cada hallazgo indica si está **VERIFICADO** (con evidencia reproducible) o es una **HIPÓTESIS** pendiente de comprobar.

## 1. Resumen

- **P0 verificados: 0. P1 verificados: 0.** No se ha tocado código de producto en esta iteración.
- Todas las comprobaciones de `docs/TESTING.md` que se podían ejecutar en este entorno pasan (ver §3).
- Hay 1 test e2e intermitente (F-01), 1 riesgo de integridad de datos no verificado (H-04) y varias mejoras P2/P3.
- El plan maestro asume documentos y un tutor con IA que **no existen** en el repositorio (ver §5): se necesita una decisión del autor antes de continuar con la Fase 8.

## 2. Inventario

| Área | Estado real (contrastado con el código) |
|---|---|
| Arquitectura | Frontend estático (HTML/CSS/ES Modules, rutas con hash, Pyodide en Web Worker, PWA) en GitHub Pages; API FastAPI + SQLAlchemy + Alembic en Render; PostgreSQL (Neon) en producción, SQLite en local. Coincide con `README.md`. |
| Funcionalidades | Conceptos con ejercicios (22 / 131, coincide con el README), curso PCAP, cursos de DAW (SQL, JS, Java, Entornos, Programación), currículo oficial, repaso espaciado, XP/logros, cuenta opcional (email y Google), RGPD (exportar/borrar), PWA. |
| Tutor con IA | **No existe.** Se añadió con la migración `20261020_d7e2a9c4f1b8_uso_del_tutor` y se retiró con `20261026_e1a2b3c4d5f6_quitar_tutor` (borra la tabla `tutor_usage`). |
| Documentos | Existen `README.md`, `SECURITY.md` y `docs/{API,AUDITORIA-Y-LICENCIAS,DEMO-Y-DEFENSA,DEPLOY,EJECUTAR-EN-WINDOWS,PLAN-CURRICULO-DAW,TESTING,auth}.md` + `docs/memoria/`. **No existen** `AUDIT.md`, `ROADMAP.md`, `ARCHITECTURE.md` ni `CHANGELOG.md`. |
| CI | `ci.yml` (backend + migraciones PostgreSQL + cursos + e2e) y `pages.yml`. Último push a `main` (#67): CI en verde. |

## 3. Pruebas ejecutadas en esta iteración

Entorno: Linux, Python 3.13.18 (la CI usa 3.12), Node 22.23.4, Playwright 1.63.0 con Chromium.

| Comprobación | Resultado |
|---|---|
| `ruff check` y `ruff format --check` (backend, e2e, scripts) | OK, 75 archivos formateados |
| `pytest --cov=app --cov-fail-under=100` | OK: 557 pasan, cobertura 100 % (1213 sentencias) |
| `build_learning.py --check` | OK: 22 conceptos, 131 ejercicios comprobados |
| `build_curriculum.py --check` | OK: 17 módulos, 64 RA, 516 CE |
| Cursos `sql`, `js`, `java`, `entornos`, `programacion` con `--check` | OK (las cinco) |
| `npm run test:unit` | OK: 68 de 68 |
| `npm audit --audit-level=high` | 0 vulnerabilidades |
| `pip-audit -r backend/requirements.txt` | Sin vulnerabilidades conocidas |
| `npx playwright test --workers=1` | 135 pasan, 1 falla (F-01). El test que falló pasó 10 de 10 en repeticiones posteriores. |

**No ejecutado** (no se marca como superado):

- Migraciones sobre PostgreSQL (`tests/test_migrations.py`): no hay PostgreSQL en este entorno. La CI las ejecuta y pasan en `main`.
- Pyodide desde jsDelivr: el proxy del entorno devuelve 403. Las e2e se ejecutaron con una copia local de Pyodide `314.0.7` (la misma versión que `PYODIDE_VERSION`) servida con `PYODIDE_URL`. **No se ha probado la carga real desde la CDN.**
- Lector de pantalla, solo teclado, zoom al 200 %, móvil real y Lighthouse: ya figuran como pendientes en `docs/TESTING.md`.

## 4. Hallazgos

### F-01 · P2 · Test e2e intermitente en el menú móvil de la portada — VERIFICADO (causa raíz parcial)

- **Componente:** `e2e/landing.spec.js:117` («móvil › menú accesible…»), `frontend/js/landing.js`, `frontend/index.html`.
- **Evidencia:** falló 2 veces seguidas (la suite completa y una repetición aislada) con `locator.click: Test timeout` porque el selector resolvió a `#menu-toggle` (el botón de la barra de la app), «element is not visible». Después pasó 10 de 10 (5 sin y 5 con `PYODIDE_URL`). La CI de `main` pasa (allí `retries: 1`; en local `retries: 0`).
- **Mecanismo observado:** justo después de `page.goto("/#/portada")` a 375 px, `getByRole("button", { name: "Menú" })` casa unas veces con `#menu-toggle` (visible, 97×42, mientras `#lp-menu-toggle` aún no existe) y otras con `#lp-menu-toggle`. En una réplica con 4 intentos el clic se recuperó en todos, así que **no se ha reproducido el bloqueo de 60 s fuera del test real**.
- **Solución propuesta:** en el test, esperar a que exista `#lp-menu-toggle` antes de localizar el botón (selector determinista). No es debilitar el test: mantiene todas las aserciones.
- **Riesgo:** bajo (solo toca el test). Hay que evitar que la espera enmascare F-02.
- **Pruebas necesarias:** repetir ese test con `--repeat-each=20 --retries=0`, en serie y con `--workers=4`.
- **Criterio de aceptación:** 0 fallos en 20 repeticiones sin reintentos.

### F-02 · P3 · Destello de la barra de la app en la portada móvil — VERIFICADO (impacto no medido)

- **Componente:** `frontend/index.html` (cabecera `.topbar` visible por defecto), `frontend/js/app.js`, `frontend/js/landing.js`.
- **Evidencia:** a 375 px, justo tras la carga de `#/portada`, `#menu-toggle` tiene tamaño 97×42 y `#lp-menu-toggle` no existe; en la medición siguiente (no más de 300 ms después) la barra ya está a 0×0 y la portada pintada. La duración exacta varía entre cargas. Ese botón abre la barra lateral de la app, no el menú de la portada.
- **No verificado:** cuánto dura el destello en un móvil real con red lenta.
- **Solución propuesta:** ocultar la barra desde el HTML cuando la ruta es la portada. La CSP de `index.html` no permite scripts en línea, así que habría que usar CSS o un script externo síncrono.
- **Riesgo:** medio (toca el arranque de la app y la accesibilidad del foco).
- **Pruebas necesarias:** `e2e/landing.spec.js`, `e2e/a11y.spec.js`, `e2e/navigation.spec.js`.
- **Criterio de aceptación:** en un perfil móvil con red limitada no aparece la barra de la app antes de la portada.

### F-03 · P3 · El servidor acepta del cliente si un ejercicio está superado y el estado (XP, niveles) — VERIFICADO (por lectura del código)

- **Componente:** `backend/app/routers/attempts.py` (`if attempt.passed: mark_completed`), `backend/app/schemas.py:193-201` (`PcapStateIn.data: dict`, solo limitado por tamaño), `backend/app/routers/course_state.py`.
- **Evidencia:** el campo `passed` y el documento de estado los decide el navegador. Ya figura en «Limitaciones conocidas» del README.
- **Por qué no es P1:** el usuario sale siempre del token, no del cuerpo (los datos están aislados por cuenta), no hay ranking entre usuarios (búsqueda sin resultados en `backend` y `frontend/js`) y el código corre en el navegador del propio alumno, así que el servidor no puede comprobarlo sin ejecución remota de código, que el plan prohíbe.
- **Sube a P1 si:** se añade un ranking, certificados o cualquier privilegio que dependa de XP/progreso.
- **Solución propuesta:** mantener y documentar. Si se añade un ranking, validar en el servidor una puntuación máxima plausible por acción.
- **Pruebas necesarias:** test de aislamiento entre usuarios (comprobar si ya está cubierto antes de añadirlo).

### H-04 · P2 · Posible pérdida de datos por «última escritura gana» al sincronizar dos dispositivos — HIPÓTESIS

- **Componente:** `PUT /course-state/{course}` y `PUT /pcap-state` (`backend/app/routers/course_state.py`, `pcap.py`).
- **Evidencia:** el `PUT` sustituye el documento completo y el docstring dice que «la app ya lo ha fusionado»; el servidor no recibe ni comprueba ningún token de versión (`updated_at` solo se devuelve).
- **No verificado:** que dos dispositivos con sesión abierta pierdan datos en la práctica (depende de cuándo fusiona el cliente).
- **Verificación propuesta:** test e2e con dos contextos de Playwright sobre la misma cuenta, guardando progreso distinto casi a la vez.
- **Solución propuesta si se confirma:** parámetro opcional `expected_updated_at` en el `PUT`; si no coincide, 409 y el cliente vuelve a fusionar.
- **Riesgo:** medio. Cambia el contrato de la API: **requiere aprobación** (ver §6).
- **Criterio de aceptación:** el test de dos contextos conserva ambos cambios.

### F-05 · P3 · La CSP de producción permite conectar a `localhost:8000` — VERIFICADO

- **Componente:** `<meta http-equiv="Content-Security-Policy">` de `frontend/index.html` (`connect-src … http://127.0.0.1:8000 http://localhost:8000`).
- **Evidencia:** está en el HTML que se publica en GitHub Pages; solo hace falta en desarrollo local.
- **Solución propuesta:** servir la CSP de desarrollo desde `e2e/serve_frontend.py` y `scripts/run_local.py`, y quitar esas dos entradas del HTML publicado.
- **Riesgo:** medio (se puede romper el arranque local o las e2e). Impacto de seguridad bajo.

### F-06 · P3 · Límite de intentos de login en memoria — DOCUMENTADO, NO VERIFICADO EN CÓDIGO

- Lo afirma el README («funcionan con un solo servidor»). No se ha leído `backend/app/rate_limit.py` en esta iteración. Con un solo servidor en Render es aceptable.

### Revisado sin hallazgos

- **XSS:** los usos de `display_name` y `email` en plantillas pasan por `escapeHtml`; `showToast` usa `textContent`. Hay 53 usos de `innerHTML` en `frontend/js`; **solo se han revisado los que interpolan datos de la cuenta**, el resto queda pendiente.
- **Worker de Pyodide:** `python-runner.js` espera a `ready` antes de enviar trabajo, aplica un tiempo máximo de 10 s (que empieza tras la carga de Python) y reinicia el worker; `pyodide-worker.js` cierra red, `eval` y constructores de funciones y documenta que no es aislamiento completo. No se ha probado la interrupción ni los bucles largos más allá de lo que cubren las e2e existentes (`e2e/console.spec.js`).
- **Backend:** límite de cuerpo (`BodySizeLimit`, 300 kB), límite de tamaño del estado, cabeceras de seguridad y CSP restrictiva en la API, CORS con lista de orígenes y cabecera `X-PLD-Session`, cobertura del 100 %.
- **Service worker (`frontend/sw.js`):** la API nunca se guarda, la web va con red primero y Pyodide con caché primero; las cachés antiguas `pld-site-*` se limpian al activar. Sin hallazgos; sigue pendiente la limitación ya documentada (no abre sin conexión una lección que no se visitó antes).

## 5. Documentación

- **D-01 · P3:** el plan maestro pide actualizar `AUDIT.md`, `ROADMAP.md`, `ARCHITECTURE.md` y `CHANGELOG.md`, que no existen. No se han creado: la arquitectura vive en `README.md` y `docs/memoria/memoria.md`. Este documento queda como único plan; si se quiere un `CHANGELOG.md`, es una decisión del autor.
- **D-02 · P3:** `docs/TESTING.md` sigue acertando con lo ejecutado; conviene añadir la variable `PYODIDE_URL` a su sección de entorno, porque es la forma de ejecutar las e2e sin acceso a jsDelivr (hoy solo se explica en `e2e/fixtures.js`).

## 6. Decisiones pendientes del autor (NEEDS_HUMAN)

1. **Tutor con IA (Fase 8):** se retiró el 26 de octubre. ¿Se quiere reintroducir? Si no, la Fase 8 queda cerrada como «no aplica». No se ha construido nada.
2. **H-04:** si se confirma, cambiar el contrato de `PUT /course-state` y `/pcap-state` (API compatible hacia atrás con parámetro opcional).
3. **Ramas y despliegue:** este trabajo va en la rama `docs/plan-mejora-auditoria`. Fusionar a `main` publica la web, así que el merge lo hace siempre la persona (regla del proyecto).

## 7. Estado por fases del plan maestro

| Fase | Estado |
|---|---|
| 0 Auditoría | Hecha (este documento). Quedan sin auditar a fondo: los 53 `innerHTML`, `rate_limit.py` y las migraciones. |
| 1 Estabilidad | Cobertura automática verde. Pendiente: H-04 y los flujos de red caída / actualización de la PWA con una prueba propia. |
| 2 UX | Sin empezar (F-02 es lo único detectado). |
| 3 Calidad del aprendizaje | Los `--check` de contenido pasan (respuestas ejecutadas). Pendiente revisar el formato de ejercicios contra la lista de campos del plan. |
| 4 Progreso | Sin empezar. |
| 5 Pyodide | Revisión de código hecha; faltan pruebas manuales de interrupción y ejecuciones largas. |
| 6 Seguridad | Revisión defensiva parcial (backend, cabeceras, CSP, XSS de cuenta). Pendiente: Google Identity, rate limit, resto de `innerHTML`. |
| 7 Accesibilidad / PWA | Solo las comprobaciones automáticas existentes (axe en e2e). Pendientes las manuales. |
| 8 Tutor IA | Bloqueada por la decisión 1 de §6. |
| 9 Rendimiento | Sin empezar (no se ha medido nada). |
| 10-11 Pruebas / documentación | Ejecución de pruebas hecha (§3); documentación: solo este archivo. |

## 8. Siguiente paso recomendado

1. Confirmar la decisión sobre el tutor y sobre H-04.
2. Estabilizar F-01 (cambio mínimo en el test, 20 repeticiones sin reintentos).
3. Verificar H-04 con el test de dos contextos antes de tocar la API.
