# Auditoría técnica: Python Learning Dashboard

**Fecha:** 2 de noviembre de 2026 · **Commit auditado:** `f6a475b` (`main`, merge del PR #67) · **Fase:** 1 de 6 (solo diagnóstico, sin cambios de código)

Esta auditoría parte de las de la semana pasada (auditoría integral y red team del 29/10/2026, sobre `5996380`) y las comprueba contra el código actual. Entre `5996380` y `f6a475b` solo cambió `.claude/agents/red-teamer.md`, así que el código de la web y de la API es el mismo. Aun así, cada hallazgo de este documento se ha vuelto a mirar en el código, y los nuevos se han reproducido cuando ha sido posible.

Etiquetas de evidencia:

- **Reproducido:** ejecutado en esta auditoría, con el comando o la prueba indicada.
- **Código:** se deduce leyendo el código (archivo y línea), sin ejecutarlo.
- **No comprobado:** no se ha podido verificar desde este entorno; se dice por qué.

No se muestran secretos ni valores de variables de entorno.

---

## 1. Estado actual

### 1.1 Git y despliegue

| Elemento | Estado | Evidencia |
|---|---|---|
| Rama `main` | `f6a475b`, árbol limpio | `git status` |
| CI (`ci.yml`) en `main` | Verde en `f6a475b` (run #215) | GitHub Actions |
| Web publicada (GitHub Pages) | Desplegada desde `944af1e` (PR #62, 26/10). Los merges posteriores (#64, #66, #67) no tocan `frontend/`, y `pages.yml` solo se lanza con cambios en `frontend/**`, así que **la web publicada coincide con el `frontend/` de `main`** | `git diff --stat 944af1e HEAD -- frontend` vacío; `sw.js` publicado con `VERSION = "v8"` y el mismo `SHELL` que el repositorio (leído con WebFetch) |
| API en Render | **No comprobado.** El proxy de este entorno rechaza `pld-api.onrender.com`. No se puede saber qué commit corre ni si `GOOGLE_CLIENT_ID` y Brevo están configurados | `curl` → `connect_rejected` |
| PR abiertos | #68 (Docker local, CI verde), #65 (recuperar el tutor con OpenAI), #63 (aviso legal), **#61 (desfasado, base anterior a #62)**, y Dependabot #19, #16, #14, #13 (los de `/android` apuntan a una carpeta que ya no existe) | `list_pull_requests` |

### 1.2 Pruebas ejecutadas en esta auditoría

| Prueba | Resultado |
|---|---|
| `ruff check` y `ruff format --check` (desde `backend/`) | Sin errores; 75 archivos formateados |
| `pytest -q --cov=app --cov-fail-under=100` | **557 pasan**, cobertura 100 % |
| `npm run test:unit` | **68 pasan** |
| `npm run test:e2e` (Chromium, Pyodide 314.0.7 servido en local) | Ver §1.3 |
| `build_learning.py --check`, `build_curriculum.py --check` y los 5 `*_course.py --check` | Todos al día y con las respuestas comprobadas |
| `pip-audit -r backend/requirements.txt` | Sin vulnerabilidades conocidas |
| `npm audit --audit-level=low` | 0 vulnerabilidades |

### 1.3 Resultado de las e2e

**136 de 136 pasan** en Chromium (3,7 min, 2 workers), con el backend real arrancado en local sobre SQLite y Pyodide 314.0.7 servido desde una copia local (jsDelivr está bloqueado en este entorno). Incluyen la auditoría automática de accesibilidad con axe-core. La copia de Pyodide y la configuración de Playwright se dejaron fuera del repositorio.

### 1.4 Lo que no se ha podido comprobar

- **Backend en producción** (Render y Neon): bloqueado por el proxy. Todo lo de la API se ha probado con la API real arrancada en local (SQLite), que es el mismo código.
- **Safari / WebKit**: solo hay Chromium en este entorno. Lo que afecta a Safari (cookies de terceros, `Partitioned`, Workers de tipo módulo) se marca como no comprobado.
- **Google Sign-In real** y el **envío de emails**: necesitan credenciales del autor.
- **Lector de pantalla y móvil real**: no hay en este entorno. La accesibilidad se ha revisado con axe-core (en las e2e) y leyendo el código.
- **Lighthouse**: no se ha medido.

---

## 2. Arquitectura detectada

```
Navegador ──► GitHub Pages: index.html (SPA con rutas #/...), 16 CSS, ~45 módulos ES, JSON del temario
   │
   ├─► Web Worker de tipo módulo (pyodide-worker.js) ──► Pyodide 314.0.7 desde jsDelivr (caché del SW)
   │        └─ ejecuta frontend/py/runner.py (el mismo que usan las pruebas del backend)
   │
   └─► API FastAPI en Render (/api/v1) ──► PostgreSQL (Neon); SQLite en local
            └─ solo si el alumno inicia sesión
```

- **Frontend sin framework**, como pide el proyecto: HTML + CSS + JS con ES Modules. Punto de entrada `frontend/js/app.js` (802 líneas, 25 `import` estáticos). No hay carga diferida: todos los módulos y las 16 hojas de estilo se cargan al abrir cualquier ruta.
- **Rutas por hash**, compatibles con GitHub Pages: `#/portada[/sección]`, `#/aprender[/...]`, `#/leccion/<slug>`, `#/pcap[/...]`, `#/daw[/...]`, `#/panel[/sección]`, `#/certificado[/...]`, `#/perfil`, `#/inicio`, `#/restablecer?token=`. El enrutador es una cadena de `if` en `navigate()` (`app.js:592-668`).
- **Datos:** el temario son JSON estáticos en `frontend/data/` (`lessons.json` 220 KB, `pcap.json` 176 KB, `learning.json` 160 KB, `courses/` 672 KB). `learning.json`, el currículo y los cursos se generan con `scripts/`; `lessons.json` y `pcap.json` se editan a mano y los validan `test_content.py` y `test_pcap.py`.
- **Estado:** varios almacenes independientes en `localStorage` (`store.js`, `pcap-store.js`, `course-store.js`, `learn/learn-store.js`, `game.js`, borradores `pld:draft:*`) y una sincronización por almacén con la API (`*-sync.js` o dentro del propio store).
- **Backend:** FastAPI con 8 routers bajo `/api/v1`, SQLAlchemy + Alembic (9 migraciones), Pydantic v2, JWT en cookie `HttpOnly; Secure; SameSite=None; Partitioned` con cabecera `X-PLD-Session` contra CSRF, Argon2, límites de tamaño de cuerpo y de intentos de login.
- **PWA:** `sw.js` (red primero para la web, caché primero para Pyodide).

La arquitectura es adecuada para un proyecto de una persona y **no hace falta cambiarla**. Los problemas están en piezas concretas (sincronización, enrutador, runner, CSS acumulado), no en la elección de tecnologías.

---

## 3. Funcionalidades existentes

| Funcionalidad | Ruta | Estado |
|---|---|---|
| Portada pública | `#/portada` | Terminada. «CodeFeed» aparece como «en desarrollo» |
| «¿Qué estudio ahora?», sesiones por conceptos, prueba de nivel, repaso espaciado | `#/aprender`, `#/sesion` | Funciona, con fallos de lógica (AUD-002 a AUD-006) |
| Lecciones del curso PCAP con teoría, consola, quiz y reto | `#/leccion/<slug>` | Terminada |
| Consola de Python (Pyodide en Worker) con `input()`, corte a los 10 s, números de línea, borrador guardado | dentro de la lección | Funciona; sin botón Detener (ver PY-01) |
| Banco PCAP, práctica, simulacro 40/65 min, certificado | `#/pcap`, `#/certificado` | Terminada |
| Cursos de DAW (Programación, BD, Entornos, JS, Java) y currículo oficial CyL | `#/daw/...` | Terminada; Entornos y Cliente con poca cobertura |
| XP, niveles, racha, logros | toda la app | Funciona; racha y XP no cuentan todo (AUD-016) |
| Cuenta: registro, login, Google, recuperación, panel, exportar y borrar datos | `#/panel/...` | En código y probada en local. **En producción no comprobado** (Google y email dependen de Render) |
| Tema claro/oscuro, PWA | toda la app | Tema funciona. PWA sin conexión incompleta (AUD-008) |
| Tutor con IA, A2A, app Android | — | **Retirados** en el PR #62. El PR #65 propone recuperar el tutor |

---

## 4. Errores reproducibles

Los IDs `AUD-*` vienen de la auditoría del 29/10 y siguen abiertos en `f6a475b` (comprobado en el código). Los IDs nuevos de esta auditoría empiezan por `PY-` (ejecución de Python), `NAV-` (navegación), `UX-` (interfaz) y `SEC-` (seguridad).

### 4.1 Integridad de datos

**AUD-001 · P0 · La sincronización puede sustituir el progreso guardado en la cuenta** (Código)
- `pcap-sync.js:30-49`, `course-store.js:150-165`, `learn/learn-store.js:38-48` y `:77-88`, `game.js:58` y `:264`; en el backend `pcap.py:28` y `course_state.py:46` hacen `state.data = body.data` (sustitución completa, sin comprobar versión).
- Caso 1: si el `GET` inicial falla (Render despertando, 5xx), el `catch` solo escribe en consola, y a partir de ahí cada cambio local hace un `PUT` con el documento local entero, que pisa el de la cuenta.
- Caso 2 (nuevo, sin fallo de red): en `learn-store.js` no hay guarda `merging`. Si el alumno hace algo en los 1,5 s de `PUSH_DELAY_MS` mientras el `GET` aún no ha vuelto, el `PUT` puede llegar antes de la fusión.
- Caso 3: dos pestañas o dispositivos a la vez: gana el último que escribe. *(Corregido el 02/11/2026: columna `version` y 409 si la cuenta cambió; la app relee, fusiona y reintenta. Los casos 1 y 2 se corrigieron con `sync-gate.js`, PR #72.)*
- **Impacto:** pérdida de progreso sin aviso.

### 4.2 Ejecución de Python

**PY-01 · P2 · No hay botón Detener** (Código). La única forma de cortar un programa es esperar al límite de 10 s (`python-runner.js:62-68`). El PR #61 lo implementó, pero no está en `main`.

**PY-02 · P2 · La carga de Pyodide no tiene tiempo límite y puede dejar la consola bloqueada** (Código). `#call()` hace `await this.#start()` antes de arrancar el temporizador (`python-runner.js:58-70`). Si la descarga de Pyodide se queda colgada (red lenta o cortada sin error), la promesa no termina nunca, `busy` sigue a `true` (`console.js:92-108`) y el botón se queda en «Ejecutando…» hasta recargar. Si la red falla con error, sí se muestra «No se pudo cargar Python».

**PY-03 · P2 · El código del alumno puede romper el intérprete para las ejecuciones siguientes** (Reproducido en CPython y en Chromium, §4.5). Todas las ejecuciones comparten el mismo intérprete. `runner.py:145` crea un `namespace` nuevo, pero los módulos (`builtins`, `sys`) son los mismos. Prueba en CPython con el `runner.py` real:

```text
1.ª ejecución: import builtins; builtins.print = lambda *a, **k: None
2.ª ejecución: print('hola')   →  salida: ''
```

La consola y la corrección de ejercicios dejan de mostrar salida hasta recargar la página (o hasta que un bucle infinito fuerce el reinicio del Worker).

**PY-04 · P3 · La salida se recorta después de generarla, no mientras se genera** (Reproducido). `runner.py:159` corta a 20 000 caracteres al final, pero `StringIO` guarda todo. En CPython, `for i in range(2_000_000): print('x'*50)` devuelve 20 000 caracteres pero llega a **230 MB de memoria** en 3,5 s. En Chromium con Pyodide, el límite de 10 s lo cortó antes de agotar la memoria (§4.5), pero no hay ningún tope de memoria propio.

**PY-05 · P3 · El resultado de la corrección se calcula en el mismo proceso que el código del alumno.** El alumno puede falsear su resultado (por ejemplo con `import js; js.postMessage(...)` o redefiniendo funciones del runner). No es un riesgo de seguridad, porque solo se engaña a sí mismo, pero significa que **la XP y los ejercicios superados no se pueden tratar como verificados** (importante para la Fase 4).

Comprobado y correcto:
- Se reutiliza un único Worker para la consola y los ejercicios (`console.js:17-27`); no se reinicializa en cada ejecución.
- Los errores de sintaxis y excepciones se capturan (también `SystemExit` y `KeyboardInterrupt`, `runner.py:153`) con traceback limitado al código del alumno y explicación en español.
- Un bucle infinito se corta a los 10 s con `terminate()` y la consola sigue funcionando (e2e `console.spec.js:39`).
- Tras cargar Python, el Worker bloquea `fetch`, `XMLHttpRequest`, `WebSocket`, `eval`, `Function`, etc. (`pyodide-worker.js:7-45`).

**Límites reales del aislamiento** (no se debe decir que es «seguro» por usar un Worker):
- El Worker evita que la página se congele, **no** es un sandbox: corre en el mismo origen y no tiene CSP propia (la CSP va en un `<meta>` y no se aplica al Worker).
- El cierre de red es una lista negra (RT-005): una API nueva del navegador que no esté en la lista quedaría abierta.
- No hay límite de memoria ni de CPU más allá de los 10 s; un programa que consuma mucha memoria puede tumbar el Worker (PY-04) o degradar el navegador.
- Pyodide se descarga de jsDelivr sin SRI (RT-002); la versión está fijada en la URL y en la CSP.

### 4.3 Navegación

**NAV-01 · P2 · Las rutas que no existen no muestran ningún error** (Reproducido, §4.5). `navigate()` manda cualquier hash desconocido a la portada con `history.replaceState` (`app.js:639-644`), y un `#/leccion/<slug>` inexistente abre otra lección sin avisar (`app.js:646-648`). Un enlace mal escrito o antiguo parece funcionar, pero lleva a otro sitio.

**AUD-010 · P2 · Si `lessons.json` no carga, no funciona nada** (Código). `init()` hace `return` antes de registrar el enrutador, `hashchange` y las sincronizaciones (`app.js:756-774`). Ni la portada ni `#/aprender`, que no necesitan ese archivo, se pueden abrir.

**AUD-008 · P1 · La PWA no funciona sin conexión tras una sola visita** (Código, confirmado también en la web publicada). `sw.js:9` solo precachea 6 archivos; ningún CSS, módulo JS, fuente ni JSON. La caché `pld-pyodide` no lleva versión y no se limpia nunca (`sw.js:8`).

### 4.4 Aprendizaje y progreso (de la auditoría del 29/10, siguen abiertos)

| ID | Prioridad | Problema | Dónde |
|---|---|---|---|
| AUD-002 | P1 | La prueba de nivel cuenta los fallos como «empezado» y da «superado» con un acierto de cuatro opciones | `learn/exam.js`, `session.js`, `recommend.js` |
| AUD-003 | P1 | Una sesión abandonada deja el concepto «dominado» sin repaso programado | `learn/mastery.js:68-114` |
| AUD-004 | P1 | El repaso espaciado se puede comprimir en una tarde (el test actual fija ese comportamiento: cambiarlo lo decide el autor) | `learn/mastery.js:108-114`, `mastery.test.mjs:99-110` |
| AUD-005 | P1 | Se «domina» un concepto sin escribir código | `learn/mastery.js:152-158` |
| AUD-006 | P1 | «Preparación» marca 100 % con 5 respuestas de 126 | `pcap-store.js:105-132`, `course-store.js:113-124` |
| AUD-007 | P1 | Explicación incorrecta en la pregunta `ent-16` | `scripts/courses/entornos_course.py` |
| AUD-016 | P2 | La racha y la XP no cuentan el núcleo por conceptos ni los cursos | `game.js` |

### 4.5 Comprobación en navegador

Prueba con Playwright (Chromium, ventana de 375 × 800 px, Pyodide 314.0.7 local), en esta auditoría:

| Acción | Resultado |
|---|---|
| Abrir `#/portada/tecnologia` | Abre la sección. Sin desplazamiento horizontal (`scrollWidth` = 375) |
| Abrir `#/no-existe` | Cambia a `#/portada` **sin ningún aviso** (NAV-01) |
| Abrir `#/leccion/no-existe` | Cambia a `#/leccion/variables` **sin ningún aviso** (NAV-01) |
| Abrir `#/daw/no-existe`, `#/pcap/no-existe`, `#/panel/no-existe`, `#/aprender/no-existe` | Muestran la página principal de su zona, sin aviso |
| Ejecutar `print("hola")` (primera vez) | `hola` en 2,4 s (incluye cargar Pyodide) |
| `import builtins; builtins.print = lambda *a, **k: None` y después `print(...)` | **Las ejecuciones siguientes no muestran nada**, tampoco `print(2+2)` (PY-03) |
| 20 millones de `print("x"*50)` | Se corta a los 10 s y la siguiente ejecución funciona |
| Recursión infinita | `RecursionError` con traceback limitado al código del alumno |
| `bytearray(3 * 10**9)` | `OverflowError` (límite de 32 bits de WebAssembly) y la consola sigue funcionando |
| Errores en consola | Solo `ERR_CONNECTION_REFUSED` de `/api/v1/health`, porque en esta prueba no había backend. No es un fallo de la web |

En el navegador, el límite de 10 s cortó la salida masiva antes de agotar la memoria, así que PY-04 queda en P3: el riesgo es real en CPython (230 MB), pero en Pyodide no se ha llegado a bloquear el Worker.

---

## 5. Problemas de seguridad

Resumen: la API está bien protegida para su tamaño (el red team del 29/10 no encontró vulnerabilidades explotables y lo he vuelto a comprobar en el código). Lo pendiente es defensa en profundidad y abuso de recursos.

| ID | Prioridad | Problema | Evidencia |
|---|---|---|---|
| AUD-009 | P1 | Sin límite de frecuencia ni cuota en los endpoints de escritura (`PUT /course-state/{curso}`, `PUT /pcap-state`, `POST /lessons/{slug}/attempts`). Solo el login, el registro, Google, la recuperación y el borrado usan `limit_auth_attempts`. Con documentos de hasta 200 KB y código de hasta 20 000 caracteres, unas pocas cuentas pueden llenar los 0,5 GB de Neon gratuito (cálculo, no ejecutado contra producción) | `grep limit_auth_attempts backend/app/routers/*.py`; `schemas.py` |
| RT-002 | P2 | Pyodide desde jsDelivr sin control de integridad | `python-runner.js:8`, CSP de `index.html:8` |
| RT-005 | P3 | Cierre de red del Worker por lista negra | `pyodide-worker.js:7-18` |
| RT-001 | P3 | El escapado contra XSS solo existe en el cliente; la API guarda nombre, código y documentos tal cual. Hoy no hay XSS: hay 54 usos de `innerHTML`/`insertAdjacentHTML` y los revisados escapan con `escapeHtml`/`renderInline` (`console.js:84-90`, `:127-131`), pero un solo olvido abriría uno | `grep -c innerHTML frontend/js` |
| RT-004 | P3 | `style-src 'unsafe-inline'` en la CSP | `index.html:8` |
| RT-003 | P3 | Anti-clickjacking por JavaScript (GitHub Pages no permite la cabecera `frame-ancestors`) | `theme-init.js` |
| RT-006 / AUD-018 | P3 | Límites de intentos en memoria (valen con una instancia, como ahora en Render) y por IP (un aula detrás de NAT comparte contador) | `rate_limit.py` |
| SEC-01 | P3 | La CSP de desarrollo de `index.html` permite `http://127.0.0.1:8000` y `http://localhost:8000`; en producción `pages.yml` la sustituye con `production_csp.py`. **No comprobado** en la web publicada (WebFetch no devuelve el `<meta>`) | `pages.yml`, `scripts/security/production_csp.py` |

Comprobado y correcto (Código y pytest): validación con Pydantic y límites de longitud; lista cerrada de cursos sincronizables; cada operación usa el usuario de la sesión (no hay IDs de usuario que vengan del cliente); `/docs` desactivado en producción; cabeceras de seguridad y `Cache-Control: no-store` en la API; límite de 413 para cuerpos grandes también sin `Content-Length`; CORS con orígenes explícitos y `allow_credentials`; token en cookie `HttpOnly` y, si el navegador la bloquea, solo en memoria (nunca en `localStorage`); los logs de seguridad guardan IP y cuenta con hash; sin secretos en el frontend; `pip-audit` y `npm audit` limpios.

**Safari (no comprobado):** la sesión usa una cookie de terceros `Partitioned`. Si Safari la bloquea, el código pasa al token en memoria (`account.js:102-127`), así que la sesión se pierde al recargar. Hay que probarlo en un Safari real.

---

## 6. Problemas de accesibilidad

Las e2e pasan axe-core (WCAG 2.1 A/AA automático) en las vistas principales. Eso no basta para decir que se cumple WCAG 2.2 AA: falta la revisión manual.

| ID | Prioridad | Problema | Evidencia |
|---|---|---|---|
| AUD-023 | P2 | Los errores de los formularios no se asocian al campo: no hay ningún `aria-invalid` en el código (WCAG 3.3.1) | `grep -r aria-invalid frontend/js` → 0 |
| AUD-022 | P2 | Tras ejecutar código o comprobar un ejercicio el foco no siempre va al resultado (la comprobación sí hace `box.focus()`, `console.js:131`; la ejecución no) | `console.js:110-116` |
| A11Y-01 | P2 | El editor es un `<textarea>` (bien para lectores de pantalla) que captura Tab; se sale con Escape y luego Tab. Está programado, pero no se anuncia en la interfaz | `console.js:181-199` |
| AUD-035 | P3 | Contraste de bordes, desplazamiento suave con movimiento reducido, Home/End en pestañas | auditoría del 29/10 |
| A11Y-02 | P3 | Solo hay 3 reglas `prefers-reduced-motion` para 16 hojas de estilo con transiciones y animaciones | `grep prefers-reduced-motion frontend/css` |
| — | — | **Sin comprobar:** lector de pantalla, solo teclado de principio a fin, zoom al 200 %, tamaño de los objetivos táctiles (WCAG 2.5.8), móvil real | §1.4 |

---

## 7. Problemas de rendimiento

| ID | Prioridad | Problema | Evidencia |
|---|---|---|---|
| AUD-024 / PERF-01 | P2 | Todo se carga al abrir cualquier ruta: 16 hojas de estilo que bloquean el renderizado y ~45 módulos (unos 676 KB de CSS + JS sin comprimir), aunque se entre a la portada | `index.html:30-52`; `du` |
| AUD-010 | P2 | La portada espera a `lessons.json` (220 KB) aunque no lo use | `app.js:744-774` |
| PY-04 | P3 | Salida sin límite durante la ejecución (ver §4.2) | — |
| — | — | Pyodide (~10 MB) solo se descarga al ejecutar por primera vez: correcto | `console.js:9-12` |
| — | — | **Sin medir:** Lighthouse, LCP y CLS en móvil | §1.4 |

---

## 8. Deuda técnica

| ID | Prioridad | Deuda | Evidencia |
|---|---|---|---|
| UX-01 | P2 | **CSS acumulado sin sistema de diseño común.** 16 hojas (unas 7 200 líneas), 74 colores hexadecimales distintos, variables definidas en `base.css` y redefinidas en `pro.css`, y hojas por «capas» (`ux.css`, `pro.css`) que sobrescriben a las anteriores. Es la causa de que la interfaz no se sienta coherente y es el punto de partida de la Fase 2 | `grep` sobre `frontend/css` |
| AUD-011 | P2 | Lógica de repaso y de fusión duplicada en cada store, y las funciones `merge*` sin pruebas unitarias | `pcap-store.js`, `course-store.js`, `learn-store.js` |
| AUD-034 | P3 | `app.js` (802 líneas), `dashboard.js` (827), `pcap.js` (774), `landing.js` (754) mezclan datos, lógica y HTML en plantillas | `wc -l` |
| NAV-02 | P3 | El enrutador es una cadena de `if` con el orden como lógica (`#/pcap` usa `startsWith`, y cualquier hash que empiece por `#/pcap…` entra) | `app.js:592-668` |
| AUD-027 | P2 | El PR #61 sigue abierto con una base anterior al #62 | GitHub |
| DOC-01 | P3 | El README dice «accesibilidad WCAG 2.1 AA» y «funciona sin conexión después de la primera visita»; ninguna de las dos está comprobada del todo (§6 y AUD-008) | `README.md` |
| DEP-01 | P3 | Los PR de Dependabot #16 y #13 actualizan `/android`, que ya no existe; se pueden cerrar | GitHub |

---

## 9. Riesgo, solución y prioridad de cada problema

Esfuerzo: S (horas), M (un día), L (varios días). «Fase» indica en qué fase de tu plan encaja.

| Prioridad | ID | Riesgo si no se arregla | Solución propuesta | Esfuerzo | Fase |
|---|---|---|---|---|---|
| **P0** | AUD-001 | Pérdida de progreso del alumno | Marca `synced` por store: no subir nada hasta que la fusión inicial salga bien; reintentar el `GET` con espera; `PUT` como leer-fusionar-escribir. Pruebas: e2e con 503 en el primer `GET` y unitarias de `merge*` | S-M | 4 (persistencia), pero conviene antes de todo |
| P1 | AUD-009 | Base de datos gratuita llena por abuso | Límite por usuario en las escrituras (p. ej. 30/min) con 429 que el frontend tolere; bajar `code` a ~5 KB | M | 6 |
| P1 | AUD-008 | La PWA promete un modo sin conexión que no funciona | Precachear el app shell completo (lista comprobada en CI) y versionar la caché de Pyodide | S-M | 5 |
| P1 | AUD-002 a 006 | Progreso y «dominio» que no reflejan lo aprendido | Ver auditoría del 29/10 (§3) | S-M cada uno | 4 |
| P1 | AUD-007 | Contenido incorrecto | Corregir la explicación en `entornos_course.py` y regenerar | S | 4 |
| P2 | PY-01, PY-02 | Consola bloqueada o sin forma de parar | Botón Detener (`terminate()` + reinicio) y tiempo límite de carga con mensaje y botón «Reintentar» | S-M | 3 |
| P2 | PY-03 | Consola que deja de funcionar sin explicación | Restaurar `builtins`, `sys.stdout/stdin` y `sys.modules` tras cada ejecución, o reiniciar el intérprete si se detectan cambios | S | 3 |
| P3 | PY-04 | Worker sin memoria | Escribir la salida en un `StringIO` con tope que lance un error claro al pasar el límite | S | 3 |
| P2 | NAV-01, AUD-010 | Enlaces rotos que parecen funcionar; app muerta si falla un JSON | Vista «Página no encontrada» con enlace al índice; registrar el enrutador antes de cargar `lessons.json` | S | 2 |
| P2 | UX-01 | Interfaz incoherente y difícil de mantener | Tokens de diseño únicos (colores, tipografía, espaciado, radios, sombras) y componentes comunes, migrando hoja por hoja | M-L | 2 |
| P2 | AUD-023, AUD-022, A11Y-01 | Formularios y editor difíciles con lector de pantalla | `aria-invalid` + `aria-describedby`, foco al resultado, ayuda visible del atajo Escape | S-M | 5 |
| P2 | AUD-024, PERF-01 | Carga lenta en móvil | Cargar CSS y módulos de cada zona con `import()` al entrar en ella | M | 2 o 5 |
| P2 | RT-002 | CDN comprometido ejecutaría código | Alojar Pyodide en el propio Pages o comprobar su hash | M | 6 |
| P2 | AUD-011 | Fusiones sin probar | Módulo común para fusión y repaso con pruebas | M | 4 |
| P3 | PY-05 | XP falseable | Documentarlo y no usar la XP como dato verificado | S | 4 |
| P3 | RT-001, RT-003, RT-004, RT-005, RT-006, SEC-01 | Defensa en profundidad | Prueba que recorra los `innerHTML`; quitar `unsafe-inline`; ampliar la lista del Worker | S cada uno | 6 |
| P3 | AUD-034, NAV-02, DOC-01, DEP-01, A11Y-02, AUD-035 | Mantenimiento y pulido | Dividir archivos al tocarlos; tabla de rutas; corregir el README; cerrar PR obsoletos | S cada uno | según se toque |

---

## 10. Prioridad de implementación recomendada

1. **AUD-001** (P0): que la sincronización no pueda pisar el progreso. Es pequeño y protege los datos antes de rediseñar nada.
2. **Fase 2 (rediseño)** empezando por la base: tokens de diseño únicos (UX-01), vista de «página no encontrada» y enrutador robusto (NAV-01, AUD-010). Después portada, catálogo y página de tema.
3. **Fase 3 (consola):** PY-01 a PY-04 juntos, porque tocan los mismos dos archivos (`python-runner.js`, `runner.py`).
4. **Fase 4 (aprendizaje):** AUD-002 a AUD-007 y AUD-011.
5. **Fase 5 (accesibilidad y PWA):** AUD-008, AUD-022, AUD-023, revisión manual.
6. **Fase 6 (seguridad):** AUD-009 y los RT.

Antes de empezar convendría decidir qué hacer con el PR #61 (recomendado: cerrarlo y rehacer lo útil, como el botón Detener, en la Fase 3) y si el PR #65 (tutor con OpenAI, de pago) sigue en pie, porque el proyecto solo usa herramientas gratuitas.

---

## 11. Actualización del 3 de noviembre de 2026: protección del progreso (Fase B)

Auditoría sobre `2bae4e1` y correcciones en la rama `claude/project-thread-0deakf`. El informe inicial
completo (matriz de hallazgos, estado de los PR y de las pruebas) está fuera del repositorio, en los
archivos del proyecto (`auditoria-plataforma/INFORME_INICIAL_FASE_A.md`).

Desde la sección 9 ya se habían corregido AUD-001 (#72, #77), PY-01 (#85), PY-02, NAV-01 y AUD-010 (#74).

### 11.1 Hallazgos nuevos y su estado

| ID | Prioridad | Problema | Evidencia | Estado |
|---|---|---|---|---|
| SYNC-01 | P0 | Al cerrar sesión, si la última subida fallaba (red, 5xx, Render despertando) o la fusión inicial no había salido bien, se borraba del navegador un progreso que el servidor no tenía | Reproducido con Playwright y el backend real: `{"localBefore":1,"localAfter":["pld:game"],"serverKnown":0}` | **Corregido.** `uploader.js` sabe qué falta por confirmar. Si algo no se ha guardado, no se borra nada: el diálogo lo explica y ofrece reintentar, cerrar sesión conservándolo o borrarlo a sabiendas. e2e en `sync.spec.js` |
| SYNC-04 | P1 | Un `PUT` fallido solo escribía en la consola: sin reintento ni aviso | Código | **Corregido.** Estado por almacén, reintentos a los 2, 10, 30 y 60 s (no con 401) y aviso `role="status"`. `uploader.test.mjs` |
| SYNC-02 | P2 | Al fusionar ganaba el historial más largo. Como cada pregunta guarda 5 intentos, con los dos llenos ganaba siempre el local aunque el otro fuera más reciente | Código | **Corregido.** Gana la copia con el último intento más reciente (`srs[id].last`, `ex[id].last`), sin cambiar el formato. `merge.test.mjs` |
| AUTH-02 | P2 | Si caducaba la sesión de A y entraba B en el mismo navegador, la fusión subía a B el progreso de A | Código | **Corregido.** `pld:owner` + `pld:stash:<id>`: lo de A se aparta sin borrarlo y vuelve cuando A entra. `local-owner.test.mjs` y e2e |
| AUTH-01 | P2 | Sesión de 30 minutos fijos sin renovación | Código | **Corregido.** La cookie se renueva cuando le queda menos de la mitad, con un máximo absoluto de `SESSION_MAX_HOURS` (12). Los clientes Bearer no cambian. `test_session_renewal.py` |
| AUD-009 | P1 | Sin límite de frecuencia en las escrituras | `grep` | **Corregido.** 120 guardados por usuario y minuto, 429 y evento `progress.rate_limited`. `test_write_limits.py` |
| PY-03 | P2 | `builtins.print = …` dejaba muda la consola hasta recargar | Reproducido (las pruebas nuevas fallan con el runner anterior y llegan a romper pytest) | **Corregido.** `runner.py` restaura `builtins`, `sys.modules` y el límite de recursión tras cada ejecución y tras los tests. `test_runner_isolation.py` y e2e |
| PY-04 | P3 | La salida se acumulaba entera y se recortaba al final | Reproducido (230 MB en CPython) | **Corregido.** Tope de salida mientras se genera (pico de memoria < 5 MB en la prueba) y aviso de «salida recortada» |
| SYNC-03 | P3 | `PUT` sin `version` sobrescribe (compatibilidad con pestañas anteriores a #77) | Código | Pendiente: exigir la versión cuando no quede ningún cliente antiguo |

### 11.2 Qué calcula el cliente y qué valida el servidor

- **La XP, el nivel, la racha, los logros y los ejercicios superados los calcula el navegador.** La corrección corre en el Worker del alumno, que puede falsearla (PY-05). El servidor valida la forma, el tamaño (200 KB por documento) y ahora la frecuencia, pero no el contenido.
- Es proporcionado para una plataforma de estudio personal sin rankings ni certificados con valor externo. Por eso la XP y el certificado **no deben presentarse como verificados**. Verificar en el servidor exigiría ejecutar código del alumno en Render, que es un riesgo mayor que el beneficio.

### 11.3 Límites reales del aislamiento de Python

El Web Worker evita que la página se congele, **pero no es una barrera de seguridad**:

- Corre en el mismo origen y no tiene una CSP propia.
- La red se cierra con una lista negra de APIs (RT-005).
- Pyodide se descarga de jsDelivr sin SRI (RT-002).
- La restauración de PY-03 cubre las funciones integradas, `sys.modules` y la recursión. Un programa todavía puede cambiar atributos de otros módulos (`math.pi = 3`) para las ejecuciones siguientes. Recargar la página o usar «Detener», que reinicia el Worker, lo arregla.

### 11.4 Riesgos pendientes

- **SYNC-03**: un `PUT` sin versión todavía sobrescribe la cuenta (ver la tabla).
- **Sesión en Safari:** si Safari bloquea la cookie, la sesión vive en memoria y no se renueva (no comprobado en Safari).
- **Datos que se quedan en el navegador:** con «Cerrar sesión y conservarlo aquí» y con lo apartado de otra cuenta, el progreso sigue en un equipo que puede ser compartido. Es una elección explícita del alumno o, en el caso de lo apartado, la alternativa a perder sus datos.
- **Lecciones desmarcadas:** si desmarcar una lección falla, no se reintenta (la importación solo añade).
- **Límites de intentos:** se guardan en memoria (una sola instancia de Render) y se reinician al reiniciar el servidor.
- **Siguen abiertos:** AUD-008 (PWA sin conexión), AUD-002 a AUD-007 (lógica de aprendizaje), RT-001 a RT-006 y AUD-023 (`aria-invalid`). Se tratan en las fases siguientes.

## 12. Actualización del 3 de noviembre de 2026: experiencia de estudio, accesibilidad y rendimiento (Fase C)

Sobre `main` en `97b2d5f`. La Fase C no rehace el diseño: el sistema visual (`tokens.css`, `docs/DISENO.md`), la portada con actividad real y las vistas de lección y sesión ya venían del rediseño de noviembre (#78 a #86). Aquí se mide lo que hay y se corrige lo que falla.

### 12.1 Cómo se ha medido

- **axe-core con WCAG 2.2 A/AA** (antes solo 2.1): 15 rutas, en móvil y escritorio, en tema claro y oscuro, con `scripts/web/inspeccionar_web.mjs --tema ambos`. Resultado: **0 infracciones en las 60 combinaciones**, sin errores de consola y sin desplazamiento horizontal.
- **Comprobaciones con Playwright de lo que axe no ve:** dónde queda el foco después de cada acción, cerrar con Esc, la letra al 200 % a 1280 y 768 px, reflujo a 320 px y `prefers-reduced-motion`.
- **Rendimiento** en Chromium, sin y con un móvil modesto simulado (CPU 4 veces más lenta y red de 1,6 Mb/s con 150 ms de latencia), con el servidor local (sin compresión, a diferencia de GitHub Pages).

Que axe no encuentre errores **no significa que la web cumpla WCAG 2.2 AA**. Falta la revisión manual con lector de pantalla (la guía para VoiceOver está en los archivos del proyecto, pendiente de que la pase el autor) y con usuarios reales.

### 12.2 Hallazgos y estado

| ID | Prioridad | Problema | Evidencia | Estado |
|---|---|---|---|---|
| C-01 | P2 | Al pulsar «Comprobar respuestas» en el quiz, el botón se oculta y el foco cae en `<body>`: con teclado o lector de pantalla hay que volver a empezar desde arriba (WCAG 2.4.3) | Playwright: `document.activeElement` = `BODY` | **Corregido.** El foco pasa a la nota (`#quiz-score`, `tabindex="-1"`). Prueba en `a11y.spec.js`, que falla con el código anterior |
| C-02 | P2 | En el simulacro PCAP, «Seguir con el examen» ocultaba la confirmación con el foco dentro, y Esc no la cerraba | Código y Playwright | **Corregido.** Esc la cierra y el foco vuelve al botón «Terminar examen» que la abrió. `a11y.spec.js` |
| C-03 | P2 | Con la letra al 200 %, la demostración de la portada se salía 12 px por la derecha a 768 px: una rejilla de una columna `auto` se ensanchaba con el código (WCAG 1.4.4) | Playwright | **Corregido** con `grid-template-columns: minmax(0, 1fr)`. Además, `body` pasa de `15px` a `0.9375rem` (crece con la letra del navegador) y `fieldset` no se ensancha por su contenido. Prueba en 5 rutas, que falla con el código anterior |
| C-04 | P2 | Al fallar un ejercicio, la corrección decía qué test fallaba, pero no qué había mostrado el programa ni con qué entrada se probó. El alumno no veía la diferencia entre lo esperado y lo obtenido | Código | **Corregido.** Por partes: «Qué falta» (o «Error al ejecutar» con la pista), «Con esta entrada», «Lo que mostró tu programa» y «Corrige el código en la consola y vuelve a comprobarlo». Sigue sin enseñar la solución. `console.spec.js` |
| AUD-023 | P2 | Los errores de los formularios no se asociaban al campo (WCAG 3.3.1) | `grep aria-invalid` → 0 | **Corregido.** `form-errors.js` marca el campo con `aria-invalid`, lo enlaza con el mensaje y le lleva el foco: errores 422, email ya registrado, contraseñas que no coinciden, contraseña común y contraseña actual incorrecta. `account.spec.js` y `my-account.spec.js` |

**Revisado sin fallos:** foco visible (contorno de 2 px), foco nunca tapado entero por las barras fijas al tabular (WCAG 2.4.11; lección, simulacro, DAW y «Aprender», en móvil y escritorio), salto al contenido, orden de tabulación, temas claro y oscuro, movimiento reducido (en la portada no queda ninguna animación con `reduce`), reflujo a 320 px con la letra normal, el editor (Tab inserta espacios y Esc permite salir) y el color nunca va solo (✓ y ✗ con texto).

**Zonas táctiles:** el inspector marca enlaces de unos 19 px de alto en las listas de conceptos y de lecciones. La regla `target-size` de axe (WCAG 2.5.8) no los da por malos, porque tienen espacio libre alrededor. Se dejan como están.

### 12.3 Rendimiento

| Medida | Equipo normal | Móvil modesto simulado |
|---|---|---|
| Primer contenido en pantalla (FCP) | 0,3 s | 1,8 s |
| Mayor contenido en pantalla (LCP) en la portada | 0,9 s | 5,9 s |
| Cambio de ruta (aprender, PCAP, DAW, lección y progreso) | 30-80 ms | 50-210 ms |
| Memoria de JavaScript (heap) | 10 MB | 10 MB |
| Primera ejecución de Python (descarga y arranque de Pyodide) | 4 s | 72 s sin comprimir (unos 6 MB comprimidos en el CDN: unos 30 s) |

- **Pyodide ya se carga solo cuando el alumno ejecuta código.** Con una red lenta, la consola avisa a los 20 s de que sigue descargando, y el límite es de 5 minutos.
- **Lo que más pesa en la primera carga son los bytes**, no el número de peticiones. La portada pide 87 recursos: `lessons.json` (58 KB comprimido), `learning.json` (39 KB) y unos 150 KB de JavaScript comprimido. Se probó `rel="modulepreload"` para los 55 módulos y **no mejoró ninguna medida**, así que no se ha incluido.
- **Candidato para una fase posterior:** no descargar `lessons.json` en la portada. Exige cambiar cuándo se pinta la barra lateral y el juego, así que no es un cambio pequeño.

### 12.4 Pendiente

- Revisión manual con lector de pantalla (VoiceOver y NVDA) y con zoom real del navegador al 200 y al 400 %.
- Medir con Lighthouse la web publicada (con compresión y HTTP/2) en un móvil real.
- Los textos nuevos de la corrección de ejercicios están solo en español, como el resto de la vista de lección.
