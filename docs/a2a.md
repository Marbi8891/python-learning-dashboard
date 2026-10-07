# A2A en el Python Learning Dashboard

Agent2Agent (**A2A**) es un protocolo abierto para que agentes de IA se describan y se hablen entre
sí. En este proyecto es **una capacidad más del backend**, junto a la API REST: la web, la app
Android y cualquier cliente A2A pueden pedir ayuda a agentes educativos sin que cambie nada de lo
que ya existe. La decisión está en [ADR-0034](adr/0034-agentes-a2a.md).

Versión del protocolo: **A2A 1.0**, con el SDK oficial [`a2a-sdk`](https://pypi.org/project/a2a-sdk/) 1.2.x.

## Arquitectura

```
                PYTHON LEARNING DASHBOARD

          Web (sin framework)        App Android
                    │                     │
                    └──────── FastAPI ────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
         API REST /api/v1/*                A2A /a2a/*
              │                                 │
              │                          Python Tutor (python-tutor)
              │                                 │
              └──────── servicios ──────────────┘
                 (app/services/learning_context.py)
                               │
              Base de datos: lecciones, progreso, intentos
```

Dentro de `backend/app/a2a/`:

| Carpeta / archivo | Qué hace |
|---|---|
| `cards/python_tutor.py` | La **Agent Card**: nombre, versión, URL, capacidades, skill e input/output |
| `agents/python_tutor.py` | La **lógica educativa**: valida la pregunta, adapta el nivel, explica errores, revisa el código **sin ejecutarlo** y prepara la respuesta. No sabe nada de A2A |
| `executors/python_tutor.py` | El **executor**: lee el mensaje A2A, pide el contexto del alumno, llama al agente y publica la tarea (enviada → en curso → artefacto → completada). Maneja errores y cancelaciones |
| `providers/` | El **modelo de lenguaje**: interfaz `AgentModelProvider`, `OllamaProvider` (local, predeterminado), `AnthropicProvider` (opcional, de pago) y `MockModelProvider` (tests) |
| `observability.py` | Una línea de log JSON por tarea (`pld.a2a`) |
| `server.py` | Registro de agentes (`AGENTS`), elección del proveedor, autenticación, límites, tareas por usuario y montaje de rutas |

## Python Tutor

Ayuda a aprender Python **como un tutor, no como un solucionador**:

1. explica el concepto o el error (`NameError`, `TypeError`, `IndentationError`…);
2. da pistas (la del ejercicio de la lección, si se indica);
3. señala lo que falla en el código, **leyéndolo, nunca ejecutándolo**;
4. propone un ejercicio adaptado al nivel si se le pide;
5. deja que el alumno lo intente.

Si el alumno pide la solución de un ejercicio que **aún no ha superado**, no se la da y le guía.
El nivel (inicial, intermedio, avanzado) sale de su progreso real o lo indica el alumno. El agente
**no inventa el progreso**: lo lee del servicio `load_learner_context` con el usuario de la sesión.

### Minimización de datos

El servidor lee del alumno solo: cuántas lecciones lleva completadas (para calcular el nivel) y,
si pregunta por una lección, su título, módulo, enunciado, pista y si la tiene superada.

Al **modelo** (Ollama local o, si se activa, Anthropic) solo le llega (`PythonTutorAgent._prompt`):

- las instrucciones del tutor (`SYSTEM_PROMPT`, iguales para todos);
- el nivel (`inicial`, `intermedio` o `avanzado`), no el progreso con el que se calcula;
- si eligió una lección: módulo, lección, enunciado y si el ejercicio está superado (sí/no);
- lo que el alumno ha escrito en esta consulta: pregunta, código y mensaje de error;
- la guía que ha preparado el propio agente (explicación del error, pista de la lección…).

Nunca el email, el nombre, el id de usuario, el historial, los intentos anteriores, otras
lecciones, otros cursos ni datos de otros usuarios. El usuario sale siempre de la sesión: un test
(`test_the_provider_only_receives_the_session_users_data`) comprueba con la API de Anthropic
simulada que lo que recibe el proveedor para un alumno no lleva nada de otro.

### Cómo responde el tutor

`SYSTEM_PROMPT` (en `agents/python_tutor.py`) fija este orden: 1) comprender el problema,
2) identificar el concepto que falla, 3) explicarlo, 4) dar una pista, 5) un ejemplo pequeño,
6) dejar que el alumno lo vuelva a intentar y 7) la solución completa solo cuando corresponde.
Respuestas cortas para preguntas sencillas, adaptadas al nivel, sin inventar resultados de
ejecución, y al analizar código separa **código analizado**, **comportamiento esperado**,
**comportamiento observado** (solo lo que diga el alumno o su error) e **hipótesis**.

## Production model provider

El agente está **desacoplado del proveedor**. El Python Tutor solo conoce esta interfaz
(`providers/base.py`):

```python
class AgentModelProvider(Protocol):
    name: str                 # «ollama», «anthropic», «mock»…
    model: str                # modelo concreto, para logs y metadatos
    unavailable_message: str  # lo que ve el alumno si el modelo no está disponible
    async def generate(self, request: ModelRequest) -> str: ...
```

```
A2A → Python Tutor Agent → AgentModelProvider → OllamaProvider      (por defecto: local y gratis)
                                              → MockModelProvider   (desarrollo y tests)
                                              → AnthropicProvider   (opcional, de pago)
                                              → OpenAIProvider      (futuro)
```

En esta fase **no se usa ninguna API de pago**: el proveedor por defecto es Ollama, y Anthropic
solo se usa si se elige expresamente (`A2A_MODEL_PROVIDER=anthropic` y `ANTHROPIC_API_KEY`).

### Comparativa de proveedores

| Proveedor | Coste de tokens | Internet | Privacidad | Uso |
|---|---:|---|---|---|
| Mock | 0 € | No | Máxima: no hay modelo | Tests |
| Ollama | 0 € (tu hardware) | No, una vez descargado el modelo | Alta: la consulta se procesa en tu equipo o servidor | Desarrollo y uso local |
| Anthropic | De pago | Sí | Depende de la configuración y del contrato con Anthropic | Opcional, futuro |
| OpenAI | De pago | Sí | Depende de la configuración | Futuro (no implementado) |

### Ollama (modelo local, predeterminado)

`providers/ollama_provider.py` llama a la API HTTP de Ollama (`POST /api/chat`, sin streaming) con
`httpx`, que ya instala el SDK de A2A: no añade dependencias.

- URL y modelo solo desde la configuración: `A2A_OLLAMA_BASE_URL` (por defecto
  `http://127.0.0.1:11434`) y `A2A_MODEL` (por defecto `qwen2.5-coder:7b`). La URL debe ser
  `http(s)://host:puerto`, sin usuario, ruta ni parámetros, o la API no arranca.
- Ninguna petición del alumno puede cambiar la URL, el host, el puerto ni el modelo: el mensaje
  solo admite `lesson_slug`, `code`, `error` y `level`, y cualquier otro campo se rechaza.
- Sin redirecciones y sin los proxies del entorno (sin SSRF). El navegador **nunca** habla con
  Ollama ni conoce su dirección: todo pasa por el backend.
- `num_predict` = `A2A_MAX_OUTPUT_TOKENS` y `num_ctx` = 8192, para que quepa el prompt más largo
  que admite el tutor. Si el modelo escribe su razonamiento entre `<think>` y `</think>`, se quita.
- Límite total por llamada `A2A_MODEL_TIMEOUT_SECONDS` (120 s por defecto; un modelo en CPU puede
  necesitar más). Sin reintentos.
- Si Ollama está apagado, tarda demasiado, no tiene el modelo o falla, la tarea acaba en
  `TASK_STATE_FAILED` con «El tutor local no está disponible ahora mismo…», sin detalles internos.
  El resto del dashboard sigue funcionando.
- Logs: proveedor, modelo, tokens (`prompt_eval_count`, `eval_count`), motivo de parada y
  duración; nunca el prompt ni la respuesta.

### Modelo recomendado

Este entorno no permite conocer tu hardware, así que hay dos opciones. Las dos son modelos
entrenados sobre todo con código (Python incluido), que explican y depuran bien y siguen
instrucciones en español. Las dos responden directamente, sin razonamiento visible largo, lo que
importa en CPU:

| Opción | Modelo | Descarga | Memoria aproximada | Cuándo |
|---|---|---|---|---|
| Ligera (por defecto) | `qwen2.5-coder:7b` | ~4,7 GB | 8 GB de RAM (mejor con GPU de 6–8 GB) | Portátil normal |
| Más calidad | `qwen2.5-coder:14b` | ~9 GB | 16 GB de RAM (mejor con GPU de 12 GB) | Equipo con más memoria |

Son cifras aproximadas: compruébalas en la ficha del modelo en ollama.com. Con menos de 8 GB,
prueba `qwen2.5-coder:3b`; responde peor, pero responde.

### Instalación y puesta en marcha

1. **Instala Ollama** en tu equipo desde [ollama.com/download](https://ollama.com/download)
   (Windows, macOS o Linux). Se queda escuchando en `http://127.0.0.1:11434`. No lo expongas a
   Internet: es un servicio interno.
2. **Descarga el modelo** (una vez; el backend nunca lo descarga solo):

   ```bash
   ollama pull qwen2.5-coder:7b
   ```

3. **Comprueba que responde:**

   ```bash
   curl http://127.0.0.1:11434/api/tags            # debe listar qwen2.5-coder:7b
   ollama run qwen2.5-coder:7b "¿Qué es una lista en Python?"
   ```

4. **Configura el backend** en `backend/.env` (además de `JWT_SECRET`):

   ```
   A2A_ENABLED=true
   A2A_MODEL_PROVIDER=ollama
   A2A_OLLAMA_BASE_URL=http://127.0.0.1:11434
   A2A_MODEL=qwen2.5-coder:7b
   ```

5. **Arranca el backend** (`uvicorn app.main:app --reload` desde `backend/`) y **el frontend**
   (`python -m http.server 5500` desde `frontend/`). En la web, **Tutor Python** responde con el
   modelo local.

6. **Valida de punta a punta** (5 consultas por la app real y revisión de los logs):

   ```bash
   python scripts/a2a/validate_tutor.py                 # o --model qwen2.5-coder:14b
   RUN_OLLAMA_INTEGRATION_TESTS=true python -m pytest backend/tests/test_a2a_ollama_integration.py -s
   ```

**Alternativa sin modelo:** `A2A_MOCK_MODEL=true` usa el modelo simulado (desarrollo y tests). No
necesita Ollama, red ni claves.

### Anthropic (opcional, de pago)

`providers/anthropic_provider.py` usa el **SDK oficial** [`anthropic`](https://pypi.org/project/anthropic/)
1.x y la Messages API. Está implementado y probado con la API simulada, pero **desactivado**: solo
se usa con `A2A_MODEL_PROVIDER=anthropic` y `ANTHROPIC_API_KEY`. La aplicación nunca hace una
llamada comercial por su cuenta.

- Modelo por defecto **`claude-opus-5-5`** (`A2A_MODEL`), con `output_config.effort = "medium"`
  fijado en el código. El modelo debe admitir `effort` (familia Claude 4.6 y posteriores).
- Con los modelos que lo admiten (Opus 5 / 5.5, Sonnet 5.5, Fable 5) se activa el **respaldo en
  el servidor** (`fallbacks: "default"`, beta `server-side-fallback-2026-07-01`): si los filtros
  de seguridad del modelo rechazan una consulta, la API la repite con el modelo que recomienda
  Anthropic en la misma llamada.
- `max_tokens` = `A2A_MAX_OUTPUT_TOKENS`; tiempo máximo por llamada `A2A_MODEL_TIMEOUT_SECONDS` y
  **un solo reintento**, con un límite total del doble.
- Destino fijo `https://api.anthropic.com`: ni la petición ni `ANTHROPIC_BASE_URL` lo cambian.
- No envía `metadata.user_id` ni ningún identificador del alumno.
- **La API key** sale solo de `ANTHROPIC_API_KEY` (entorno o gestor de secretos), como
  `SecretStr`. Nunca está en el código, los tests, los logs, la base de datos, la Agent Card ni
  las respuestas. Sin ella, con `anthropic`, **la API no arranca**.
- Antes de usarlo en producción: **límite de gasto en la Anthropic Console** y revisión legal de
  la política de privacidad (ver «Privacidad»).

### Modelo simulado

`MockModelProvider` (`A2A_MOCK_MODEL=true`) no llama a nada: devuelve la guía del agente marcada
como «Modo de desarrollo». Tiene prioridad sobre `A2A_MODEL_PROVIDER`, así que los tests nunca
necesitan Ollama, Internet ni claves. La Agent Card lo indica.

### Errores del proveedor

Cada proveedor traduce sus fallos a las excepciones de `providers/base.py`
(`ModelTimeoutError`, `ModelUnavailableError`, `ModelConfigurationError`, `ModelRequestError`,
`ModelRefusedError`, `EmptyModelResponseError`, `MalformedModelResponseError`…), sin la petición
ni la respuesta dentro. Si el modelo no está disponible, el alumno ve el `unavailable_message`
del proveedor; si falla otra cosa, un mensaje genérico. El log guarda solo el tipo de error.

### Cambiar de proveedor

1. Una clase en `providers/` con `name`, `model`, `unavailable_message` y
   `async generate(request) -> str`, que lance las excepciones de `providers/base.py`.
2. Un valor más en `A2A_MODEL_PROVIDER` (`config.py`) y su rama en `build_model_provider`
   (`server.py`); si necesita clave, como `SecretStr`.
3. Sus tests simulando la API, como `tests/test_a2a_ollama.py` o `tests/test_a2a_providers.py`.

Los agentes, el executor, la Agent Card y el frontend no cambian.

### Coste y límites

Todo con el `RateLimiter` en memoria que ya usa la API (sin Redis ni más infraestructura):

| Límite | Por defecto | Variable |
|---|---|---|
| Mensajes por usuario y minuto (cualquier llamada JSON-RPC) → 429 | 20 | `A2A_RATE_LIMIT_PER_MINUTE` |
| Consultas al modelo por usuario y día → tarea rechazada con explicación | 100 | `A2A_DAILY_LIMIT_PER_USER` |
| Consultas al modelo de todos los usuarios por minuto | 60 | `A2A_GLOBAL_LIMIT_PER_MINUTE` |
| Tokens de salida por respuesta | 4096 | `A2A_MAX_OUTPUT_TOKENS` |
| Entrada: pregunta / código / error | 4000 / 20 000 / 4000 caracteres | — |

Con Ollama estos límites protegen la CPU o GPU del servidor; con Anthropic, además, el gasto. Los
mensajes no válidos no gastan consultas. **Limitaciones:** los contadores se pierden al reiniciar
y no se comparten entre instancias (hoy hay una). La aplicación no lleva un presupuesto en euros:
si algún día se usa Anthropic en producción, **es obligatorio configurar un límite de gasto en la
Anthropic Console**. Cada llamada deja en el log sus tokens (`a2a.model`).

## Agent Card

Es pública y está en la ruta estándar de A2A:

- `GET /a2a/python-tutor/.well-known/agent-card.json`
- `GET /.well-known/agent-card.json` (el agente principal del servidor)

```json
{
  "name": "Python Tutor",
  "version": "0.1.0",
  "supportedInterfaces": [
    { "url": "http://127.0.0.1:8000/a2a/python-tutor", "protocolBinding": "JSONRPC", "protocolVersion": "1.0" }
  ],
  "capabilities": { "streaming": false, "pushNotifications": false },
  "securitySchemes": { "bearer": { "httpAuthSecurityScheme": { "scheme": "Bearer", "bearerFormat": "JWT" } } },
  "securityRequirements": [{ "schemes": { "bearer": {} } }],
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain"],
  "skills": [{ "id": "python-learning", "name": "Aprender Python", "tags": ["python", "fundamentals", "debugging", "code explanation", "exercises"] }]
}
```

Solo declara lo implementado: JSON-RPC, sin streaming ni notificaciones push.

## Endpoints

| Método | Ruta | Sesión | Qué hace |
|---|---|---|---|
| GET | `/.well-known/agent-card.json` | | Agent Card del agente principal |
| GET | `/a2a/python-tutor/.well-known/agent-card.json` | | Agent Card del Python Tutor |
| POST | `/a2a/python-tutor` | ✔ | JSON-RPC 2.0 de A2A 1.0: `SendMessage`, `GetTask`, `ListTasks`, `CancelTask` |

Cabeceras de la petición JSON-RPC:

- `A2A-Version: 1.0` (obligatoria; sin ella el SDK la toma como 0.3 y responde `-32009`).
- `Authorization: Bearer <token>`, o en la web la cookie de sesión con `X-PLD-Session: cookie`.

La respuesta trae `X-Request-ID`, el mismo id que aparece en el log de la tarea.

### Formato del mensaje

- **Texto** (obligatorio, máx. 4000 caracteres): la pregunta.
- **Datos** (opcional, un objeto): `lesson_slug`, `code` (máx. 20 000), `error` (máx. 4000) y
  `level` (`inicial`, `intermedio` o `avanzado`). Cualquier otro campo se rechaza.
- Archivos y URLs se **rechazan**: el agente no descarga nada.

Si el mensaje no es válido, la tarea acaba en `TASK_STATE_REJECTED` con una explicación.

## Autenticación y seguridad

- La Agent Card es pública (solo describe). **Todo lo demás exige sesión**, la misma de la API
  REST: no hay otro login ni otra tabla de usuarios.
- El usuario sale siempre de la sesión, nunca del mensaje. Cada usuario solo ve **sus tareas**:
  pedir la de otro responde «tarea no encontrada».
- Se mantienen CORS (lista explícita de orígenes; se añade `A2A-Version` a las cabeceras
  permitidas), cabeceras de seguridad, límite de 300 KB por petición y el registro de ataques.
- Límites de mensajes y de consultas al modelo (ver «Coste y límites»).
- Ninguna URL de la petición se descarga (se rechazan partes `url` y archivos) y el destino del
  modelo es fijo: sin SSRF. Los agentes no leen ni escriben archivos.
- El contexto de cada llamada **no lleva el token ni las cookies** (el SDK por defecto copiaría
  todas las cabeceras).
- El código del alumno **nunca se ejecuta** en el servidor (ni `exec`, ni `eval`, ni
  `subprocess`): el modelo lo analiza como texto. Para ejecutarlo está la consola de la web con
  Pyodide. Un test sustituye esas funciones por otras que fallan y comprueba que nada las llama.
- Los errores internos no llegan al cliente: la tarea acaba en `TASK_STATE_FAILED` con un mensaje
  genérico, y el log guarda solo el tipo de error.
- Las tareas viven en memoria (las 20 últimas por usuario) y se borran al reiniciar.
- Logs (`pld.a2a`): agente, proveedor, modelo, tarea, conversación, id de petición, seudónimo del
  usuario, duración, resultado y tipo de error; y por llamada al modelo, tokens y motivo de parada.
  Nunca la API key, el JWT, cookies, contraseñas, el prompt, la pregunta, el código ni la
  respuesta. Los logs DEBUG del SDK de Anthropic (que llevan la petición) se silencian.

## Variables de entorno

| Variable | Por defecto | Qué hace |
|---|---|---|
| `A2A_ENABLED` | `false` | Monta las rutas A2A |
| `A2A_MODEL_PROVIDER` | `ollama` | `ollama`, `anthropic` o `mock` |
| `A2A_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | URL interna de Ollama (solo configuración, nunca de una petición) |
| `A2A_MODEL` | (vacía) | Modelo; vacía = `qwen2.5-coder:7b` con Ollama o `claude-opus-5-5` con Anthropic |
| `ANTHROPIC_API_KEY` | (vacía) | **Secreto**, solo con `anthropic`. Solo en el entorno o el gestor de secretos |
| `A2A_MOCK_MODEL` | `false` | Modelo simulado (gana a `A2A_MODEL_PROVIDER`). Desarrollo y tests, **nunca en producción** |
| `A2A_MAX_OUTPUT_TOKENS` | `4096` | Tokens de salida por respuesta (256–32 000) |
| `A2A_MODEL_TIMEOUT_SECONDS` | `120` | Segundos por llamada al modelo (Anthropic: con un reintento, como mucho el doble) |
| `A2A_BASE_URL` | `http://127.0.0.1:8000` | URL pública de la API que se anuncia en la Agent Card |
| `A2A_RATE_LIMIT_PER_MINUTE` | `20` | Mensajes al tutor por usuario y minuto |
| `A2A_DAILY_LIMIT_PER_USER` | `100` | Consultas al modelo por usuario y día |
| `A2A_GLOBAL_LIMIT_PER_MINUTE` | `60` | Consultas al modelo de todos los usuarios por minuto |

`render.yaml` no activa A2A: en el plan gratuito de Render no hay memoria para un modelo local.
Activarlo en producción (con Ollama en un servidor propio o con Anthropic) es una decisión aparte.

## Arrancarlo en local

```bash
cd backend
pip install -r requirements-dev.txt
# en backend/.env, además de JWT_SECRET:
#   A2A_ENABLED=true
#   A2A_MODEL_PROVIDER=ollama      # con Ollama en marcha y el modelo descargado (ver arriba)
#   A2A_MODEL=qwen2.5-coder:7b
# o, sin modelo:
#   A2A_ENABLED=true
#   A2A_MOCK_MODEL=true
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

La web (`cd frontend && python -m http.server 5500`) muestra entonces **Tutor Python** en el menú.

## Tests

```bash
cd backend && python -m pytest tests/test_a2a.py tests/test_a2a_ollama.py tests/test_a2a_providers.py
cd backend && python -m pytest --cov=app           # todo el backend (100 % de cobertura)
npm run test:unit                                  # incluye tests/unit/tutor.test.mjs
npx playwright test e2e/tutor.spec.js              # web → API → A2A → agente → respuesta
```

`tests/test_a2a.py` cubre la Agent Card, la interacción, la sesión (Bearer y cookie con CSRF), los
errores JSON-RPC, el aislamiento entre usuarios, el contexto educativo, la validación de entrada,
el límite de tamaño, el límite por usuario, la cancelación, CORS, que el código no se ejecuta, que
los logs y las respuestas no llevan secretos y las piezas por separado.

**Los tests no necesitan Ollama, un modelo, Internet ni API keys.** `conftest.py` activa
`A2A_MOCK_MODEL=true` y borra `ANTHROPIC_API_KEY` del entorno.

- `tests/test_a2a_ollama.py` simula la API de Ollama (`httpx.MockTransport`): URL, modelo y prompt
  correctos, respuesta, respuesta vacía, errores HTTP, timeout, JSON inválido, Ollama apagado,
  URLs no permitidas, redirecciones, proxies, logs sin contenido, contexto minimizado y aislamiento
  entre usuarios de punta a punta.
- `tests/test_a2a_providers.py` hace lo mismo con el SDK de Anthropic contra una API simulada.
- `tests/test_a2a_ollama_integration.py` es **opcional**: solo se ejecuta con
  `RUN_OLLAMA_INTEGRATION_TESTS=true` y un Ollama de verdad. CI no lo necesita.

### Validación manual de punta a punta

[`scripts/a2a/validate_tutor.py`](../scripts/a2a/validate_tutor.py) prueba la ruta real: comprueba
que Ollama responde y tiene el modelo, arranca un uvicorn temporal, crea un alumno de prueba y
hace 5 consultas (concepto, error, depuración, ejercicio y solución; la primera con el cliente
oficial de A2A). Después revisa el log del servidor buscando la clave, el JWT, la contraseña, el
email, el nombre, la pregunta y el código, y muestra los tokens usados.

```bash
python scripts/a2a/validate_tutor.py                       # Ollama (gratis)
python scripts/a2a/validate_tutor.py --provider anthropic  # DE PAGO: clave solo en el entorno
```

## Privacidad

Qué datos van a cada sitio:

- **Backend:** recibe la consulta con la sesión del alumno y lee de la base de datos su nivel y,
  si elige una lección, sus datos (ver «Minimización de datos»). Las tareas viven en memoria.
- **Ollama (modo local, predeterminado):** los mensajes del tutor se procesan con el modelo local
  configurado en Ollama y no necesitan enviarse a un proveedor externo de IA. Le llega solo el
  contexto educativo mínimo. En este modo la aplicación no llama a Anthropic ni a OpenAI. No se ha
  comprobado la telemetría del propio Ollama (por ejemplo, la búsqueda de actualizaciones), así que
  no se afirma que sea «100 % privado».
- **Proveedor externo (solo si se activa Anthropic):** le llega el mismo contexto mínimo, como
  encargado del tratamiento.

La [política de privacidad](../frontend/privacidad.html) explica la finalidad, los datos, ambos
modos, la minimización, que el código no se ejecuta y que no hay que escribir secretos ni datos
personales. **REVISIÓN LEGAL PENDIENTE:** el texto no lo ha revisado un profesional. Antes de usar
un proveedor externo en producción hay que confirmar la base legal, las transferencias
internacionales y el acuerdo de tratamiento de datos.

## Conectar un cliente A2A

### Con curl

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -d "username=tu@email.com&password=tu-contraseña" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -s -X POST http://127.0.0.1:8000/a2a/python-tutor \
  -H "Authorization: Bearer $TOKEN" -H "A2A-Version: 1.0" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"SendMessage","params":{"message":{
        "messageId":"m-1","role":"ROLE_USER","parts":[
          {"text":"¿Por qué falla mi ejercicio?"},
          {"data":{"lesson_slug":"variables","code":"precio = 49,99","error":"TypeError: ..."}}]}}}'
```

Respuesta (resumida):

```json
{"jsonrpc":"2.0","id":1,"result":{"task":{
  "id":"…","contextId":"…","status":{"state":"TASK_STATE_COMPLETED"},
  "artifacts":[{"name":"respuesta","parts":[{"text":"Estás en **Variables y print()** …","mediaType":"text/plain"}],
                "metadata":{"level":"inicial","provider":"mock","model":"mock"}}]}}}
```

Para seguir la conversación, envía el siguiente mensaje con el mismo `contextId`.

### Con el cliente oficial de Python

[`scripts/a2a/tutor_client.py`](../scripts/a2a/tutor_client.py) usa `a2a.client.create_client`:
lee la Agent Card, inicia sesión y envía la pregunta.

```bash
python scripts/a2a/tutor_client.py http://127.0.0.1:8000 tu@email.com "¿Qué es una tupla?"
```

### Desde Android (en el futuro)

La app usaría el mismo endpoint con su token Bearer (como el resto de la API). No hace falta otra
implementación de A2A en Kotlin: basta con enviar el JSON-RPC de arriba.

## Añadir un agente nuevo

Ejemplo: un «DAW Agent» con id `daw`.

1. `app/a2a/cards/daw.py` con `build_daw_card(agent_url, mock_model) -> AgentCard` (solo lo que
   haga de verdad).
2. `app/a2a/agents/daw.py` con la lógica educativa, sin nada del protocolo.
3. `app/a2a/executors/daw.py` con un `AgentExecutor` pequeño, como el del tutor.
4. Una entrada en `AGENTS` de `server.py`:

   ```python
   AgentSpec(id="daw", build_card=build_daw_card, build_executor=lambda model: DawExecutor(DawAgent(model)))
   ```

Sus rutas (`/a2a/daw` y su Agent Card) se montan solas, con la misma sesión, el mismo límite y
tareas aisladas por usuario. No hay que tocar el núcleo.

## Siguientes pasos previstos

- **Otros proveedores** (OpenAI, modelo local) detrás de `AgentModelProvider`.
- **Streaming**: activar `capabilities.streaming` y publicar actualizaciones parciales; el
  executor ya sigue el flujo tarea → actualizaciones → artefacto.
- **MCP** para que los agentes lean lecciones, progreso y ejercicios como herramientas
  (agente → herramientas), y A2A para que hablen entre sí (agente → agente): el Python Tutor podría
  consultar al futuro DAW Agent.
