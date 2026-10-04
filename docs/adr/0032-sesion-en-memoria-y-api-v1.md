# ADR-0032: Token de sesión solo en memoria y API versionada (`/api/v1`)

- **Estado:** Aceptada (el autor la aprobó el 2026-10-04). Pendiente de fusionar en `main`.
- **Fecha:** 2026-10-04
- **Revisa:** ADR-0003 (autenticación), ADR-0022 (seguridad integral)

## Contexto

La rama `security/hardening-defaults` trae cuatro cambios:

- el token de acceso pasa de `localStorage` a una variable en memoria;
- el token caduca a los 30 minutos (antes, 60);
- las respuestas de la API llevan su propia CSP;
- la API se versiona en `/api/v1`. Las rutas `/api/...` antiguas siguen funcionando, marcadas como *deprecated*.

La rama no actualizaba los e2e (6 fallaban) y no pasaba el lint. Hay que integrarla con el núcleo educativo (ADR-0031).

## Opciones

| Opción | A favor | En contra |
|---|---|---|
| A. Token en `localStorage` (como hasta ahora) | La sesión sobrevive a recargar | Un XSS puede robar el token y usarlo fuera del navegador |
| **B. Token solo en memoria** | No queda guardado nada que se pueda robar después | Recargar la página cierra la sesión: no hay token de refresco |
| C. Cookie `HttpOnly` y token de refresco | Lo más seguro y sin perder la sesión | Con la web y la API en dominios distintos exige `SameSite=None` y protección CSRF, o un dominio común |

## Decisión

Se elige **B** como paso intermedio. El objetivo es **C** cuando la web y la API compartan dominio.

**Por qué es asumible:**

- **Sin cuenta:** el progreso vive en el navegador (`pld:*`), así que recargar no pierde nada.
- **Con cuenta:** al volver a iniciar sesión se fusiona con la copia de la cuenta (web, app y conceptos), sin pérdidas.

**Al integrarla:**

- se corrige el lint de la rama;
- los e2e que leían el token de `localStorage` inician sesión por la interfaz o por la API;
- un test nuevo comprueba que **no queda ningún JWT en el almacenamiento del navegador** y que el progreso local sobrevive a la recarga;
- los tests que interceptaban `/api/health` y `/api/auth/login` pasan a usar `/api/v1`.

**El núcleo educativo no cambia de código:** usa `request("/api/course-state/learn")` y `api.js` lo dirige a `/api/v1`.

## Consecuencias

- **Recargar cierra la sesión.** Si en el uso diario resulta incómodo, el siguiente paso es la opción C, no volver a A.
- **La app Android sigue en las rutas antiguas** (`/api/...`), que se mantienen por compatibilidad. **Pendiente:** pasarla a `/api/v1` y, después, retirar esas rutas.
- **`docs/security/revision-2026-10.md`:** se actualiza el riesgo del token.
