# Recuperación de contraseña e inicio de sesión con Google

Cómo recupera el acceso quien ha olvidado su contraseña, y qué protege cada paso. Reutiliza la autenticación existente (Argon2, JWT con `token_version`, límites y eventos de seguridad): no hay un segundo sistema.

## Flujo

1. **Login → «¿Has olvidado tu contraseña?»**: la persona escribe su correo y pulsa «Enviar instrucciones».
2. `POST /api/v1/auth/forgot-password` (o `/auth/password-reset/request`, que usan la web y Android) responde **siempre** `202` con el mismo mensaje, exista o no la cuenta.
3. Si la cuenta existe, se borra cualquier enlace anterior, se crea uno nuevo y se envía por email en segundo plano: `FRONTEND_URL/#/restablecer?token=…`.
4. La web abre el formulario «Nueva contraseña» + «Repite la nueva contraseña» y quita el token de la barra de direcciones.
5. `POST /api/v1/auth/reset-password` (o `/auth/password-reset/confirm`) con `{token, new_password}` responde `204`. Si el enlace no vale: `400` «Este enlace de recuperación no es válido o ha caducado. Pide uno nuevo.»
6. La web muestra «Tu contraseña se ha actualizado correctamente» y vuelve al login.

## Decisiones de seguridad

| Riesgo | Medida |
|---|---|
| Enumeración de cuentas | Misma respuesta y código para cualquier email. El email se envía en segundo plano, así que el tiempo de respuesta no depende del SMTP |
| Adivinar el token | `secrets.token_urlsafe(32)` (256 bits). Límite por IP en todo `/auth/*`. Cada intento fallido deja el evento `auth.password_reset_failed` (T1110) |
| Robo de la base de datos | Solo se guarda el **SHA-256** del token (`password_reset_tokens.token_hash`), nunca el token |
| Enlace viejo o reutilizado | Caduca a los `PASSWORD_RESET_MINUTES` (30 por defecto, UTC; deja de valer cuando `now >= expires_at`). Un solo uso: `UPDATE … WHERE used_at IS NULL` atómico, así que de dos peticiones simultáneas solo gana una. Pedir otro borra los anteriores: como mucho hay **uno activo** |
| Bombardeo de emails a una víctima | Como mucho 3 emails por cuenta cada 15 minutos, aunque lleguen de muchas IPs. La respuesta no cambia al superarlo |
| Password reset poisoning y Host header | El enlace sale de `FRONTEND_URL` (configuración), nunca de `Host`, `X-Forwarded-Host`, `Origin` ni `Referer` |
| Open redirect | No hay parámetro de redirección: después del cambio la web siempre vuelve a su propio login |
| Fuga del token | Va en el fragmento `#`, que el navegador no envía a ningún servidor ni en `Referer`. No aparece en respuestas de la API ni en logs. Sin SMTP no se envía ni se registra |
| Sesiones robadas | Al cambiar la contraseña se incrementa `token_version`: todas las sesiones abiertas (cookie o Bearer) dejan de valer |
| Bloqueo malicioso | Quien controla el email recupera el acceso aunque un atacante haya bloqueado la cuenta a base de fallos |
| CSRF | Los dos endpoints no usan sesión ni cookie, así que no hay nada que falsificar |
| Contraseña débil | Misma política que el registro (8–128 caracteres, sin las más comunes ni el email o el nombre). Se comprueba **antes** de gastar el enlace. Argon2 no trunca |
| Datos en logs | Los eventos solo llevan seudónimos (HMAC) del email y de la IP. Nunca la contraseña, el token ni el contenido del email |

## Configuración

| Variable | Para qué |
|---|---|
| `FRONTEND_URL` | Base de los enlaces del email (equivale a `PASSWORD_RESET_URL_BASE`) |
| `PASSWORD_RESET_MINUTES` | Vida del enlace, 30 por defecto (equivale a `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`) |
| `BREVO_API_KEY` + `SMTP_FROM` | Envío por la API HTTPS de Brevo. Es lo que funciona en el plan gratuito de Render, que bloquea SMTP. Tiene prioridad sobre SMTP |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Envío del email. Puerto 587 con STARTTLS o 465 con TLS directo. Prueba: `python -m app.mailer tu@email.com`. Pasos en [DEPLOY.md](DEPLOY.md#5-emails-de-recuperación-de-contraseña) |

Sin `BREVO_API_KEY` ni `SMTP_HOST` no se envía nada, y la web ofrece el email de contacto en lugar del formulario.

## Límites conocidos

- Los límites viven en memoria: con varias instancias del backend, cada una cuenta por separado (ADR-0022). Hoy hay una sola instancia.
- Si la cuenta existe, se escriben filas en la base de datos (unos milisegundos). Igualarlo del todo exigiría escrituras ficticias, y no compensa.

## Inicio de sesión con Google

1. La web descarga Google Identity Services (`accounts.google.com/gsi/client`) **solo** al abrir el
   inicio de sesión o «Eliminar mi cuenta», y solo si `config.js` tiene `googleClientId` y
   `/api/health` no dice `"google": false`.
2. `POST /api/v1/auth/google` con `{credential, accept_privacy}`. El servidor valida el ID token con la
   biblioteca oficial (`google.oauth2.id_token.verify_oauth2_token`: firma, audiencia = `GOOGLE_CLIENT_ID`,
   caducidad) y exige `email_verified`. Cuenta nueva: hace falta aceptar la privacidad.
3. **Cuenta existente sin email verificado** (creada con contraseña y nunca recuperada por email):
   la contraseña se anula, se cierran las demás sesiones y se registra `google_linked` (PLD-SEC-008).
   Google y el enlace de recuperación rellenan `users.email_verified_at`.
4. La sesión es la misma que con contraseña (cookie `HttpOnly` o token en memoria, ADR-0033).
5. **Borrar la cuenta**: `POST /api/v1/users/me/delete` con la sesión y **exactamente uno** de
   `password` o `google_credential` (un ID token nuevo del mismo email). Si no, 422.

Errores: 401 si la credencial no vale o es de otra audiencia, 403 si en el borrado es de otra cuenta,
503 si el servidor no tiene `GOOGLE_CLIENT_ID`. Ninguno repite el token ni el email.

## Tests

- `backend/tests/test_password_reset.py`: las dos rutas, emails mal formados, anti-enumeración, hash, token manipulado, caducidad exacta, usuario inexistente, límite por IP, cabeceras falsas, secretos en logs, payloads grandes y reutilización.
- También `test_account.py`, `test_hardening.py` y `test_attack_detection.py`.
- `e2e/account.spec.js`: solicitud, enlace no válido, contraseñas distintas, enlace incompleto y vuelta al login.
- El email nunca se envía en los tests: se sustituye `send_email` por un buzón falso.
- Google: `backend/tests/test_google_auth.py` (sin llamadas a Google: se sustituye `verify_oauth2_token`) y `e2e/account.spec.js` con un Google Identity falso. Son pruebas **simuladas**: el inicio de sesión real con Google se prueba a mano con una cuenta de prueba (ver [DEPLOY.md](DEPLOY.md)).
