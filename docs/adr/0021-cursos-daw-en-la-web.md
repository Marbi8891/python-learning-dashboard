# ADR-0021: Cursos de DAW también en la web

- **Estado:** Aceptada e implementada
- **Fecha:** 2026-09-29
- **Revisa:** ADR-0016 (cursos de DAW), ADR-0018 (estado de los cursos en la cuenta)

## Contexto

Los cursos de Programación, Bases de datos, Entornos, JavaScript y Java solo estaban en la app Android. La web solo tenía el PCAP. El autor pidió «más funciones para la web» y eligió, de entre las opciones, llevar allí estos cursos.

Ya existía todo lo necesario:

- los JSON de cada curso, generados y comprobados por `scripts/courses/`;
- el endpoint `/api/course-state/{curso}` (ADR-0018);
- el mismo formato de progreso en la web y en la app.

## Opciones

| Opción | Resumen | Veredicto |
|---|---|---|
| A. Copiar los JSON a `frontend/` al desplegar | Un paso más en el workflow de Pages | Descartada: en local (`Iniciar-Dashboard.bat`) no estarían, y habría dos copias |
| B. Duplicar los JSON en el repositorio | Un generador que escribe en dos carpetas | Descartada: dos fuentes que se pueden desincronizar |
| **C. Mover los JSON a `frontend/data/courses/`** | La app ya usa `frontend/data` como carpeta de assets | **Elegida**: una sola copia, y la ruta dentro del APK (`courses/<id>/`) no cambia |

## Decisión

- **Datos:**
  - Los JSON pasan de `android/app/src/main/assets/courses/` a `frontend/data/courses/<id>/`.
  - Los generadores escriben ahí y `CoursesTest` los lee de ahí.
  - La app no cambia de código: `frontend/data` ya era una de sus carpetas de assets.
- **Web:** zona nueva `#/daw` con la entrada «Cursos DAW» en el menú, implementada en `js/daw.js`:
  - **catálogo** con el progreso de cada curso;
  - **panel** con el acierto por bloque, ponderado por su peso, y las lecciones de cada bloque;
  - **lección**: teoría, ejemplo, ejercicio con pista, mini-quiz corregido, reto, dudas y fuentes;
  - **práctica** por bloque o «Repaso de hoy», con los tres tipos de ejercicio de la app: test, completar el hueco y ordenar líneas (el de «encontrar el error» es un test).
- **Reglas de corrección:** son las mismas que en la app (ADR-0017).
  - En «completar el hueco» no cuentan los espacios ni el `;` final.
  - En «ordenar líneas» se comparan los textos de las líneas.
  - Las líneas se ordenan **pulsando botones**, no arrastrando, para que funcione igual con teclado y lector de pantalla.
- **Progreso (`js/course-store.js`):**
  - Un documento por curso en `localStorage` (`pld:course:<id>`), con el mismo formato que la app: respuestas, repaso espaciado y mejor racha.
  - Con sesión iniciada:
    - al entrar, se trae de la cuenta y se fusiona con las mismas reglas que la app;
    - cada cambio se sube a `/api/course-state/<id>`, agrupando los que llegan seguidos en un solo envío.
  - Los campos que la web no conoce se conservan, para no borrar nada que añada la app.
- **Resaltado de código:** se añaden las gramáticas de SQL, Java y JavaScript de Highlight.js 11.9.0, la misma versión que ya se usaba.
- **Backend:** no cambia. Solo se amplía la lista `COURSES` con `entornos` y `programacion` (ADR-0020).

## Trade-offs y consecuencias

- `course-store.js` repite la lógica de repaso y fusión de `pcap-store.js` (unas 40 líneas), en lugar de refactorizar la zona PCAP.
  - **Por qué:** se evita cualquier riesgo en el PCAP, que está en producción.
  - **Deuda:** si se toca alguna de las dos, unificarlas en un módulo común.
- **Lista de cursos duplicada:** los títulos y el orden de los cursos están en `DAW_COURSES` (web) y en `PldApplication.kt` (app).
- **Peticiones al iniciar sesión:** se hacen 5 GET, una por curso, en paralelo. Son 5 documentos pequeños por usuario, no una consulta por fila (no es N+1).
- **Pruebas:** `e2e/daw.spec.js` cubre:
  - catálogo, teoría, mini-quiz, completar el hueco y ordenar líneas;
  - la sincronización con la cuenta, conservando los datos de la app;
  - accesibilidad WCAG 2.1 AA con axe.
- **Ejecutar el código de los cursos de Python en la web con Pyodide** (la web ya lo carga para el PCAP) queda como siguiente paso.
- **Al aplicar el cambio** hay que **borrar** la carpeta antigua `android/app/src/main/assets/courses/`: si no, el APK tendría assets duplicados.
