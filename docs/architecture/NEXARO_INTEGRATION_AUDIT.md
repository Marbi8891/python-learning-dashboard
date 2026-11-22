# Auditoría de integración NEXARO AI ↔ Python Learning Dashboard (Fase 0)

- **Fecha:** 21/11/2026
- **Tipo:** solo lectura. No se ha cambiado código, no se ha ejecutado ninguna prueba ni se ha hecho ninguna llamada a NEXARO, Ollama o Render.
- **PLD auditado:** `main` en `78080ca` (Merge PR #178). La rama de trabajo `fix/ciberseguridad-progreso` no se ha tocado.
- **NEXARO auditado:** `Downloads\NEXARO-AI-Frontend\NEXARO-AI-Frontend`, rama `main` en `5af114e` (NEXARO AI 3.0.0). No se ha modificado.
- **Fuera de alcance:** `C:\Users\pc\nexaro-ai` (otra construcción de NEXARO, con contenedores `nexaro-backend-1`, `nexaro-caddy-1` y `nexaro-ollama-1`) y «NEXARO Personal AI» (puerto 8001; ver §4).
- **Secretos:** no se ha leído `.env` ni `backend/.local-secret`. Las variables aparecen solo por su nombre.

Documentos relacionados: [`NEXARO_INTEGRATION_CONTRACT.md`](NEXARO_INTEGRATION_CONTRACT.md) (contrato) y [`NEXARO_INTEGRATION_PLAN.md`](NEXARO_INTEGRATION_PLAN.md) (fases y pruebas).

## 1. Resumen

1. **La integración es viable, pero NEXARO v3 todavía no está preparado para que lo llame otro servidor.** No tiene autenticación de servicio. Su middleware rechaza cualquier `Host` que no sea de loopback, y al arrancar se niega a aceptar hosts de red salvo con `NEXARO_ACCEPT_NETWORK_RISK=1`. Solo existe `POST /api/chat`, con streaming NDJSON. No hay endpoints de tutor, pista, explicación de errores ni revisión de código.
2. **Hoy solo funciona una topología sin tocar NEXARO:** el backend de PLD corriendo directamente en el mismo equipo (fuera de Docker) y llamando a `http://127.0.0.1:8080`. Ninguna otra (PLD en Docker, Render) funciona sin cambios en NEXARO o sin debilitar sus controles.
3. **En producción, NEXARO no es alcanzable.** La API de PLD está en Render (Frankfurt) y NEXARO corre en el PC del autor, sin TLS, sin autenticación y solo en loopback. Llevarlo a producción exige decidir antes dónde se aloja la inferencia.
4. **Ya hay trabajo previo sin fusionar.** `feature/nexaro-local-ai-connection` (19/11/2026) tiene un router `/api/v1/tutor` completo y probado, pero apunta a otro producto, «NEXARO Personal AI», con API keys y `POST /api/v1/chat`. No sirve tal cual para NEXARO v3. Ver §4.
5. **PLD tiene todo lo necesario** para alojar el módulo sin rehacer nada: `CurrentUser`, `RateLimiter`, `security_events`, `BodySizeLimit`, `httpx` ya instalado, cabeceras de seguridad, cliente `request()` en `api.js` y un panel de asistente accesible (`assistant.js`).

## 2. Estado de PLD (`main`)

### 2.1 Backend

| Pieza | Estado real | Relevancia para la IA |
|---|---|---|
| `backend/app/main.py` | FastAPI con `lifespan` (exige `JWT_SECRET`). CORS con credenciales y solo `cors_origins`. Cabeceras de seguridad en `/api/*`, incluida `Cache-Control: no-store`. `BodySizeLimit` cuenta los bytes reales (máximo 300 000). Nueve routers bajo `/api/v1`. `/api/v1/health` devuelve `status`, `email` y `google`. | El router `ai` se registra en la misma tupla. `health` puede añadir `ai: bool` sin revelar ninguna URL. |
| `config.py` | `pydantic-settings`, `.env` y `extra="ignore"`. Usa el patrón de un secreto sin valor por defecto (`jwt_secret: str \| None`). | Aquí van `NEXARO_*`, con `SecretStr` para el token. |
| `deps.py` | `CurrentUser`: Bearer o cookie `__Host-pld_session`, esta solo con `X-PLD-Session: cookie` (CSRF). Revisa `token_version` y renueva la sesión. `WritingUser` = `CurrentUser` + `write_limiter` (120/min). `get_lesson_or_404(db, slug)`. | Las rutas de IA usan `CurrentUser` y un limitador propio (no `WritingUser`, que es para progreso). El contexto se saca de la lección con `get_lesson_or_404`. |
| `database.py` | Motor SQLAlchemy síncrono: SQLite en local, PostgreSQL (Neon) con `pool_pre_ping` en producción. Rutas síncronas. | Una llamada lenta a NEXARO dentro de una ruta `def` ocupa un hilo del pool de AnyIO (40 por defecto). Hay que acotar la concurrencia (ver R-07). |
| `models.py` | `Lesson` (slug, title, theory, exercise, starter, checks, `assistant` JSON con FAQ, quiz, challenge), `User`, `LessonProgress`, `ExerciseAttempt` (código del alumno), `Entitlement`… | **En la BD solo hay lecciones del curso de Python** (`lessons.json`). Los cursos de DAW, Ciberseguridad, Excel y Career existen solo como JSON del frontend y documentos `course_states`. |
| `rate_limit.py` | `RateLimiter` en memoria (por instancia) y `SharedRateLimiter` en BD (autenticación). `client_ip()` respeta `TRUSTED_PROXY_HOPS`. | Se añade `ai_limiter` por usuario. En memoria basta mientras haya una sola instancia (Render free). |
| `security_events.py` | `Event` → técnica ATT&CK y JSON en `pld.security`, con IP seudonimizada mediante HMAC. | Nuevos eventos: `ai.rate_limited`, `ai.upstream_error`, `ai.payload_rejected`. Sin contenido del alumno. |
| `entitlements.py` | `require_entitlement(feature_key)`, concedido solo en el servidor. | Opción de limitar la IA a un plan (decisión D-06). |
| `requirements.txt` | Ya incluye `httpx>=0.27,<1.0`. | No hace falta ninguna dependencia nueva. |

### 2.2 Frontend

- `frontend/js/api.js` centraliza `request(method, path, {json, signal…})`. Usa la cookie HttpOnly y el token solo en memoria, con un tiempo de espera de 90 s (`apiTimeoutMs`), y gestiona el 401 con `pld:session-expired`. `serverInfo` lee `/api/v1/health` al cargar.
- `frontend/js/assistant.js` es el panel del asistente de cada lección, con FAQ preparadas y una pista estática. **No es una IA.** Tiene botón, `aria-expanded`, Escape y foco. Es el punto natural para añadir «Preguntar al tutor IA».
- `frontend/js/markdown.js` es un renderizador seguro que ya se usa con texto no confiable y sirve para las respuestas del modelo.
- La CSP de `index.html` tiene `connect-src 'self' https://pld-api.onrender.com … http://127.0.0.1:8000 http://localhost:8000`. El navegador **no** necesita llegar a NEXARO, así que la CSP no cambia. `scripts/security/production_csp.py` y `test_production_csp.py` impiden publicar orígenes `http:`.
- El service worker (`sw.js`) nunca guarda en caché `/api/`. Cada archivo JS nuevo exige regenerar `precache.js` (`node scripts/web/build_precache.mjs`).
- Python del alumno: Pyodide en un Web Worker que bloquea la red. La integración **no lo toca**.

### 2.3 Despliegue y pruebas

- **Producción:** frontend en GitHub Pages y API en Render (`render.yaml`, Docker, Frankfurt, plan gratuito, se suspende tras 15 minutos), con PostgreSQL en Neon (UE). Hacer merge a `main` publica la web.
- **Local con Docker:** `docker-compose.yml` levanta `db` (postgres:16), `api` (puerto `8000:8000` en todas las interfaces del host) y `web` (puerto 5500). Usa la red por defecto del proyecto y no tiene ningún servicio NEXARO.
- **Local nativo:** `Iniciar-Dashboard.bat` y `serve_frontend` (la API sirve también la web).
- **Pruebas:** `pytest --cov=app --cov-fail-under=100` (100 % de cobertura obligatoria), ruff, `npm run test:unit`, Playwright e2e con axe (WCAG 2.2 AA), comprobación del precache y comprobación de despliegue. `test_privacy_policy.py` exige que `privacidad.html` describa el sistema real.

## 3. Estado de NEXARO AI v3

| Aspecto | Estado real (código) |
|---|---|
| Entrypoint | `app.py` con `create_app()`. FastAPI sin `/docs`, sin CORS y con el frontend estático en el mismo origen. |
| Chat | `POST /api/chat` con `ChatRequest {model (1-120, nombre validado), messages[1..200] de {role: user\|assistant, content ≤ 100 000}, temperature 0-2, num_ctx 512-32768, agent_id?, project_id?}` y `extra="ignore"`. El modelo tiene que estar instalado (400 si no). |
| Respuesta del chat | **Siempre** `StreamingResponse` `application/x-ndjson` con HTTP 200. Cada línea es un evento de Ollama ya saneado (`message.content`, `done`…). **Los errores llegan dentro del flujo** como `{"error": "..."}` con estado 200. Los errores previos al stream sí usan estados HTTP: 429 (más de 2 streams), 400 (modelo), 404 (agente), 422 (validación). |
| Prompt de sistema | Solo lo construye el servidor, a partir de `agent.system_prompt` y `project.instructions` guardados en SQLite. El cliente **no puede** enviar `system`. |
| Agentes sembrados | `general`, `tutor-programacion`, `tutor-daw`, `programador`, `ciberseguridad`, `analista`… **Se pueden editar y borrar con `PUT/DELETE /api/agents/{id}` sin autenticación.** |
| Estado de conversación | Sin estado: el cliente envía el historial entero. NEXARO **no guarda** conversaciones (están en el `localStorage` de su propia web). |
| `GET /api/health` | `{status, ollama, database, version}`, con un ping a Ollama de 3 s. |
| `GET /api/models` | Modelos instalados. |
| Middleware | 1) `Host` en `NEXARO_ALLOWED_HOSTS` (por defecto `localhost,127.0.0.1,[::1]`). 2) En escrituras: rechaza `Sec-Fetch-Site` cross-site y un `Origin` distinto del `Host`; **una petición sin `Origin` ni `Sec-Fetch-Site` (server-to-server) pasa**. 3) Content-Length ≤ 4 MiB y JSON obligatorio. 4) 120 escrituras/min **por IP del cliente**. 5) Log de auditoría solo con metadatos. |
| Concurrencia | `max_chat_streams = 2` **global**, en memoria. |
| Arranque | `check_network_exposure`: si hay hosts no locales sin `NEXARO_ACCEPT_NETWORK_RISK=1`, lanza `RuntimeError`. |
| Autenticación | **Ninguna**: ni usuarios ni tokens de servicio. Es monousuario por diseño (`SECURITY_ARCHITECTURE.md`). |
| IA y herramientas | `ai_policy.py`: cuerpo cerrado hacia Ollama (sin `tools`, `format`, `keep_alive` ni `images`), `tool_calls` descartados y `authorize_tool` que lo deniega todo. `num_predict` ≤ 4096. **No se puede pedir salida JSON estructurada** (`format` está prohibido). |
| Timeouts hacia Ollama | Inactividad de 300 s durante el stream, conexión en 10 s. |
| Docker | `compose.yaml`: `nexaro-ai` en `127.0.0.1:8080`, solo lectura, `cap_drop ALL`, 512 MB, 1 CPU, redes `nexaro` (bridge) y `ollama-local_default` (externa). |
| Ollama | Stack aparte (`C:\Docker\ollama-local\compose.yaml`) **sin puertos publicados** en el host (corregido el 21/11/2026), con `OLLAMA_HOST=0.0.0.0:11434` dentro de la red. La red `ollama-local_default` **no es `internal`** y Ollama no tiene autenticación: cualquier contenedor unido a esa red habla con Ollama sin pasar por NEXARO. |

## 4. Trabajo previo en PLD (ramas sin fusionar)

| Rama | Qué hace | ¿Sirve para NEXARO v3? |
|---|---|---|
| `origin/feature/nexaro-local-ai-connection` (5 commits, 19/11/2026, **no fusionada**) | `backend/app/routers/tutor.py` (`GET /tutor/status`, `POST /tutor`), `NEXARO_URL` + `NEXARO_API_KEY` (`SecretStr`), `tutor_limiter` a 10/min, `Event.TUTOR_LIMITED`, HMAC de la conversación por usuario, «defang» de delimitadores, `test_tutor.py` (236 líneas), `e2e/tutor.spec.js`, `docs/TUTOR.md`, RAT-6 y `host.docker.internal` en Compose. | **No tal cual.** Llama a `POST /api/v1/chat` con `{message, conversation_id, mode: "tutor"}` y `Authorization: Bearer`, que es la API de **NEXARO Personal AI** (puerto 8001), no la de NEXARO v3. Sí se pueden reutilizar el diseño, los límites, los mensajes de error, la UI con estados y la estructura de las pruebas. |
| `origin/feat/tutor-ia` | Tutor sobre una API compatible con OpenAI (Groq por defecto) con `TUTOR_API_KEY`. | Otro proveedor externo. Choca con «solo herramientas gratuitas» si se depende de una capa gratuita de terceros y envía datos fuera. No se usa como base. |
| `origin/claude/tutor-hibrido-3s4dln`, `origin/feature/adaptive-python-tutor` | Tutor híbrido y adaptativo en el frontend, con A2A (`tutor.js`, `tutor-protocol.js`). | Ajeno a esta integración. Riesgo de conflictos en `assistant.js`, `widgets.css` e `index.html` si se fusionan después. |

`docs/DECISIONS.md` en `main` dice que **DEC-011 está reservado** por la rama `feature/tutor-nexaro` (que ya no aparece en el remoto) y que el tutor de la ruta profesional (D5) espera a que se fusione. En `feature/nexaro-local-ai-connection` la decisión se registra como DEC-022. Antes de escribir una DEC nueva hay que aclarar qué número usar (decisión D-01).

## 5. Red: quién llega a quién

`localhost` dentro de un contenedor es el propio contenedor. Opciones evaluadas:

| # | Topología | URL desde PLD | `Host` que ve NEXARO | ¿Funciona hoy sin cambiar NEXARO? | Valoración |
|---|---|---|---|---|---|
| T1 | PLD nativo (uvicorn en el host) → NEXARO publicado en `127.0.0.1:8080` | `http://127.0.0.1:8080` | `127.0.0.1:8080` (permitido) | **Sí**. Sin `Origin`, el control CSRF pasa. | Válida para desarrollo local. Cualquier proceso local ya podía llamar a NEXARO, así que no añade superficie. |
| T2 | PLD en Docker → `host.docker.internal:8080` | `http://host.docker.internal:8080` | `host.docker.internal:8080` → **400 «Host no permitido»** | No | Habría que añadir un host no local (arranque bloqueado) o forzar `Host: localhost` desde PLD, lo que desactiva el sentido del control anti-rebinding. Además, en Docker Desktop para Windows, que se llegue a un puerto publicado solo en `127.0.0.1` del host está **sin verificar**. Descartada. |
| T3 | PLD `api` y `nexaro-ai` en una **red Docker privada nueva** (`pld-nexaro`, `internal: true`) | `http://nexaro-ai:8080` | `nexaro-ai:8080` → 400 | No | **Es la recomendada**, una vez que NEXARO tenga autenticación de servicio y permita un host de servicio sin `ACCEPT_NETWORK_RISK` (ver el contrato, NX-REQ-01/02). PLD **no** se une a `ollama-local_default`. |
| T4 | PLD en Render → NEXARO en el PC del autor (túnel, IP pública) | — | — | No | Expone el PC del autor a Internet. **Descartada** sin un rediseño (D-02). |
| T5 | NEXARO alojado junto a PLD en la nube (mismo proveedor, red privada) | URL privada | host de servicio | No | Exige recursos para un LLM (CPU/RAM) que el plan gratuito de Render no ofrece. Pendiente de decisión (D-02). |

## 6. Diagrama de despliegue objetivo (local, T3)

```text
 Host Windows (Docker Desktop)
 ┌────────────────────────────────────────────────────────────────────────────┐
 │  Navegador ──► 127.0.0.1:5500 (web)        Navegador ──► 127.0.0.1:8080     │
 │       │                                       (UI propia de NEXARO, aparte)  │
 │       ▼ fetch credentials:include                                            │
 │  127.0.0.1:8000 ─┐                                                           │
 │                  ▼                                                           │
 │  ┌─────────── red pld_default ───────────┐                                   │
 │  │  web (http.server)   api (PLD FastAPI)│──┐                                │
 │  │                      db (postgres)    │  │                                │
 │  └───────────────────────────────────────┘  │                                │
 │                       red pld-nexaro (internal: true, nueva)                 │
 │                                             ▼                                │
 │                      ┌────────────── nexaro-ai (FastAPI) ─────────────┐      │
 │                      │  token de servicio · host de servicio permitido │      │
 │                      └──────────────────────┬─────────────────────────┘      │
 │                        red ollama-local_default (solo nexaro-ai y ollama)    │
 │                                             ▼                                │
 │                                     ollama:11434 (sin puerto en el host)     │
 └────────────────────────────────────────────────────────────────────────────┘
```

Reglas: el navegador nunca conoce `nexaro-ai` ni `ollama`. Ni PLD `api` ni `db` se unen a `ollama-local_default`. Solo `api` se une a `pld-nexaro`.

## 7. Flujo de datos de una petición

```text
1. Alumno pulsa «Pedir pista» en la lección <slug>.
2. assistant.js → request("POST", "/api/v1/ai/hint", {json:{lesson_slug, question, code?, locale}})
      cookie HttpOnly + X-PLD-Session (CSRF) · sin token de NEXARO · sin user_id
3. PLD: BodySizeLimit → CurrentUser (sesión) → ai_limiter(user.id) → Pydantic (límites)
4. PLD: get_lesson_or_404(slug) → contexto propio (título, enunciado truncado)
         + código del alumno solo si lo ha marcado, truncado y delimitado
5. PLD → NEXARO: POST {NEXARO_BASE_URL}/api/chat
         {model: NEXARO_MODEL, agent_id: <agente PLD>, messages:[{role:user, content: <contexto+pregunta>}]}
         Authorization: Bearer <NEXARO_SERVICE_TOKEN>   (cuando exista, NX-REQ-01)
         timeout, sin redirects, límite de bytes de la respuesta
6. NEXARO: middleware → agente (system prompt en el servidor) → ai_policy → Ollama (stream)
7. PLD lee el NDJSON, concatena message.content, corta al máximo de caracteres y detecta {"error"}
8. PLD → navegador: {answer, mode, request_id, ai_generated: true}  (sin modelo interno, sin prompt)
9. assistant.js lo pinta con markdown.js y la etiqueta «Generado por IA · no es la corrección oficial».
   Nada toca progreso, XP, mastery ni attempts.
```

## 8. Matriz de datos enviados a NEXARO

| Dato | ¿Se envía? | Origen | Límite | Motivo / control |
|---|---|---|---|---|
| Pregunta del alumno | Sí | Cuerpo de la petición | 2 000 caracteres | Imprescindible. Texto no confiable, siempre con rol `user`. |
| Código del alumno | Solo si lo marca (casilla desmarcada por defecto) | Cuerpo | 8 000 caracteres | Puede contener datos personales. Opt-in explícito. |
| Mensaje de error (explain-error) | Sí, en ese modo | Cuerpo (salida de Pyodide) | 4 000 caracteres | Se recortan las rutas del worker si aparecen. |
| Título y enunciado de la lección | Sí | BD de PLD (`Lesson`) | Enunciado ≤ 1 500 y teoría ≤ 3 000 | Contenido público del curso. El cliente no lo envía. |
| Historial del chat | Solo los últimos N turnos de la sesión del navegador | Cuerpo | N ≤ 6 y ≤ 2 000 caracteres por turno | NEXARO no tiene estado. PLD no lo persiste en v1 (Fase 5). |
| `user_id`, email, nombre, IP | **No** | — | — | Minimización. NEXARO no necesita la identidad. Para correlacionar solo se usa `request_id` (UUID aleatorio, sin vínculo con el usuario fuera de los logs de PLD). |
| Progreso, XP, mastery, entitlements | **No** | — | — | La IA no los necesita ni puede alterarlos. |
| Cookies o JWT de PLD | **No** | — | — | El cliente HTTP saliente no reenvía cabeceras del navegador. |
| Token de servicio de NEXARO | Solo PLD → NEXARO | Variable de entorno | — | Nunca va a los logs, a las respuestas ni al frontend. |

Retención: PLD **no guarda** el contenido en v1. NEXARO v3 no guarda conversaciones y su log de auditoría solo tiene método, ruta y estado. Ollama no persiste peticiones. Hay que confirmar que `NEXARO_LOG_LEVEL=DEBUG` no registra cuerpos (en el código revisado no lo hace).

## 9. Riesgos

| Id | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R-01 | NEXARO sin autenticación de servicio: si se abre a una red Docker, cualquier contenedor de esa red lo usa, incluidos sus CRUD de agentes y modelos. | Alta si se expone | Alto | NX-REQ-01 (token de servicio obligatorio si hay hosts no locales) y la red `pld-nexaro` `internal`. |
| R-02 | Se pide `NEXARO_ACCEPT_NETWORK_RISK=1` «para que funcione». | Media | Alto | Prohibido en esta integración. Se documenta como antipatrón. |
| R-03 | Se une PLD a `ollama-local_default` y habla directamente con Ollama sin autenticación. | Media | Alto | Regla explícita en la configuración. Prueba de Compose que verifica que `api` no está en esa red. |
| R-04 | El agente `tutor-programacion` se puede editar y borrar sin autenticación desde la UI de NEXARO, así que el comportamiento del tutor cambia sin que PLD lo sepa. | Media | Medio | NX-REQ-04: agentes `pld-*` de solo lectura sembrados por NEXARO, o `agent_id` configurable en PLD con comprobación al arrancar. |
| R-05 | Errores dentro del stream con HTTP 200: PLD podría mostrar `{"error":…}` como si fuera una respuesta. | Alta | Medio | El parser NDJSON de PLD trata cualquier línea con `error` como un fallo (503 manejado). Hay pruebas. |
| R-06 | Límites de NEXARO globales y por IP: todo PLD comparte 2 streams y 120 escrituras/min, y un alumno puede bloquear a los demás. | Alta | Medio | `ai_limiter` por usuario en PLD (p. ej., 10/min) + semáforo global ≤ 2 en PLD para fallar rápido con 429. NX-REQ-05 para límites por servicio. |
| R-07 | Rutas síncronas de PLD bloqueadas decenas de segundos (LLM en CPU) agotan los hilos de AnyIO y degradan todo PLD (login, progreso). | Media | Alto | Ruta `async` con `httpx.AsyncClient` compartido, o semáforo que limite las llamadas IA simultáneas. Timeout total ≤ `NEXARO_TIMEOUT_SECONDS`. |
| R-08 | Inyección de prompt mediante el código o la pregunta del alumno. | Alta | Bajo (solo texto, sin herramientas) | Rol `user`, delimitadores con «defang», ninguna acción derivada de la salida y la etiqueta «IA · no oficial». |
| R-09 | El modelo da la solución completa o «aprueba» un ejercicio. | Alta | Medio (pedagógico) | Instrucciones del agente, una respuesta de PLD que **nunca** toca progreso y el aviso en la UI. Se evalúa con un conjunto de casos fuera de la CI. |
| R-10 | XSS a través de la respuesta del modelo. | Media | Alto | `markdown.js` (escapa HTML), sin `innerHTML` de texto bruto, CSP de la web. Prueba e2e con una respuesta maliciosa simulada. |
| R-11 | Fuga del token de servicio a logs o respuestas. | Baja | Alto | `SecretStr`, nunca registrar cabeceras ni cuerpos, prueba que busca el token en `caplog` y en las respuestas. |
| R-12 | SSRF por configuración (`NEXARO_BASE_URL` apuntando a metadatos de la nube o a la red interna). | Baja | Medio | Solo `http(s)`, allowlist de hosts (`NEXARO_ALLOWED_HOSTS` en PLD), sin redirects y validación al arrancar. |
| R-13 | Privacidad: un tratamiento nuevo (pregunta y código enviados a un motor de IA) sin reflejarlo en `privacidad.html` ni en el RAT. | Alta | Medio (legal) | RAT nuevo, texto en `privacidad.html` y prueba en `test_privacy_policy.py`, antes de activarlo para nadie que no sea el autor. |
| R-14 | Producción: NEXARO no es alcanzable desde Render. | Cierta | Medio | `NEXARO_ENABLED=false` por defecto; la UI oculta la IA (`health.ai=false`). Decisión D-02. |
| R-15 | Conflictos con las ramas de tutor sin fusionar (`assistant.js`, `widgets.css`, `index.html`, `DECISIONS.md`, `CHANGELOG.md`). | Alta | Bajo | Decidir antes cuál se abandona o se reutiliza (D-01). |
| R-16 | Catálogo: el servidor solo valida lecciones de Python. DAW y Ciberseguridad no están en la BD. | Cierta | Bajo | v1 limitada a `course="python"`. Ampliarla después leyendo los JSON de `frontend/data/` en el servidor (D-05). |
| R-17 | Salida estructurada imposible: NEXARO prohíbe `format`, así que `review-code` no puede forzar JSON. | Cierta | Bajo | `review-code` devuelve Markdown validado (longitud, texto). O bien se intenta un JSON, se valida con Pydantic y, si falla, se usa el texto. NX-REQ-06 opcional. |

## 10. Inventario de archivos candidatos

### PLD (esta rama, a partir de la Fase 1)

| Archivo | Cambio | Fase |
|---|---|---|
| `backend/app/config.py` | `nexaro_enabled`, `nexaro_base_url`, `nexaro_service_token: SecretStr \| None`, `nexaro_timeout_seconds`, `nexaro_model`, `nexaro_agent_*`, `nexaro_allowed_hosts`, `ai_rate_limit_per_minute`, `ai_max_concurrency`, límites de tamaño | 1 |
| `backend/app/nexaro_client.py` (nuevo) | Cliente `httpx.AsyncClient`: timeouts, `follow_redirects=False`, límite de bytes, parser NDJSON, mapeo de errores y validación de URL | 1 |
| `backend/app/ai_context.py` (nuevo) | Construye el mensaje a partir de `Lesson`, con truncado y «defang» | 2 |
| `backend/app/routers/ai.py` (nuevo) | `GET /ai/status`, `POST /ai/chat`, `/ai/hint`, `/ai/explain-error`, `/ai/review-code` | 1-3 |
| `backend/app/schemas.py` | `AiRequest`, `AiAnswer`, `AiStatus` (o `schemas_ai.py`) | 2 |
| `backend/app/rate_limit.py` | `ai_limiter` | 2 |
| `backend/app/security_events.py` | `AI_RATE_LIMITED`, `AI_UPSTREAM_ERROR` | 2 |
| `backend/app/main.py` | Registrar el router, `health.ai`, cerrar el cliente en `lifespan` y validar la configuración al arrancar | 1 |
| `backend/tests/test_ai_*.py` (nuevos) | Ver el plan §4 | 1-3 |
| `frontend/js/ai/ai-api.js`, `frontend/js/ai/ai-panel.js` (nuevos) | Encima de `request()`. Panel dentro de `assistant.js` | 4 |
| `frontend/js/assistant.js`, `frontend/index.html`, `frontend/css/widgets.css`, `frontend/i18n/en.json` | Punto de entrada, estados y textos | 4 |
| `frontend/precache.js` | Regenerado con el script, nunca a mano | 4 |
| `e2e/ai-tutor.spec.js` (nuevo) | Con backend y NEXARO simulados, más axe | 4 |
| `frontend/privacidad.html`, `docs/REGISTRO_TRATAMIENTOS.md`, `backend/tests/test_privacy_policy.py` | Tratamiento nuevo | 2/4 |
| `docker-compose.yml` | Variables `NEXARO_*` vacías por defecto y red externa opcional `pld-nexaro` (perfil `ai`) | 1 |
| `docs/API.md`, `docs/DECISIONS.md`, `docs/TUTOR.md` (o un documento nuevo), `CHANGELOG.md` | Documentación | 1-4 |

### NEXARO (otro repositorio y otra rama; **no** los cambia esta rama)

`nexaro/config.py`, `nexaro/security.py`, `app.py`, `nexaro/seeds.py`, `nexaro/routers/agents.py`, `compose.yaml`, `tests/test_security.py` y `SECURITY/*.md`. Detalle en el contrato, §4.

## 11. Decisiones pendientes (para el autor)

| Id | Decisión | Opciones | Recomendación |
|---|---|---|---|
| D-01 | Qué hacer con `feature/nexaro-local-ai-connection` y la numeración DEC (DEC-011 reservado / DEC-022) | a) Abandonarla y reutilizar ideas · b) Rebasarla y adaptarla a v3 | a). Su contrato es el de otro producto. Se cita como antecedente. |
| D-02 | Dónde corre NEXARO fuera del PC del autor | a) Solo local por ahora · b) Servidor propio con TLS y token · c) Nunca en producción | a). La IA queda desactivada en Render hasta que haya una decisión. |
| D-03 | Cambios en NEXARO (NX-REQ-01…06) | Hacerlos en el repositorio NEXARO, en una rama propia y con sus pruebas | Requisito previo para T3. Sin ellos, solo T1 (PLD nativo). |
| D-04 | Primera topología que se implementa | T1 (nativo, sin tocar NEXARO) o esperar a T3 | T1 para Fases 1-2, con el código ya preparado para el token. |
| D-05 | Cursos cubiertos en v1 | Solo Python (BD) · también DAW y Ciberseguridad (JSON) | Solo Python. |
| D-06 | ¿La IA es Free o va con plan? | `require_entitlement("ai_tutor")` o abierta a cualquier cuenta | Abierta a cuentas con sesión mientras sea solo local. |
| D-07 | ¿Se persisten las conversaciones? | No (v1) · Sí (Fase 5, con RGPD) | No. |
| D-08 | Modelo | Nombre fijo en `NEXARO_MODEL` · descubrirlo con `/api/models` | Fijo. Si no está instalado, `/ai/status` dice que la IA no está disponible. |
