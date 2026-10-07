# ADR-0034: Agentes A2A junto a la API REST (Python Tutor)

- **Estado:** Propuesta (pendiente de que el autor la apruebe en el PR). Proveedor por defecto:
  Ollama, un modelo local y gratuito; Anthropic opcional y desactivado (decisión del autor,
  2026-10-06: en esta fase no se gasta en APIs de pago).
- **Fecha:** 2026-10-06
- **Relacionada:** ADR-0003 (los ejercicios se ejecutan en el navegador), ADR-0022 (seguridad
  integral), ADR-0033 (sesión en cookie `HttpOnly`)

## Contexto

Queremos que el dashboard pueda usar agentes educativos especializados (primero un tutor de
Python; después DAW, PCAP, revisión de código, planificador de estudio y progreso) y que esos
agentes puedan hablar entre sí más adelante. Agent2Agent (A2A) es el protocolo abierto para eso:
cada agente publica una **Agent Card** y atiende **tareas** con mensajes y artefactos.

No se quiere rehacer nada: el frontend sigue sin framework, FastAPI sigue siendo el backend y la
API REST `/api/v1/*` no cambia. A2A es una capacidad más.

## Decisión

1. **SDK oficial `a2a-sdk[fastapi]` 1.2.x** (A2A 1.0). No se implementa el protocolo a mano: la
   Agent Card, el JSON-RPC, las tareas y sus estados los da el SDK.
2. **Misma app y mismo proceso.** Las rutas del agente se añaden a la app FastAPI existente bajo
   `/a2a/<agente>`; no hay un segundo servidor.
   - `GET /a2a/python-tutor/.well-known/agent-card.json` y `GET /.well-known/agent-card.json`
     (la ruta estándar de descubrimiento sirve al agente principal): **públicas**, solo describen.
   - `POST /a2a/python-tutor`: JSON-RPC de A2A 1.0. **Requiere sesión.**
3. **Solo JSON-RPC, sin streaming ni push.** La card solo declara lo implementado. El executor ya
   publica la secuencia tarea → en curso → artefacto → completada, así que el streaming solo
   necesitará activar la capacidad.
4. **Autenticación: la de la API.** La ruta JSON-RPC usa `get_current_user` (Bearer o cookie con
   `X-PLD-Session`, ADR-0033). No hay otra tabla de usuarios ni otro sistema de login.
5. **Tareas aisladas por usuario.** El propietario de cada tarea es el usuario de la sesión (id y
   fecha de alta); `GetTask`, `ListTasks` y `CancelTask` de otro usuario responden «no existe».
   Las tareas viven **en memoria** (las 20 últimas por usuario) y se pierden al reiniciar: son
   conversaciones de un momento, no datos del alumno.
6. **Capas separadas** en `backend/app/a2a/`: `cards/` (la ficha), `agents/` (lógica educativa,
   sin protocolo), `executors/` (protocolo, validación y errores), `providers/` (modelo de
   lenguaje) y `server.py` (registro de agentes y rutas). Los datos del alumno salen de
   `app/services/learning_context.py`, no de consultas dentro del executor.
7. **Modelo intercambiable.** El agente recibe un `AgentModelProvider`. Por defecto,
   **Ollama** (`OllamaProvider`): un modelo local y gratuito que solo el backend llama, con URL y
   modelo de la configuración. **Anthropic** (`AnthropicProvider`, SDK oficial) está implementado
   pero solo se usa si se elige expresamente y hay `ANTHROPIC_API_KEY` (si no, la API no arranca).
   El **simulado** (`A2A_MOCK_MODEL=true`) sirve para tests. OpenAI sería otra clase con la misma
   interfaz. A2A está **desactivado por defecto**.
8. **El código del alumno es texto.** Nunca se ejecuta en el servidor (ni `exec`, ni `eval`, ni
   `subprocess`). Para ejecutarlo sigue estando Pyodide en el navegador (ADR-0003).
9. **Al proveedor solo le llega el contexto educativo mínimo** de la consulta (nivel, lección,
   enunciado, si está superado, y la pregunta, el código y el error), nunca datos que identifiquen
   al alumno ni de otros usuarios. Límites de coste con el `RateLimiter` existente: consultas por
   usuario y día y de todos por minuto, más `max_tokens` y tiempo máximo por llamada.

## Alternativas descartadas

- **Un servidor A2A aparte** (otro puerto o servicio): duplica despliegue, CORS y autenticación.
- **REST de A2A además de JSON-RPC:** más superficie sin un cliente que lo necesite.
- **Guardar las tareas en la base de datos** (el SDK trae `DatabaseTaskStore`): añade tablas y
  datos personales que conservar y borrar (RGPD) sin necesidad todavía.
- **Acoplar el tutor a Anthropic** (llamar al SDK desde el agente): impediría cambiar a OpenAI o
  a un modelo local sin tocar la lógica educativa.

## Consecuencias

- La web tiene una sección **Tutor Python** (`#/tutor`) que solo aparece si la Agent Card responde.
- `A2A-Version` se añade a las cabeceras permitidas por CORS; los orígenes siguen siendo una lista
  explícita. Las cabeceras de seguridad de la API se aplican también a `/a2a/` y a la Agent Card.
- Nuevo límite: 20 mensajes por usuario y minuto (`A2A_RATE_LIMIT_PER_MINUTE`), además del límite
  de tamaño del cuerpo (300 KB) y de 4000/20000/4000 caracteres para pregunta, código y error.
- Logs `pld.a2a`: agente, tarea, conversación, id de petición, seudónimo del usuario, duración,
  resultado y tipo de error; nunca la pregunta, el código ni credenciales.
- La dependencia nueva trae `protobuf` y `google-api-core` (las usa el SDK para sus tipos). Solo
  se importa con `A2A_ENABLED=true`: sin A2A la API ocupa lo mismo que antes (unos 18 MB menos
  que con el SDK cargado, importante en la instancia gratuita de 512 MB).
- Con varias instancias del backend, las tareas en memoria y el límite por usuario no se
  compartirían; hoy hay una sola (igual que el límite de login, ADR-0022).
