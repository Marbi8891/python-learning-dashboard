# Recuperación de contraseña

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
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Envío del email. Puerto 587 con STARTTLS o 465 con TLS directo. Prueba: `python -m app.mailer tu@email.com`. Pasos en [DEPLOY.md](DEPLOY.md#5-emails-de-recuperación-de-contraseña) |

Sin `SMTP_HOST` no se envía nada, y la web ofrece el email de contacto en lugar del formulario.

## Límites conocidos

- Los límites viven en memoria: con varias instancias del backend, cada una cuenta por separado (ADR-0022). Hoy hay una sola instancia.
- Si la cuenta existe, se escriben filas en la base de datos (unos milisegundos). Igualarlo del todo exigiría escrituras ficticias, y no compensa.

## Tests

- `backend/tests/test_password_reset.py`: las dos rutas, emails mal formados, anti-enumeración, hash, token manipulado, caducidad exacta, usuario inexistente, límite por IP, cabeceras falsas, secretos en logs, payloads grandes y reutilización.
- También `test_account.py`, `test_hardening.py` y `test_attack_detection.py`.
- `e2e/account.spec.js`: solicitud, enlace no válido, contraseñas distintas, enlace incompleto y vuelta al login.
- El email nunca se envía en los tests: se sustituye `send_email` por un buzón falso.
