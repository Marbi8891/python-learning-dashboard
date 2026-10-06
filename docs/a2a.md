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
| `providers/` | El **modelo de lenguaje**: interfaz `AgentModelProvider` y el modelo simulado `MockModelProvider` |
| `observability.py` | Una línea de log JSON por tarea (`pld.a2a`) |
| `server.py` | Registro de agentes (`AGENTS`), autenticación, límite por usuario, tareas por usuario y montaje de rutas |

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

Qué datos del alumno usa (minimización): lecciones completadas y totales y, solo si pregunta por una
lección, su título, enunciado, pista, si la tiene completada y cuántos intentos lleva. Nunca el
email, el nombre, el historial completo ni el código de intentos anteriores.

### Modelo de lenguaje

El agente no depende de ningún proveedor. Recibe un objeto con este método:

```python
class AgentModelProvider(Protocol):
    name: str
    async def generate(self, request: ModelRequest) -> str: ...
```

`ModelRequest` lleva las instrucciones de tutor (`system`), la pregunta con el contexto mínimo
(`prompt`) y la guía que ha preparado el agente (`outline`). Hoy solo existe `MockModelProvider`,
que devuelve esa guía marcada como «Modo de desarrollo». Para Anthropic, OpenAI o un modelo
local basta con otra clase con `generate` y elegirla en `build_model_provider` (`server.py`).

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
- Límite de **20 mensajes por usuario y minuto** (429).
- El contexto de cada llamada **no lleva el token ni las cookies** (el SDK por defecto copiaría
  todas las cabeceras).
- El código del alumno **nunca se ejecuta** en el servidor. Para eso está la consola de la web
  con Pyodide.
- Los errores internos no llegan al cliente: la tarea acaba en `TASK_STATE_FAILED` con un mensaje
  genérico, y el log guarda solo el tipo de error.
- Las tareas viven en memoria (las 20 últimas por usuario) y se borran al reiniciar.

## Variables de entorno

| Variable | Por defecto | Qué hace |
|---|---|---|
| `A2A_ENABLED` | `false` | Monta las rutas A2A. Sin modelo (de momento, `A2A_MOCK_MODEL=true`) el servidor no arranca |
| `A2A_MOCK_MODEL` | `false` | Usa el modelo simulado. Solo para desarrollo y tests, **nunca en producción** |
| `A2A_BASE_URL` | `http://127.0.0.1:8000` | URL pública de la API que se anuncia en la Agent Card (en Render: `https://pld-api.onrender.com`) |
| `A2A_RATE_LIMIT_PER_MINUTE` | `20` | Mensajes al tutor por usuario y minuto |

No hay ninguna clave nueva: el modelo simulado no la necesita.

## Arrancarlo en local

```bash
cd backend
pip install -r requirements-dev.txt
# en backend/.env, además de JWT_SECRET:
#   A2A_ENABLED=true
#   A2A_MOCK_MODEL=true
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

La web (`cd frontend && python -m http.server 5500`) muestra entonces **Tutor Python** en el menú.

## Tests

```bash
cd backend && python -m pytest tests/test_a2a.py   # solo A2A
cd backend && python -m pytest --cov=app           # todo el backend (100 % de cobertura)
npm run test:unit                                  # incluye tests/unit/tutor.test.mjs
npx playwright test e2e/tutor.spec.js              # web → API → A2A → agente → respuesta
```

`tests/test_a2a.py` cubre la Agent Card, la interacción, la sesión (Bearer y cookie con CSRF), los
errores JSON-RPC, el aislamiento entre usuarios, el contexto educativo, la validación de entrada,
el límite de tamaño, el límite por usuario, la cancelación, CORS, que el código no se ejecuta, que
los logs y las respuestas no llevan secretos y las piezas por separado.

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
                "metadata":{"level":"inicial","model":"mock"}}]}}}
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

- **Proveedor real** (Anthropic, OpenAI o local) detrás de `AgentModelProvider`, con su variable
  de entorno para la clave y la política de privacidad actualizada (se enviarían preguntas y
  código a un tercero).
- **Streaming**: activar `capabilities.streaming` y publicar actualizaciones parciales; el
  executor ya sigue el flujo tarea → actualizaciones → artefacto.
- **MCP** para que los agentes lean lecciones, progreso y ejercicios como herramientas
  (agente → herramientas), y A2A para que hablen entre sí (agente → agente): el Python Tutor podría
  consultar al futuro DAW Agent.
