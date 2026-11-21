# Plan por fases y pruebas: integración NEXARO AI en PLD

Estado: **propuesta de la Fase 0**. Cada fase empieza solo cuando el autor la aprueba. Contrato en
[`NEXARO_INTEGRATION_CONTRACT.md`](NEXARO_INTEGRATION_CONTRACT.md) y riesgos y decisiones en
[`NEXARO_INTEGRATION_AUDIT.md`](NEXARO_INTEGRATION_AUDIT.md) (§9 y §11).

Reglas comunes (de `CLAUDE.md`): rama `feat/nexaro-ai-integration` (o derivadas `feat/nexaro-ai-*`), cambios pequeños con `git diff` revisado, sin push a `main`, sin merge, sin `deploy.ps1`, sin servicios de pago y con 100 % de cobertura en el backend. Ninguna fase cambia el login, la sesión, Pyodide, el PCAP, DAW ni la PWA.

## Fase 0: auditoría (esta)

Entregables: los tres documentos de `docs/architecture/`. Sin código. **Pendiente:** aprobación y respuesta a D-01…D-08.

## Fase 1: conectividad mínima y segura (backend, sin UI)

| Archivo | Cambio |
|---|---|
| `backend/app/config.py` | Variables `NEXARO_*` y `AI_*` (contrato §5) y validador de URL y allowlist |
| `backend/app/nexaro_client.py` | `NexaroClient` (async, timeouts, sin redirects, `trust_env=False`, límite de bytes, parser NDJSON y errores tipados `NexaroUnavailable`/`NexaroBusy`) |
| `backend/app/routers/ai.py` | Solo `GET /ai/status` |
| `backend/app/main.py` | Registrar el router, `health.ai`, crear y cerrar el cliente en `lifespan` y validar la configuración al arrancar si `NEXARO_ENABLED` |
| `docker-compose.yml` | `NEXARO_ENABLED`/`NEXARO_BASE_URL`/`NEXARO_MODEL` vacías por defecto. Sin red nueva hasta NX-REQ-07 |
| `backend/tests/test_ai_config.py`, `test_nexaro_client.py`, `test_ai_status.py` | Ver la tabla de pruebas |
| `docs/API.md`, `CHANGELOG.md` | Ruta nueva |

Criterio de salida: con `NEXARO_ENABLED=false` (por defecto) todo PLD se comporta igual (las suites existentes en verde). Con NEXARO simulado (`httpx.MockTransport`), `/ai/status` responde según el contrato.

## Fase 2: tutor y pistas

| Archivo | Cambio |
|---|---|
| `backend/app/ai_context.py` | Contexto a partir de `Lesson`, truncado, «defang» y plantillas por modo |
| `backend/app/schemas.py` (o `schemas_ai.py`) | `AiRequest`, `AiAnswer`, `AiStatus` con `extra="forbid"` |
| `backend/app/routers/ai.py` | `POST /ai/chat` y `POST /ai/hint` |
| `backend/app/rate_limit.py` | `ai_limiter` (`AI_RATE_LIMIT_PER_MINUTE`) y semáforo `AI_MAX_CONCURRENCY` |
| `backend/app/security_events.py` | `AI_RATE_LIMITED` (T1499.003) y `AI_UPSTREAM_ERROR` |
| `docs/REGISTRO_TRATAMIENTOS.md` | RAT nuevo (tutor IA) |
| `backend/tests/test_ai_chat.py`, `test_ai_hint.py`, `test_ai_security.py` | Ver la tabla de pruebas |

Verificación manual (solo T1): PLD nativo con `NEXARO_BASE_URL=http://127.0.0.1:8080`, NEXARO v3 encendido y un modelo instalado. La calidad pedagógica (que no dé la solución) se evalúa con un pequeño conjunto de casos **fuera de la CI** (no hay un modelo en CI).

## Fase 3: explicación de errores y revisión de código

`POST /ai/explain-error` y `POST /ai/review-code` en `routers/ai.py` y plantillas en `ai_context.py`. La salida es Markdown validado (longitud y texto no vacío). Si se aprueba NX-REQ-06, JSON validado con Pydantic y, si no valida, el texto. Pruebas en `test_ai_review.py`.

## Fase 4: frontend

| Archivo | Cambio |
|---|---|
| `frontend/js/ai/ai-api.js` | `aiStatus()`, `askAi(mode, body, {signal})` sobre `request()` de `api.js`. Sin tokens nuevos ni almacenamiento |
| `frontend/js/ai/ai-panel.js` | Sección «Tutor IA» dentro del panel de `assistant.js`: estados (comprobando, disponible, no disponible, error), casilla «Enviar mi código» desmarcada, botón Reintentar, cancelación y la etiqueta «Generado por IA · no es la corrección oficial» |
| `frontend/js/assistant.js` | Montar el panel solo si `serverInfo.ai` y hay sesión |
| `frontend/index.html`, `frontend/css/widgets.css`, `frontend/i18n/en.json` | Marcado, estilos (tema claro y oscuro, responsive) y textos |
| `frontend/privacidad.html` + `backend/tests/test_privacy_policy.py` | Describir el tratamiento |
| `frontend/precache.js` | Regenerado con `node scripts/web/build_precache.mjs` |
| `tests/unit/ai-logic.test.mjs`, `e2e/ai-tutor.spec.js` | Ver la tabla de pruebas |

Implementado: la lógica sin DOM ni red (cuerpos, límites, historial, niveles de pista y mensajes de error) está en `frontend/js/ai/ai-logic.js`, que es lo que prueban los unitarios. `ai-api.js` depende de `window`. `console.js` expone `lastRunError()` para «Explicar mi error». `#assistant-messages` lleva `tabindex="0"`, porque con el tutor el panel tiene menos sitio y la lista pasa a tener scroll (axe `scrollable-region-focusable`).

## Fase 5: persistencia (solo con una decisión documentada, D-07)

Tablas `ai_conversations`/`ai_messages` (propietario = sesión), migración Alembic revisada, exportación en `/users/me/export`, borrado en cascada con la cuenta, retención configurable y paginación. Fuera del alcance mientras D-07 = «No».

## Fase 6: streaming (después de que el chat sin streaming sea estable)

SSE o NDJSON de PLD hacia el navegador. Cancelación al desconectarse el cliente (cerrar el stream hacia NEXARO), backpressure, sin peticiones colgadas y las mismas cabeceras de sesión y CSRF. Pruebas con chunks, errores a mitad del stream y desconexión.

## Prerrequisitos en NEXARO (repositorio aparte, D-03)

NX-REQ-01 (token de servicio), NX-REQ-02 (host de servicio), NX-REQ-04 (agentes bloqueados) y NX-REQ-07 (red `pld-nexaro`) son necesarios para la topología T3 (PLD en Docker). Se hacen en una rama del repositorio de NEXARO con sus propias pruebas (`tests/test_security.py`) y su documentación en `SECURITY/`. **Esta rama no los toca.**

## Pruebas

### Backend (pytest, NEXARO simulado con `httpx.MockTransport`; nada sale a la red)

| Caso | Archivo | Fase |
|---|---|---|
| 401 sin sesión en cada `/ai/*` | `test_ai_security.py` | 1-3 |
| `NEXARO_ENABLED=false` → `health.ai=false`, `/ai/status` sin llamadas y `/ai/chat` 404 | `test_ai_status.py` | 1 |
| Configuración: URL con credenciales, path, esquema raro o host fuera de la allowlist → error al arrancar. Host no local sin token → error | `test_ai_config.py` | 1 |
| No sigue redirects (301 hacia otro host → 503) | `test_nexaro_client.py` | 1 |
| Timeout, conexión rechazada, 5xx, 429, NDJSON mal formado, línea `{"error"}` con 200, stream vacío → 503/429 con un mensaje genérico | `test_nexaro_client.py` | 1-2 |
| Respuesta que supera `NEXARO_MAX_RESPONSE_BYTES` → cortada | `test_nexaro_client.py` | 1 |
| `lesson_slug` inexistente → 404. `course` ≠ `python` → 422 | `test_ai_chat.py` | 2 |
| Campos prohibidos (`user_id`, `model`, `agent_id`, `system`, `temperature`, `role: system` en `history`) → 422 | `test_ai_security.py` | 2 |
| Tamaños: pregunta, código, error e historial por encima del límite → 422. Cuerpo > `MAX_BODY_BYTES` → 413 | `test_ai_security.py` | 2 |
| El contexto enviado a NEXARO sale de la BD, no del cliente. Sin email, nombre ni id del usuario. Código solo si se envía | `test_ai_chat.py` | 2 |
| «Defang» de delimitadores en el código y la pregunta | `test_ai_context.py` | 2 |
| Rate limit por usuario (el 11.º → 429 + evento `ai.rate_limited`). Otro usuario no se ve afectado | `test_ai_chat.py` | 2 |
| Semáforo global: con `AI_MAX_CONCURRENCY` ocupado → 429 inmediato | `test_ai_chat.py` | 2 |
| Token de servicio presente en la cabecera saliente y **ausente** de `caplog`, de las respuestas y de `/ai/status` | `test_ai_security.py` | 1-2 |
| Las rutas IA no cambian `lesson_progress`, `exercise_attempts`, `course_states` ni `pcap_states` (recuento de filas antes y después, aunque el modelo diga «ejercicio aprobado») | `test_ai_security.py` | 2-3 |
| `tool_calls` o `thinking` en el stream → se ignoran y no llegan al navegador | `test_nexaro_client.py` | 2 |
| `review-code`: código con `import os; os.system(...)` → ni PLD ni el mock lo ejecutan (solo texto) | `test_ai_review.py` | 3 |
| Cabeceras de seguridad y `no-store` en `/ai/*` | `test_security_headers.py` (ampliar) | 1 |
| Cobertura 100 % de los módulos nuevos | `--cov-fail-under=100` | todas |

### Frontend

| Caso | Archivo | Fase |
|---|---|---|
| Sin API o con `health.ai=false` → no aparece el tutor IA. FAQ y pista estática igual que antes | `e2e/ai-tutor.spec.js` | 4 |
| `/ai/status` no disponible → mensaje y Reintentar. Error de red manejado | `e2e/ai-tutor.spec.js` | 4 |
| La respuesta simulada con `<img onerror>` o `<script>` se pinta escapada | `e2e/ai-tutor.spec.js` | 4 |
| La casilla del código empieza desmarcada. Sin marcarla, el cuerpo no lleva `code` | `e2e/ai-tutor.spec.js` | 4 |
| Nada en `localStorage`/`sessionStorage`/IndexedDB con el token de servicio ni URLs de NEXARO | `e2e/ai-tutor.spec.js` | 4 |
| Uso con teclado (Tab, Escape, foco al cerrar) y axe WCAG 2.2 AA en tema claro y oscuro, móvil y escritorio | `e2e/ai-tutor.spec.js` | 4 |
| Sin conexión: con el SW activo y sin red, la lección y Pyodide funcionan y el tutor IA aparece desactivado | `e2e/study.spec.js -g PWA` (ampliar) | 4 |
| Lógica del tutor (cuerpos, límites, historial, pistas, mensajes de error) | `tests/unit/ai-logic.test.mjs` | 4 |

### Comandos de `docs/TESTING.md` que hay que ejecutar en cada fase

- Siempre que se cambie el backend: `cd backend && ruff check . ../e2e ../scripts && ruff format --check . ../e2e ../scripts` y `cd backend && python -m pytest -q --cov=app --cov-fail-under=100`.
- Fase 4: `npm run test:unit`, `npm run test:e2e`, `node scripts/web/build_precache.mjs` + `--check`, `npx playwright test e2e/study.spec.js -g PWA` y `npx playwright test e2e/idiomas.spec.js` (i18n).
- Antes de proponer un PR: `pip-audit -r backend/requirements.txt`, `npm audit --audit-level=high` y la comprobación de despliegue (`production_csp.py`, `verify_pages_artifact.py`, `frontend_static.mjs`). La CSP de la web **no debe cambiar**.

Ninguna de estas pruebas se ha ejecutado en la Fase 0: aquí no hay código.

## Criterios de aceptación (del kit, adaptados)

- PLD funciona igual con NEXARO apagado o desactivado (la opción por defecto).
- Login y sesión sin cambios. El navegador no conoce ni el token ni la URL de NEXARO.
- NEXARO no queda abierto a Internet ni a redes Docker sin token. PLD no se une a la red de Ollama.
- Un usuario solo consulta con su sesión y sobre lecciones que existen. No se acepta `user_id` del cliente.
- Ningún servidor ejecuta código del alumno. La IA no cambia progreso ni resultados oficiales.
- Todo endpoint tiene esquemas, límites y pruebas. Documentación de despliegue local actualizada. La producción queda desactivada hasta D-02.
