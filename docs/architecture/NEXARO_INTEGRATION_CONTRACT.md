# Contrato de integración NEXARO AI ↔ PLD

Estado: **integración PLD implementada en backend y frontend; contrato interno con NEXARO sujeto a las limitaciones descritas en §3.4**. Este documento contiene decisiones de arquitectura y pendientes del lado NEXARO; no debe leerse como si las rutas de PLD estuvieran pendientes.

La implementación actual está en `backend/app/routers/ai.py`, `backend/app/ai_context.py`, `backend/app/nexaro_client.py` y `frontend/js/ai/`. Guía de uso/configuración: [`docs/TUTOR-IA.md`](../TUTOR-IA.md).

El contrato tiene dos capas:

1. **Pública (navegador → PLD):** `/api/v1/ai/*`. La define y la controla PLD.
2. **Interna (PLD → NEXARO):** la API **real** de NEXARO v3 (§3) más los cambios que necesita NEXARO (§4), marcados como **PENDIENTE** mientras no existan.

## 1. Principios

- El navegador solo habla con PLD. Nunca conoce la URL de NEXARO, el token, el modelo, el agente ni el system prompt.
- El usuario sale siempre de `CurrentUser`. El cuerpo no acepta `user_id`, roles, permisos, `model`, `agent_id`, `system`, `temperature` ni credenciales. Con `extra="forbid"`, enviarlos da **422**.
- PLD construye el contexto con datos propios (lección de la BD). El cliente solo aporta la pregunta y, si quiere, su código o error.
- La salida de la IA es **texto no confiable**, siempre etiquetado como generado por IA. **Ninguna** ruta `/ai/*` escribe progreso, intentos, XP, mastery ni entitlements.
- Si NEXARO falla o está desactivado, PLD sigue igual y la IA se oculta.

## 2. Capa pública: PLD `/api/v1/ai/*`

Todas las rutas exigen sesión (`CurrentUser`: cookie `__Host-pld_session` con `X-PLD-Session: cookie`, o `Authorization: Bearer`). Todas llevan las cabeceras de seguridad de la API y `Cache-Control: no-store`.

### 2.1 `GET /api/v1/ai/status`

Respuesta `200`:

```json
{ "enabled": true, "available": true, "modes": ["chat", "hint", "explain-error", "review-code"] }
```

- `enabled`: `NEXARO_ENABLED` y configuración válida. Si es `false`, `available` es `false` y PLD no llama a NEXARO.
- `available`: NEXARO responde a `/api/health` con `status: ok` y `NEXARO_MODEL` está instalado (resultado en caché de 30 s; timeout de 5 s).
- **No** incluye URL, versión de NEXARO, nombre del modelo ni agentes.
- `401` sin sesión.

Además, `GET /api/v1/health` añade `"ai": <enabled>` (sin red), para que la web decida si muestra el punto de entrada.

### 2.2 Cuerpo común (`AiRequest`, `extra="forbid"`)

| Campo | Tipo | Límite | Notas |
|---|---|---|---|
| `course` | `Literal["python"]` | — | v1 solo Python (D-05). |
| `lesson_slug` | `str` | 1-50, patrón de slug | Se valida con `get_lesson_or_404` (404). |
| `question` | `str` | 1-2 000 (`AI_MAX_QUESTION_CHARS`) | Obligatorio en `chat` y `hint`. |
| `code` | `str` | 0-8 000 (`AI_MAX_CODE_CHARS`) | Solo si el alumno lo marca. Obligatorio en `review-code`. |
| `error` | `str` | 0-4 000 | Obligatorio en `explain-error`. |
| `history` | `list[{role: "user"\|"assistant", content ≤ 2 000}]` | ≤ 6 elementos | Solo `chat`. PLD no lo guarda. |
| `hint_level` | `int` | 1-3 | Solo `hint`: pistas graduadas. |
| `locale` | `Literal["es", "en"]` | — | Por defecto `es`. |

El campo `exercise_id` del ejemplo del kit **no existe** en PLD: el ejercicio es el de la lección (`Lesson.exercise`), identificado por `lesson_slug`.

### 2.3 Rutas de generación

| Ruta | Modo | Requisitos del cuerpo | Fase |
|---|---|---|---|
| `POST /api/v1/ai/chat` | Tutor conversacional sobre la lección | `question`, `history?`, `code?` | 2 |
| `POST /api/v1/ai/hint` | Pista graduada del ejercicio, sin solución completa | `question`, `hint_level`, `code?` | 2 |
| `POST /api/v1/ai/explain-error` | Explica un error de Python | `error`, `code?` | 3 |
| `POST /api/v1/ai/review-code` | Revisión estática (sin ejecutar) | `code` | 3 |

Respuesta `200` (`AiAnswer`):

```json
{
  "answer": "Markdown (≤ AI_MAX_ANSWER_CHARS = 6000)",
  "mode": "hint",
  "ai_generated": true,
  "official_evaluation": false,
  "request_id": "uuid4"
}
```

Sin `model`, sin system prompt, sin razonamiento interno (si un modelo devuelve `thinking`, se descarta). `request_id` es un UUID aleatorio que PLD solo registra en sus logs de seguridad.

### 2.4 Errores (mensajes en español, sin detalles internos)

| Estado | Cuándo |
|---|---|
| 401 | Sin sesión o con la sesión caducada (comportamiento actual de `CurrentUser`) |
| 404 | `lesson_slug` inexistente, o IA desactivada (`NEXARO_ENABLED=false`) |
| 413 | Cuerpo > `MAX_BODY_BYTES` (middleware actual) |
| 422 | Validación: campos de más, tamaños o modo sin su campo obligatorio |
| 429 | `ai_limiter` por usuario o semáforo global de PLD ocupado. También si NEXARO responde 429. Mensaje: «El tutor está ocupado…» |
| 503 | NEXARO caído, timeout, 5xx, NDJSON mal formado, línea `{"error"}` dentro del stream, respuesta vacía o modelo no instalado. Mensaje: «El tutor no responde ahora mismo». |

## 3. Capa interna: API real de NEXARO v3 (lo que existe hoy)

### 3.1 `GET /api/health`

`200 {status: "ok"|"degraded", ollama: "connected"|"unreachable", database: "ok"|"error", version}`. Sin autenticación. PLD solo usa `status`.

### 3.2 `GET /api/models`

Lista de modelos instalados. PLD la usa en `/ai/status` para comprobar `NEXARO_MODEL` (D-08).

### 3.3 `POST /api/chat`

Petición que construye PLD:

```json
{
  "model": "<NEXARO_MODEL>",
  "agent_id": "<NEXARO_AGENT_TUTOR | _REVIEW>",
  "messages": [
    {"role": "user", "content": "…historial…"},
    {"role": "assistant", "content": "…"},
    {"role": "user", "content": "<contexto PLD + pregunta>"}
  ]
}
```

- `temperature` y `num_ctx` no se envían: los impone el agente en el servidor.
- `project_id` no se usa.
- Los roles permitidos son solo `user` y `assistant`. Las instrucciones de cada modo (pista, error, revisión) **no pueden** ir como `system`. Hoy van al principio del mensaje `user`, que es más débil (R-04 y R-08). Por eso existe NX-REQ-04.
- Cabeceras que envía PLD: `Content-Type: application/json`, `Content-Length` (lo pone httpx) y, en el futuro, `Authorization`. **Nunca** `Origin` ni `Cookie`.

Respuesta: `200 application/x-ndjson`. PLD lee línea a línea:

- `{"message": {"content": "…"}, "done": false}` → concatena `content`.
- `{"done": true, …}` → fin.
- `{"error": "…"}` → **fallo** (503 hacia el navegador; el texto de NEXARO no se reenvía).
- Una línea que no es JSON → fallo.
- Al superar `AI_MAX_ANSWER_CHARS` o `NEXARO_MAX_RESPONSE_BYTES`, corta, cierra el stream y devuelve lo acumulado con `…`.

Errores antes del stream: `400` (modelo no instalado), `404` (agente borrado), `422`, `429` (más de 2 streams o 120 escrituras/min por IP), `403` (Origin o Sec-Fetch-Site), `400 Host no permitido`, `413`, `415`.

### 3.4 Lo que **no** existe en NEXARO (pendiente; PLD ya lo adapta)

| Elemento | Estado |
|---|---|
| Autenticación de servicio (token, mTLS) | **PENDIENTE** (NX-REQ-01) |
| Host de servicio sin `NEXARO_ACCEPT_NETWORK_RISK` | **PENDIENTE** (NX-REQ-02) |
| Endpoints de tutor, pista, explicación de errores o revisión de código | **No existen.** PLD los implementa sobre `/api/chat` con un agente y una plantilla. No se piden a NEXARO. |
| Respuesta sin streaming | No existe. PLD agrega el NDJSON. Opcional: NX-REQ-03. |
| Agentes de solo lectura para PLD | **PENDIENTE** (NX-REQ-04) |
| Límites por servicio (no por IP) | **PENDIENTE** (NX-REQ-05) |
| Salida JSON estructurada (`format`) | Prohibida por `ai_policy`. Opcional: NX-REQ-06. |
| Versión en las rutas (`/api/v1`) | No existe. PLD fija la versión que espera con `/api/health.version` (aviso en el log si no coincide). |

## 4. Cambios necesarios en NEXARO (otra rama, en el repositorio de NEXARO)

| Id | Cambio | Detalle mínimo | Prueba en NEXARO |
|---|---|---|---|
| **NX-REQ-01** | Token de servicio | `NEXARO_SERVICE_TOKENS_SHA256` (lista de hashes, rotación con dos vigentes). `Authorization: Bearer` comparado con `hmac.compare_digest` sobre el SHA-256. Se aplica a `/api/chat`, `/api/health` y `/api/models` cuando la petición llega por un host de servicio. El resto de rutas (CRUD de agentes, modelos, pulls, learning) queda **denegado** para el token de servicio (403). | 401 sin token o con uno erróneo. 403 en CRUD con token de servicio. El token nunca aparece en el log de auditoría. |
| **NX-REQ-02** | Host de servicio | `NEXARO_SERVICE_HOSTS` (p. ej., `nexaro-ai`), separado de `NEXARO_ALLOWED_HOSTS`. `check_network_exposure` lo acepta **solo si** hay al menos un token configurado. Sin token, sigue el `RuntimeError`. | Arranque con un host de servicio sin token → error. Con token → arranca. `Host: nexaro-ai` sin Bearer → 401. |
| NX-REQ-03 | `stream: false` opcional | `ChatRequest.stream: bool = True`. Con `false`, devuelve `{message:{content}, done:true}` o el error con su estado HTTP. | Error de Ollama → 502 con JSON, no 200. |
| **NX-REQ-04** | Agentes PLD de solo lectura | Sembrar `pld-tutor` y `pld-review` con `locked=1`. `PUT/DELETE` → 409 si está bloqueado. Contienen las reglas pedagógicas (no dar la solución sin un intento previo, pistas graduadas, no evaluar). | `PUT/DELETE` sobre un agente bloqueado → 409. El seed es idempotente. |
| NX-REQ-05 | Límites por cliente de servicio | Rate limit y `max_chat_streams` por token de servicio (clave = id del token, no la IP). Estado en memoria, que basta con un solo proceso. | Un token agotado no afecta a la UI local. |
| NX-REQ-06 | (Opcional) `format: "json"` solo para el agente `pld-review` | Lista blanca por agente en `ai_policy`. | `format` sigue prohibido para el cliente. |
| NX-REQ-07 | Compose | Red externa `pld-nexaro` (`internal: true`) además de las actuales. Sin puertos nuevos en el host. | `docker inspect`: `ollama` no está en `pld-nexaro`. |

Mientras NX-REQ-01 y 02 no estén fusionados en NEXARO, **solo** se admite la topología T1 (PLD nativo → `http://127.0.0.1:8080`). PLD envía el Bearer en cuanto `NEXARO_SERVICE_TOKEN` tenga valor. Hoy NEXARO ignora la cabecera.

## 5. Configuración de PLD (solo los nombres)

| Variable | Por defecto | Validación al arrancar |
|---|---|---|
| `NEXARO_ENABLED` | `false` | Si es `true`, `NEXARO_BASE_URL` y `NEXARO_MODEL` son obligatorias. |
| `NEXARO_BASE_URL` | — | Esquema `http` o `https`, sin credenciales, sin path, sin query. Host incluido en `NEXARO_ALLOWED_HOSTS`. `https` obligatorio si el host no es de loopback ni un nombre de servicio Docker de la allowlist. |
| `NEXARO_ALLOWED_HOSTS` | `127.0.0.1,localhost,nexaro-ai` | Allowlist anti-SSRF. |
| `NEXARO_SERVICE_TOKEN` | — (`SecretStr`) | Obligatorio si el host no es de loopback. Sin valor por defecto. Mínimo 32 caracteres. |
| `NEXARO_MODEL` | — | Nombre validado con el mismo patrón que usa NEXARO. |
| `NEXARO_AGENT_TUTOR` / `NEXARO_AGENT_REVIEW` | `tutor-programacion` / `programador` (hoy) → `pld-tutor` / `pld-review` (cuando exista NX-REQ-04) | Patrón `^[a-zA-Z0-9_-]{1,64}$`. |
| `NEXARO_TIMEOUT_SECONDS` | `120` | Total por petición (1-300). |
| `NEXARO_MAX_RESPONSE_BYTES` | `262144` | — |
| `AI_RATE_LIMIT_PER_MINUTE` | `10` | Por usuario. |
| `AI_MAX_CONCURRENCY` | `2` | Plazas de PLD hacia NEXARO (≤ `NEXARO_MAX_CHAT_STREAMS`); sin plaza, 429 al momento. |
| `NEXARO_AGENT_TUTOR` | `tutor-programacion` | Patrón de id de NEXARO. Chat, pistas y errores. |
| `NEXARO_AGENT_REVIEW` | `programador` | Patrón de id de NEXARO. Revisión de código. |

Implementado en la Fase 2: los tamaños (pregunta 2 000, código 8 000, turno 2 000, respuesta 6 000, enunciado 1 500, teoría 3 000) son constantes en `schemas.py` y `ai_context.py`, no variables de entorno.

Fase 3: `error` llega ya recortado por el runner de Pyodide (`frontend/py/runner.py` quita las líneas internas del traceback), así que el servidor solo limita su tamaño y lo trata como texto no confiable. `review-code` devuelve Markdown con tres apartados que pide la instrucción. No se valida su estructura porque NEXARO no permite `format` (NX-REQ-06).

El único evento nuevo es `ai.rate_limited` (T1499.003); los fallos de NEXARO van al log `pld.ai` con `request_id`, sin contenido, porque no son una técnica de ataque.

Cliente HTTP: un único `httpx.AsyncClient` creado en `lifespan` y cerrado al salir, con `follow_redirects=False`, `trust_env=False` (ignora los proxies del entorno), `Timeout(connect=5, read=NEXARO_TIMEOUT_SECONDS, write=10, pool=5)` y un contador de respuestas en curso (`AI_MAX_CONCURRENCY`). Solo se registran el estado y la duración: nunca el cuerpo, las cabeceras ni el token.

## 6. Plantilla del mensaje (PLD → NEXARO)

```text
[Modo: pista nivel 2 · Idioma: es]
Instrucciones del modo: <texto fijo de PLD para el modo>
Lección: <Lesson.title>
<ejercicio>
<Lesson.exercise truncado, con defang>
</ejercicio>
<codigo_del_alumno>          (solo si se ha enviado)
<code truncado, con defang>
</codigo_del_alumno>
Pregunta del alumno: <question>
```

El «defang» neutraliza `<ejercicio` y `<codigo_del_alumno` dentro del texto del alumno (técnica de `feature/nexaro-local-ai-connection`). **No es un control de seguridad**: el control real es que la salida no puede ejecutar nada (sin herramientas) ni escribir progreso.
