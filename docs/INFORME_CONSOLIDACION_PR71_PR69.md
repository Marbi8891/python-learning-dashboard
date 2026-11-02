# Informe de consolidación de los PR #71 y #69

Fecha: 2 de noviembre de 2026 · Rama de trabajo: `claude/project-thread-g2kykr`

Este informe distingue tres estados:

- **Preparado:** el cambio está en una rama o en un PR abierto. No está en `main`.
- **Fusionado:** el cambio está en `main`.
- **Publicado:** la acción `pages.yml` publica `main` en GitHub Pages en cada merge. Por eso todo lo fusionado
  en `frontend/` queda publicado. Lo que no es del frontend (agentes, scripts, documentación) entra en `main`,
  pero no cambia la web.

## 1. Estado inicial de los PR

| PR | Rama | Base | Head | Estado | CI |
|---|---|---|---|---|---|
| #71 `fix(sync)` AUD-001 | `claude/project-thread-agb5v1` | `main` @ `9f2afc2` (al día) | `239e2e6` | Abierto, sin conflictos | Verde |
| #69 `feat(agentes)` mejorador-web | `claude/project-thread-crudrw` | `main` @ `f6a475b` (desfasada 2 merges) | `f391fcc` | Abierto, sin conflictos | Verde (sobre la base antigua) |

## 2. Auditoría del PR #71

Archivos: `frontend/js/sync-gate.js` (nuevo), `pcap-sync.js`, `course-store.js`, `learn/learn-store.js`,
`game.js`, `tests/unit/sync-gate.test.mjs` y `e2e/sync.spec.js`.

| # | Comprobación | Resultado |
|---|---|---|
| 1-4 | Diff completo, 7 archivos, `sync-gate.js` y los 4 almacenes | Revisados. Los 4 almacenes usan la puerta, y `push()` y `save*()` comprueban `ready`. |
| 5 | Ninguna escritura antes de la fusión inicial | Correcto. `push()` sale si la puerta no está abierta. La única subida de cuenta que no pasa por la puerta es `POST /api/progress/import` (lecciones completadas), y ese endpoint ya fusiona en el servidor. |
| 6 | Reintentos sin escrituras duplicadas | Correcto. `sync()` comparte la promesa en curso y `restart()` invalida las antiguas. Hay una prueba unitaria. |
| 7 | Una fusión de otra sesión no se usa | **Defecto D1** (ver abajo). La puerta no se abría, pero los datos de la otra cuenta ya se habían mezclado con los locales. |
| 8 | Cerrar sesión no pierde más datos locales | Correcto con el arreglo. `flush*` intenta fusionar y subir antes de borrar. Si el servidor no responde, los datos se borran igual que antes del PR (es lo que se quiere en equipos compartidos). |
| 9 | Cursos independientes | Correcto. Hay una puerta por curso y un fallo en uno no bloquea a los demás. |
| 10 | Datos de versiones anteriores | Correcto. No cambian las claves de `localStorage`, las funciones `merge*` ni el formato que se envía al backend. |
| — | Rendimiento al entrar | **Defecto D2** (ver abajo). Se hacían 8 `PUT` a la vez y dos e2e del panel fallaban de forma intermitente. |

### D1. La copia leída de otra sesión se mezclaba con los datos locales

`merge()` hacía el `GET` y la fusión juntos, y la puerta comprobaba la sesión **después**. Si la cuenta A
cambiaba a la B mientras se leía, la copia de A se fusionaba con los datos locales y se guardaba en el
navegador. Después, la fusión de B subía esos datos a la cuenta de B.

- Lo reproduje con el `sync-gate.js` original: un script devuelve `datos locales de B tras la respuesta tardía de A: [ 'cuenta de A' ]`.
- **Arreglo:** `createSyncGate({ load, merge })`. `load()` solo lee. Entre la lectura y `merge(remote)` se
  comprueba la sesión, y si ha cambiado, la copia se descarta. Añadí 2 pruebas unitarias: una lectura de
  otra sesión y un fallo al fusionar.

### D2. Ráfaga de subidas al entrar (e2e intermitentes)

El #71 subía al instante el resultado de cada fusión, así que al entrar salían 8 `PUT` a la vez. Antes se
subían con la espera de 1,5 s. Con eso, el panel se repintaba más tarde y le quitaba el foco al alumno.

- Fallos repitiendo `e2e/dashboard.spec.js`: **0 de 96 en `main`** y **4 de unas 140 con el #71**
  (`:146` «Reintentar» y `:200` navegación con teclado en el móvil).
- **Arreglo:** cursos, núcleo y logros vuelven a subir con la espera de 1,5 s. PCAP sigue subiendo al momento,
  como antes. `flush*` sube en el momento al cerrar sesión.
- No se cambió ningún test para que pasara. Probé a esperar en el test, pero no lo dejé: el fallo estaba en el código.

## 3. Pruebas del PR #71

Todas las ejecuté sobre el código de cada momento, con Chromium y Pyodide 314.0.7 servido en local.

| Prueba | #71 tal cual | #71 + correcciones (PR #72) |
|---|---|---|
| `npm run test:unit` | 75/75 | 77/77 |
| `npm run test:e2e` | 138/138 | 138/138 |
| `dashboard.spec.js` + `sync.spec.js` ×12, 4 workers | 4 fallos intermitentes | 120/120 |
| `e2e/sync.spec.js` con el código de `main` (503 en la primera lectura) | Fallan 2/2 (reproduce el P0) | — |
| Fallo de lectura inicial, 503, fusión tardía y cambio de sesión | Pruebas unitarias y e2e | Pasan, más el caso nuevo de cambio de sesión |
| CI de GitHub (backend, cursos, e2e) | Verde | Verde |

## 4. Fusión del PR #71

- El #71 **no se fusionó tal cual** por D1 y D2.
- Preparé el **PR #72**, que contiene el commit `239e2e6` del #71 sin cambios y la corrección `f249cc3`.
  El autor eligió «Fusionar #72 y cerrar #71».
- El autor fusionó el **#72** en `main` el 02/11 a las 11:11, con un merge commit (`89fe0c6`) y la CI en verde.
  El **#71 está cerrado** como sustituido. → **Fusionado y publicado.**

## 5. Auditoría del PR #69

| # | Regla del agente `mejorador-web` | Dónde está | Resultado |
|---|---|---|---|
| 1 | Nunca modifica `main` | §1 «Nunca en `main`» y paso 1 del flujo | Cumple |
| 2 | Trabaja en ramas `mejora/…` | Paso 1 del flujo | Cumple |
| 3 | No publica ni fusiona | §1, sin `push`, `merge` ni `deploy.ps1`. `/mejorar-web` lo repite | Cumple |
| 4 | Mejoras pequeñas y verificables | Una por ejecución, unos 5 archivos y unas 150 líneas como mucho | Cumple |
| 5 | No toca el backend | Lista de lo que no puede tocar | Cumple |
| 6 | No toca secretos | No lee `.env` ni `.local-secret` | Cumple |
| 7 | No toca la CSP sin autorización | La CSP y `config.js` están fuera de su alcance | Cumple |
| 8 | Respeta estilos y tokens | Usa los tokens de `base.css` | Cumple |
| 9 | Respeta claro y oscuro | Lo pide la guía. **El inspector solo captura el tema claro** (ver mejora R3) | Cumple a medias |
| 10 | WCAG 2.1 AA | axe-core con las mismas etiquetas que `a11y.spec.js` | Cumple |
| 11 | Pruebas antes de terminar | Paso 6, con las pruebas de `docs/TESTING.md` | Cumple |
| 12 | Antes y después | `--comparar` y la sección del informe final | Cumple |

Sobre el script `scripts/web/inspeccionar_web.mjs`:

- **Playwright y axe-core funcionan.** Inspeccionó 9 rutas × 2 vistas (18 páginas) con 0 infracciones axe y
  0 errores de consola, y reproduce MW-001 con 110 px.
- **No modifica el proyecto.** `git status --short` queda igual antes y después de ejecutarlo en un worktree
  limpio. Escribe en `mktemp` o en `--salida`.
- Solo admite `localhost` y `127.0.0.1`. Con `--url` apunta a un servidor que ya esté arrancado.
- El agente solo tiene `Bash`, `Edit` y `Write` para escribir. Sus límites son instrucciones, no permisos
  técnicos, así que la protección real es la regla del repositorio: el merge lo hace la persona.

## 6. Pruebas del PR #69

| Prueba | Resultado |
|---|---|
| `npm run test:unit` con #69 actualizado con `main` | 77/77 |
| Inspector, 9 rutas × móvil y escritorio | Se ejecuta. 0 axe, 0 errores de consola, desborde solo en `#/practicar` móvil |
| Merge de `main` en la rama | Sin conflictos. Actualicé la rama en GitHub (head `91f8476`) |
| CI de GitHub sobre la rama actualizada | backend, cursos y e2e en verde |
| e2e | No aplican: el PR no cambia la web |

## 7. Fusión del PR #69

Lo fusioné por **squash** el 02/11 (`16ed47a`), con `expectedHeadSha` `91f8476`. Antes comprobé que estaba
abierto, con base `main`, sin conflictos y con la CI en verde, y que el #72 ya estaba fusionado.
→ **Fusionado.** No cambia la web publicada.

## 8. Problemas detectados y corregidos

| ID | Problema | Estado |
|---|---|---|
| D1 | La lectura de otra sesión se mezclaba con los datos locales (#71) | Corregido. **Fusionado** (#72) |
| D2 | Ráfaga de 8 `PUT` al entrar y e2e del panel intermitentes (#71) | Corregido. **Fusionado** (#72) |
| MW-001 | `#lx-concept-select` se salía 109 px a 390 px y 179 px a 320 px. Causa: `min-width: auto` en un elemento flex, que hace que el `select` mida lo que su opción más larga (458 px). También se salía de su panel en escritorio (458 > 432 px) | Corregido con `min-width: 0; max-width: 100%` en `.lx-inline-form select` y una prueba e2e nueva que fallaba antes. **Preparado** en esta rama (PR propio) |

Medidas de MW-001 (Playwright, antes → después):

| Vista | Desborde de la página | Ancho del selector / formulario |
|---|---|---|
| Móvil 390 px (claro) | 109 → 0 px | 458 / 308 → 208 / 308 |
| Móvil 320 px (oscuro) | 179 → 0 px | 458 / 238 → 238 / 238 |
| Escritorio 1366 px | 0 → 0 px | 458 / 432 → 332 / 432 |

El inspector `--comparar` da `#/practicar (movil): desborde px 110 → 0` y ningún cambio en las demás rutas
medidas. La lista desplegable sigue mostrando el texto completo. Mantiene la altura de 40 px y el nombre
accesible «Concepto». Pasan `learn.spec.js`, `a11y.spec.js` y `ux.spec.js` (41/41), y la suite completa 139/139.

## 9. Estado de las ramas

| Rama | Estado |
|---|---|
| `claude/project-thread-agb5v1` (#71) | PR cerrado sin fusionar. Su commit está en `main` a través del #72 |
| `claude/project-thread-crudrw` (#69) | Fusionada por squash. La rama sigue en GitHub y se puede borrar |
| `claude/project-thread-g2kykr` | #72 fusionado. Rehecha desde `main` con MW-001 y este informe (PR nuevo, **preparado**) |

## 10. Estado de `main`

`16ed47a` (squash del #69) sobre `89fe0c6` (merge del #72). Contiene el arreglo de AUD-001 **publicado** y el
agente mejorador-web, que no afecta a la web. MW-001 **todavía no** está en `main`.

## 11. Primeras mejoras detectadas por el agente

Ejecuté `/mejorar-web` **en modo inspección**, con `claude -p --agent mejorador-web` sobre `main` + #69.
El agente lanzó el inspector completo, miró las capturas de móvil y escritorio y revisó el tema oscuro en
`#/aprender`, `#/teoria`, `#/practicar`, `#/pcap` y `#/portada`. **No cambió ningún archivo** (`git status`
limpio). El inventario completo, con todos los campos de cada mejora, y las capturas están en la carpeta del
proyecto `mejorador-web/inventario-2026-11-02/`, porque `.claude/informes/` no se sube a Git.

Resultado general: 0 infracciones axe y 0 errores de consola en 18 páginas. El único desborde es MW-001, ya
corregido. En el tema oscuro no apareció nada propio. **Sin medir:** las vistas con sesión (no había backend) y
el rendimiento más allá del inspector (las cargas en local van de unos 600 a 880 ms, sin valores que destaquen).

| Orden | ID | Problema | Ruta | Archivo | Prioridad del autor | Impacto | Esfuerzo |
|---|---|---|---|---|---|---|---|
| 1 | MW-005 | El botón flotante del asistente (60×60, fijo) tapa texto en móvil, también en las lecciones (confirmado en la captura) | `#/pcap`, `#/leccion/*`, `#/inicio` | `frontend/css/widgets.css:34-43` | 1 Móvil | Alto | S |
| 2 | MW-006 | Las pestañas de la lección se cortan en móvil («C…») sin indicar que hay más | `#/leccion/*` | `frontend/css/content.css:30-47` | 1 Móvil / 2 Navegación | Medio-alto | S |
| 3 | MW-002 | Los enlaces del pie del menú lateral miden 21 px de alto | Todas (menú móvil) | `frontend/css/sidebar.css:333-336`, `ux.css:57-62` | 2 Navegación | Medio | S |
| 4 | MW-007 | En móvil, el editor corta la última línea visible y el código de ejemplo se desborda sin aviso | `#/leccion/*` | `frontend/css/console.css:48-64`, `content.css:149` | 5 Editor | Medio | S |
| 5 | MW-004 | Portada en móvil: radios de 18×18, enlaces de índice de 19 px y 36 zonas táctiles pequeñas | `#/portada` | `frontend/css/landing.css` | 1 Móvil / 6 Accesibilidad | Medio | M |
| 6 | MW-003 | Los radios de idioma de PCAP miden 13×13 | `#/pcap` | `frontend/css/pcap.css:22-31` | 6 Accesibilidad | Bajo-medio | S |
| 7 | MW-008 | El paso «3 Comprueba» queda solo en una segunda fila | `#/leccion/*` | Sin localizar (`content.css` o `ux.css`) | 7 Consistencia | Bajo | S |

Cada mejora tiene en el inventario: la descripción con evidencia, la ruta, el archivo, la captura antes, el
resultado esperado, la solución propuesta, la prueba de regresión (archivo e2e y aserción) y la captura después
como «pendiente (se toma al aplicar la mejora)». Todas están **identificadas**: ninguna se ha preparado ni fusionado.

El agente recomienda empezar por **MW-005**, porque es lo único que oculta contenido y se arregla con un solo
bloque de CSS, y seguir con **MW-006**.

## 12. Recomendaciones para continuar la Fase 2

1. **Fusionar el PR de MW-001** (este). Es pequeño, tiene prueba de regresión y la suite completa en verde.
2. **Aplicar las candidatas de una en una** con `/mejorar-web MW-NNN`, en el orden de la tabla de la sección 11.
   Cada una en su rama `mejora/…`, con captura antes, prueba que falla, cambio mínimo y captura después.
3. **R3. Ampliar el inspector al tema oscuro** (`--tema oscuro` o una tercera vista con `colorScheme: "dark"`).
   Hoy la regla 9 del agente depende de que alguien lo mire a mano.
4. **Coordinar con el hilo «Auditar y rediseñar la web»**, que lleva la Fase 2 (404 y rutas, tokens, portada,
   catálogo y tema). Las mejoras MW que toquen tokens o colores deben ir después de su PR de tokens, para no
   chocar en el CSS.
5. Para la fase de persistencia queda pendiente que **dos pestañas o dispositivos escriban a la vez**: gana el
   último que escribe. Necesita una versión o una fusión en el servidor.
6. Para probar en la nube: hay que enlazar Pyodide en `frontend/_pyo` (lo instala `npm i pyodide@314.0.7` en una
   carpeta temporal) y lanzar las e2e con `PYODIDE_URL=http://localhost:5500/_pyo/`. Sin eso fallan las e2e que
   ejecutan Python.
