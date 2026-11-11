# Career Roadmap · Auditoría y arquitectura (Sprint 0)

Estado: **propuesta, sin código funcional**. Auditoría hecha sobre `main` en `d0c88c6` (04/11/2026,
después de fusionar el motor adaptativo 2.0 del PR #97 y la documentación del PR #99).
El Sprint 1 no empieza hasta que el autor apruebe este documento y las decisiones de §8.

Todo lo que se cita aquí existe en el repositorio en esa versión. Lo que todavía no existe se marca
como **(nuevo)**.

## 1. Arquitectura real encontrada

### 1.1 Frontend (`frontend/`)

- HTML, CSS y **JavaScript ES modules sin framework ni bundler**. Se publica tal cual en GitHub Pages
  (`.github/workflows/pages.yml`). Una única página, `index.html`, con secciones `<section class="page" id="*-view">`
  que se muestran u ocultan (`learn-view`, `home-view`, `pcap-view`, `daw-view`, `profile-view`, `private-view`…).
- **Navegación por hash** en `frontend/js/app.js` (`navigate()`): `#/portada`, `#/aprender`, `#/inicio`,
  `#/leccion/<slug>`, `#/pcap`, `#/daw[/…]`, `#/panel/<sección>`, `#/perfil`, `#/certificado`. Cada zona
  grande tiene su módulo con `openX(hash)` e `isXRoute()`: `learn/learn-app.js`, `daw.js`, `pcap.js`, `landing.js`.
  Una ruta desconocida enseña «Página no encontrada» (`not-found.js`).
- **Python en el navegador** con Pyodide dentro de un Web Worker (`pyodide-worker.js`, `python-runner.js`, `console.js`).
- **Contenido estático generado**: `frontend/data/*.json` sale de scripts en `scripts/` con modo `--check`
  que la CI ejecuta. Regla del proyecto: nunca se edita a mano un JSON generado.
  - `learning.json` (22 conceptos con prerrequisitos, CE, dificultad e importancia; 131 ejercicios) ← `scripts/learning/`.
  - `lessons.json` (curso PCAP: 7 módulos, 27 lecciones) y `pcap.json` (banco del examen).
  - `courses/<id>/{lessons,bank}.json` para 6 cursos de DAW (Programación UT1-UT9, Bases de datos UD1-UD3,
    Entornos, Lenguajes de marcas, JavaScript, Java) ← `scripts/courses/*_course.py`, ids en `ids.lock.json`.
  - `curriculum/daw-cyl.json` (17 módulos, 64 RA, 516 CE) y `resources.json` (recursos externos con licencia).
- **Estilos**: tokens en `css/tokens.css`, componentes en `widgets.css`, `ux.css`, `pro.css`; guía en `docs/DISENO.md`.
  Componentes reutilizables ya presentes: `meter` (barra de progreso accesible), tarjetas, chips, toasts.
- **Idiomas**: español e inglés (`js/i18n.js`, `frontend/i18n/*.json`, `docs/IDIOMAS.md`).
- **PWA**: `sw.js` + `precache.js` generado por `scripts/web/build_precache.mjs` (cualquier archivo nuevo debe entrar ahí).

### 1.2 Persistencia del progreso (clave para este módulo)

El progreso **no vive en tablas relacionales**: cada zona guarda un **documento JSON** en el navegador
(`localStorage`) y, con sesión, en la cuenta. Patrón común (DEC-002):

| Pieza | Archivo | Qué hace |
|---|---|---|
| Fusión antes de subir | `js/sync-gate.js` | No sube nada hasta haber fusionado la copia de la cuenta (AUD-001) |
| Control de versiones | `js/doc-sync.js` | Envía la versión leída; ante 409 relee, fusiona y reintenta |
| Subida diferida | `js/uploader.js` | Agrupa cambios y reintenta |
| Ejemplo más reciente | `js/learn/planner-store.js` | Documento `planner` añadido en el PR #97 con este patrón |

Documentos actuales: `learn` (motor adaptativo), `planner`, `game` (XP y logros), `sql`, `js`, `java`,
`entornos`, `marcas`, `programacion` (cursos) y el PCAP aparte.

### 1.3 Backend (`backend/`)

- **FastAPI** (`app/main.py`), SQLAlchemy 2, Alembic (10 migraciones), PostgreSQL en Neon (producción)
  y SQLite en local/pruebas. Desplegado en Render (`render.yaml`, `Dockerfile`; `docker-compose.yml` en local).
- Todas las rutas cuelgan de **`/api/v1`**. Routers existentes:

| Prefijo | Router | Uso |
|---|---|---|
| `/auth/*` | `auth.py` | registro, login, Google, logout, recuperación de contraseña |
| `/users/me/*` | `account.py` | perfil, contraseña, actividad, exportación RGPD, borrado |
| `/modules`, `/lessons/{slug}` | `lessons.py` | lecciones del curso PCAP |
| `/progress` | `progress.py` | lecciones completadas |
| `/lessons/{slug}/attempts` | `attempts.py` | intentos de ejercicio |
| `/pcap-state` | `pcap.py` | documento del PCAP |
| `/course-state/{course}` | `course_state.py` | documentos `COURSES` de `schemas.py` |
| `/dashboard`, `/dashboard/activity` | `dashboard.py` | panel del alumno |
| `/health` | `main.py` | estado (email y Google disponibles) |

- **Modelos** (`app/models.py`): `Module`, `Lesson`, `User`, `LessonProgress`, `ExerciseAttempt`,
  `PasswordResetToken`, `PcapState`, `CourseState` (clave `user_id`+`course`, `data` JSON, `version`), `AccountEvent`.
- **Autenticación** (`app/deps.py`, `security.py`, `session_cookie.py`): JWT en cookie HttpOnly (o Bearer),
  `token_version` para revocar, renovación con caducidad absoluta (AUTH-01). `CurrentUser` y
  **`WritingUser`** (120 escrituras/min por usuario, AUD-009).
- **Aislamiento entre usuarios**: el usuario sale **siempre del token**; ningún endpoint de progreso
  acepta un id de usuario en la URL o el cuerpo, así que no hay superficie de IDOR (`tests/test_security_isolation.py`).
- **Límites**: cuerpo ≤ 300 kB (`BodySizeLimit`), documento ≤ 200 kB (`MAX_PCAP_STATE_BYTES`), cabeceras de
  seguridad y `Cache-Control: no-store` en `/api/`, OpenAPI solo con `ENABLE_DOCS=true`.

### 1.4 Motor adaptativo 2.0 (PR #97, `docs/ADAPTIVE_ENGINE.md`)

Funciones **puras y deterministas** en el navegador, probadas con `node --test`:

- `js/srs.js`: repaso espaciado común (Leitner, cajas 0-5: 0/1/3/7/14/30 días).
- `js/learn/mastery.js`: evidencias por ejercicio, dominio = base ponderada por nivel × retención,
  **confianza** separada del dominio, estados (`nuevo`…`dominado`, «Pocas evidencias», «Se está olvidando»),
  errores típicos activos, `cleanLearning`/`mergeLearning` que conservan campos desconocidos (DEC-007).
- `js/learn/recommend.js`: prioridad explicable `P = 0,25R + 0,25E + 0,20D + 0,15W + 0,15T` con `why`,
  prerrequisitos firmes antes de contenido nuevo (`missingPrerequisites`, `READY_SCORE = 0,6`),
  `selectExercises` con nivel objetivo, `fitPlanToBudget`.
- `js/learn/planner.js`: plan de «Hoy», exámenes y entregas, historial y `acceptanceRate`.

**Esto ya cubre casi todo lo que el prompt pide para la «primera versión» y la «segunda versión» del
motor** (reglas deterministas, mastery 0-100 que no confunde completado con dominio, recencia, consistencia,
repetición espaciada, debilidades, ajuste de dificultad, olvido y recomendaciones explicables), pero solo
para los 22 conceptos de Python (DEC-004).

### 1.5 Gamificación (`js/game.js`, `js/game-data.js`)

XP **calculados a partir de hechos** (lecciones, quizzes, retos, preguntas del PCAP, simulacros), nunca
contador de clics; niveles (`LEVELS`), racha (`streak`) y logros (`BADGES`, cada uno con `test()`).
Sincronizado como documento `game`. Ya cumple la regla del prompt de premiar resultados verificables.

### 1.6 IA

**No hay ninguna IA en `main`.** El tutor, A2A y el proveedor Ollama/Anthropic se retiraron con el PR #62
(26/10). El PR #65 (tutor con OpenAI, de pago) sigue sin fusionar y está aparcado.

### 1.7 Pruebas y CI (`docs/TESTING.md`, `.github/workflows/ci.yml`)

- Backend: 33 archivos `pytest`, **cobertura obligatoria del 100 %** (`--cov-fail-under=100`), ruff,
  pip-audit, migraciones en PostgreSQL real.
- Frontend: 22 archivos `node --test` (`tests/unit/`), unos 180 e2e Playwright (`e2e/`) con backend real,
  axe-core WCAG 2.2 AA, WebKit para navegación.
- Generadores: `build_learning.py --check`, `build_curriculum.py --check`, `<curso>_course.py --check`.

### 1.8 Agentes de Claude Code (`.claude/agents/`)

| Pedido en el prompt | ¿Existe? |
|---|---|
| `career-orchestrator`, `career-architect`, `career-backend`, `career-frontend`, `career-curriculum`, `career-adaptive`, `career-qa-security`, `career-devops-docs` | **No existe ninguno** |
| `revisor-daw` (revisión con evidencias) | Sí |
| `buscador-mejoras` (mejoras priorizadas, `/mejoras`) | Sí |
| `mejorador-web` (inspección del frontend, `/mejorar-web`) | Sí |
| `red-teamer` (auditoría de seguridad, solo lectura) | Sí |

Esta auditoría la ha hecho la sesión principal, no un `career-architect`. Ver la decisión D4 en §8.

## 2. Choques con decisiones ya tomadas

| Choque | Con qué | Propuesta |
|---|---|---|
| «Primer empleo tecnológico» y 4 itinerarios genéricos | **DEC-001**: plataforma personal para DAM/DAW y PCAP, sin SaaS | Career Roadmap como itinerario **personal** del autor, sin profesores, aulas ni pagos, y enlazado con lo que ya estudia en DAW |
| 14 tablas relacionales y 15 endpoints REST | **DEC-002** y el patrón de documentos por usuario | Catálogo estático generado + **un documento `career`** (§4). Tablas solo si un requisito real lo exige |
| Motor adaptativo propio del roadmap | El motor 2.0 del PR #97 | **Reutilizarlo**: las competencias se calculan agregando dominio de conceptos, preparación de cursos y evidencias de proyecto |
| Sprint 7, «IA cloud» | El autor **no quiere gastar en APIs de pago** (06/10 y siguientes); la IA se retiró en #62 | Posponer o limitar a modelo simulado y Ollama local (D2) |
| Contenidos de Django, Redis, PyTorch, Transformers, Nmap… | Regla «no inventar datos» y volumen de contenido | Itinerarios B-D como **esqueleto** con recursos externos con licencia; solo A se rellena con contenido propio |
| Nombres en inglés (Overview, Skills Matrix…) | La web es en español con i18n | Textos en español con traducción al inglés vía `i18n` |
| `feature/career-roadmap` | `CLAUDE.md`: ramas `tipo/descripcion` | Vale: `feature/career-roadmap` cumple el formato |
| PR #95 (memoria intermodular) y #96 (Bases de datos, 14 lecciones) abiertos | Fase 3 del roadmap usa el curso de SQL | Fusionar #96 antes del Sprint 3 evita tocar `sql/lessons.json` en paralelo. #95 no choca |

## 3. Componentes reutilizables

| Necesidad del roadmap | Se reutiliza | Qué falta |
|---|---|---|
| Autenticación, sesión, límites | `CurrentUser`, `WritingUser`, cookie de sesión | Nada |
| Guardar progreso por usuario sin IDOR | `/api/v1/course-state/{course}` + `state_documents.save` (versión y 409) | Añadir `"career"` a `COURSES` |
| Sincronización segura | `sync-gate.js`, `doc-sync.js`, `uploader.js` (como `planner-store.js`) | `career-store.js` **(nuevo)** |
| Dominio por concepto | `mastery.js` (`conceptStats`, `allStats`, `explainStats`) | Agregar conceptos → competencia |
| Preparación por curso y bloque | `course-store.js` (`courseReadiness`, `courseBlockStats`), `pcap-store.js` (`readiness`) | Mapear bloques a competencias |
| Prerrequisitos y recomendaciones | `recommend.js` (`missingPrerequisites`, `priority`, `why`) | Capa de fases sobre esas funciones |
| Plan diario y entregas | `planner.js` (`exams` con `kind: "entrega"`) | Proyectos del roadmap como entregas |
| Repaso espaciado | `srs.js` | Nada |
| Evaluaciones tipo test | Formato `bank.json` y la tanda de práctica de `daw.js` | Bancos de evaluación por fase **(nuevo contenido)** |
| Ejercicios de Python | Pyodide, `console.js`, `learning.json` | Nada para la fase 1 |
| Recursos externos | `resources.json` con licencias, `scripts/resources/` | Recursos de las fases sin contenido propio |
| Currículo oficial | `daw-cyl.json` (RA/CE) | Enlazar competencias con RA cuando aplique |
| XP y logros | `game.js` (`BADGES`, XP por hechos) | Logros de hitos del roadmap |
| Panel del alumno | `dashboard.js`, `/api/v1/dashboard` | Una tarjeta de resumen del roadmap |
| Estilos | `tokens.css`, `meter`, tarjetas | `career.css` **(nuevo, pequeño)** |
| Generación con `--check` | Patrón de `scripts/courses/course_builder.py` e `ids.lock.json` | `scripts/career/` **(nuevo)** |

### Qué contenido propio hay ya para el itinerario Backend Junior

| Fase | Contenido existente |
|---|---|
| 1. Python Fundamentals | 22 conceptos y 131 ejercicios (`learning.json`), curso PCAP, Programación UT1-UT6 |
| 2. Professional Python | `excepciones`, `modulos`, `archivos`; lecciones PCAP de módulos y paquetes. Faltan typing, decorators, generators, context managers, logging, dataclasses, SOLID |
| 3. Databases & SQL | Curso Bases de datos UD1-UD3 + ampliación (y 14 lecciones más en #96). Faltan PostgreSQL específico, SQLAlchemy y migraciones |
| 4. Backend Development | **Nada**. Solo recursos externos |
| 5. Software Testing | Concepto `depuracion`; Entornos UD1 (sin pruebas unitarias aún) |
| 6. Frontend Development | JavaScript (5 bloques, incluye DOM y asincronía), Lenguajes de marcas (HTML/CSS, JSON) |
| 7. DevOps & Deployment | **Nada** propio |
| 8. Career Preparation | **Nada** propio |

Conclusión: las fases 1, 3 y 6 se apoyan en contenido real; 2 y 5 se completan con poco; **4, 7 y 8 son
contenido nuevo** y es la mayor parte del esfuerzo (Sprint 3).

## 4. Diseño propuesto

### 4.1 Principio

Career Roadmap es una **capa de organización y evidencia** encima de lo que ya existe, no un segundo
sistema. No mide de nuevo lo que el motor 2.0 ya mide.

### 4.2 Catálogo: estático y generado

```
scripts/career/roadmaps.py        (nuevo) define itinerarios, fases, unidades, competencias, proyectos
scripts/career/build_career.py    (nuevo) valida y genera; --check en CI
scripts/career/ids.lock.json      (nuevo) ids estables, solo crecen (DEC-007)
frontend/data/career/index.json   (nuevo, generado) lista de itinerarios
frontend/data/career/<id>.json    (nuevo, generado) un itinerario completo
```

Esquema de un itinerario (borrador):

```json
{
  "id": "python-backend-junior", "version": 1, "title": {"es": "…", "en": "…"},
  "level": "junior", "months": 8, "objectives": ["…"],
  "skills": [{ "id": "sql-consultas", "category": "databases", "target": 3,
               "sources": { "concepts": [], "courseBlocks": ["sql:ud3"], "projects": ["crm"] } }],
  "phases": [{ "id": "fundamentals", "requires": [], "objectives": ["…"],
               "units": [{ "id": "…", "links": [{"kind": "concept", "id": "bucles"}, {"kind": "resource", "id": "…"}] }],
               "assessment": { "bank": "…", "pass": 0.7 }, "project": "mini-proyecto" }],
  "projects": [{ "id": "crm", "phase": "databases", "criteria": ["…"], "evidence": ["repo", "readme", "tests"] }]
}
```

Validaciones del generador: ids únicos y estables, sin ciclos en `requires` de fases y competencias,
toda referencia (`concept`, `courseBlock`, `resource`, RA/CE) existe en su JSON, categorías del conjunto
fijo (Programming, Backend, Databases, Frontend, Testing, DevOps, AI/ML, Professional Skills).
**Añadir un itinerario = añadir datos, sin tocar la lógica** (requisito de la Fase 2 del prompt).

### 4.3 Progreso: un documento `career` por usuario

`pld:career` en el navegador y `/api/v1/course-state/career` en la cuenta (D1):

```json
{ "v": 1, "active": "python-backend-junior",
  "roadmaps": { "python-backend-junior": { "enrolledAt": "ISO", "months": 8,
      "units":   { "<unidad>": { "status": "hecha", "at": "ISO" } },
      "assessments": { "<fase>": [{ "score": 0.8, "at": "ISO" }] },
      "projects": { "<proyecto>": { "repo": "https://github.com/…", "checklist": {"tests": true}, "at": "ISO" } },
      "review": { "<fase>": "ISO" } } },
  "profile": { "goal": "…", "weeklyHours": 6 } }
```

- Sin datos personales nuevos más allá de enlaces que pone el alumno. Las URL se validan (`https:` y
  dominio) y se pintan siempre con `escapeHtml`/`safeUrl`.
- Topes de tamaño (intentos por fase, longitud de textos) para no pasar de 200 kB.
- Limpieza y fusión con las reglas del planificador: gana lo más reciente y se conservan campos desconocidos.

### 4.4 Cálculo (funciones puras, `frontend/js/career/` (nuevo))

- **Dominio de una competencia (0-100)** = media ponderada de sus fuentes, cada una con su propia medida
  ya existente: dominio de conceptos (`conceptStats`), preparación de bloques de curso (`courseReadiness`),
  evaluaciones de fase y evidencias de proyecto (lista de comprobación). La **confianza** sale del número
  y la variedad de fuentes con datos; con confianza baja se enseña «Pocas evidencias», como en el motor.
- **Estado de fase**: `locked` si algún `requires` no está completo; `available`; `in_progress`;
  `completed` (unidades hechas + evaluación ≥ umbral + proyecto con evidencias); `needs_review` si alguna
  competencia de la fase está «Se está olvidando» o la evaluación caducó. Nunca depende de la posición.
- **Recomendación**: la fase activa elige candidatos y `recommend.js` los ordena con sus `why`. No se
  recomienda una unidad avanzada si sus competencias previas no llegan a `READY_SCORE`.
- **Duración configurable**: `months` solo da un ritmo orientativo; nunca bloquea.
- La IA, si llega, **no puede conceder competencias** (se cumple por diseño: el dominio solo lee evidencias deterministas).

### 4.5 Interfaz

Ruta `#/carrera` (nueva, español; `#/career` como alias si se quiere en inglés) con subrutas
`#/carrera/resumen`, `/ruta`, `/competencias`, `/proyectos`, `/evaluaciones`, `/preparacion`.
Módulo `js/career/career-app.js` con `openCareer(hash)` e `isCareerRoute()`, enganchado en `navigate()`
igual que `learn-app.js`; nueva `<section id="career-view">` y entrada en el menú lateral. Estados de
carga, error, vacío y éxito con los componentes actuales; móvil, tableta y escritorio con las mismas
media queries.

### 4.6 Backend

| Cambio | Archivo | Motivo |
|---|---|---|
| Añadir `"career"` a `COURSES` | `app/schemas.py` | Guardar el documento con versión, 409 y límites |
| Tests del documento | `tests/test_course_state.py`, `test_security_isolation.py` | Aislamiento y validación |
| Resumen en el panel (opcional) | `routers/dashboard.py` | Si el panel debe mostrar el roadmap |

**No se crean** `/api/roadmaps`, `/api/skills`, etc.: el catálogo es estático (lo sirve Pages, funciona sin
backend como el resto de la web) y el progreso ya tiene endpoint. Se reconsideraría si hubiera que
**validar en el servidor** entregas o calificaciones, que hoy ninguna parte de la plataforma hace. Las 14
entidades del prompt quedan representadas así: catálogo (Roadmap, RoadmapPhase, LearningUnit, Skill,
Project, Assessment) en JSON generado; progreso del usuario (UserRoadmap, UserPhaseProgress,
UserUnitProgress, UserSkill, ProjectSubmission, AssessmentAttempt, LearningEvidence) en el documento
`career`; `Recommendation` se calcula, no se guarda. No hace falta ninguna migración.

### 4.7 IA (Sprint 7, opcional)

Sin IA de pago (D2). Si el autor la quiere, se recupera del historial (antes de #62) la abstracción de
proveedores con modelo simulado por defecto y Ollama local, llamada solo desde el backend, desactivada por
defecto y con cuota. El roadmap funciona entero sin ella.

## 5. Archivos

### A crear

| Archivo | Sprint |
|---|---|
| `scripts/career/{roadmaps.py,build_career.py,ids.lock.json}` | 1 |
| `frontend/data/career/index.json`, `python-backend-junior.json` (generados) | 1 |
| `frontend/js/career/career-data.js` (limpieza, fusión, cálculo puro) | 1 |
| `frontend/js/career/career-store.js` (sincronización) | 1 |
| `tests/unit/career-data.test.mjs` | 1 |
| `frontend/js/career/career-app.js` y vistas | 2 |
| `frontend/css/career.css` | 2 |
| `e2e/career.spec.js` | 2 |
| `frontend/data/career/{full-stack,data-ml,cybersecurity}.json` (generados) | 3 |
| `docs/CAREER_ROADMAP_{IMPLEMENTATION,DATA_MODEL,ADAPTIVE_ENGINE,TESTING,USER_GUIDE}.md` | según sprint |
| `docs/CAREER_ROADMAP_API.md` (corto: el documento `career` y por qué no hay más endpoints) | 1 |
| `docs/CAREER_ROADMAP_AGENT_LOG.md` | 0 (este PR) |

### A modificar

| Archivo | Cambio | Sprint |
|---|---|---|
| `backend/app/schemas.py` | `"career"` en `COURSES` | 1 |
| `backend/tests/test_course_state.py` | casos del documento `career` | 1 |
| `.github/workflows/ci.yml` | `build_career.py --check` | 1 |
| `frontend/index.html` | `<section id="career-view">` y enlace en el menú | 2 |
| `frontend/js/app.js` | rama de `navigate()` para `#/carrera` | 2 |
| `frontend/i18n/*.json` | textos | 2 |
| `frontend/precache.js` | regenerado con los archivos nuevos | 2 |
| `frontend/js/game.js` | logros y XP por hitos verificables | 8 |
| `frontend/js/dashboard.js` (y quizá `routers/dashboard.py`) | tarjeta del roadmap | 4 |
| `docs/DECISIONS.md` | DEC-011… con D1-D4 | 1 |
| `docs/TESTING.md`, `docs/README.md`, `README.md` | pruebas e índice | cada sprint |

## 6. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Volumen de contenido (fases 4, 7, 8 y tres itinerarios más) | Alto: es lo más costoso y no se puede inventar | Itinerario A primero; B-D como esqueleto con recursos externos; contenido propio por fases |
| Duplicar el motor adaptativo | Alto | Prohibido: `career-data.js` solo agrega funciones de `mastery.js`, `course-store.js` y `recommend.js` |
| Cobertura 100 % del backend | Medio | El cambio en backend es mínimo y se cubre con tests |
| Documento `career` desde una pestaña antigua | Medio | `cleanCareer` conserva lo desconocido; el documento es nuevo, así que las versiones antiguas no lo tocan |
| Tamaño del documento (> 200 kB) | Bajo | Topes por lista y por texto, test de límite |
| XSS con enlaces de proyecto | Medio | Solo `https:`, `safeUrl`, `escapeHtml`; test e2e con una URL maliciosa |
| e2e con Pyodide inestables bajo carga en el contenedor | Bajo | Conocido (PR #97); en la CI de GitHub pasan |
| Choque con #96 en el curso de SQL | Bajo | Fusionar #96 antes del Sprint 3 |
| «Primer empleo» sugiere promesas de empleabilidad | Medio (legal y honestidad) | Textos como orientación, sin prometer empleo, igual que los avisos de `ADAPTIVE_ENGINE.md` |
| IA de pago | Alto para el autor | D2 |

## 7. Plan de sprints, esfuerzo y criterios de aceptación

Se fusionan los dos planes del prompt (9 y 11 sprints) en uno, porque el diseño de §4 elimina el sprint
de «modelo de datos y backend» separado. Esfuerzo: S ≈ 1 sesión, M ≈ 2-3, L ≈ 4 o más.

| Sprint | Contenido | Esfuerzo | Criterios de aceptación |
|---|---|---|---|
| **0** | Esta auditoría y el registro | S | Documento revisado por el autor; D1-D4 decididas |
| **1** | Esquema del catálogo, generador con `--check`, itinerario A con fases/unidades/competencias enlazadas a contenido existente, documento `career` (backend + store), cálculo puro de estados y dominio | M | `build_career.py --check` en CI; prerrequisitos sin ciclos; tests unitarios de estados (bloqueo por `requires`, no por posición) y de dominio (completado ≠ dominio); aislamiento entre usuarios del documento; pytest 100 %, ruff, unit y e2e verdes |
| **2** | Vistas Resumen, Ruta, Competencias (con filtro), Proyectos, Evaluaciones y Preparación; navegación; responsive | M | e2e de navegación y estados (carga, error, vacío), axe WCAG 2.2 AA sin fallos, 320/768/1440 px sin scroll horizontal, inglés y español |
| **3** | Contenido de las fases 2, 4, 5, 7 y 8 del itinerario A; esqueleto de B, C y D | L | Cada unidad enlaza a contenido propio o a un recurso con licencia; ninguna sin fuente; generador valida referencias |
| **4** | Progreso y Skills Matrix completa; tarjeta en el panel | S-M | Nivel actual/objetivo, fecha de última evidencia y evidencias visibles por competencia; tests de agregación |
| **5** | Evaluaciones de fase (bancos `bank.json`) y proyectos con lista de comprobación y enlace al repositorio | M | Umbral de aprobado configurable; validación de URL; topes de tamaño; tests |
| **6** | Recomendaciones del roadmap con `recommend.js`, repaso de fases (`needs_review`) y conexión con el planificador | M | Mismo progreso + misma fecha = misma recomendación; cada una con `why`; no recomienda lo avanzado sin base (caso Python 85 / SQL 45 / FastAPI 65 / Testing 30 del prompt como test) |
| **7** | IA opcional (solo si D2 lo permite) | M | Funciona con IA apagada; nunca concede competencias; sin claves en el frontend |
| **8** | Gamificación: logros de hitos (Fundamentos completados, Primera API, Portfolio…) | S | XP solo por hechos verificables; tests de `game-data` |
| **9** | Revisión de seguridad (`red-teamer`), regresión completa, documentación final y README | S-M | Sin hallazgos altos abiertos; todas las pruebas de `docs/TESTING.md` verdes; docs `CAREER_ROADMAP_*` completas |

Ninguna dependencia nueva prevista (DEC-010). Cada sprint va en su propio PR; el merge lo hace el autor.

## 8. Decisiones que necesita el autor

| Id | Pregunta | Recomendación |
|---|---|---|
| **D1** | ¿Persistencia como documento `career` + catálogo estático (§4) o tablas relacionales y endpoints `/api/v1/roadmaps…`? | Documento: reutiliza sincronización, versión, aislamiento y límites; sin migraciones; funciona sin backend |
| **D2** | ¿Qué hacer con el Sprint 7 (IA)? | Posponerlo. Si se hace, solo modelo simulado y Ollama local, nada de pago |
| **D3** | Alcance de los itinerarios B, C y D | Esqueleto con fases, competencias y recursos externos; contenido propio solo en A |
| **D4** | Agentes `career-*` | No crear 8 agentes nuevos: reutilizar `revisor-daw` (revisión de cada sprint), `red-teamer` (Sprint 9), `mejorador-web` (inspección visual del Sprint 2) y `buscador-mejoras`. Si se quiere uno nuevo, solo `career-curriculum` para el Sprint 3 |
