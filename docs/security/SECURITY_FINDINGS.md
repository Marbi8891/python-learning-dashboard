# Registro de hallazgos de seguridad

Registro central del equipo AppSec. **Solo lo edita `security-lead`**; los especialistas le
devuelven sus hallazgos con la plantilla de abajo. Flujo y severidad: [`AGENT_WORKFLOW.md`](AGENT_WORKFLOW.md).

| Última revisión | Commit | Tipo | Responsable |
|---|---|---|---|
| 19/10/2026 | `708431f` (`main`) | Línea base completa al crear el equipo | security-lead |

La siguiente revisión incremental parte de `git diff 708431f..HEAD`.

## Resumen

| ID | Título | Severidad | Estado | Responsable |
|---|---|---|---|---|
| PLD-SEC-001 | Sin pruebas de aislamiento entre cuentas en la mayoría de rutas privadas | Informativa | Corregido | security-qa |
| PLD-SEC-002 | Atributos de la barra lateral con datos del contenido sin escapar | Baja | Abierto | frontend-security |
| PLD-SEC-003 | La CSP de producción permite `localhost:8000` en `connect-src` | Baja | Abierto | frontend-security |
| PLD-SEC-004 | El Worker de Pyodide probablemente no tiene CSP | Baja | Probable, pendiente de prueba | frontend-security |
| PLD-SEC-005 | Dependencias de pip sin *hashes* ni archivo de bloqueo | Baja | Abierto | dependency-security |
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
- **Estado**: confirmado (lectura del código) → abierto.
- **Responsable**: frontend-security.
- **Ubicación**: `frontend/js/app.js:111` (`data-module="${module.slug}"`) y `frontend/js/app.js:119`
  (`href` y `data-slug` con `lesson.slug`). El título sí pasa por `escapeHtml`.
- **Condiciones**: un slug con comillas en el JSON (error de contenido o commit malicioso).
- **Impacto**: XSS almacenado en la web publicada para todos los visitantes; requiere acceso de escritura al repositorio.
- **Recomendación**: `escapeHtml()` en los tres atributos, o validar el formato `^[a-z0-9-]+$` de los
  slugs en `backend/tests/test_content.py`.
- **Prueba de regresión**: test unitario o de contenido que rechace un slug con `"`.

### PLD-SEC-003 · La CSP de producción permite `localhost:8000` en `connect-src`
- **Severidad**: Baja.
- **Estado**: confirmado → abierto (ya anotado en la auditoría de la Fase 1).
- **Responsable**: frontend-security.
- **Ubicación**: `frontend/index.html:8`.
- **Impacto**: un XSS podría hablar con un servidor local de quien visita la web. Sin XSS no tiene efecto.
- **Recomendación**: quitar los orígenes locales de la CSP publicada y usar otra CSP para el modo
  local (`backend/app/local_site.py`), comprobando que `npm run test:e2e` sigue en verde.
- **Prueba de regresión**: test que lea el `<meta>` de `frontend/index.html` y rechace `http:`.

### PLD-SEC-004 · El Worker de Pyodide probablemente no tiene CSP
- **Severidad**: Baja. El código del alumno no llega a la sesión ni a `localStorage` desde el Worker.
- **Estado**: **probable**, no verificado. Según la especificación CSP, un Worker toma la política de
  las cabeceras de su propia respuesta, y GitHub Pages no envía cabecera CSP.
- **Responsable**: frontend-security.
- **Ubicación**: `frontend/js/pyodide-worker.js`.
- **Impacto**: código pegado por el alumno (`import js; js.fetch(...)`) podría hacer peticiones a
  cualquier origen desde su navegador. La consola ya avisa al pegar código que toca la red.
- **Recomendación**: probarlo en un e2e con Pyodide local antes de decidir nada.
- **Prueba de regresión**: e2e que ejecute un `fetch` a un origen no permitido desde el Worker.

### PLD-SEC-005 · Dependencias de pip sin *hashes* ni archivo de bloqueo
- **Severidad**: Baja. Rangos con límite superior y `pip-audit` en CI.
- **Estado**: confirmado → abierto.
- **Responsable**: dependency-security.
- **Ubicación**: `backend/requirements.txt`, `backend/Dockerfile`.
- **Impacto**: una versión nueva comprometida dentro del rango entraría en la siguiente imagen.
- **Recomendación**: valorar `pip-compile --generate-hashes` para la imagen de producción; requiere
  cambiar el Dockerfile, así que necesita autorización.

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
