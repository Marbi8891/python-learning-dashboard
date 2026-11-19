# Tutor de programación con NEXARO Personal AI

Función **opcional y solo local**. El panel del asistente de cada lección puede ofrecer, además de
las respuestas preparadas, un tutor con IA. El tutor guía con pistas y preguntas, y no da la
solución hasta que el alumno ha hecho un intento y la pide. Lo responde NEXARO Personal AI, el
asistente del autor que funciona con Ollama en su propio ordenador. No usa servicios de pago.

## Cómo funciona

```
navegador ──POST /api/v1/tutor──▶ backend de PLD ──POST /api/v1/chat (mode: tutor)──▶ NEXARO ──▶ Ollama
          ◀── respuesta + conversación firmada ──┘
```

- **Desactivado por defecto.** Sin `NEXARO_URL` y `NEXARO_API_KEY`, `/api/v1/health` devuelve
  `tutor: false`, el formulario no aparece y `/api/v1/tutor` responde 404. La web de GitHub Pages
  nunca lo tiene: no puede llegar al ordenador del autor.
- **La clave de NEXARO solo está en el backend.** El navegador nunca la recibe.
- **El ejercicio lo pone el servidor.** El navegador envía la lección, la pregunta y, si el alumno
  lo marca, su código. El enunciado se lee de la base de datos. El código del alumno no puede
  cerrar ni falsificar los delimitadores del contexto.
- **Cada conversación es del alumno que la empezó.** Todas las conversaciones pertenecen a la misma
  clave de NEXARO. Por eso el id viaja firmado con HMAC para ese usuario. Un id ajeno o manipulado
  empieza una conversación nueva: así nadie continúa la de otro ni el modelo recibe un historial
  ajeno.
- **Límites.** 10 preguntas por alumno y minuto (`TUTOR_RATE_LIMIT_PER_MINUTE`), pregunta de hasta
  2.000 caracteres y código de hasta 8.000. El tiempo de espera es de 200 s, porque un modelo local
  en CPU tarda.
- **Estado y reintento.** Al abrir el panel, la web pregunta `GET /api/v1/tutor/status` (con sesión).
  El backend consulta la salud pública de NEXARO (`/api/health`, 5 s como mucho, sin la clave ni datos
  del alumno) y responde `{available}`. El panel muestra «Comprobando», «Tutor conectado», «no
  disponible» o «no se pudo comprobar», con un botón **Reintentar**. Sin tutor, el resto de la lección
  (respuestas preparadas, consola, ejercicios) funciona igual.
- **El código solo viaja si el alumno lo marca.** La casilla «Enviar también mi código» empieza
  desmarcada.
- **Errores.** Si NEXARO no responde o falla, el alumno ve «El tutor no responde ahora mismo» y el
  panel pasa a «no disponible». El detalle interno de NEXARO no se reenvía. La web espera hasta 210 s
  (el backend, 200 s) porque un modelo en CPU tarda.
- NEXARO aplica su propio filtro: no responde preguntas sobre su modelo ni su infraestructura.

## Activarlo en local (Docker en el Mac)

1. En NEXARO Personal AI (<http://127.0.0.1:8001>), crea una organización y, en **Developer**, una
   clave de API con el permiso de chat. Copia el secreto: solo se muestra una vez.
2. En la raíz de este repositorio, crea un archivo `.env` (está en `.gitignore`):

   ```
   JWT_SECRET=<mínimo 32 caracteres>
   NEXARO_URL=http://host.docker.internal:8001
   NEXARO_API_KEY=<el secreto de la clave>
   ```

3. Ejecuta `docker compose up --build` y abre <http://localhost:5500>. Inicia sesión: el tutor
   necesita una cuenta. En una lección, abre el asistente.

VERIFY: Docker Desktop para Mac hace llegar `host.docker.internal` a los puertos del Mac
publicados en `127.0.0.1`, como el 8001 de NEXARO. En Linux no es así.

## Por qué no se conecta la web de GitHub Pages directamente a NEXARO

El PR #180 empezó con un widget que llamaba desde `https://marbi8891.github.io` a
`http://127.0.0.1:8001/api/chat` con la cookie de sesión de NEXARO. Se descartó (19/11/2026) porque
no puede funcionar ni es seguro:

- **CORS.** NEXARO no tiene `CORSMiddleware`: el navegador bloquea la respuesta a otro origen.
- **Origin.** `/api/chat` usa cookie y comprueba `Origin` contra `ALLOWED_ORIGINS` (CSRF): GitHub
  Pages no está ni debe estar.
- **Cookies de terceros.** Desde github.io la cookie de `127.0.0.1` es de terceros: Chrome, Safari y
  Firefox la bloquean o la van a bloquear.
- **Red local.** Chrome pide permiso para que una web pública llame a la red local (Private
  Network Access / Local Network Access). Safari trata `http://127.0.0.1` desde HTTPS como contenido
  mixto.
- **CSP publicada.** `scripts/security/production_csp.py` rechaza orígenes `http:` en la web
  publicada: el cambio de CSP del PR rompía `test_production_csp.py`.
- **Seguridad.** Abrir NEXARO a github.io dejaría que cualquier XSS de la web pública hablara con
  el asistente del autor.

Con el backend de PLD en medio la conexión es de servidor a servidor: no hace falta CORS en NEXARO, la
clave no llega al navegador y la web publicada no cambia.

## Decisión (DEC-022 en `DECISIONS.md`)

El 26/10/2026 el autor retiró el tutor con IA para simplificar el proyecto (PR #62). El 17/11/2026
decidió recuperarlo con estas condiciones: opcional, desactivado por defecto, solo local, gratuito,
con la clave solo en el backend y sin dependencias nuevas (`httpx` ya lo usaba el backend).

Trade-offs:

- Un modelo pequeño en CPU es lento (decenas de segundos) y puede equivocarse o saltarse la regla
  de no dar la solución. NEXARO lo mide con `make eval` (categoría `tutor`).
- El tutor solo existe mientras el ordenador del autor tiene NEXARO encendido.

## Datos personales

El tutor envía a NEXARO la pregunta y, si el alumno lo marca, su código. NEXARO guarda la
conversación en su base de datos, en el mismo ordenador. Ver RAT-6 en `REGISTRO_TRATAMIENTOS.md`.

NEEDS_HUMAN: antes de activarlo en un despliegue público habría que actualizar `privacidad.html` y
revisar dónde corre el modelo.

## Código y pruebas

- Backend: `backend/app/routers/tutor.py` y `backend/tests/test_tutor.py`. NEXARO se simula, así que
  las pruebas no salen a la red.
- Frontend: `frontend/js/assistant.js` y `e2e/tutor.spec.js`. Esta prueba simula `/health` y
  `/tutor` e incluye la auditoría WCAG del panel en tema claro y oscuro.
