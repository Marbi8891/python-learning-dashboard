# Ruta AI Engineer & AI Product Developer · Fase A: auditoría y propuesta técnica

Estado: **propuesta, sin cambios de código**. Fecha: 18/11/2026.
Base auditada: `main` en `2dc7ff2` (= `origin/main`, PR #100 fusionado). Rama local activa:
`feature/tutor-nexaro` con un único commit WIP (`02cb550`) sin fusionar.
Destino propuesto en el repo: `docs/AI_CAREER_PATH_AUDIT.md`, en la rama de la Fase B.

Marcas: **UNKNOWN** (no lo sé), **ASSUMPTION** (supuesto que tomo), **VERIFY** (comprobar antes de
depender de ello), **NEEDS_HUMAN** (decisión tuya).

---

## 0. Resumen ejecutivo

1. **Esto ya está medio diseñado.** El 04/11 se hizo la auditoría del *Career Roadmap* (Sprint 0,
   `docs/CAREER_ROADMAP_ARCHITECTURE.md`): catálogo estático generado + un documento `career` por
   usuario + cálculo puro que agrega el motor adaptativo 2.0. Sus decisiones D1-D4 **siguen
   pendientes** y el Sprint 1 no ha empezado. La ruta de IA no debe ser un segundo sistema: es **un
   itinerario más dentro de ese diseño** (`applied-ai-engineer`), con tres añadidos: plan temporal,
   evidencias de proyecto y objetivo económico.
2. **Cero migraciones y un único cambio de backend** (`"career"` en `COURSES`). El prompt pide
   migraciones "cuando sean necesarias": con este diseño no lo son.
3. **La evaluación es el problema de verdad, no la interfaz.** Pyodide solo ejecuta Python puro.
   FastAPI, PostgreSQL, Redis, Docker, Ollama o Qdrant no se pueden evaluar en el navegador. Propuesta:
   retos de Python puro que reproducen el núcleo de cada técnica (BM25, similitud coseno, chunking,
   validación de *structured outputs*, bucle de agente con LLM simulado y permisos), cuestionarios y
   **evidencias de proyecto con lista de comprobación**. La competencia solo sube con eso.
4. **Volumen de contenido:** 8 módulos × ~11 temas × 4 niveles ≈ 350 unidades. No se puede escribir
   todo con calidad ni sin inventar. Propuesta: esqueleto completo de los 8 módulos en la Fase D y
   contenido propio solo de M1 y M4 al principio (justificación en §6).
5. **El tutor IA solo existe en local** y está en una rama WIP. El criterio de finalización 5
   («recibir correcciones de la IA») solo se cumplirá en tu Mac con NEXARO encendido, nunca en
   GitHub Pages. La corrección base tiene que ser determinista.
6. **Objetivo de 70.000 €:** las cifras del prompt son tus objetivos, no datos de mercado. Pasar de
   un sueldo de entrada a 55-70 k en 36 meses es muy agresivo en España por cuenta ajena; es más
   realista sumando actividad propia o empleo remoto desde fuera. El dashboard debe enseñar la
   **brecha** con datos tuyos, sin prometer nada (**VERIFY** con datos de mercado reales en la Fase C).
7. **Los datos económicos no deberían salir del navegador por defecto** (§4.4).

---

## 1. Qué hay ahora (verificado en el repositorio)

| Área | Estado real | Evidencia |
|---|---|---|
| Frontend | HTML + CSS + JS ES Modules sin bundler; SPA con navegación por hash (`app.js → navigate()`); cada zona tiene `openX(hash)`/`isXRoute()` | `frontend/js/app.js`, `learn/learn-app.js`, `daw.js`, `pcap.js` |
| Python en navegador | Pyodide en Web Worker; no carga paquetes extra (`loadPackage`/`micropip` no aparecen) | `pyodide-worker.js`, `python-runner.js` |
| Contenido | JSON generados por scripts con `--check` en CI; prohibido editarlos a mano | `scripts/learning`, `scripts/courses`, `scripts/curriculum`, `scripts/resources` |
| Conceptos | 22 conceptos de Python (`algoritmos` … `poo`). **No hay** typing, asyncio, decoradores, generadores, pytest, logging, dataclasses | `frontend/data/learning.json` |
| Progreso | Documentos JSON por zona (localStorage + cuenta) con versión y 409; `sync-gate`, `doc-sync`, `uploader` (DEC-002, DEC-007) | `COURSES = ("sql","js","java","entornos","marcas","programacion","learn","game","planner")` en `backend/app/schemas.py:191` |
| Motor adaptativo 2.0 | Dominio ≠ completado, confianza, olvido, prerrequisitos, recomendación explicable con `why`, planificador con exámenes/entregas y presupuesto | `learn/mastery.js`, `recommend.js`, `planner.js`, `srs.js` |
| Gamificación | XP por hechos verificables, niveles, racha, logros con `test()` | `game.js`, `game-data.js` |
| Backend | FastAPI, SQLAlchemy 2, Alembic (10 migraciones), PostgreSQL (Neon) / SQLite local, todo bajo `/api/v1`, usuario siempre desde el token (sin IDOR), documentos ≤ 200 kB | `backend/app/`, `migrations/versions/` |
| IA | En `main`: ninguna. En `feature/tutor-nexaro` (WIP): `/api/v1/tutor` → NEXARO → Ollama, desactivado sin `NEXARO_URL`/`NEXARO_API_KEY`, enunciado leído de la BD, conversación firmada con HMAC (DEC-011) | `routers/tutor.py`, `docs/TUTOR.md` |
| PWA | `sw.js` + `precache.js` generado (119 archivos); todo archivo nuevo debe entrar | `scripts/web/build_precache.mjs` |
| Pruebas | Backend con cobertura 100 % obligatoria, ruff, pip-audit; 22 archivos unitarios de frontend; 25 e2e Playwright con axe WCAG 2.2 AA | `docs/TESTING.md`, `.github/workflows/ci.yml` |
| Agentes | `revisor-daw`, `buscador-mejoras`, `mejorador-web`, `red-teamer` | `.claude/agents/` |
| Reglas | Merge a `main` = publicar (lo hace el autor); ramas `tipo/descripcion`; sin servicios de pago; nada de secretos | `CLAUDE.md` |

### Línea base de pruebas (ejecutadas hoy en una VM Linux, sin tocar el repo)

| Prueba | Resultado |
|---|---|
| `node --test tests/unit/*.test.mjs` | **164/164 OK** |
| `build_learning.py --check`, `build_curriculum.py --check`, `build_resources.py --check` | OK |
| `build_precache.mjs --check` | OK (119 archivos) |
| `pytest` del backend | **No ejecutado**: la VM tiene Python 3.10 y `sqlalchemy>=2.1.1` no se instala. Hay que correrlo en tu Mac o en la CI |
| e2e Playwright | No ejecutado (necesita navegadores y backend) |

Nota: `npm run test:unit` usa el glob `tests/unit/*.test.mjs` (comprobado en `package.json`), que es
lo que se ejecutó. No hay fallos en la línea base.

---

## 2. Choques del prompt con el repositorio y con decisiones previas

| # | Choque | Con qué | Propuesta |
|---|---|---|---|
| C1 | Crear un itinerario nuevo y aparte | Career Roadmap Sprint 0 (mismo problema, ya diseñado) | Un solo sistema `career`; la ruta de IA es un itinerario de datos. El itinerario «Python Backend Junior» del Sprint 0 se **absorbe** en M1-M2 para no duplicar |
| C2 | «Crear migraciones versionadas» | DEC-002 (documentos por usuario) | No hacen falta. Se reconsidera solo si un requisito exige validar algo en el servidor |
| C3 | M7 enseña SaaS, multi-tenancy, pagos | DEC-001 (PLD sin SaaS) | No es conflicto: es **contenido** del módulo. PLD no se convierte en SaaS. Dejarlo escrito para que nadie lo lea como cambio de rumbo |
| C4 | «Retos de programación» en todos los módulos | Pyodide = Python puro en navegador | Retos ejecutables solo donde tiene sentido; en M2, M5-M7 la prueba es el proyecto (§5) |
| C5 | «Recibir correcciones de la IA» | Tutor solo local, rama WIP | Corrección determinista siempre; IA como explicación y pistas cuando esté disponible |
| C6 | Tutor con ejercicios de la ruta | `tutor.py` lee el enunciado **de la BD** (lecciones PCAP) | Las unidades de la ruta están en JSON estático: hay que ampliar el tutor para leer el enunciado del catálogo en el servidor (Fase E), sin aceptar el enunciado que mande el navegador |
| C7 | Registrar salario e ingresos | Datos financieros personales; `REGISTRO_TRATAMIENTOS.md` no los contempla | Solo en el navegador por defecto (§4.4) |
| C8 | Horas de estudio | No hay medición de tiempo de estudio fiable. **VERIFY**: aparecen «minutos» en `planner`/`dashboard`, que parecen presupuestos, no tiempo real | Registro de sesiones manual y corto (fecha, minutos, módulo), no un cronómetro en segundo plano |
| C9 | «Terminar DAW es la prioridad» | El planificador ya tiene exámenes y entregas | Regla dura: las entregas/exámenes de DAW consumen primero el presupuesto diario; la ruta de IA usa lo que queda |
| C10 | Fase F «despliegue» | `CLAUDE.md`: merge = publicar, lo haces tú; despliegue Hetzner en otra rama | La Fase F deja el PR listo; no hay merge ni despliegue por mi parte |

---

## 3. Componentes que se reutilizan

| Necesidad del prompt | Se reutiliza | Qué falta |
|---|---|---|
| Lecciones, cuestionarios, banco de preguntas | Formato `courses/<id>/{lessons,bank}.json` + `course_builder.py` | Generador `scripts/career/` |
| Retos de Python ejecutables y corregidos | Pyodide, `console.js`, formato de ejercicios de `learning.json` (respuestas comprobadas por el generador) | Ejercicios nuevos de M1/M3/M4/M5 |
| No dar una competencia por leer | `mastery.js`: dominio por evidencias, confianza aparte, olvido | Agregación concepto → competencia |
| Prerrequisitos y siguiente actividad | `recommend.js` (`missingPrerequisites`, `READY_SCORE`, `why`) | Capa de módulos encima |
| Plan diario, convivencia con DAW | `planner.js` (`exams`, `kind: "entrega"`, `fitPlanToBudget`) | Prioridad DAW explícita + etapas de 36 meses |
| Repaso | `srs.js` | Nada |
| XP, niveles, insignias, racha | `game.js` | Logros de hitos verificables de la ruta |
| Recursos externos con licencia | `resources.json` + `build_resources.py` | Recursos de M2-M8 |
| Sincronización segura | `sync-gate.js`, `doc-sync.js`, `uploader.js`, `planner-store.js` como modelo | `career-store.js` |
| Aislamiento, límites, versión | `/api/v1/course-state/{course}` | `"career"` en `COURSES` + tests |
| Componentes visuales | `meter`, tarjetas, chips, tokens | `career.css` pequeño; gráfica en SVG nativo (DEC-010: sin librerías) |
| Tutor | `/api/v1/tutor` (cuando se fusione) | Contexto de unidad de la ruta |

---

## 4. Diseño propuesto (resumen; el detalle va en la Fase B)

### 4.1 Catálogo estático generado

```
scripts/career/roadmaps/applied_ai.py   datos del itinerario (8 módulos)
scripts/career/build_career.py          valida y genera; --check en CI
scripts/career/ids.lock.json            ids estables, solo crecen (DEC-007)
frontend/data/career/index.json         generado
frontend/data/career/applied-ai-engineer.json  generado
```

Entidades dentro del JSON: `modules` (los 8) → `units` (cada una con `level`: fundamentos /
intermedio / avanzado / profesional, objetivos, explicación, enlaces a conceptos, cursos o recursos) →
`assessments` (banco + umbral) → `projects` (los 4 repos reales) → `skills` (con fuentes de evidencia) →
`roles` (los 9 puestos, cada uno con competencias y nivel mínimo) → `stages` (las 6 etapas de 36 meses,
con duración por defecto). Los 4 niveles son **un campo de la unidad**, no cuatro copias del contenido.

El generador valida: ids únicos, sin ciclos de prerrequisitos, toda referencia existe, cada unidad
tiene contenido propio o un recurso con licencia, cada competencia tiene al menos una fuente de
evidencia evaluable.

### 4.2 Documento `career` (progreso, se sincroniza)

```json
{ "v": 1, "active": "applied-ai-engineer",
  "roadmaps": { "applied-ai-engineer": {
    "startedAt": "ISO",
    "stages":   { "s1": { "start": "2026-12-01", "months": 6 } },
    "units":    { "<unidad>": { "status": "hecha", "at": "ISO" } },
    "assessments": { "<id>": [{ "score": 0.8, "at": "ISO" }] },
    "evidence": [{ "id": "…", "project": "nexaro-personal-ai", "kind": "pr",
                   "url": "https://github.com/…", "note": "…", "skills": ["rag-hibrido"], "at": "ISO" }],
    "checklists": { "portfolio": {}, "interview": {} },
    "studyLog": [{ "d": "2026-11-18", "min": 45, "module": "m4" }] } } }
```

- `kind` ∈ repo, pr, commit, tests, demo, docs, deploy, result. URL opcional (JobRadar no está en
  GitHub): si hay URL, solo `https:`, pintada con `safeUrl`/`escapeHtml`.
- Topes por lista y por texto para no pasar de 200 kB; test de límite.
- `cleanCareer`/`mergeCareer` con las reglas del planificador (gana lo más reciente, se conserva lo desconocido).

### 4.3 Cálculo (funciones puras en `frontend/js/career/`)

- **Competencia 0-100** = media ponderada de sus fuentes: dominio de conceptos (`mastery.js`),
  preparación de bloques de curso, evaluaciones del módulo y evidencias de proyecto verificadas por
  lista de comprobación. **Leer una lección aporta 0.** Confianza baja → «Pocas evidencias».
- **Estado de módulo**: bloqueado / disponible / en curso / superado (evaluación ≥ umbral + proyecto con
  evidencias) / a repasar (olvido o evaluación caducada).
- **Puestos recomendados**: cobertura de las competencias de cada puesto; se enseña qué falta, no un
  porcentaje de «empleabilidad».
- **Siguiente actividad**: primero DAW (entregas y exámenes del planificador), luego la ruta, ordenado
  por `recommend.js` con su `why`.
- La IA **no puede** modificar ninguna de estas funciones ni escribir evidencias.

### 4.4 Objetivo económico (separado y local)

Documento `pld:career-finance` **solo en `localStorage`**, sin endpoint. Campos por año: salario bruto
por cuenta ajena, facturación propia, gastos del negocio (incluida la cuota de autónomo, que la metes
tú), **beneficio antes de impuestos = facturación − gastos**, e **ingreso combinado = salario bruto +
beneficio**. Se dibujan por separado y con etiquetas distintas; nunca se suman facturación y salario.
Sin cálculo de IRPF (fuera de alcance; sería inventar). Exportar/importar JSON para no perderlo.

Trade-off: no se ve en otro dispositivo. Ganas que ningún dato financiero llega a la base de datos de
Neon ni al registro de tratamientos. Si lo quieres sincronizado: opt-in explícito, documento aparte y
actualizar `REGISTRO_TRATAMIENTOS.md` y `privacidad.html` (NEEDS_HUMAN).

### 4.5 Pantalla «Mi Carrera en IA»

Ruta `#/carrera` con subrutas `resumen`, `ruta`, `competencias`, `proyectos`, `plan`, `objetivo`,
`preparacion`. Módulo `js/career/career-app.js` enganchado en `navigate()` como `learn-app.js`; nueva
`<section id="career-view">` y entrada de menú. Visualización de evolución: SVG nativo con la cobertura
de competencias por puesto en el tiempo y tu banda salarial objetivo encima, con texto alternativo y
tabla equivalente (WCAG). Textos en español e inglés vía `i18n`.

### 4.6 Backend

| Cambio | Archivo |
|---|---|
| `"career"` en `COURSES` | `app/schemas.py` |
| Tests de guardado, 409, límite y aislamiento entre usuarios | `tests/test_course_state.py`, `tests/test_security_isolation.py` |
| (Fase E) el tutor acepta contexto «unidad de la ruta», leyendo el enunciado del catálogo en el servidor | `routers/tutor.py`, `tests/test_tutor.py` |

Nada más. Cobertura 100 % se mantiene.

---

## 5. Cómo se evalúa cada módulo (lo que de verdad prueba una competencia)

| Módulo | Ejecutable en Pyodide | Evaluación |
|---|---|---|
| M1 Python Engineering | Sí: POO, typing, dataclasses, generadores, decoradores, errores, `asyncio` básico (**VERIFY** `asyncio` en el worker), mini-tests estilo pytest con `assert` | Retos corregidos + cuestionario + PR real en NEXARO con tests |
| M2 Backend | Parcial: validación tipo Pydantic a mano, SQL en el curso existente (SQLite) | Cuestionario + evidencias (endpoint con tests, migración, auth) en un repo |
| M3 AI Fundamentals | Parcial: tokenización de juguete, similitud coseno, softmax, atención en Python puro. NumPy existe en Pyodide pero no se carga hoy y engorda la PWA (**VERIFY** coste) | Cuestionario + informe de comparación de modelos locales con datos medidos |
| M4 LLM Engineering | **Sí, lo central**: chunking, BM25, fusión híbrida (RRF), reranking simple, validar una salida contra un esquema, detectar respuesta sin fuente | Retos corregidos + mejora medible del RAG de NEXARO (antes/después con un conjunto de preguntas) |
| M5 AI Agents | Sí: bucle de agente con LLM simulado, registro de herramientas, permisos y confirmación humana | Retos + agente en NEXARO con permisos y tests de denegación |
| M6 Infra & MLOps | No | Cuestionario + evidencias (workflow de CI, compose, despliegue, logs) |
| M7 AI Product | No | Cuestionario + documento de producto con métricas y amenazas LLM (OWASP LLM Top 10) |
| M8 Career & Business | No | Listas de comprobación de portfolio/CV/entrevista + propuesta comercial |

Las evidencias se marcan tú mismo (no hay forma honesta de que el navegador verifique un PR). Para que
no sea un «autoaprobado»: cada evidencia exige enlace o nota concreta y su lista de criterios del
proyecto; la competencia sube con evidencia **y** evaluación, no con una sola.

---

## 6. Alcance de contenido (Fase D)

- **Esqueleto completo** de los 8 módulos: objetivos, unidades con nivel, competencias, proyecto,
  criterios y recursos externos con licencia. Así la ruta se ve entera desde el primer día.
- **Contenido propio primero en M1** (coincide con los meses 1-6 y con Programación de DAW; reutiliza
  los 22 conceptos y añade los que faltan) **y M4** (es el núcleo diferencial del perfil Applied AI y
  trabaja directamente sobre el RAG de NEXARO, que ya estás construyendo con BM25 + embeddings).
- M2-M3 y M5-M8: contenido propio en iteraciones posteriores, módulo a módulo.

---

## 7. Plan incremental

Cada fase = una rama desde `main` y un PR. El merge lo haces tú. Esfuerzo: S ≈ 1 sesión, M ≈ 2-3, L ≥ 4.

| Fase | Contenido | Esfuerzo | Criterio de aceptación |
|---|---|---|---|
| **A** | Este documento | S | Lo apruebas y decides §8 |
| **B** | Generador `build_career.py --check` + esquema + datos del itinerario (esqueleto) + documento `career` (backend + store) + cálculo puro + ADR en `DECISIONS.md` | M | `--check` en CI; tests unitarios de estados (bloqueo por prerrequisitos), de dominio (leer ≠ dominar) y de fusión; aislamiento entre usuarios; pytest 100 %, ruff, unit y e2e verdes |
| **C** | Pantalla «Mi Carrera en IA», plan de 36 meses editable, objetivo económico local, gráfica SVG, entrada en el menú, precache | M | e2e de navegación y estados (carga, vacío, error), axe WCAG 2.2 AA en claro y oscuro, 320/768/1440 px, ES/EN, la PWA abre sin conexión |
| **D** | Contenido propio M1 y M4 + bancos de evaluación + recursos de M2-M8 | L | Cada unidad con fuente; cada respuesta de reto comprobada por el generador |
| **E** | Proyectos y evidencias, prioridad DAW en el planificador, logros, tutor sobre unidades de la ruta | M | URL maliciosa no se ejecuta (e2e); la ruta funciona entera con el tutor apagado; el tutor nunca escribe en `career` |
| **F** | `red-teamer`, regresión completa, documentación (`docs/AI_CAREER_PATH.md`, `TESTING.md`, `README.md`) | S-M | Sin hallazgos altos abiertos; todas las pruebas de `TESTING.md` verdes |

Dependencias: cerrar y fusionar `feature/tutor-nexaro` antes de la Fase E. Ninguna dependencia nueva.

### Archivos previstos

Crear: `scripts/career/*`, `frontend/data/career/*` (generados), `frontend/js/career/{career-data,career-store,career-finance,career-app}.js`,
`frontend/css/career.css`, `tests/unit/career-*.test.mjs`, `e2e/career.spec.js`, `docs/AI_CAREER_PATH.md`.
Modificar: `backend/app/schemas.py`, `backend/tests/test_course_state.py`, `test_security_isolation.py`,
`.github/workflows/ci.yml`, `frontend/index.html`, `frontend/js/app.js`, `frontend/i18n/*.json`,
`frontend/precache.js` (regenerado), `frontend/js/game-data.js`, `frontend/js/learn/planner.js`,
`docs/DECISIONS.md`, `docs/CAREER_ROADMAP_*.md` (marcar que este documento los sustituye en lo que choquen).

---

## 8. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| La ruta de IA le quita tiempo a DAW | Alto | Prioridad dura de DAW en el planificador; la ruta usa el presupuesto sobrante |
| Volumen de contenido | Alto | Esqueleto + M1/M4 primero (§6) |
| Contenido de IA que caduca rápido (MCP, LangGraph, modelos) | Medio | Fecha de revisión por unidad; recursos externos para lo volátil |
| Evidencias autodeclaradas | Medio | Evidencia + evaluación, criterios por proyecto |
| Datos financieros en la cuenta | Medio (RGPD) | Solo locales por defecto |
| Cifras salariales leídas como promesa | Medio | Etiquetadas como objetivos tuyos; sin «probabilidad de empleo» |
| Duplicar el motor adaptativo | Alto | `career-data.js` solo agrega funciones existentes |
| Tutor de modelo pequeño se equivoca o da la solución | Medio | Solo pistas; nunca conceda competencias; eval de NEXARO (`make eval`) |

---

## 9. Decisiones que necesito de ti (NEEDS_HUMAN)

| Id | Pregunta | Recomendación |
|---|---|---|
| **D1** | ¿Documento `career` + catálogo estático, o tablas y endpoints nuevos? | Documento (sin migraciones, reutiliza sincronización y aislamiento) |
| **D2** | ¿El itinerario «Python Backend Junior» del Sprint 0 se absorbe en M1-M2 o se mantienen los dos? | Absorberlo: una sola ruta activa |
| **D3** | Datos económicos: ¿solo en el navegador o sincronizados? | Solo en el navegador |
| **D4** | Contenido propio inicial: ¿M1 + M4? | Sí |
| **D5** | ¿Fusionar `feature/tutor-nexaro` antes de la Fase E? | Sí, terminarlo primero |
| **D6** | Agentes `career-*`: ¿crear nuevos? | No; reutilizar `revisor-daw`, `red-teamer`, `mejorador-web` |
| **D7** | **UNKNOWN**: ¿«NEXARO Risk Engine» es ARGOS u otro repo? ¿Dónde está? | Dímelo para enlazar sus competencias |
| **D8** | Nombre de rama para la Fase B | `feature/ai-career-path` desde `main` |
