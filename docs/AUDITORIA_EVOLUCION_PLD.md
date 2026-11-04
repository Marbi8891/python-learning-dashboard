# Auditoría de evolución: PLD hacia el aprendizaje adaptativo (Fase 0)

Fecha: 04/11/2026 · Base: `main` en `d0b3884` · Alcance: solo lectura y pruebas, **sin cambios de código**.

Este documento es la Fase 0 del plan «Evolución hacia una plataforma personal de aprendizaje
adaptativo». Reutiliza las auditorías anteriores sin repetirlas: [`AUDITORIA_TECNICA.md`](AUDITORIA_TECNICA.md)
(técnica y seguridad), [`AUDITORIA_TEMARIO_DAW.md`](AUDITORIA_TEMARIO_DAW.md) (temario), el informe del
red team del 29/10 y la auditoría integral del 29/10 (ids `AUD-*`, `RT-*`, `SYNC-*`). Cada hallazgo
heredado se ha vuelto a comprobar contra el código de `d0b3884`; los nuevos empiezan por `EVO-`.

**Cómo leerlo.** Cada afirmación lleva una etiqueta:

- **[H] Hecho comprobado:** visto en el código o reproducido con una prueba (se cita dónde).
- **[Hip] Hipótesis:** razonable, pero no medido.
- **[P] Propuesta:** lo que recomiendo hacer; lo decide el autor.

Prioridades: **P0** crítico · **P1** alto · **P2** medio · **P3** bajo.

---

## 1. Estado real del proyecto

### 1.1 Pruebas ejecutadas en esta auditoría (04/11/2026, contenedor en la nube)

| Suite | Orden | Resultado |
|---|---|---|
| Backend | `cd backend && python -m pytest -q --cov=app --cov-fail-under=100` | **649 passed**, cobertura 100 % |
| Lint | `ruff check . ../e2e ../scripts` | Sin errores |
| Unitarias del frontend | `npm run test:unit` | **130/130** |
| Núcleo por conceptos | `python scripts/learning/build_learning.py --check` | Al día: 22 conceptos, 131 ejercicios comprobados |
| Currículo DAW | `python scripts/curriculum/build_curriculum.py --check` | Al día: 17 módulos (9 con RA oficiales), 64 RA, 516 CE |
| Cursos DAW | `python scripts/courses/<curso>_course.py --check` (los 6) | Los 6 correctos |
| End-to-end | `npx playwright test` (Chromium del contenedor, Pyodide servido en local según `TESTING.md`) | **196/197**; 1 intermitente (§1.2) |

No se han ejecutado: migraciones contra PostgreSQL (no hay servidor en el contenedor), `pip-audit` /
`npm audit` (no aportan a esta fase), WebKit/Safari (no hay proyecto de WebKit en `playwright.config.js`).

### 1.2 Resultado de las e2e

**196 de 197 pasan** (5,6 min, 3 workers). Falla una: `my-account.spec.js:26` «plan de estudio: fecha
de examen por curso y meta diaria que se guardan», en la línea 34 (`toBeFocused`: el campo de fecha
pierde el foco tras guardar). Repetida sola 5 veces con 1 worker, **pasa las 5**: es **intermitente**
bajo carga, no un fallo determinista (ver EVO-16). El mismo tipo de fallo ya se vio en «Aprender» y se
arregló con `focusSelector` en `app.js` (#87).

### 1.3 Cifras del producto [H]

- 22 conceptos y 131 ejercicios en el núcleo adaptativo (`frontend/data/learning.json`): 48 `output`,
  31 `choice`, 23 `code`, 16 `bug`, 7 `fill`, 6 `order`. Entre 3 y 9 ejercicios por concepto.
- 6 cursos de DAW con 520 preguntas en `frontend/data/courses/*/bank.json` y 56 lecciones; solo 10
  lecciones tienen `objectives` con referencias a RA en `main` (24 cuando se fusione #96).
- PCAP: 126 preguntas (`frontend/data/pcap.json`) en 5 bloques con peso oficial.
- Currículo: 17 módulos; 9 con RA y CE literales del RD 405/2023; 8 sin RA en el catálogo.
- Pruebas: 649 pytest, 130 unitarias, 197 casos e2e en 21 ficheros `*.spec.js`.

### 1.4 Pull requests abiertos [H]

| PR | Estado frente a `main` | Qué hacer |
|---|---|---|
| **#96** Bases de datos (14 lecciones) | Base `d0b3884` (= `main`), fusiona sin conflictos. 3 archivos: `sql_course.py`, `sql/lessons.json`, `AUDITORIA_TEMARIO_DAW.md` | Independiente de F1. Fusionarlo **antes** de F1 evita tocar `lessons.json` en paralelo si F1 mapea lecciones a RA |
| **#95** Memoria del Proyecto Intermodular | Base `d0b3884`, sin conflictos. Solo `docs/memoria/*` y `DEMO-Y-DEFENSA.md` | Independiente. Al terminar F1 habrá que añadir el motor 2.0 a la memoria: mejor hacerlo sobre #95 ya fusionado |
| **#84** Estrategia de producto y roadmap | Base antigua (11 commits por detrás), pero sin conflictos. 4 documentos en inglés + README | **Choca con el objetivo actual**: está orientado a negocio (precios, B2B, academias, piloto con 10-20 usuarios). Sus ADR-005 (sincronización sin conflictos) y ADR-006 (recomendaciones transparentes primero) coinciden con este plan. [P] No fusionarlo tal cual; rescatar esas dos decisiones en `docs/DECISIONS.md` y cerrarlo o dejarlo aparcado |
| **#61** Auditoría integral y mejoras (21/10) | 37 commits por detrás y **con conflictos** (base anterior a #62) | Ya documentado como obsoleto (AUD-027). [P] Cerrarlo; lo útil (`progress-file.js`, `check_site.py`) se rehace desde `main` si se quiere |
| #65 Tutor híbrido con OpenAI | Base `944af1e` | Base de la Fase 3. No tocar ahora (API de pago) |
| #68 Docker local · #63 aviso legal · Dependabot #19, #16, #14, #13 | — | Fuera de alcance. #16 y #13 apuntan a `/android`, que ya no existe |

Ningún PR abierto toca `frontend/js/learn/*`, `learning.json` ni `scripts/learning/*`, así que **F1 no
duplica trabajo de ninguna rama abierta** [H] (`git diff --stat origin/main...<rama>` de cada una).

---

## 2. Arquitectura actual [H]

```
GitHub Pages ─ HTML + CSS + JS (ES modules, sin framework) + datos JSON generados
   │  sw.js (network-first para la web, cache-first para Pyodide; la API nunca se cachea)
   │  Web Worker + Pyodide ─ ejecuta y corrige Python (frontend/py/runner.py, el mismo que usa pytest)
   │  i18n.js ─ español en el código; inglés traduciendo el DOM por coincidencia exacta (i18n/en.json)
   │
   └─ fetch con cookie HttpOnly + cabecera X-PLD-Session ─► FastAPI (Render, Docker)
                                                            └─ SQLAlchemy + Alembic ─► PostgreSQL (Neon) / SQLite local
```

**Almacenes de progreso en el navegador** (cada uno con su clave de `localStorage` y su documento en la cuenta):

| Almacén | Clave local | Documento en la API | Modelo de dominio / repaso |
|---|---|---|---|
| Núcleo por conceptos | `pld:learn` | `/api/course-state/learn` | `learn/mastery.js`: dominio por concepto + Leitner por concepto (cajas 0-5) |
| PCAP | `pld:pcap` | `/api/pcap-state` | `pcap-store.js`: Leitner **por pregunta** (cajas 1-5) + «preparación» por bloques |
| Cursos DAW (6) | `pld:course:<id>` | `/api/course-state/<id>` | `course-store.js`: Leitner **por pregunta** + «preparación» por bloques |
| Lecciones PCAP completadas | `pld:completed` | `/api/progress` (tabla `lesson_progress`) | — |
| Gamificación | `pld:game` | `/api/course-state/game` | `game.js`: XP **calculada** a partir de hechos, no un contador |
| Tiempo diario | `pld:daily-study-minutes` | ninguno (solo local) | `learn-app.js:51` |

La sincronización de los documentos es común: `sync-gate.js` (no sube nada hasta fusionar la copia
de la cuenta, AUD-001), `doc-sync.js` (versión optimista y 409 → releer, fusionar, reintentar),
`uploader.js` (reintentos y aviso), `local-owner.js` (progreso de otra cuenta apartado, AUTH-02). En el
servidor, `state_documents.py` guarda el documento entero con `UPDATE … WHERE version = :leída`.
El backend **no interpreta** los documentos de progreso: los guarda como JSON opaco de hasta 200 KB
(`schemas.py:184`) y todo el cálculo de dominio se hace en el navegador.

**Agentes de Claude Code** (`.claude/agents/`): `revisor-daw` (revisión con evidencias),
`buscador-mejoras` (propuestas priorizadas), `red-teamer` (seguridad, solo lectura), `mejorador-web`
(una mejora pequeña de frontend por rama). [P] **No hace falta ningún agente nuevo para F1**: la
revisión del motor la cubre `revisor-daw` y la seguridad, `red-teamer`. Un agente de QA o de IA
duplicaría responsabilidades; se puede reconsiderar en la Fase 3.

---

## 3. Funcionalidades existentes [H]

**Motor de aprendizaje (`frontend/js/learn/`)**

- `mastery.js`: registro de intentos (últimos 5 por ejercicio, contador total `n`, registro de 300
  eventos), errores típicos con racha de corrección (`FIXED_STREAK = 2`) y caducidad (21 días),
  dominio por concepto ponderado por nivel (1 / 1,5 / 2) sobre **todos** los ejercicios del concepto,
  estados `nuevo · leido · aprendiendo · progreso · dominado`, Leitner por concepto con intervalos
  0-1-3-7-14-30 días, validación de documentos externos (`cleanLearning`) y fusión (`mergeLearning`).
- `recommend.js`: plan de «Hoy» por reglas en orden fijo (repasos vencidos → errores → DAW débil →
  nuevo con prerrequisitos firmes → repaso general), cada acción con su **motivo en texto**; bloqueo
  por prerrequisitos (`READY_SCORE = 0.6`); selección de ejercicios por puntuación (errores activos,
  fallados, nuevos, nivel adecuado); ajuste del plan al tiempo disponible (`fitPlanToBudget`, 15-180 min,
  sin saltarse la prioridad).
- `exam.js`: competencias DAW ponderadas, avisos «refuerza X antes de Y», preparación estimada,
  simulacro con reparto por competencias, prueba de nivel.
- `session.js`: ciclo intento → explicación → nuevo intento; los reintentos no cuentan para el dominio
  ni para la nota.
- `activity.js`: resumen real para la portada («Continúa donde lo dejaste»), sin datos de ejemplo.

**Resto de la plataforma:** Python en el navegador con límite de 10 s y red cortada en el worker;
cursos DAW con progreso por lección; currículo oficial con RA y CE; progreso por módulo oficial
(`dashboard-data.js:116`, «practicada» frente a «dominada» con 2 aciertos seguidos); PCAP con
simulacro de 40 preguntas/65 min y plan por fecha de examen (`pcap.js:116`); cuenta con email o Google,
recuperación de contraseña, exportación y borrado (RGPD); PWA; inglés; WCAG 2.2 AA con axe.

---

## 4. Funcionalidades incompletas [H]

| Id | Qué falta | Evidencia |
|---|---|---|
| EVO-01 | **Tres modelos de dominio distintos** que no se hablan: conceptos (`mastery.js`), preguntas de cursos y PCAP (`course-store.js`, `pcap-store.js`) y módulos oficiales (`dashboard-data.js:105`, 2 aciertos seguidos). Un mismo alumno puede ver «dominado» en un sitio y «practicada» en otro | Lectura de los tres archivos |
| EVO-02 | El núcleo adaptativo solo cubre **22 conceptos de Programación en Python**. Las 520 preguntas de los cursos DAW no tienen concepto, prerrequisitos ni errores típicos: solo `lesson`, `block` y `module` | `bank.json` de cada curso |
| EVO-03 | **Sin enlace estructurado con RA/CE.** Los conceptos tienen `ut` (unidad) pero no RA ni CE; las lecciones citan los RA en texto libre (`objectives`) | `learning.json`, `courses/*/lessons.json` |
| EVO-04 | **Sin confianza estadística**: el dominio se muestra con porcentaje aunque solo haya un intento | `conceptStats` en `mastery.js:140` |
| EVO-05 | **Sin retención**: un concepto dominado hace un año sigue «dominado» | Reproducido (§6) |
| EVO-06 | El plan diario **no conoce fechas de examen** ni entregas: `recommend.js` no lee `plan.examDate` (solo existe en PCAP y cursos) | `grep examDate frontend/js` |
| EVO-07 | No se puede **posponer ni rechazar** una tarea del plan, ni consultar el **historial** de planes | `learn-app.js` |
| EVO-08 | El tiempo diario solo se guarda en el navegador (`pld:daily-study-minutes`): no viaja con la cuenta | `learn-app.js:48` |
| EVO-09 | Sin analítica de estudio (horas, tiempo por asignatura, evolución semanal) más allá de la actividad diaria del panel | `routers/dashboard.py` |
| AUD-008 | La PWA solo precachea 6 archivos: sin conexión solo funciona lo ya visitado | `sw.js:9` (sigue igual) |

---

## 5. Problemas técnicos

| Id | P | Problema | Evidencia |
|---|---|---|---|
| AUD-011 | P2 | Leitner y fusión **duplicados** en `mastery.js`, `course-store.js` y `pcap-store.js` (`INTERVAL_DAYS` copiado tres veces, con cajas 0-5 en uno y 1-5 en los otros) | [H] `grep INTERVAL_DAYS` |
| EVO-10 | P1 | **`cleanLearning` descarta los campos que no conoce.** Si F1 añade campos al documento `learn`, una pestaña con el JavaScript anterior los borraría al fusionar y volvería a subir el documento sin ellos. `cleanProgress` de los cursos sí conserva lo desconocido | [H] `mastery.js:224-262` frente a `progress-guard.js:44` |
| EVO-11 | P2 | La historia por ejercicio guarda solo 5 resultados sin fecha individual; el registro, 300 eventos. Para dar **evidencias identificables** hace falta guardar algo más (p. ej. fecha del último acierto) | [H] `mastery.js:19-21` |
| EVO-12 | P3 | Los textos del motor («Toca repasarlo…») se traducen por coincidencia exacta del DOM: cada frase nueva con datos necesita su entrada con huecos en `i18n/en.json` | [H] `i18n.js:1-10` |
| AUD-034 | P3 | `app.js`, `dashboard.js`, `pcap.js`, `landing.js` > 750 líneas mezclando datos y HTML | [H] `wc -l` |
| EVO-16 | P2 | Prueba intermitente: tras guardar la fecha de examen en «Mi panel», el campo pierde a veces el foco (1 fallo de 6 ejecuciones). [Hip] Causa probable: un repintado en segundo plano, como en #87 | [H] fallo `e2e/my-account.spec.js:34`; la vista está en `private.js:293-297` |
| EVO-13 | P3 | Las e2e solo corren en Chromium: no hay prueba en WebKit/Safari aunque el autor usa Mac | [H] `playwright.config.js:19` |

Tamaño: un documento `learn` con los 131 ejercicios intentados 5 veces ocupa **~34 KB** de los 200 KB
permitidos [H] (medido con `mastery.js`). Hay margen para F1.

---

## 6. Problemas de aprendizaje adaptativo

Reproducidos con un script de Node sobre los módulos reales y `learning.json` (no forma parte del repo):

```
AUD-004 box/due tras 5 sesiones el mismo día: 5 2026-12-04
AUD-003 estado sin cerrar sesión: dominado nextReview: null
Repetir 1 ejercicio 20 veces -> score 0.14 n 20
Dominio 1 año después sin practicar: dominado
AUD-002 placed con 1 acierto: true kind: output
```

| Id | P | Problema | Estado |
|---|---|---|---|
| AUD-004 | **P1** | El repaso espaciado se **comprime en una tarde**: cada sesión sube una caja aunque no tocara repasar; 5 sesiones seguidas = repaso a 30 días | [H] Reproducido. El test `mastery.test.mjs:99` no lo impide |
| AUD-003 | **P1** | Si se abandona la sesión, el concepto queda «dominado» **sin repaso programado**: el repaso solo se programa en `finish()` | [H] Reproducido |
| EVO-05 | **P1** | **Sin decaimiento**: lo dominado no se olvida nunca para el motor | [H] Reproducido |
| AUD-002 | **P1** | La prueba de nivel da un concepto por **superado con un solo acierto** de opción múltiple o de salida (25 % de acertar al azar en `choice`); además, un fallo en la prueba cuenta como «empezado» y saca el concepto de «nuevo» | [H] Reproducido (`session.js:120`, `recommend.js:37`) |
| AUD-006 | **P1** | «Preparación» de PCAP y cursos llega al **100 % con una respuesta acertada por bloque** (5 de 126 en PCAP): la tasa usa solo las preguntas respondidas | [H] `pcap-store.js:140`, `course-store.js:144` |
| AUD-005 | P2 | «Dominado» exige un acierto de nivel ≥ 2, pero **8 de 22 conceptos no tienen ningún ejercicio de código** (`algoritmos`, `variables`, `tipos`, `operadores`, `bucles`, `modulos`, `trazado`, `depuracion`) | [H] Recuento sobre `learning.json` |
| EVO-04 | P1 | Se muestran porcentajes sin evidencia suficiente (ver §4) | [H] |
| EVO-14 | P2 | La prioridad del plan es un **orden fijo de reglas**, no una puntuación: no se puede comparar un repaso vencido de algo poco importante con un error reciente en algo clave | [H] `recommend.js:58-124` |

**Lo que ya está bien y hay que conservar** [H]: repetir el mismo ejercicio **no infla** el dominio (20
aciertos del mismo ejercicio = 0,14, el peso de ese ejercicio); los reintentos tras la explicación no
cuentan; los errores se corrigen con aciertos en ejercicios que los detectan; cada recomendación ya
lleva su motivo; el plan respeta los prerrequisitos.

---

## 7. Problemas de sincronización

Comprobado en el código de `d0b3884` [H]: AUD-001, SYNC-01, SYNC-02, SYNC-04, AUTH-01 y AUTH-02
**siguen corregidos** (puerta de sincronización, versión con 409, uploader con reintentos, propietario
local), y sus pruebas pasan (`sync-gate.test.mjs`, `doc-sync.test.mjs`, `merge.test.mjs`,
`uploader.test.mjs`, `local-owner.test.mjs`, `test_state_versions.py`).

| Id | P | Problema |
|---|---|---|
| SYNC-03 | P3 | `PUT` sin `version` sigue sobrescribiendo (compatibilidad con pestañas antiguas) — `state_documents.py:53`. Sigue abierto |
| EVO-10 | **P1 para F1** | Campos nuevos en `learn` se perderían con clientes antiguos (ver §5). **Es el principal riesgo de compatibilidad de F1** |
| EVO-15 | P2 | La fusión de `ex` elige la copia con el intento más reciente y se queda con su historia de 5: los intentos de la otra copia se pierden de la historia (no del contador `n`). Con evidencias nuevas habrá que fusionar por unión de eventos, no por «gana el más reciente» [H] `mastery.js:273-282` |

---

## 8. Problemas de seguridad

Sin hallazgos P0 ni P1 abiertos [H]. Revisado de nuevo: el usuario sale siempre del token
(`deps.py`), escrituras limitadas a 120/min (AUD-009, `test_write_limits.py`), documentos de 200 KB
como máximo, `cleanLearning` valida ids y tipos antes de pintar. Siguen abiertos, sin cambios:
RT-001 (escapado solo en cliente, P3), RT-002 (Pyodide sin SRI, P2), RT-003/004/005 (P3),
RT-006/AUD-018 (límites en memoria, P3), SEC-01 (P3). Detalle en `AUDITORIA_TECNICA.md` §5.

Para fases futuras [P]: la Fase 3 (tutor IA) es la que más superficie añade: claves solo en backend,
presupuesto, minimización de datos. Se revisará con `red-teamer` antes de abrirla.

---

## 9. Dependencias y deuda técnica

- Frontend sin dependencias de ejecución salvo Pyodide 314.0.7 y highlight.js (vendorizado). Pruebas:
  `@playwright/test 1.63.0`, `@axe-core/playwright 4.10.2` (Dependabot #19 propone 4.13.0) [H].
- Backend: FastAPI, SQLAlchemy, Alembic, PyJWT, Argon2 (`requirements.txt`) [H].
- [P] **F1 no necesita ninguna dependencia nueva**: todo son funciones puras de JavaScript y, como mucho,
  un id nuevo en `COURSES` del backend.
- Deuda principal: AUD-011 (Leitner triplicado), EVO-01 (tres modelos de dominio), AUD-034 (archivos grandes).

---

## 10. Oportunidades de mejora

1. **Un único módulo de repaso espaciado** (`learn/srs.js`) usado por conceptos, PCAP y cursos [P].
2. **Evidencias en vez de «último intento»**: dominio = media ponderada por dificultad y antigüedad de
   la mejor evidencia de cada ejercicio distinto; confianza = cantidad y variedad de evidencias [P].
3. **Grafo de conocimiento con RA/CE**: añadir `module`, `ra`, `ce`, `difficulty` e `importance` a
   cada concepto en `scripts/learning/concepts.py` (nunca a mano en el JSON), validados contra
   `daw-cyl.json` en `build_learning.py --check` [P].
4. **Recomendador por puntuación explicable** con la fórmula del plan (R, E, D, W, T normalizados) y
   restricciones duras (prerrequisitos, repasos vencidos primero) [P].
5. **Documento `planner`** separado para fechas de examen, tiempo disponible y estado de las tareas,
   para no tocar el formato de `learn` más de lo necesario [P].

---

## 11. Riesgos

| Riesgo | Prob. | Impacto | Mitigación [P] |
|---|---|---|---|
| Un cliente antiguo borra los campos nuevos de `learn` (EVO-10) | Media (pestañas abiertas, caché del SW) | Pérdida de evidencias | Paso 1 de F1: hacer que `cleanLearning` **conserve lo desconocido** y publicarlo **antes** de añadir campos; los campos nuevos han de poder **recalcularse** desde `log` y `ex` |
| Cambiar la definición de «dominado» baja los porcentajes que el autor ya ve | Alta | Confusión, no pérdida | Explicarlo en la interfaz y en `ADAPTIVE_ENGINE.md`; el motor nuevo se calcula a partir de los mismos datos |
| Cambiar ids de conceptos, ejercicios o preguntas | Baja | Progreso huérfano | Prohibido; `ids.lock.json` y `build_learning.py --check` ya lo vigilan para cursos. [P] Añadir candado equivalente para `learning.json` |
| Ajustar pesos sin datos reales | Alta | Recomendaciones discutibles | Pesos como constantes con pruebas de **propiedades** (vencido gana, prerrequisito bloquea), no de valores exactos; no afirmar mejoras sin uso real |
| Trabajo en paralelo con Cursor sobre los mismos archivos | Media | Conflictos | Reparto de archivos por tarea (§13) y un PR por tarea |
| Textos nuevos sin traducir | Alta | Interfaz mezclada en inglés | Prueba `idiomas.spec.js` y entradas con huecos en `en.json` |

---

## 12. Recomendaciones priorizadas

| # | P | Recomendación | Hallazgos |
|---|---|---|---|
| 1 | P0 (integridad) | Compatibilidad hacia delante del documento `learn` antes de cambiar nada más | EVO-10 |
| 2 | P1 | Arreglar el Leitner actual: no subir de caja antes de la fecha; programar repaso también al abandonar | AUD-004, AUD-003 |
| 3 | P1 | Prueba de nivel más exigente y que no marque «empezado» | AUD-002 |
| 4 | P1 | «Preparación» con cobertura mínima y estado «sin datos suficientes» | AUD-006, EVO-04 |
| 5 | P1 | Motor de dominio 2.0 con evidencias, confianza y retención | EVO-04, EVO-05, EVO-11, EVO-15 |
| 6 | P1 | Módulo SRS único | AUD-011 |
| 7 | P1 | Recomendador con puntuación explicable | EVO-14, EVO-06 |
| 8 | P1 | Planificador diario con posponer, rechazar e historial | EVO-07, EVO-08 |
| 9 | P2 | Modelo de conocimiento con RA/CE; después, extender a cursos DAW | EVO-02, EVO-03, EVO-01 |
| 10 | P2 | PWA sin conexión real | AUD-008 |
| 11 | P2 | Conservar el foco al repintar «Mi panel» (prueba intermitente) | EVO-16 |
| 12 | P3 | WebKit en las e2e | EVO-13 |

---

## 13. Plan técnico de la Fase 1 (Motor adaptativo 2.0)

### 13.1 Decisiones que debe tomar el autor antes de empezar

- **D1 · Alcance de F1:** [P recomendado] F1 sobre los **22 conceptos del núcleo** (Programación) y
  unificar el repaso de cursos y PCAP; dejar que los cursos DAW entren en el grafo de conceptos en una
  F1-bis, porque necesita crear conceptos y errores para 520 preguntas (trabajo de contenido, no de motor).
- **D2 · Dónde guardar el plan:** [P recomendado] documento nuevo `planner` (`/api/course-state/planner`,
  un id más en `COURSES`), que los clientes antiguos no conocen ni tocan.
- **D3 · Cambio visible del dominio:** aceptar que algunos «dominado» actuales pasen a «en progreso» o
  «sin datos suficientes» al aplicar evidencias y retención.

### 13.2 Diseño propuesto [P]

**Evidencia.** Por ejercicio distinto: resultado del último intento, fecha del último acierto (`okAt`,
campo nuevo, recalculable desde `log` si falta), número de intentos, nivel y tipo. Los reintentos no
cuentan (como ahora).

**Dominio** (determinista y reproducible, `now` como parámetro):

```
peso(e)        = dificultad(e) × frescura(e)              dificultad: 1 / 1,5 / 2 (como hoy)
frescura(e)    = 0,5 ^ (días desde okAt / vida_media)     vida_media según la caja de Leitner del concepto
dominio(c)     = Σ peso(e) · acierto(e)  /  Σ dificultad(e) de TODOS los ejercicios de c
confianza(c)   = min(1, distintos/K) × min(1, tipos_distintos/T)     K = 4, T = 2 (a validar)
estado         = «sin datos suficientes» si confianza < 0,5; si no, los estados actuales
```

- Repetir un ejercicio solo refresca su `okAt`: no suma más peso (se conserva la propiedad actual).
- Se muestra el porcentaje **solo** con confianza ≥ 0,5; si no, «Aún no hay evidencias suficientes».
- Cada valor se puede explicar: «4 ejercicios distintos de 3 tipos; el último acierto, hace 12 días».

**Repaso espaciado** (`learn/srs.js`, compartido): cajas 0-5 con los intervalos actuales; solo se sube
de caja si el repaso **estaba vencido** (arregla AUD-004); fallar baja a la caja 1; al registrar un
intento fuera de sesión se programa el repaso si no lo hay (AUD-003); repaso manual = sesión de
práctica, que no adelanta la caja.

**Recomendador:** P = 0,25 R + 0,25 E + 0,20 D + 0,15 W + 0,15 T, cada factor en [0, 1]:
R = días de retraso del repaso / intervalo (tope 1); E = errores activos del concepto, normalizado;
D = 1 − dominio; W = `daw` / 3; T = 1 − días hasta el examen / 60 (0 sin fecha). Restricciones duras:
un concepto con prerrequisitos flojos no se propone como nuevo (se propone el prerrequisito); los
repasos vencidos van primero. Cada acción devuelve los factores para explicar el porqué.
Los pesos se validan con **pruebas de propiedades** y escenarios; no se presentan como óptimos.

**Planificador:** usa `fitPlanToBudget` (ya existe) con el tiempo del documento `planner`; cada tarea
tiene estado `pendiente · hecha · pospuesta · rechazada` y fecha; un rechazo baja la prioridad de ese
concepto ese día; historial de los últimos 30 días.

### 13.3 Tareas, archivos y estimación

Estimación en sesiones de trabajo (S ≈ medio día, M ≈ 1-2 días, L ≈ 3-5 días). Son estimaciones [Hip].

| Tarea | Prioridad | Archivos | Pruebas nuevas | Esfuerzo |
|---|---|---|---|---|
| **F1.0** Compatibilidad: `cleanLearning` conserva campos desconocidos; candado de ids de `learning.json` | P0 | `learn/mastery.js`, `scripts/learning/build_learning.py`, `scripts/learning/ids.lock.json` (nuevo) | `mastery.test.mjs`, `merge.test.mjs`: documento con campos futuros sobrevive a limpiar y fusionar | S |
| **F1.1** Leitner y prueba de nivel corregidos (AUD-002/003/004) | P1 | `learn/mastery.js`, `learn/session.js`, `learn/recommend.js` | Actualizar `mastery.test.mjs:99` (decisión del autor) y añadir casos de sesión abandonada y diagnóstico | S |
| **F1.2** Módulo `learn/srs.js` común; `pcap-store.js` y `course-store.js` lo usan sin cambiar su formato | P1 | `learn/srs.js` (nuevo), `pcap-store.js`, `course-store.js` | `srs.test.mjs` (nuevo); `merge.test.mjs` sigue pasando | M |
| **F1.3** Preparación con cobertura mínima (AUD-006) | P1 | `pcap-store.js`, `course-store.js`, `learn/exam.js`, vistas en `pcap.js`, `daw.js` | Unitarias de `readiness`; e2e `pcap.spec.js` | S |
| **F1.4** Modelo de conocimiento: `module`, `ra`, `ce`, `difficulty`, `importance` por concepto | P2 | `scripts/learning/concepts.py`, `build_learning.py` (valida RA/CE contra `daw-cyl.json`), `learning.json` regenerado | `build_learning.py --check`, `test_content.py` o test nuevo en backend | M |
| **F1.5** Dominio 2.0: evidencias (`okAt`), frescura, confianza, estado «sin datos suficientes» | P1 | `learn/mastery.js`, `learn/ui.js`, `learn/learn-app.js`, `dashboard.js`, `i18n/en.json` | `mastery.test.mjs`: reproducibilidad, repetición no infla, confianza por variedad, decaimiento; e2e `learn.spec.js` | L |
| **F1.6** Fusión por unión de evidencias (EVO-15) | P1 | `learn/mastery.js` | `merge.test.mjs`: dos dispositivos, ninguna evidencia perdida | S |
| **F1.7** Recomendador por puntuación con explicación | P1 | `learn/recommend.js`, `learn/activity.js`, `learn/learn-app.js` | `recommend.test.mjs`: vencido primero, prerrequisitos, proximidad de examen, explicación presente | M |
| **F1.8** Documento `planner` (fechas, tiempo, estado de tareas, historial) | P1 | `backend/app/schemas.py` (`COURSES`), `learn/planner-store.js` (nuevo), `learn/learn-app.js`, `dashboard.js` | pytest de `course-state/planner`; `planner.test.mjs`; e2e completar/posponer/rechazar y sincronizar entre dos contextos | M |
| **F1.9** Documentación: `ADAPTIVE_ENGINE.md` y `DECISIONS.md`; ampliar `TESTING.md` (no crear `TEST_STRATEGY.md`, ya existe equivalente) | — | `docs/` | — | S |

Total orientativo: 4 S + 4 M + 1 L ≈ **10-15 días de trabajo**. Orden: F1.0 → F1.1 → F1.2 → F1.3 →
F1.5 → F1.6 → F1.7 → F1.8, con F1.4 en paralelo (solo toca `scripts/learning/`) y F1.9 al final.
Un PR por tarea.

### 13.4 Reparto Claude Code / Cursor [P]

- Claude Code: contratos (firmas de `srs.js`, `conceptStats` v2, `planner`), criterios de aceptación,
  revisión con `revisor-daw`, coordinación de pruebas.
- Cursor: implementa una tarea cada vez en su rama.
- Regla de archivos: `mastery.js` lo tocan F1.0, F1.1, F1.5 y F1.6 **en serie**; F1.4 (`scripts/learning/*`)
  y F1.8 (backend + `planner-store.js`) pueden ir en paralelo porque no comparten archivos.

### 13.5 Criterios de aceptación de F1 (del encargo, con su prueba)

| Criterio | Cómo se comprueba |
|---|---|
| El dominio es reproducible | Unitaria: mismo documento + mismo `now` → mismo resultado |
| Las evidencias se pueden identificar | `conceptStats` devuelve la lista de ejercicios que cuentan y su fecha |
| Repetir una pregunta no infla | Unitaria: 20 aciertos del mismo ejercicio = peso de un ejercicio |
| Se distingue confianza de dominio | Unitaria: mismo dominio con 1 y con 6 evidencias → distinta confianza |
| Poca evidencia se detecta | Unitaria + e2e: «sin datos suficientes», sin porcentaje |
| Repasos vencidos primero | `recommend.test.mjs` |
| Se respetan prerrequisitos | `recommend.test.mjs` (ya existe; se mantiene) |
| No se pierde progreso al sincronizar | `merge.test.mjs` con campos nuevos y antiguos, e2e `sync.spec.js` con dos contextos |
| Pruebas unitarias y E2E | Todas las suites de `TESTING.md` en verde, sin bajar la cobertura del 100 % del backend |

### 13.6 Métricas que se podrán medir después de F1 [P]

Repasos hechos a tiempo (vencidos completados / vencidos), recomendaciones aceptadas (hechas /
propuestas, desde `planner`), errores recurrentes que pasan a corregidos, evolución de simulacros
(`exams`). **No se afirmará que el algoritmo mejora el aprendizaje** hasta tener semanas de uso real.

---

## 14. Documentos objetivo: qué existe ya [H]

| Pedido | Equivalente actual | Propuesta [P] |
|---|---|---|
| `ROADMAP_ADAPTIVE.md` | `ROADMAP_2026_2027.md` solo en #84 (negocio) | Crear al aprobar F1, con las fases de este plan |
| `ARCHITECTURE_ADAPTIVE.md` | §2 de este documento y `memoria.md` | Fusionar en `ADAPTIVE_ENGINE.md` para no duplicar |
| `ADAPTIVE_ENGINE.md` | No existe | Crear en F1.9 |
| `AI_ARCHITECTURE.md`, `SECURITY_AI.md` | Retirados con #62; propuesta en #65 | Fase 3 |
| `TEST_STRATEGY.md` | `docs/TESTING.md` | Ampliar `TESTING.md` |
| `DECISIONS.md` | ADR sueltos en #84 (en inglés) | Crear en F1.9 con ADR-005/006 de #84 y D1-D3 |
