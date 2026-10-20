# Tutor híbrido: modo gratuito e IA avanzada (ADR-0038)

El Tutor de Python tiene dos modalidades:

| | **Gratuito** (por defecto) | **IA avanzada** (opcional) |
|---|---|---|
| Quién responde | El proveedor de siempre: tutor sin IA (`mock`), Ollama local o Anthropic, según `A2A_MODEL_PROVIDER` | OpenAI (API de Responses), solo si el backend lo tiene activado |
| Coste | Ninguno de proveedor de pago (salvo que el despliegue elija Anthropic como proveedor principal) | De pago, por tokens |
| Límites | Los de siempre: mensajes por minuto, consultas por día y por minuto en memoria | Cuota en la base de datos: por usuario y día y total por día, más límites de entrada y salida |
| Si falla | Mensaje de error y, si hay plan, la respuesta sin IA | Explica el motivo y da la respuesta gratuita (sin IA). Nunca reintenta con otro proveedor de pago |
| Estado actual | Activo (producción: `A2A_MODEL_PROVIDER=mock`) | **Desactivado** (`A2A_ADVANCED_PROVIDER=none`). No se ha hecho ninguna llamada real a OpenAI |

Las dos comparten todo lo demás: el plan pedagógico determinista (ADR-0036), el contenido revisado
del curso, la memoria de la conversación, las preguntas de comprobación corregidas sin modelo y la
autenticación de la API.

## Arquitectura

### Antes

```
web (tutor.js) ──A2A──► PythonTutorExecutor ──► PythonTutorAgent.plan() ──► respond()
                          límites en memoria                                  └─ un único proveedor
                                                                                (A2A_MODEL_PROVIDER)
```

### Después

```
web (tutor.js)
 ├─ GET /api/v1/tutor/modes ───────────────► ¿hay IA avanzada? ¿cuánta cuota me queda?
 └─ A2A SendMessage {texto, data:{mode?, alternative?, …}}
        │
        ▼
   PythonTutorExecutor  (decide la modalidad: el cliente solo la pide)
    1. parse_message → TutorQuery (campos desconocidos = rechazo)
    2. PythonTutorAgent.plan()  (determinista, sin modelo; igual en las dos modalidades)
    3. ¿mode=advanced?
         ├─ ¿activada? ¿pregunta+código+error ≤ A2A_ADVANCED_MAX_INPUT_CHARS?   si no → rechazo + respuesta gratuita
         ├─ ¿necesita modelo? (las comprobaciones y saludos no: no gastan cuota)
         └─ UsageLedger.reserve_advanced()  (tabla tutor_usage, antes de llamar)  si no queda → rechazo + respuesta gratuita
    4. respond(plan, modelo concedido)  ──► OpenAIProvider | proveedor gratuito
    5. contabilidad: tokens de la avanzada o +1 consulta gratuita (tutor_usage)
```

Piezas:

| Archivo | Qué hace |
|---|---|
| `backend/app/a2a/providers/openai_provider.py` | `OpenAIProvider`: SDK oficial `openai`, `responses.create`, `store=False`, destino fijo, sin reintentos (una consulta de la cuota = como mucho una llamada facturable), plazo total, errores traducidos a los de `providers/base.py`, logs sin contenido |
| `backend/app/a2a/providers/base.py` | `ModelReply`: el texto con `input_tokens` y `output_tokens` (sigue siendo un `str`, los demás proveedores no cambian) |
| `backend/app/a2a/executors/python_tutor.py` | `AdvancedMode`, `_check_advanced`, `_reserve`: la decisión de modalidad, los rechazos y la contabilidad |
| `backend/app/services/tutor_usage.py` | `UsageLedger`: cuotas y consumo en `tutor_usage` |
| `backend/app/a2a/server.py` | `build_advanced_mode` (configuración) y `GET /api/v1/tutor/modes` |
| `backend/app/a2a/agents/python_tutor.py`, `tutor_pedagogy.py` | Explicación alternativa, nota revisada «lista frente a tupla», escalera de comprobaciones, más ejercicios sin repetir |
| `frontend/js/tutor.js`, `tutor-protocol.js`, `css/widgets.css` | Selector de modalidad, cuota, avisos de privacidad, botones de pista, explicación alternativa y otro ejercicio |

No hay un segundo sistema de proveedores: OpenAI es otra clase que cumple `AgentModelProvider`.

## Cómo se decide la modalidad

1. El cliente pide `mode: "advanced"` en la parte de datos del mensaje A2A. Sin ese campo (la web en
   modo gratuito, la app Android y cualquier cliente anterior) la petición es gratuita.
2. El servidor solo concede la avanzada si: está configurada, el texto cabe en el límite, el plan
   necesita un modelo y `reserve_advanced()` encuentra cuota (del usuario y global).
3. Cualquier otro campo (`provider`, `model`, `quota`…) hace que el mensaje se rechace
   (`invalid_input`): el cliente no puede elegir proveedor, modelo ni cuota.
4. Si no se concede, la tarea queda `TASK_STATE_REJECTED` con `metadata.reason` y el texto incluye el
   motivo y la respuesta gratuita (preparada, sin ninguna llamada a un modelo):

| `reason` | Cuándo |
|---|---|
| `advanced_unavailable` | El servidor no tiene IA avanzada (o está mal configurada) |
| `advanced_input_too_long` | Pregunta + código + error superan `A2A_ADVANCED_MAX_INPUT_CHARS` |
| `advanced_limit_reached` | El alumno ha usado sus consultas de hoy |
| `advanced_global_limit` | Se ha llegado al total diario de todos los alumnos |

Si OpenAI falla (`provider_timeout`, `provider_rate_limited`, `provider_unavailable`), la tarea
queda `TASK_STATE_FAILED` con el motivo y la respuesta sin IA. Un 429 o una clave inválida no se
cobran y la consulta se devuelve al alumno; un timeout o un 5xx sí cuentan (OpenAI puede haberlos
procesado). El proveedor no reintenta: si el alumno pulsa «Reintentar», es otra consulta de su cuota.

Lo contrario no ocurre nunca: una petición gratuita no se convierte en una llamada de pago, aunque
el proveedor gratuito falle.

## Conversación educativa

La misma en las dos modalidades (el modelo, si lo hay, recibe el plan como guía):

1. Pregunta del alumno.
2. Explicación adaptada al nivel y al tema (un concepto cada vez, términos definidos).
3. Ejemplo de código mínimo.
4. Resultado esperado, comprobado (en CI para `learning.json`; en los tests para las notas revisadas).
5. Errores explicados (tipo de error, hechos e hipótesis del análisis estático).
6. Acciones: **Pedir una pista** (graduada, sin la solución de un ejercicio pendiente),
   **Explícamelo de otra forma** (`alternative: true`: otra explicación del mismo tema) y
   **Otro ejercicio** (sin repetir; cuando se acaban los de programar, uno de predecir la salida).
7. Pregunta de comprobación «¿qué muestra este programa?», corregida por el sistema comparando con
   la salida verificada. Si falla, explica el motivo y propone otra del mismo nivel; si acierta, lo
   reconoce y propone una más difícil y, al final, un reto de programar. **Nunca se pregunta a la
   IA si la respuesta es correcta.**

Ejemplo de aceptación: «No entiendo la diferencia entre una lista y una tupla en Python» activa la
nota revisada `lista-tupla` (`tutor_pedagogy.PRECISION_NOTES`): mutable frente a inmutable, ejemplo
`lista[0] = 10` con su salida y la comprobación `tup-05`; después `tup-06` (otra oportunidad) o
`tup-07` (reto). Lo prueban `backend/tests/test_tutor_hybrid.py` y `e2e/tutor-hybrid.spec.js`.

El tutor **no modifica el progreso**: no marca lecciones como completadas, no escribe notas, ni
permisos, ni cuentas. Solo lee el contexto educativo (ADR-0036). Las lecciones se completan con los
ejercicios superados en el navegador, como siempre.

## Variables de entorno

Todas en el backend. Las claves, solo en el entorno o en el gestor de secretos de Render, nunca en
el repositorio ni en el navegador.

| Variable | Por defecto | Qué hace |
|---|---|---|
| `A2A_ADVANCED_PROVIDER` | `none` | `none` (desactivada), `openai` (de pago) o `mock` (simulada, para tests y e2e) |
| `OPENAI_API_KEY` | — | Secreto. Obligatoria con `openai` |
| `A2A_ADVANCED_MODEL` | — | Modelo de OpenAI disponible en tu cuenta. Obligatorio con `openai`: no se fija ninguno en el código |
| `A2A_ADVANCED_REASONING_EFFORT` | — | Solo para modelos de razonamiento (`none`, `minimal`, `low`, `medium`, `high`). Con 600 tokens de salida conviene `low` o menos: el razonamiento cuenta dentro de `max_output_tokens` |
| `A2A_ADVANCED_DAILY_LIMIT_PER_USER` | `10` | Consultas avanzadas por usuario y día (UTC) |
| `A2A_ADVANCED_GLOBAL_DAILY_LIMIT` | `200` | Consultas avanzadas de todos los usuarios por día (UTC) |
| `A2A_ADVANCED_MAX_INPUT_CHARS` | `6000` | Pregunta + código + error (la pregunta sola ya tiene un máximo de 4000) |
| `A2A_ADVANCED_MAX_OUTPUT_TOKENS` | `600` | Tokens de salida por respuesta |
| `A2A_ADVANCED_TIMEOUT_SECONDS` | `30` | Segundos por llamada (sin reintentos) |

Si `A2A_ADVANCED_PROVIDER=openai` pero falta la clave o el modelo, la API arranca igual, la IA
avanzada queda desactivada y el log dice qué falta (sin mostrar la clave): el modo gratuito no se
cae por una configuración incompleta.

`render.yaml` no se ha cambiado: activar la IA avanzada en Render es una decisión de despliegue que
toma el autor (ver «Antes de activarla en producción»).

## Límites y estimación de costes

Valores iniciales, no definitivos: se cambian con las variables anteriores sin tocar código.

Tamaño de una consulta, medido con el prompt real del tutor:

- Instrucciones del tutor: unos 2400 caracteres; contexto + guía preparada + pregunta: unos
  1800 caracteres en una pregunta corta. En total, del orden de **1200–1500 tokens de entrada**.
- Con el máximo de entrada (6000 caracteres del alumno) y una guía larga: hasta unos **4500 tokens**.
- Salida: como mucho **600 tokens** (las respuestas recortadas lo dicen).

Peor caso con los valores iniciales:

| | Entrada | Salida |
|---|---|---|
| Un alumno, un día (10 consultas) | ≤ 45 000 tokens | ≤ 6 000 tokens |
| Todos, un día (200 consultas) | ≤ 900 000 tokens | ≤ 120 000 tokens |
| Todos, 30 días | ≤ 27 M tokens | ≤ 3,6 M tokens |

Coste mensual máximo = 27 × P<sub>entrada</sub> + 3,6 × P<sub>salida</sub>, con los precios por
millón de tokens del modelo elegido en <https://openai.com/api/pricing> (consúltalos al elegirlo:
cambian y dependen del modelo). Por ejemplo, con precios hipotéticos de 0,40 $ y 1,60 $ por millón
saldría ≤ 16,56 $ al mes; el uso real será mucho menor que este peor caso. Para un tope duro
independiente de la app, configura además un límite de gasto en la cuenta de OpenAI.

La contabilidad real está en la tabla `tutor_usage` (consultas y tokens por usuario, día y
modalidad) y en los logs `a2a.model` (tokens por llamada, sin contenido).

## Privacidad: qué se envía a OpenAI

Solo con la IA avanzada activada y elegida por el alumno:

- Las instrucciones del tutor (`SYSTEM_PROMPT`).
- Lo que el alumno escribe en el tutor: pregunta, código y mensaje de error.
- Contexto educativo mínimo: nivel estimado y su base, estado de los conceptos de esa pregunta, la
  lección elegida (título, enunciado, si está superada y nº de intentos) y extractos de los tres
  últimos turnos de esa conversación.

**No** se envía: email, nombre, id de usuario, token, cookies, IP, el código de intentos anteriores
ni el resto del progreso. Tampoco los campos `user` o `safety_identifier` de la API. Se envía
`store=False` para que OpenAI no guarde la respuesta para recuperarla después; OpenAI puede
conservar datos de la API un tiempo para vigilar abusos según sus condiciones, que hay que revisar.

El texto del alumno va delimitado y marcado como datos, y las instrucciones del tutor dicen que se
ignore cualquier orden dentro de él. El código del alumno nunca se ejecuta en el servidor y la
respuesta del modelo solo se muestra (escapada) al alumno: no puede cambiar notas, progreso,
permisos ni cuentas.

En la web, la opción explica qué se envía y a quién antes de elegirla. La política de privacidad
publicada (`frontend/privacidad.html`) **todavía no menciona OpenAI**: el borrador está en
`docs/legal/expediente/borradores/tutor-hibrido-openai.md` y lo tiene que aprobar el autor.

### Antes de activarla en producción

1. Revisar y aprobar el borrador legal (tratamiento de datos de OpenAI, transferencia
   internacional, conservación, encargado del tratamiento) y actualizar la política de privacidad.
2. Crear la clave en OpenAI con límite de gasto y elegir un modelo disponible en la cuenta.
3. En Render: `A2A_ADVANCED_PROVIDER=openai`, `OPENAI_API_KEY` (secreto), `A2A_ADVANCED_MODEL`.
4. Aplicar la migración `d7e2a9c4f1b8` (tabla `tutor_usage`; el arranque de Render ya ejecuta
   `alembic upgrade head`).
5. Prueba manual con una cuenta de prueba (no personal): la pregunta de aceptación, una
   comprobación fallada y otra acertada, el límite diario y `GET /api/v1/tutor/modes`.

## Pruebas

| Qué | Cómo |
|---|---|
| Backend (proveedor con la API de OpenAI simulada, cuotas, aislamiento, privacidad, corrección determinista) | `cd backend && python -m pytest -q tests/test_tutor_hybrid.py` (y la suite completa con `--cov=app --cov-fail-under=100`) |
| Protocolo de la web | `npm run test:unit` (`tests/unit/tutor-hybrid.test.mjs`) |
| Web de punta a punta (selector, límites, carga, teclado, móvil, axe) | `npm run test:e2e` (`e2e/tutor-hybrid.spec.js`); el backend de e2e usa `A2A_ADVANCED_PROVIDER=mock` |

Ningún test usa una clave real ni sale a Internet: la API de OpenAI se simula con
`httpx2.MockTransport`, así que se ejecuta el SDK oficial de verdad. Una llamada real a OpenAI solo
debe hacerse en un entorno controlado y con autorización.

Probarlo en local sin coste:

```bash
cd backend
A2A_ENABLED=true A2A_MOCK_MODEL=true A2A_ADVANCED_PROVIDER=mock uvicorn app.main:app --reload
```

## Limitaciones conocidas

- Las cuotas se reservan con un cerrojo del proceso: con una sola instancia (el despliegue actual)
  son exactas; con varias, dos peticiones simultáneas podrían superar el límite en una consulta.
- El día de la cuota es UTC (en España se reinicia a las 01:00 o 02:00).
- Un timeout o un 5xx de OpenAI cuentan como consulta: OpenAI puede haberlos procesado.
- Los tokens son los que informa OpenAI; si una respuesta no los trae, se cuenta la consulta sin
  tokens.
- La memoria de la conversación sigue siendo en RAM (ADR-0036): se pierde al reiniciar.
- La app Android no tiene todavía el selector: sigue usando el modo gratuito (no envía `mode`).

## Comprobaciones manuales pendientes

- [ ] Llamada real a OpenAI con un modelo de la cuenta del autor, en un entorno controlado.
- [ ] Revisión y aprobación del borrador legal y actualización de `privacidad.html`.
- [ ] Prueba en un móvil real con lector de pantalla (TalkBack o VoiceOver).
- [ ] Revisar con datos reales si 10 consultas diarias y 600 tokens son adecuados.
