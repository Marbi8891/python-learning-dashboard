# ADR-0003: Autenticación, progreso y corrección de ejercicios

- **Estado:** Aceptada
- **Fecha:** 2026-09-25

## Contexto

El frontend está en `marbi8891.github.io` y la API estará en otro dominio. Hacen falta cuentas de usuario, progreso sincronizado entre dispositivos y registro de ejercicios. Ejecutar en el servidor código escrito por usuarios es el mayor riesgo del proyecto.

## Decisiones

### 1. Sesión: JWT en la cabecera `Authorization: Bearer`

| Opción | A favor | En contra |
|---|---|---|
| **A. Bearer JWT** (elegida) | Funciona entre dominios distintos sin configurar cookies; sin estado en el servidor | Si hay XSS, el token se puede robar (el frontend nunca inyecta HTML sin escapar: ADR-0002) |
| B. Cookie `HttpOnly` | El JavaScript no puede leer el token | Entre dominios exige `SameSite=None`, CSRF y choca con el bloqueo de cookies de terceros |

- Token de 60 minutos (`ACCESS_TOKEN_MINUTES`) y sin *refresh token* en el MVP: al caducar, se vuelve a iniciar sesión. Se añadirá cuando haga falta.
- `JWT_SECRET` es obligatorio y de al menos 32 caracteres: la API **no arranca** sin él.

### 2. Contraseñas

- Hash con **Argon2** (`argon2-cffi`), entre 8 y 128 caracteres.
- El login devuelve el mismo error y tarda lo mismo exista o no el email, para no revelar qué cuentas existen.
- Límite de 5 intentos de login o registro por minuto e IP. Se guarda en memoria, así que vale para una sola instancia; con varias habría que usar Redis.

### 3. Progreso

- Tabla `lesson_progress` con restricción única por usuario y lección. Marcar como completada es idempotente.
- `POST /api/progress/import` fusiona el progreso guardado en el navegador (`localStorage`) al iniciar sesión.

### 4. Corrección de ejercicios

- **Los tests se ejecutan en el navegador** (Pyodide). El backend **no ejecuta código**: solo guarda el intento (`code` de máximo 20 000 caracteres y `passed`) y, si ha superado los tests, marca la lección como completada.
- Consecuencia aceptada: un usuario podría enviar `passed: true` sin resolver el ejercicio. En una app para aprender solo se engaña a sí mismo. **Este resultado no sirve para certificar a nadie.**
- Si algún día hiciera falta una corrección fiable (por ejemplo, para certificar), habría que usar un sandbox aislado: contenedor efímero sin red, con límites de CPU, memoria y tiempo, y usuario sin privilegios. Requiere su propio ADR.

### 5. Esquema de base de datos

- Migraciones con **Alembic** desde ahora, porque ya hay datos de usuarios que no se pueden perder.
- Un test y la CI comprueban que los modelos y las migraciones coinciden (`alembic check`), también en PostgreSQL.

### 6. Recuperación de contraseña y RGPD (añadido en 0.3.0)

- **Recuperación de contraseña:**
  - Token aleatorio de un solo uso que caduca a los 30 minutos. Solo se guarda su hash SHA-256.
  - Pedir un enlace nuevo invalida el anterior.
  - La respuesta es siempre la misma, exista o no el email, y el email se envía en segundo plano.
- **Cambio de contraseña:** `token_version` se incrementa, así que dejan de valer todas las sesiones abiertas.
- **Exportación** (`/api/users/me/export`) y **borrado de cuenta** (pide la contraseña). El borrado elimina de forma explícita el progreso, los intentos y los tokens, sin depender de `ON DELETE CASCADE`.
- **Consentimiento de privacidad:** es obligatorio para registrarse y se guarda su fecha (`privacy_accepted_at`).
