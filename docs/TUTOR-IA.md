# Tutor con IA del asistente

El asistente de cada lección (botón del robot, abajo a la derecha) tiene dos partes:

1. **Respuestas preparadas** (`lesson.assistant` en `data/lessons.json`): preguntas frecuentes y una pista
   del ejercicio. Funcionan siempre, sin cuenta y sin conexión.
2. **Tutor con IA** (opcional): el alumno escribe cualquier duda con sus palabras y la responde un modelo
   de lenguaje. Solo aparece si el servidor tiene `TUTOR_API_KEY`.

## Cómo funciona

```
Navegador (assistant.js) ──POST /api/v1/tutor/ask──► FastAPI (routers/tutor.py, app/tutor.py)
   pregunta, lección, historial,                       añade instrucciones y la teoría de la lección
   código y error de la consola (opcional)              └──► API del proveedor (Groq, gratis)
```

- **La clave nunca llega al navegador**: solo la tiene el backend.
- **Hace falta cuenta.** Así se puede limitar a cada alumno (`TUTOR_QUESTIONS_PER_HOUR`, 20 por defecto) y
  la capa gratuita no se agota. Sin sesión, el asistente pide iniciarla.
- **Pedagogía** (`SYSTEM_PROMPT` en `app/tutor.py`): responde en español, paso a paso y con ejemplos cortos.
  En el ejercicio da pistas y hace preguntas en vez de dar la solución, salvo que el alumno ya lo haya
  intentado y la pida. Los errores de Python los explica con palabras sencillas.
- **Contexto:** el tutor recibe el título, la teoría y el enunciado de la lección abierta, los últimos 6
  mensajes de la conversación y, si la casilla está marcada, el código del editor y el último error.
- **Privacidad:** no se guarda nada en la base de datos y los logs solo registran el tipo de fallo, nunca
  la pregunta. Se informa en `privacidad.html` (apartados 2, 3 y 4).
- **Transparencia (Reglamento de IA, art. 50.1):** el panel avisa de que las respuestas las genera una IA,
  que pueden tener errores y que no hay que escribir datos personales.
- **Si falla el proveedor** (caído, lento o sin cupo), la API responde 502 con un mensaje claro y las
  respuestas preparadas siguen funcionando.

## Activarlo

1. Crea una cuenta gratuita en <https://console.groq.com> y genera una API key. No hace falta tarjeta.
2. Añádela al backend como `TUTOR_API_KEY`: en local, en `backend/.env`; en producción, en el panel de
   Render (Environment). No la subas nunca al repositorio.
3. Reinicia la API. `/api/v1/health` pasará a decir `"tutor": true` y la web mostrará la caja de texto.

### Otro proveedor

`app/tutor.py` usa el formato de *chat completions* de OpenAI, que admiten muchos proveedores. Para cambiar
de proveedor basta con cambiar `TUTOR_API_URL` y `TUTOR_MODEL`. Por ejemplo, Ollama en tu PC (gratis y sin
enviar nada fuera) sería `TUTOR_API_URL=http://localhost:11434/v1/chat/completions` y
`TUTOR_MODEL=llama3.2`, con cualquier valor en `TUTOR_API_KEY`. Si cambias de proveedor en producción,
actualiza también el apartado 4 de `privacidad.html`.

## Pruebas

- `cd backend && python -m pytest -q tests/test_tutor.py`: endpoint, validación, límite, fallos del
  proveedor y que la pregunta no acaba en los logs. Nunca llama al proveedor real.
- `npx playwright test e2e/tutor.spec.js`: el panel con y sin tutor, con y sin sesión, el envío del
  código, el historial, los errores y axe (WCAG 2.2 AA). El proveedor se simula con `page.route`.
