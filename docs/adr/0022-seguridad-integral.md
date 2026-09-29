# ADR-0022: Seguridad integral de la web, la API y los datos personales

- **Estado:** Aceptada e implementada, salvo las acciones manuales indicadas
- **Fecha:** 2026-09-29

## Contexto

El autor pidió que la web fuera segura en todos los sentidos: para quien la visita, en el tratamiento de los datos personales y en todo lo demás.

Se hicieron tres auditorías de solo lectura, con evidencias de fichero y línea:

- backend y despliegue;
- frontend;
- cadena de suministro y repositorio.

No apareció nada crítico. Estos fueron los hallazgos principales.

| # | Gravedad | Hallazgo |
|---|---|---|
| 1 | Alta | El límite de intentos se podía **saltar falsificando `X-Forwarded-For`**. Con `--forwarded-allow-ips='*'`, uvicorn tomaba la primera IP de la cabecera, que escribe el cliente, y así se abría la fuerza bruta de contraseñas. |
| 2 | Alta | **XSS desde el código Python del alumno**: la salida del Worker (`hint.line`, `case/total`) acababa en `innerHTML` sin escapar. Con ingeniería social («pega este código») se podía robar la sesión. |
| 3 | Alta | Los workflows `ci.yml` y `android.yml` no tenían `permissions:`. El token se quedaba en `.git/config` mientras se instalaban dependencias de terceros. |
| 4 | Media | No había límite por cuenta y el diccionario del limitador crecía sin fin. Argon2 usaba 64 MiB por hash en una instancia de 512 MB: unos pocos logins simultáneos la dejaban sin memoria. |
| 5 | Media | Sin SMTP, **el enlace de recuperación se escribía en el log**, y quien leyera los logs podía tomar cualquier cuenta. Además, `starttls()` no verificaba el certificado. |
| 6 | Media | El tamaño del cuerpo no tenía límite antes de parsearlo y los intentos de ejercicio no tenían límite (se podía agotar la memoria o la base de datos). |
| 7 | Media | Los datos de `localStorage` y de la cuenta se pintaban sin validar, así que era posible una XSS persistente en un equipo compartido. |
| 8 | Media | Al cerrar sesión quedaban en el navegador el progreso, los borradores y otros datos, y se mezclaban entre cuentas en equipos compartidos. |
| 9 | Media | No había Content-Security-Policy ni defensa contra marcos (*clickjacking*). |
| 10 | Media | `package.json` incluía el SDK de AWS y `dotenv`, que no se usaban: 29 paquetes de superficie de ataque sin valor. Dependabot no cubría npm, Gradle ni Docker, y la CI no escaneaba dependencias. |
| 11 | Baja | Otros hallazgos menores:<br>• `/docs` era público;<br>• faltaba `Cache-Control: no-store`;<br>• no había cierre de sesión en el servidor;<br>• carrera al usar el enlace de recuperación;<br>• TLS a la base de datos no impuesto;<br>• el JWT no exigía `exp`;<br>• el service worker borraba cachés ajenas del mismo origen;<br>• la analítica podía enviar el token de recuperación;<br>• la política de privacidad estaba incompleta;<br>• faltaban entradas en `.gitignore` y `.dockerignore`;<br>• la clave de firma no se borraba si fallaba la compilación. |

## Decisión: qué se ha corregido

**Backend** (tests en `tests/test_hardening.py`; cobertura del 100 %):

- **IP real:**
  - `TRUSTED_PROXY_HOPS=1` (definido en el Dockerfile) y se usa la **última** IP de `X-Forwarded-For`, que es la que añade Render.
  - Se han quitado `--proxy-headers` y `--forwarded-allow-ips='*'`.
- **Límites:**
  - **Por cuenta:** 10 fallos bloquean la cuenta 15 minutos, vengan de la IP que vengan.
  - **Emails de recuperación:** 3 cada 15 minutos.
  - El limitador purga las claves caducadas.
- **Argon2id** con los parámetros mínimos de OWASP: 19 MiB, t=2, p=1. Los hashes antiguos se rehacen al iniciar sesión.
- **Sesiones:**
  - nuevo endpoint `POST /api/auth/logout-all`, que incrementa `token_version`;
  - el JWT exige `exp` y `sub`;
  - el enlace de recuperación se marca como usado con un UPDATE condicional (un solo uso aunque lleguen peticiones simultáneas).
- **Email:**
  - STARTTLS con el contexto por defecto, que verifica el certificado y el nombre;
  - no se registra nunca el cuerpo del mensaje;
  - los emails aparecen enmascarados en el log.
- **Tamaño:**
  - middleware ASGI que responde 413 a partir de 300 KB, también sin `Content-Length`;
  - solo se guardan los 50 intentos más recientes por lección.
- **Respuestas:** `Cache-Control: no-store` en toda la API. `/docs`, `/redoc` y `/openapi.json` solo existen con `ENABLE_DOCS=true` (activado en `docker-compose` para desarrollo).
- **Base de datos:** a una URL remota de Postgres sin `sslmode` se le añade `sslmode=require`.
- **Docker:** el usuario sin privilegios ya no es dueño del código.

**Frontend** (tests en `e2e/security.spec.js`):

- **XSS por la salida del Worker:** solo se aceptan números y cadenas. Además:
  - `progress-guard.js` valida los tipos de todo el progreso que llega de `localStorage` o de la cuenta;
  - `safeUrl` solo admite enlaces `https://`;
  - `contactEmail` se escapa.
- **Cerrar sesión o borrar la cuenta:**
  - antes se sube lo pendiente;
  - después se borran del navegador todas las claves `pld:*` salvo las preferencias, y la página se recarga para que no quede nada en memoria;
  - una opción permite cerrar la sesión en todos los dispositivos.
- **Content-Security-Policy** en `<meta>`, en las 4 páginas:
  - `script-src 'self'` más la ruta exacta de Pyodide en jsDelivr, con `wasm-unsafe-eval`;
  - `connect-src` limitado a la API;
  - `object-src 'none'`, `base-uri 'self'` y `form-action`;
  - el script en línea pasa a `js/theme-init.js`.
  - Un test comprueba que ninguna página de la app provoca infracciones de la CSP.
- **Clickjacking:** si la web se carga dentro de un marco, no se muestra. Hace falta así porque GitHub Pages no permite enviar `X-Frame-Options`, y `frame-ancestors` no funciona en `<meta>`.
- **Otros cambios:**
  - `Referrer-Policy: strict-origin-when-cross-origin`;
  - el service worker solo borra sus propias cachés;
  - la analítica respeta Global Privacy Control y no envía nunca lo que va tras `?` en la ruta.
- **Política de privacidad actualizada:**
  - aviso del *ping* al servidor;
  - todos los datos que se sincronizan;
  - «hash» en lugar de «cifrado»;
  - borrado de los datos del navegador al cerrar sesión;
  - límite de 50 intentos por lección;
  - nueva sección de seguridad.

**Cadena de suministro:**

- `permissions: contents: read` y `persist-credentials: false` en todos los workflows.
- `pip-audit` y `npm audit` en la CI.
- Validación del wrapper de Gradle.
- La clave de firma se borra con `trap`, falle o no la compilación.
- Dependabot cubre pip, npm, Gradle, Docker y Actions.
- Se han quitado el SDK de AWS y `dotenv`.
- `.gitignore` y `.dockerignore` más completos (claves, `.env.*`, cobertura, `.local-secret`).
- `SECURITY.md` con dos canales de contacto y plazo de respuesta.

## Trade-offs

- **Estilos en línea en la CSP:** se mantiene `style-src 'unsafe-inline'`, porque los medidores usan atributos `style` y `style-src-attr` no funciona en todos los navegadores. El riesgo es solo de inyección CSS: los scripts siguen restringidos.
- **Pyodide en la CSP:** se permite la ruta de Pyodide en jsDelivr por si algún navegador aplica la CSP del documento al Worker. Solo es esa ruta de esa versión.
- **Borrado al cerrar sesión:** borrar el progreso local también afecta a quien usa su propio ordenador. No pierde nada, porque está en su cuenta y vuelve al iniciar sesión.
- **Enumeración de emails en el registro:** el registro sigue diciendo «ese email ya está registrado». Es habitual en apps pequeñas y se asume. El login y la recuperación no revelan qué cuentas existen.

## Pendiente (NEEDS_HUMAN o VERIFY)

1. **Dominio propio para la web (recomendado):** el origen `marbi8891.github.io` lo comparten todos los repositorios de Pages del usuario, y cualquiera de ellos podría leer el token de `localStorage`. Se arregla con un subdominio propio, por ejemplo `app.mrabehfathi.com`, con un CNAME en Pages y el nuevo origen en `CORS_ORIGINS`.
2. **Ajustes de GitHub:** las casillas que lista `SECURITY.md` (secret scanning, CodeQL, permisos de Actions, protección de `main`, email privado en los commits).
3. **VERIFY que Render sigue AÑADIENDO la IP del cliente al final de `X-Forwarded-For`**, que es lo que dice su propia respuesta pública. Comprobación tras desplegar: 6 logins fallidos con un `X-Forwarded-For` inventado distinto cada vez deben acabar en 429.
4. **Autoalojar Pyodide:** eliminaría el último tercero en tiempo de ejecución. Son unos 10 MB; `config.pyodideUrl` ya lo permite.
5. **Revisión jurídica:** la redacción legal de la política de privacidad (bases jurídicas, LSSI) es orientativa y no sustituye a un asesor.
