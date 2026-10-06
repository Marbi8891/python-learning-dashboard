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
| `providers/` | El **modelo de lenguaje**: interfaz `AgentModelProvider`, `AnthropicProvider` (producción) y `MockModelProvider` (desarrollo y tests) |
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

Al **proveedor del modelo** solo le llega (`PythonTutorAgent._prompt`):

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
    name: str    # «anthropic», «mock»…
    model: str   # modelo concreto, para logs y metadatos
    async def generate(self, request: ModelRequest) -> str: ...
```

```
A2A → Python Tutor Agent → AgentModelProvider → AnthropicProvider   (hoy, producción)
                                              → MockModelProvider   (desarrollo y tests)
                                              → OpenAIProvider      (futuro)
                                              → LocalModelProvider  (futuro)
```

### Anthropic (proveedor inicial de producción)

`providers/anthropic_provider.py` usa el **SDK oficial** [`anthropic`](https://pypi.org/project/anthropic/)
1.x y la Messages API:

- Modelo por defecto **`claude-opus-5-5`** (`A2A_MODEL`), con `output_config.effort = "medium"`
  fijado en el código. El modelo debe admitir `effort` (familia Claude 4.6 y posteriores).
- Con los modelos que lo admiten (Opus 5 / 5.5, Sonnet 5.5, Fable 5) se activa el **respaldo en
  el servidor** (`fallbacks: "default"`, beta `server-side-fallback-2026-07-01`): si los filtros
  de seguridad del modelo rechazan una consulta, la API la repite con el modelo que recomienda
  Anthropic en la misma llamada. Si aun así se rechaza, la tarea falla con el mensaje genérico.
- `max_tokens` = `A2A_MAX_OUTPUT_TOKENS` (incluye el razonamiento del modelo). Si se corta, la
  respuesta lo dice.
- Tiempo máximo por llamada `A2A_MODEL_TIMEOUT_SECONDS` y **un solo reintento** (red, 429, 5xx);
  además, un límite total (el doble) para que ninguna tarea quede colgada.
- Destino fijo `https://api.anthropic.com`: ni la petición ni `ANTHROPIC_BASE_URL` lo cambian
  (sin SSRF).
- No envía `metadata.user_id` ni ningún identificador del alumno.
- Errores del SDK → excepciones propias (`ModelTimeoutError`, `ModelRateLimitedError`,
  `ModelConfigurationError`, `ModelRefusedError`, `EmptyModelResponseError`,
  `MalformedModelResponseError`…), sin la petición ni la respuesta dentro. El alumno ve un mensaje
  genérico y el log, el tipo de error.

**La API key** sale solo de `ANTHROPIC_API_KEY` (variable de entorno o gestor de secretos; en
Render, una variable secreta). Se lee como `SecretStr`, se entrega solo al cliente del SDK y nunca
está en el código, en los tests, en los logs, en la base de datos, en la Agent Card ni en las
respuestas al frontend. Sin ella, con `A2A_MODEL_PROVIDER=anthropic`, **la API no arranca**.

### Modelo simulado

`MockModelProvider` (`A2A_MOCK_MODEL=true`) no llama a nada ni necesita clave: devuelve la guía
del agente marcada como «Modo de desarrollo». Tiene prioridad sobre `A2A_MODEL_PROVIDER`, así que
los tests y el desarrollo nunca gastan ni envían datos fuera. La Agent Card lo indica.

### Cambiar de proveedor

1. Una clase en `providers/` con `name`, `model` y `async generate(request) -> str`, que lance las
   excepciones de `providers/base.py`.
2. Un valor más en `A2A_MODEL_PROVIDER` (`config.py`) y su rama en `build_model_provider`
   (`server.py`), con su clave como `SecretStr`.
3. Sus tests simulando la API, como `tests/test_a2a_providers.py`.

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

Los mensajes no válidos no gastan consultas. **Limitaciones:** los contadores se pierden al
reiniciar y no se comparten entre instancias (hoy hay una). La aplicación no lleva un presupuesto
en euros: **en producción es obligatorio configurar un límite de gasto adecuado en la Anthropic
Console** (límites del workspace o de la organización), que es el tope definitivo. Cada llamada deja en el log sus tokens de entrada y salida (`a2a.model`) para
vigilar el consumo.

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
| `A2A_ENABLED` | `false` | Monta las rutas A2A. Sin proveedor válido el servidor no arranca |
| `A2A_MODEL_PROVIDER` | `anthropic` | `anthropic` o `mock` |
| `ANTHROPIC_API_KEY` | (vacía) | **Secreto.** Obligatoria con `anthropic`. Solo en el entorno o el gestor de secretos, nunca en el repositorio |
| `A2A_MODEL` | `claude-opus-5-5` | Modelo de Anthropic |
| `A2A_MOCK_MODEL` | `false` | Modelo simulado (gana a `A2A_MODEL_PROVIDER`). Desarrollo y tests, **nunca en producción** |
| `A2A_MAX_OUTPUT_TOKENS` | `4096` | Tokens de salida por respuesta (256–32 000) |
| `A2A_MODEL_TIMEOUT_SECONDS` | `45` | Segundos por llamada al proveedor (con un reintento, como mucho el doble) |
| `A2A_BASE_URL` | `http://127.0.0.1:8000` | URL pública de la API que se anuncia en la Agent Card (en Render: `https://pld-api.onrender.com`) |
| `A2A_RATE_LIMIT_PER_MINUTE` | `20` | Mensajes al tutor por usuario y minuto |
| `A2A_DAILY_LIMIT_PER_USER` | `100` | Consultas al modelo por usuario y día |
| `A2A_GLOBAL_LIMIT_PER_MINUTE` | `60` | Consultas al modelo de todos los usuarios por minuto |

En Render, `ANTHROPIC_API_KEY` se añade como variable secreta del servicio `pld-api` (no está en
`render.yaml`, que no activa A2A). Activarlo en producción es una decisión aparte: antes hay que
fijar el límite de gasto en la consola de Anthropic.

## Arrancarlo en local

```bash
cd backend
pip install -r requirements-dev.txt
# en backend/.env, además de JWT_SECRET:
#   A2A_ENABLED=true
#   A2A_MOCK_MODEL=true            # sin API key ni llamadas externas
# o, para probar con Claude (la clave, solo en tu entorno, nunca en el repositorio):
#   A2A_ENABLED=true
#   A2A_MODEL_PROVIDER=anthropic
#   ANTHROPIC_API_KEY=…
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

La web (`cd frontend && python -m http.server 5500`) muestra entonces **Tutor Python** en el menú.

## Tests

```bash
cd backend && python -m pytest tests/test_a2a.py tests/test_a2a_providers.py   # solo A2A
cd backend && python -m pytest --cov=app           # todo el backend (100 % de cobertura)
npm run test:unit                                  # incluye tests/unit/tutor.test.mjs
npx playwright test e2e/tutor.spec.js              # web → API → A2A → agente → respuesta
```

`tests/test_a2a.py` cubre la Agent Card, la interacción, la sesión (Bearer y cookie con CSRF), los
errores JSON-RPC, el aislamiento entre usuarios, el contexto educativo, la validación de entrada,
el límite de tamaño, el límite por usuario, la cancelación, CORS, que el código no se ejecuta, que
los logs y las respuestas no llevan secretos y las piezas por separado.

**Los tests no necesitan API key ni red.** `conftest.py` activa `A2A_MOCK_MODEL=true` y borra
`ANTHROPIC_API_KEY` del entorno. `tests/test_a2a_providers.py` prueba el SDK oficial de verdad
contra una API de Anthropic simulada (`httpx2.MockTransport`): inicialización, falta de clave,
modelo simulado, errores 4xx/5xx/429, red caída, timeout, respuestas rechazadas, vacías o
malformadas, que la clave y el contenido nunca llegan a los logs, el contexto minimizado, el
aislamiento entre usuarios y los límites de coste.

### Validación manual con Anthropic (gasta dinero real)

Fuera de CI, [`scripts/a2a/validate_anthropic.py`](../scripts/a2a/validate_anthropic.py) prueba la
ruta real: arranca un uvicorn temporal con `A2A_MODEL_PROVIDER=anthropic`, crea un alumno de
prueba, hace 5 consultas (concepto, error, depuración, ejercicio y solución; la primera con el
cliente oficial de A2A) y revisa el log del servidor buscando la clave, el JWT, la contraseña, el
email, el nombre, la pregunta y el código. Al final muestra las llamadas y los tokens consumidos.

```bash
read -rs ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY   # no queda en el historial
python scripts/a2a/validate_anthropic.py claude-opus-5-5
unset ANTHROPIC_API_KEY
```

La clave solo se lee del entorno: nunca como argumento, en un archivo ni en el repositorio.

## Privacidad

La [política de privacidad](../frontend/privacidad.html) explica la finalidad, los datos que se
envían, el proveedor (Anthropic), la minimización, que el código no se ejecuta y que no hay que
escribir secretos ni datos personales. **REVISIÓN LEGAL PENDIENTE:** el texto no lo ha revisado un
profesional; antes de activar el tutor en producción conviene confirmar la base legal, las
transferencias internacionales y el acuerdo de tratamiento de datos con Anthropic.

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
