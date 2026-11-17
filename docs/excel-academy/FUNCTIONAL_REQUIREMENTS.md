# Requisitos funcionales · Excel profesional

**Anexo 3 de la [especificación maestra](MASTER_SPECIFICATION.md)** · Versión 1.0 · 16/11/2026 · Estado: **pendiente de revisión del propietario**.
Leyenda: **[H]** hecho comprobado · **[R]** recomendación · **[Hip]** hipótesis · **[D]** decisión pendiente (ver registro DP en la maestra).

Este anexo sustituye a la sección 3 y 4 del doc original 02. Conserva los identificadores RF-01…RF-20 y RNF-01…RNF-08 para que la trazabilidad con los documentos originales no se pierda, y añade RF-21 en adelante. Cada requisito lleva su fase (numeración de [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)) y su criterio de aceptación.

## 1. Qué es el producto

Un curso de Excel de Microsoft 365 en español de España, dentro de Python Learning Dashboard (PLD), con la ruta `#/academia/excel` y el nombre visible **«Excel profesional»** (DA-01, DA-02). Es el primer curso de la familia **academia** (DA-04). Reutiliza el sistema de cursos de DAW: generador en Python, JSON en `frontend/data/courses/`, vistas de `daw.js` y un documento de progreso por curso sincronizado con la cuenta (DA-03, DA-10).

«Excel Academy» es solo el nombre interno del proyecto en estos documentos. No aparece en la interfaz.

## 2. Relación con DAW (invariante)

| Id | Requisito | Aceptación | Fase |
|---|---|---|---|
| RF-23 | Los seis cursos de DAW, el PCAP, la portada, el panel, los logros y los certificados se comportan igual que en `main` | `DAW_COURSES` idéntico al de `main` (prueba `catalog.test.mjs`); `--check` de los seis cursos de DAW produce el mismo JSON byte a byte; `#/daw/cursos` muestra 6 tarjetas sin Excel (`e2e/excel.spec.js`); toda la batería existente en verde | P0 y siempre |
| RF-24 | Ninguna vista de DAW cuenta Excel (el panel por módulo, la preparación y el simulacro de DAW no lo incluyen) | e2e de panel y DAW sin cambios; `private.js` sigue usando PCAP + `DAW_COURSES` | P0 y siempre |

## 3. Usuarios y modos

| Modo | Qué puede hacer | Persistencia |
|---|---|---|
| Anónimo | Estudiar, hacer ejercicios, ver su progreso | `localStorage` `pld:course:excel` |
| Con cuenta | Lo mismo, y su progreso se fusiona y sincroniza entre dispositivos | Documento `excel` de `course_states`, por la API existente |
| Sin conexión (PWA) | Lo ya visitado; los cambios se suben al volver | Igual que DAW |

No hay roles nuevos. No hay docente ni administrador de Excel en el piloto.

## 4. Requisitos funcionales

Prioridad: A alta · M media · B baja. «Piloto» = M01 y M02.

### 4.1 Catálogo y rutas

| Id | Requisito | Prior. | Aceptación | Fase |
|---|---|---|---|---|
| RF-25 | El curso está registrado en `frontend/js/catalog.js` en la familia academia, con estado `planned` hasta que haya contenido | A | **[H] implementado en PR #159**: `ACADEMY_COURSES` con `id: "excel"`, `status: "planned"`; prueba `catalog.test.mjs` | P0 |
| RF-01 | Página principal del curso con presentación, horas, módulos, progreso y «Continuar» | A | e2e P-E2E-01: enlace directo y recarga en `#/academia/excel` | P2 |
| RF-02 | Lista de los 25 módulos con unidades, horas, nivel y estado | A | M01 y M02 activos; M03-M25 visibles como «próximamente», sin enlace | P2 |
| RF-03 | Página de unidad con los apartados de la plantilla de unidad ([CURRICULUM_M1_M2.md](CURRICULUM_M1_M2.md) §2) | A | El generador rechaza una unidad sin los mínimos; e2e abre una unidad y la recarga | P2 |
| RF-26 | Rutas `#/academia/excel`, `#/academia/excel/<unidad>` y `#/academia/excel/<unidad>/practica`; las rutas desconocidas dan la página 404 existente | A | e2e de enlace directo, recarga y 404 | P2 |

### 4.2 Ejercicios

| Id | Requisito | Prior. | Aceptación | Fase |
|---|---|---|---|---|
| RF-04 | Cuadrícula de datos con letras de columna y números de fila, como `<table>` con encabezados | A | P-ACC-03; a 320 px la página no se desplaza en horizontal | P1 (componente), P2 (uso) |
| RF-05 | Editor de fórmulas: escribir, comprobar con Intro o botón, ver el resultado o el error explicado con su posición | A | P-E2E-02; mensajes en `role="status"` | P1 (componente), P2 (uso) |
| RF-06 | Test teórico con explicación de la respuesta correcta y de cada distractor | A | Tipo `choice` existente; `why[]` opcional validado por el generador | P2 |
| RF-07 | «¿Qué devuelve esta fórmula?» con respuesta numérica, de texto o de opción | A | Tipo `formula-result`; el generador calcula la fórmula con el motor y se para si no coincide | P1 (tipo), P2 (contenido) |
| RF-27 | «Escribe la fórmula» corregida por comprobaciones (`value`, `fill`, `variants`, `references`, `noConstants`, `functions`), nunca comparando el texto | A | Tipo `formula`; el generador exige que la solución pase todas y que cada error frecuente falle al menos una | P1 (tipo), P2 (contenido) |
| RF-08 | Pistas de una en una y solución solo a petición; ver la solución registra el intento como fallado | A | Prueba unitaria P-UNI-07 y e2e | P2 |
| RF-09 | Descarga de .xlsx de práctica | A | **Aplazado** por DA-11 (el lector XLSX no se desarrolla); sustituido en el piloto por ejercicios de cuadrícula | P4 (con autorización) |
| RF-10 | Comprobación de un .xlsx resuelto en el navegador, sin subirlo | A | **Aplazado** por DA-11 | P4 (con autorización) |
| RF-11 | Rúbricas de autoevaluación, mostradas como «revisado por ti», nunca «aprobado» | M | Tipo `rubric`; en el piloto solo en `xl1-archivos` | P3 |
| RF-28 | Simulación de práctica: bloque de ejercicios de una unidad o módulo con datos nuevos, sin pistas, al final del módulo | M | Reutiliza el simulacro por bloques de DAW (`exam.blocks`) con preguntas `formula-result` y `formula` del módulo; se registra en `exams` | P3 |

### 4.3 Progreso y seguimiento

| Id | Requisito | Prior. | Aceptación | Fase |
|---|---|---|---|---|
| RF-12 | Marcar unidad como completada y continuar | A | Existe en DAW (`done`, `lastLesson`); e2e P-E2E-03 y 04 | P2 |
| RF-21 | El panel del curso distingue **completada** (marcada por el alumno) de **superada** (cumple los criterios de la unidad) | A | Prueba unitaria del cálculo; DAW no cambia (en DAW solo existe «completada») | P3 |
| RF-13 | Repaso espaciado de las preguntas falladas | M | `srs` existente (Leitner) sin cambios | P2 |
| RF-14 | Panel propio del curso con los indicadores de §5 | A | Prueba unitaria de cada indicador con un documento sintético | P3 (P2 parcial: unidades completadas y ejercicios aprobados) |
| RF-29 | El progreso anónimo se fusiona con la cuenta al iniciar sesión, en los dos sentidos | A | **[H] implementado en PR #159** (`e2e/excel.spec.js`, prueba 1) | P0 |
| RF-15 | Proyectos empresariales por entregas | A | Fuera del piloto | P4 |
| RF-16 | Constancia de progreso imprimible | B | Fuera del piloto; si se hace, dice «formativa» | P4 |

### 4.4 Avisos, compatibilidad y acceso

| Id | Requisito | Prior. | Aceptación | Fase |
|---|---|---|---|---|
| RF-17 | Etiqueta de versión (**[2019+]**, **[2021+]**, **[365]**) en cada función que no exista en todas | A | El generador rechaza una función sin etiqueta conocida; en M01-M02 ninguna la necesita | P2 |
| RF-18 | Avisos fijos: PLD no está afiliado a Microsoft; el contenido fiscal es educativo | A | Texto visible en la página del curso (e2e) | P2 |
| RF-22 | Aviso de corrección formativa: «La corrección se hace en tu navegador y sirve para aprender; no es una evaluación oficial» | A | Texto visible en la página del curso (e2e) | P2 |
| RF-19 | Funciona sin conexión una vez visitado | M | Archivos del motor y de las vistas en `precache.js` (`build_precache.mjs --check`) | P1-P2 |
| RF-20 | Accesible con teclado y lector de pantalla, sin depender del color | A | P-ACC-01/02/03 | P1-P2 |

## 5. Indicadores de seguimiento

Todos salen del documento `excel`; ninguno lee los de otros cursos. Los campos de cada pregunta (`functions`, `level`, `competences`) son datos del banco, no del progreso.

| Indicador | Definición exacta | Fase |
|---|---|---|
| Unidades completadas | Claves de `done` que son unidades del curso | P2 |
| Unidades superadas | Unidades que cumplen su `pass` ([CURRICULUM_M1_M2.md](CURRICULUM_M1_M2.md) §5) | P3 |
| Ejercicios aprobados | Preguntas cuyo último intento en `answers` es `true` | P2 |
| Funciones dominadas | Funciones con ≥ 2 preguntas en el banco, todas con el último intento correcto y ≥ 2 aciertos en total | P3 |
| Precisión en fórmulas | Preguntas `formula` acertadas al primer intento / preguntas `formula` intentadas | P3 |
| Nivel alcanzado | Nivel pedagógico más alto (1-5) con ≥ 80 % de sus preguntas con el último intento correcto | P3 |
| Competencias | % de preguntas superadas por competencia | P3 |
| Tiempo de estudio | **Estimado**: suma de los minutos previstos de las unidades completadas, con la etiqueta «estimado» (DA-08) | P2 |

**Niveles ≠ XP.** El «nivel alcanzado» es un indicador pedagógico (reconocimiento, aplicación, resolución, caso profesional, proyecto). No da puntos, no sube de nivel al usuario y no toca `game.js`. El piloto no tiene XP ni logros (DA-07). Si se quieren después, es la decisión DP-07.

## 6. Requisitos no funcionales

| Id | Requisito | Cómo se mide | Fase |
|---|---|---|---|
| RNF-01 | Sin dependencias de ejecución nuevas | `package.json`, `requirements.txt` y `frontend/vendor/` sin cambios de ejecución | Siempre |
| RNF-02 | Sin backend, tablas ni migraciones nuevas | Solo `"excel"` en `COURSES` (**[H]** PR #159) | P0 y siempre |
| RNF-03 | El motor no usa `eval`, `Function` ni equivalentes | P-SEG-01 (prueba que lee el código fuente) | P1 |
| RNF-04 | Comprobar una fórmula: < 50 ms p95 | P-REN-01 | P1 |
| RNF-05 | Leer un .xlsx de 1 MB < 1,5 s en un Worker | Aplazado con el lector (P4) | P4 |
| RNF-06 | El documento `excel` ≤ 60 KB con todo el curso hecho (el backend admite 200 KB) | Prueba con un documento sintético máximo | P3 |
| RNF-07 | DAW, PCAP y el resto siguen igual | = RF-23 | Siempre |
| RNF-08 | WCAG 2.2 AA en las páginas nuevas, en tema claro y oscuro | axe con 0 infracciones (P-ACC-01) | P2 |
| RNF-09 | El motor da el mismo resultado en Node 22 y en el navegador | P-INT-06 | P1 |
| RNF-10 | Los módulos del motor pesan < 60 KB sin minificar | P-REN-02 | P1 |
| RNF-11 | Funciona en Chromium y WebKit (Safari) | Prueba de humo P-E2E-09 en el job WebKit de CI | P2 |

## 7. Fuera del alcance del piloto

Lector y descarga de .xlsx (DA-11), M03 en adelante (DA-12), proyectos, constancia, evaluación verificada en el servidor, XP y logros, tiempo medido, docente o clase, subida de archivos, ejecución de macros o de Power Query en la web.
