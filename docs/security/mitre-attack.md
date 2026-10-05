# Modelo de amenazas con MITRE ATT&CK

- **Matriz:** MITRE ATT&CK Enterprise v19. Las técnicas marcadas con ✓id se comprobaron una a una en attack.mitre.org el 29-09-2026.
- **Decisión:** [ADR-0023](../adr/0023-mitre-attack.md).
- **Capa para ATT&CK Navigator:** [`attack-navigator-layer.json`](attack-navigator-layer.json). Para verla, abre <https://mitre-attack.github.io/attack-navigator/>, elige «Open Existing Layer» y luego «Upload from local».

## Qué protegemos

| Activo | Dónde está |
|---|---|
| Cuentas: email, nombre y hash Argon2id | Neon Postgres, a través de la API en Render |
| Progreso, intentos de código y estado de los cursos | Neon, y `localStorage` en el navegador |
| Sesiones (JWT de 1 hora con `token_version`) | `localStorage` del navegador (`pld:token`) |
| Secretos: `JWT_SECRET`, `DATABASE_URL`, SMTP y la clave de firma Android | Variables de Render y GitHub Secrets; la `.jks` está en el PC del autor |
| La web y la app | GitHub Pages y las releases de GitHub |

**Quién podría atacar:** bots que prueban contraseñas filtradas, escáneres automáticos, alguien que engaña a un compañero para que pegue código, o alguien con acceso a un equipo compartido del instituto. Es un proyecto de estudio sin datos de pago: no se modela un atacante estatal.

## Cómo leer la tabla

- **Estado:**
  - ✔ cubierto y probado con un test;
  - ◐ cubierto en parte o solo documentado;
  - ✘ no cubierto, con el motivo.
- **Detección:** es el evento del registro de seguridad (`pld.security`, en `backend/app/security_events.py`) que delata la técnica. Cada línea es JSON con `event`, `attack` (el ID de la técnica), la IP seudonimizada y la ruta.

## Reconocimiento y desarrollo de recursos

| Técnica | Escenario | Controles (mitigación ATT&CK → evidencia) | Detección | Estado |
|---|---|---|---|---|
| T1595.002 Vulnerability Scanning | Un escáner busca rutas y versiones conocidas | M1056 Pre-compromise:<br>• `/docs` y `/openapi.json` desactivados en producción (`ENABLE_DOCS`, `main.py`); | Logs de acceso de Render | ◐ |
| T1589.002 Email Addresses | Averiguar qué emails tienen cuenta | • La recuperación responde siempre igual (`auth.py`, `RESET_ACCEPTED`).<br>• El login da el mismo error con y sin cuenta.<br>• **Riesgo aceptado:** el registro responde 409 si el email existe (ver ADR-0023). | `auth.password_reset_requested` con `known` | ◐ |
| T1593.003 Code Repositories | Buscar secretos en el repositorio público | M1013:<br>• los secretos están solo en Render y GitHub Secrets;<br>• `.gitignore` cubre `.env`, `*.jks` y `*.keystore`;<br>• secret scanning de GitHub (NEEDS_HUMAN: activarlo). | Alertas de GitHub | ◐ |

## Acceso inicial

| Técnica | Escenario | Controles | Detección | Estado |
|---|---|---|---|---|
| T1190 Exploit Public-Facing Application | Inyección SQL o desbordamiento en la API | M1050 y M1016:<br>• ORM con parámetros (SQLAlchemy);<br>• Pydantic valida los tipos y longitudes;<br>• cuerpo limitado a 300 KB (`BodySizeLimit`);<br>• `pip-audit` y `npm audit` en la CI;<br>• Dependabot. | `request.too_large`, CI | ✔ |
| T1189 Drive-by Compromise | Una XSS convierte la web en trampa | M1021 y M1050:<br>• CSP estricta sin `unsafe-eval` (`index.html`);<br>• todo se escapa (`escapeHtml`, `safeUrl`);<br>• `progress-guard.js` valida lo leído de `localStorage`;<br>• *frame-buster* (`theme-init.js`). | e2e `security.spec.js` | ✔ |
| T1195.001 / T1195.002 Supply Chain | Una dependencia o una Action maliciosa | M1051 y M1016:<br>• dependencias mínimas (se retiraron AWS SDK y dotenv);<br>• lockfiles;<br>• la CI con `permissions: contents: read` y `persist-credentials: false`;<br>• validación del wrapper de Gradle;<br>• Pyodide fijado a una versión en la CSP. | Dependabot, `pip-audit` y `npm audit` | ◐ (las Actions no están fijadas por SHA: ver pendientes) |
| T1078 Valid Accounts | Entrar con una contraseña robada o adivinada | M1027:<br>• política de contraseñas (`password_policy.py`);<br>• bloqueo por cuenta;<br>• sesiones de 1 hora.<br>M1032 MFA: no se implementa. | `auth.login_ok` como base para ver anomalías | ◐ |
| T1566.002 Spearphishing Link | Un falso email de «restablecer contraseña» | M1017: los emails reales solo enlazan a `frontend_url`, y el texto avisa de que, si no lo pediste, lo ignores. | — | ◐ |

## Ejecución

| Técnica | Escenario | Controles | Detección | Estado |
|---|---|---|---|---|
| ✓id T1204.004 Malicious Copy and Paste | «Pega este código en la consola» para robar la sesión | M1038, M1021 y M1017:<br>• **aviso al pegar** en la consola código que usa `js`, `fetch`, `localStorage`, `eval`… (`console.js`, `isRiskyPaste`);<br>• el código corre en un Web Worker sin acceso a `localStorage` ni al DOM (M1048);<br>• la salida se escapa. | e2e «avisa si se pega…» | ✔ |
| T1059.006 Python / T1059.007 JavaScript | Ejecutar código arbitrario en el navegador de otra persona | M1048: el Worker está aislado del DOM y la CSP limita `script-src` a la propia web y a la versión fijada de Pyodide. | — | ✔ |

## Persistencia y manipulación de cuentas

| Técnica | Escenario | Controles | Detección | Estado |
|---|---|---|---|---|
| T1098 Account Manipulation | Cambiar la contraseña de otra persona con el enlace de recuperación | M1018:<br>• el enlace es de un solo uso, caduca a los 30 minutos y se guarda como hash;<br>• se reclama con un UPDATE condicional;<br>• cambiar la contraseña cierra todas las sesiones;<br>• máximo 3 emails por cuenta cada 15 minutos. | `auth.password_reset_requested` y `auth.password_reset_done` | ✔ |

## Acceso a credenciales

| Técnica | Escenario | Controles | Detección | Estado |
|---|---|---|---|---|
| ✓id T1110.001 Password Guessing | Muchas contraseñas contra una cuenta | M1036: límite por IP (5 por minuto, con la IP real tras el proxy) y bloqueo por cuenta (10 fallos en 15 minutos). | `auth.login_failed`, `auth.account_locked` y `auth.rate_limited` | ✔ |
| ✓id T1110.002 Password Cracking | Robar los hashes y crackearlos | M1027: Argon2id (19 MiB, t=2), que se re-hashea al entrar. | — | ✔ |
| ✓id T1110.003 Password Spraying | La misma contraseña común contra muchas cuentas | M1027: **se rechazan las contraseñas comunes** y las que contienen el email o el nombre. | Muchos `auth.login_failed` con `account` distinto y la misma `ip` | ✔ |
| ✓id T1110.004 Credential Stuffing | Pares email/contraseña filtrados de otras webs | M1027 y M1036: la lista de comunes, el bloqueo por cuenta y el límite por IP.<br>M1032 MFA: no. | `auth.login_failed` con `known=true` | ◐ |
| ✓id T1606.001 Web Cookies (Forge Web Credentials) | Fabricar un JWT | M1054:<br>• HS256 con un secreto de 32 o más caracteres;<br>• se exigen `exp` y `sub`;<br>• algoritmo fijo (no se acepta `none`). | **`auth.token_forged`** (firma o algoritmo ajenos) | ✔ |
| ✓id T1539 Steal Web Session Cookie | Robar el token de un navegador | M1021 y M1054:<br>• cookie `HttpOnly` que JavaScript no puede leer, aceptada solo con la cabecera `X-PLD-Session`;<br>• CSP y escapado (para que no haya XSS);<br>• el token no se envía en la URL;<br>• cerrar sesión borra los datos locales;<br>• `logout-all`. | `auth.token_revoked_used` | ✔ (cookie `HttpOnly`, ADR-0033) |
| T1528 Steal Application Access Token | Llevarse el token de recuperación por Referer o analítica | M1041: la política de *referrer* no envía la ruta a otros sitios (`strict-origin-when-cross-origin`), la analítica quita la `?` y el token solo existe hasheado en la base de datos. | — | ✔ |
| T1552.001 Credentials In Files | Secretos en el repositorio o en la imagen | `.gitignore` y `.dockerignore`; la clave de firma se borra con `trap` en la CI. | secret scanning (NEEDS_HUMAN) | ◐ |
| T1557 Adversary-in-the-Middle | Interceptar el tráfico | M1041: HTTPS (Pages y Render), `sslmode=require` hacia Neon y STARTTLS con verificación del certificado. | — | ✔ |

## Descubrimiento y movimiento lateral

| Técnica | Escenario | Controles | Detección | Estado |
|---|---|---|---|---|
| ✓id T1087.004 Cloud Account | Listar las cuentas | M1018: no hay ningún endpoint que liste usuarios; cada petición solo ve los datos de su propio `user.id`. | — | ✔ |
| ✓id T1550.001 Application Access Token | Reutilizar un token robado desde otro sitio | M1047 y M1013:<br>• caducidad de 1 hora;<br>• `token_version` invalida todos los tokens al cerrar sesión en todas partes o al cambiar la contraseña. | **`auth.token_revoked_used`** y `auth.logout_all` | ✔ |

## Impacto

| Técnica | Escenario | Controles | Detección | Estado |
|---|---|---|---|---|
| T1485 Data Destruction | Borrar la cuenta de otra persona con una sesión robada | • El borrado pide la contraseña.<br>• Un intento sin ella queda registrado.<br>• M1053: copias de Neon (VERIFY: la retención de la restauración a un instante, PITR, del plan). | `auth.login_failed` con `action=delete` y `account.deleted` | ◐ |
| T1565.001 Stored Data Manipulation | Meter HTML o datos enormes en el progreso | Pydantic, el límite de tamaño, `cleanProgress` y el escapado al pintar. | e2e «dato manipulado» | ✔ |
| ✓id T1499.003 Application Exhaustion Flood | Agotar la memoria o la CPU | M1037:<br>• límite de cuerpo (413);<br>• Argon2 con 19 MiB;<br>• solo se guardan los últimos 50 intentos por lección;<br>• el limitador purga claves. | `request.too_large` y `auth.rate_limited` | ✔ |
| ✓id T1531 Account Access Removal | Bloquear a propósito la cuenta de alguien con 10 fallos | • El bloqueo dura solo 15 minutos.<br>• **Restablecer la contraseña lo levanta** (quien controla el email recupera el acceso). | `auth.account_locked` | ✔ |
| T1491.002 External Defacement | Cambiar la web publicada | La web solo se publica desde `main` con Actions. NEEDS_HUMAN: proteger `main` y exigir la CI. | — | ◐ |

## Qué falta (priorizado)

1. **NEEDS_HUMAN, en los ajustes de GitHub:**
   - secret scanning y push protection;
   - CodeQL;
   - Actions con permisos de solo lectura;
   - regla de protección de `main`.
   Ver `SECURITY.md`.
2. **Alertas:** los eventos ya están en los logs de Render, pero nadie los mira. Opción barata: un *log stream* de Render hacia un servicio con alertas por texto, por ejemplo cuando aparece `auth.token_forged`.
3. **MFA (M1032):** TOTP opcional. Se aplaza porque es un proyecto de estudio y el coste en complejidad es alto.
4. **Fijar las Actions por SHA** (T1195.002). Dependabot sabe actualizarlas.
5. **`SameSite=Strict`** para la cookie de sesión (T1539). Ya es `HttpOnly` (ADR-0033); `Strict` requiere un dominio propio compartido con la API.
6. **VERIFY:** la retención de las copias de Neon y de los logs de Render en el plan gratuito.

## Cómo buscar ataques en los logs de Render

En *Logs*, filtra por `pld.security`:

- `"attack": "T1110"` → fuerza bruta. Si la misma `ip` aparece con muchas `account` distintas, es *password spraying*.
- `auth.token_forged` → alguien fabrica sesiones. No debería aparecer nunca.
- `auth.token_revoked_used` → se está usando un token de antes de cerrar sesión: un token posiblemente robado.
- `request.too_large` en ráfaga → un intento de agotar el servidor.
