# ADR-0023: Proteger la web con la matriz MITRE ATT&CK

- **Estado:** Aceptada e implementada, salvo lo marcado como NEEDS_HUMAN
- **Fecha:** 2026-09-29
- **Relacionada con:** [ADR-0022](0022-seguridad-integral.md) (endurecimiento previo)

## Contexto

El autor pidió usar la matriz MITRE ATT&CK para proteger la web.

ADR-0022 ya había cerrado los hallazgos de una auditoría. Faltaban dos cosas:

- revisar las amenazas con un **marco común**, técnica por técnica, para ver qué queda sin cubrir;
- poder **detectar** los ataques: hasta ahora solo se bloqueaban y no quedaba rastro.

ATT&CK describe lo que hace un atacante (tácticas y técnicas) y enlaza cada técnica con mitigaciones (M-IDs) y fuentes de detección. Se usó ATT&CK Enterprise v19, comprobando en attack.mitre.org las técnicas y mitigaciones clave (T1110, T1606.001, T1499, T1550.001, T1087.004, T1204.004, T1539 y T1531).

## Decisión

### PROPUESTA

1. **Modelo de amenazas por táctica** en `docs/security/mitre-attack.md`. Cada fila recoge:
   - técnica y escenario;
   - controles con su M-ID y el fichero que lo prueba;
   - evento de detección;
   - estado ✔/◐/✘.

   Va acompañado de una **capa de ATT&CK Navigator** (`docs/security/attack-navigator-layer.json`) con el mismo contenido en colores.
2. **Registro de eventos de seguridad (M1047 Audit)** en `backend/app/security_events.py`: el logger `pld.security` escribe una línea JSON por evento, con el ID de la técnica. Estos son los eventos:
   - login fallido o correcto;
   - cuenta bloqueada;
   - límite de IP;
   - **token falsificado** (firma o algoritmo ajenos, T1606.001);
   - **token revocado reutilizado** (T1550.001/T1539);
   - cierre de sesión en todas partes;
   - recuperación pedida o completada;
   - borrado de cuenta (y un intento de borrado sin la contraseña);
   - cuerpo demasiado grande (T1499.003).
3. **Seudonimización en el registro:**
   - la IP y el email nunca aparecen en claro: se guarda un HMAC-SHA256 con el secreto del servidor, truncado a 16 caracteres hexadecimales;
   - así se puede correlacionar (misma IP contra muchas cuentas = *password spraying*) sin saber quién es;
   - contraseñas, tokens y enlaces nunca se registran.
4. **Política de contraseñas (M1027)** en `backend/app/password_policy.py`, aplicada al registrarse y al restablecer la contraseña. Rechaza:
   - las contraseñas más comunes (lista local, con variantes en español);
   - las que repiten uno o dos caracteres;
   - las secuencias de números;
   - las que contienen el email o una parte del nombre de 4 o más letras (sin tener en cuenta tildes).

   La respuesta es 422 con el motivo en español, y el enlace de recuperación sigue sin usar si la contraseña no vale.
5. **Abuso del bloqueo (T1531):** restablecer la contraseña levanta el bloqueo de la cuenta, porque quien controla el email recupera el acceso aunque un atacante la haya bloqueado a base de fallos.
6. **Aviso al pegar código (T1204.004, M1017):** la consola avisa, sin bloquear, cuando se pega código que usa `js`, `pyodide`, `fetch`, `localStorage`, `eval`… El código del alumno ya corre en un Worker sin acceso a `localStorage` ni al DOM (M1048).

### BENEFICIOS

- Hay un **inventario comprobable**: cada técnica relevante tiene un estado y una evidencia, y lo que falta queda a la vista y priorizado.
- **Detección**: los ataques dejan rastro buscable en los logs de Render por ID de técnica (`"attack": "T1110"`), sin añadir servicios.
- Las contraseñas débiles, que son la vía más barata para T1110.003 y T1110.004, dejan de aceptarse.
- Se cumple el RGPD: minimización y seudonimización (art. 25 y 32) en los registros.

### PROBLEMAS

- **Nadie mira los logs todavía:** la detección sin alertas es solo forense. Ver «Pendientes».
- La lista de contraseñas comunes es corta: no sustituye a una comprobación contra filtraciones (Have I Been Pwned). Se descartó para no enviar datos de la contraseña a un tercero ni depender de un servicio externo.
- El seudónimo depende de `JWT_SECRET`: al rotarlo se pierde la correlación con los eventos anteriores. Es aceptable.
- El aviso al pegar puede dar falsos positivos, por ejemplo con código que menciona `base64`. Por eso solo avisa.

### TRADE-OFFS

- **Registro 409 al registrarse (T1589.002):** revela que un email tiene cuenta. Ocultarlo exigiría confirmar el email antes de crear la cuenta, que es un flujo nuevo y depende del SMTP. Se acepta con el límite por IP como freno.
- **Token en `localStorage` (T1539):** una XSS podría leerlo. Las alternativas son:
  - una cookie `HttpOnly` con `SameSite=Strict`, que exige que la web y la API compartan un dominio registrable. Hoy son `github.io` y `onrender.com`: una cookie entre sitios necesitaría `SameSite=None` y protección CSRF;
  - mitigarlo con la CSP estricta, el escapado y los tests e2e, más la caducidad de 1 hora y `token_version`.

  Se elige la segunda opción. Se reconsiderará con un dominio propio.
- **Sin MFA (M1032):** es la mitigación más fuerte contra T1078 y T1110, pero el coste en complejidad es alto para un proyecto de estudio sin datos de pago. Queda en pendientes.
- **Bloqueo por cuenta frente a T1531:** el bloqueo frena la fuerza bruta, pero un atacante puede usarlo para echar a alguien. Se limita a 15 minutos y restablecer la contraseña lo levanta.

### RECOMENDACIÓN

Implementar los puntos 1 a 6 (hecho) y, en este orden:

1. **NEEDS_HUMAN:** activar en GitHub secret scanning, push protection, CodeQL y la protección de `main` (`SECURITY.md`).
2. Enviar los logs de Render a un servicio con alertas para `auth.token_forged` y ráfagas de `auth.login_failed`. VERIFY: qué ofrece el plan de Render.
3. Fijar las GitHub Actions por SHA.
4. Con un dominio propio, pasar el token a una cookie `HttpOnly`.
5. MFA opcional con TOTP.

## Verificación

- **DONE:** `pytest` pasa con 456 tests y cobertura del 100 % (`tests/test_attack_detection.py` cubre cada evento, la seudonimización, la política de contraseñas y el levantamiento del bloqueo). `ruff` está limpio. Los e2e de `security.spec.js` (aviso al pegar y registro con una contraseña común), `account.spec.js` y `daw.spec.js` están en verde.
- **VERIFY:**
  - que la capa JSON se abre en ATT&CK Navigator (formato de capa 4.5);
  - la retención de los logs de Render y de las copias de Neon en el plan gratuito;
  - las técnicas marcadas sin ✓id en el modelo, que no se comprobaron una a una en attack.mitre.org.
- **ASSUMPTION:** Render conserva las líneas de `logging` de la aplicación en su panel de *Logs*, como hace con el resto de la salida estándar.
