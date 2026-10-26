# Política de seguridad

## Cómo avisar de una vulnerabilidad

**No abras un issue público.** Usa una de estas dos vías, con los pasos para reproducirla:

1. [Informe privado de vulnerabilidad](../../security/advisories/new) en GitHub.
2. Email a **mrabehfathiprofesional@gmail.com**, con el asunto «Seguridad».

Recibirás respuesta en un plazo de 7 días.

## Versiones con soporte

Solo la última versión de `main`, que es la que está desplegada:

- la web (GitHub Pages);
- la API (Render).

## Medidas del proyecto

**Contraseñas**
- Se guardan como hash con Argon2id.
- El login tarda lo mismo aunque el email no exista y da un mensaje genérico.

**Sesiones**
- El token JWT caduca a los 30 minutos. En la web va en una cookie `HttpOnly; Secure; SameSite=None; Partitioned` que JavaScript no puede leer, y la API solo la acepta junto con la cabecera `X-PLD-Session` (protección CSRF). Si el navegador bloquea la cookie, el token se guarda solo en memoria, nunca en `localStorage`.
- Se puede cerrar la sesión en todos los dispositivos (`/api/auth/logout-all`).
- Cambiar la contraseña invalida todos los tokens emitidos.

**Límites de intentos**
- Por IP real: detrás de Render se toma la última IP de `X-Forwarded-For`, que es la que no puede falsear el cliente.
- Por cuenta: 10 fallos bloquean la cuenta 15 minutos.
- Emails de recuperación: 3 cada 15 minutos por cuenta.

**API**
- Solo acepta el origen de la web (CORS).
- Las respuestas llevan las cabeceras de seguridad y `Cache-Control: no-store`.
- Los cuerpos de las peticiones se limitan a 300 KB.
- `/docs` está desactivado en producción.
- La conexión a la base de datos va siempre por TLS.

**Datos personales (RGPD)**
- Se puede descargar y borrar todo desde la cuenta.
- Al cerrar sesión se borran también del navegador.
- Solo se guardan los 50 intentos de ejercicio más recientes por lección.
- Los emails se enmascaran en los logs, y los enlaces de recuperación no se escriben nunca en ellos.

**Web**
- Content-Security-Policy.
- Protección contra el *clickjacking* (que otra página muestre la web dentro de un marco para engañar al usuario).
- Todo lo que viene de fuera, es decir, del navegador, de la cuenta o del código del alumno, se valida o se escapa antes de convertirlo en HTML.
- Python se ejecuta en un Web Worker aislado.

**Dependencias**
- La CI pasa `pip-audit` y `npm audit`.
- El token de las GitHub Actions es de solo lectura.

**Secretos**
- `backend/.env` y las claves están en `.gitignore`.
- `JWT_SECRET` es obligatorio y tiene al menos 32 caracteres.

**Registro de eventos**
- El logger `pld.security` escribe una línea JSON por evento: fallos de login, bloqueos, tokens falsos o revocados, recuperaciones y borrados.
- La IP y el email van seudonimizados (HMAC con el secreto del servidor).
- No se aceptan las contraseñas más comunes ni las que contienen el email o el nombre.
