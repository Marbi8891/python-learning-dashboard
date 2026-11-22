# Itinerario «AI Engineer & AI Product Developer»

Ruta profesional de 8 módulos hacia Applied AI Engineering + AI Product Development, que convive con
DAW. Decisión: [DEC-012](DECISIONS.md). Auditoría y propuesta: [AI_CAREER_PATH_AUDIT.md](AI_CAREER_PATH_AUDIT.md).

## 1. Estado por fases

| Fase | Estado |
|---|---|
| A · Auditoría y propuesta | Aprobada el 18/11/2026 (D1-D6 y D8; D7 pendiente) |
| B · Modelo de datos y arquitectura | Implementada en `feature/ai-career-path` (PR #176), pendiente de fusionar |
| **C · Pantalla «Mi Carrera en IA»** | **Implementada en `feature/ai-career-path-ui` (sobre la Fase B), pendiente de revisión** |
| D · Contenido de M1 y M4 y evaluaciones | Sin empezar |
| E · Proyectos, evidencias en la interfaz, logros y tutor | Sin empezar (el tutor espera a `feature/tutor-nexaro`) |
| F · Pruebas, documentación y despliegue | Sin empezar |

## 2. Arquitectura

```
scripts/career/applied_ai.py   ──▶ build_career.py --check ──▶ frontend/data/career/{index,applied-ai-engineer}.json
   (datos del itinerario)            (valida y genera)              (catálogo estático: Pages y PWA)
                                                                              │
frontend/js/career/career-data.js  ◀────────────────────────────────────────┘
   limpieza, fusión, cambios y cálculos puros; agrega:
     · mastery.js (dominio de conceptos)    · pcap-store.js FULL_COVERAGE (bloques de los cursos)
     · recommend.js READY_SCORE              · srs.js (fechas)
frontend/js/career/career-store.js  ── pld:career ⇄ /api/v1/course-state/career
   sync-gate.js + doc-sync.js + uploader.js (mismo patrón que planner-store.js)
frontend/js/career/career-finance.js  ── funciones puras; nunca va a la cuenta (D3)
```

- **Backend:** un solo cambio, `"career"` en `COURSES` (`backend/app/schemas.py`). Reutiliza versión y 409,
  límite de 200 kB, usuario sacado del token (sin IDOR), exportación RGPD y borrado de la cuenta.
  **Sin migraciones.**
- **Frontend:** `initCareerSync()` en `app.js` y `flushCareerSync()` antes de cerrar sesión en `account.js`.
  Pantalla «Mi Carrera en IA» en `#/carrera` (Fase C, §8).
- **PWA:** los módulos y los 2 JSON del itinerario están en `precache.js`, así que funcionan sin conexión.

## 3. Catálogo (`frontend/data/career/applied-ai-engineer.json`)

| Bloque | Contenido |
|---|---|
| `levels` | fundamentos, intermedio, avanzado, profesional (campo de cada unidad, no copias del contenido) |
| `modules` (8) | `m1`…`m8`, con `requires`, `units`, `assessment` (`bank: null` hasta la Fase D) y `project` (criterios y listas) |
| `units` (90) | `id` `mN.nombre`, `level`, `objectives`, `skills`, `links` (concepto, bloque de curso o recurso que ya existen) y `pending` |
| `skills` (32) | 10 categorías; `sources`: conceptos, bloques, evaluaciones, criterios y listas. Siempre con una fuente evaluable |
| `projects` (4) | NEXARO Personal AI, NEXARO Risk Engine (sin repositorio: D7), Python Learning Dashboard y JobRadar, con sus criterios |
| `roles` (9) | puestos objetivo con nivel mínimo por competencia y banda salarial |
| `stages` (6) | plan orientativo de 36 meses con los módulos de cada etapa |
| `salary` | bandas del autor (objetivos, no datos de mercado) y objetivo por defecto de 70.000 € |
| `checklists` | portfolio, entrevistas y negocio |

Prerrequisitos: M1 y M8 sin requisitos; M2 y M3 ← M1; M4 ← M1 y M3; M5 ← M4; M6 ← M2; M7 ← M2 y M4.
Las unidades de M1 y M2 enlazan con contenido real de PLD (conceptos de `learning.json` y bloques de
Programación, Bases de datos, JavaScript y Lenguajes de marcas). Ahí queda el antiguo «Python Backend Junior».

## 4. Documento `career` (progreso, se sincroniza)

```json
{ "v": 1, "active": "applied-ai-engineer", "activeAt": "ISO",
  "roadmaps": { "applied-ai-engineer": {
    "startedAt": "ISO",
    "stages":      { "s1": { "start": "2026-12-01", "months": 9, "at": "ISO" } },
    "units":       { "m1.poo": { "status": "hecha", "at": "ISO" } },
    "assessments": { "m1": [{ "score": 0.8, "at": "ISO" }] },
    "evidence":    [{ "id": "ev-…", "project": "nexaro-personal-ai", "criterion": "npa-rag-eval",
                      "kind": "pr", "url": "https://…", "note": "…", "at": "ISO" }],
    "criteria":    { "npa-rag-eval": { "met": true, "at": "ISO" } },
    "checklists":  { "pf-github": { "done": true, "at": "ISO" } },
    "studyLog":    [{ "id": "st-…", "d": "2026-11-18", "min": 45, "module": "m4", "at": "ISO" }] } } }
```

| Regla | Valor |
|---|---|
| Topes | 5 itinerarios, 100 evidencias, 366 sesiones, 10 intentos por evaluación, nota ≤ 120 caracteres, URL ≤ 240, sesión ≤ 600 min |
| Tamaño | El peor caso posible (todo al tope y con caracteres no ASCII) cabe en los 200 kB del servidor: lo comprueba un test |
| Enlaces | Solo `https:`, con dominio y sin credenciales (`safeHttpsUrl`); lo demás se descarta |
| Tipos de evidencia | repo, pr, commit, tests, demo, docs, deploy, result |
| Borrados | Marcados con `deleted` para que la fusión no los resucite |
| Fusión | Gana lo cambiado más tarde; se unen intentos y listas; `startedAt` más antiguo; se conservan los campos desconocidos (DEC-007) |

## 5. Cálculos (`career-data.js`, funciones puras)

| Función | Qué calcula |
|---|---|
| `skillStats` / `allSkillStats` | Dominio 0-1, confianza y estado: sin-evidencias, insuficiente, aprendiendo, progreso, adquirida o repasar. Grupos: práctica (conceptos y bloques), evaluación y proyecto, con pesos 0,3 / 0,4 / 0,3 normalizados. «Adquirida» pide ≥ 0,7, evidencias suficientes y, si la competencia lo declara, un criterio de proyecto cumplido |
| `criterionMet` | Un criterio solo cuenta marcado **y** con al menos una evidencia sin borrar |
| `moduleStatuses` | bloqueado (orientativo) / disponible / en-curso / completado / repasar. Completado = unidades + evaluación aprobada + criterios y listas del proyecto. Un prerrequisito se da por cumplido si está completado o sus competencias llegan a `READY_SCORE` |
| `roleCoverage` | Cobertura de cada puesto (0-1) y lo que falta, ordenado |
| `stagePlan` | Fechas de las 6 etapas; mover o alargar una desplaza las siguientes |
| `nextActivities` | Hasta 3 actividades con su motivo, de la etapa actual primero. Se pausa con un examen o entrega de DAW a 7 días o menos (`dawPriority`) |
| `studyTotals` | Minutos apuntados: total, por módulo, 7 y 30 días |
| `career-finance.js` `projection` | Por año: salario bruto, facturación, gastos, beneficio = facturación − gastos, combinado = salario + beneficio, distancia al objetivo y crecimiento. Sin IRPF |

## 6. Dónde se guardan los datos económicos (decidido: opción C)

Al cerrar sesión, `clearLocalData()` (`store.js`) borra del navegador lo personal porque su copia está
en la cuenta. Los datos económicos **no** están en la cuenta (D3), así que se perderían. El 18/11/2026
el autor eligió la opción C entre estas:

| Opción | Qué pasa | Problema |
|---|---|---|
| A. Clave fuera de `pld:` | Sobrevive al cierre de sesión | AUTH-02 no la aparta por cuenta: otra cuenta en el mismo navegador la vería |
| B. Clave `pld:` normal | AUTH-02 la aparta por cuenta | Se borra en cada cierre de sesión |
| **C. Clave `pld:` excluida del borrado al cerrar sesión (elegida)** | No se pierde al cerrar sesión, y si entra otra cuenta se aparta para la primera (AUTH-02) | Sin sesión, quien use ese navegador la ve, como cualquier progreso sin cuenta |

Implementación: `FINANCE_KEY = "pld:career-finance"` (`career-finance.js`) está en `LOCAL_ONLY_KEYS`, y
`clearedOnLogout()` (`local-owner.js`) decide qué borra el cierre de sesión. Lo prueban
`tests/unit/local-owner.test.mjs` y `e2e/security.spec.js`.

Hecho en la Fase C:
- Botón «Borrar mis datos económicos» (pide una segunda pulsación), exportación e importación JSON.
- Con datos económicos, el aviso tras cerrar sesión dice que se quedan en el navegador y dónde borrarlos.
- Borrar la cuenta tampoco los borra (no están en ella): el formulario de borrado lo dice y ofrece una
  casilla «Borrar también mis datos económicos de este navegador» (también al borrar con Google).

## 7. Limitaciones conocidas

- Ningún banco de evaluación todavía (`bank: null`): hasta la Fase D ningún módulo se puede completar.
  Es intencionado: sin evaluación no hay competencia.
- Los objetivos de las unidades y los títulos de los criterios solo están en español (el inglés repite el texto).
- Los umbrales (0,7, 180 días, 7 días de prioridad DAW) son hipótesis iniciales, como DEC-009.
- `nextActivities` no está conectado al planificador ni al plan de «Hoy» (Fase E).
- Las evidencias las declara el alumno; el navegador no puede verificar un PR. Por eso una competencia
  nunca sube solo con evidencias.
- **Fallos previos corregidos en `fix/subida-unica` (base de esta rama):** (1) un `flush()` durante la
  subida inicial tras entrar mandaba un segundo PUT con la misma versión y bloqueaba el cierre de
  sesión aunque todo estuviera guardado; ahora `uploader.js` hace una sola subida a la vez. (2) Los
  repintados en segundo plano borraban lo escrito en los formularios (el nombre nuevo volvía al
  antiguo); ahora lo conserva `form-keep.js`. Con 5 workers, los cuatro E2E que fallaban pasaron 60 de 60.

## 8. Pantalla «Mi Carrera en IA» (Fase C)

`frontend/js/career/career-app.js`, cargado solo en `#/carrera` (zona diferida de `app.js`, como Excel).

| Ruta | Contenido |
|---|---|
| `#/carrera` o `/resumen` | Siguiente actividad (o «DAW primero» con un examen o entrega a 7 días o menos), competencias y los 3 puestos más cercanos |
| `/ruta` | Los 8 módulos con su estado, requisitos (orientativos), unidades con su casilla «estudiada» y enlaces a la teoría, la práctica de DAW o el recurso |
| `/competencias` | Las 32 competencias por categoría, con dominio, estado y su explicación (`explainSkill`) |
| `/proyectos` | Los 4 proyectos y sus criterios (cumplido solo con evidencia); añadir evidencias es la Fase E |
| `/plan` | Las 6 etapas con fechas; tras empezar el itinerario, cada etapa se mueve o alarga y vuelve al plan original |
| `/objetivo` | Objetivo y años (salario, facturación, gastos), tabla, gráfica SVG, bandas del catálogo, exportar, importar y borrar |
| `/preparacion` | Listas de portfolio, entrevistas y negocio, y qué falta para cada puesto |

- No calcula nada nuevo: todo sale de `career-data.js` con `allStats` (`mastery.js`) y `courseBlockStats`
  de los cursos de DAW. Si no cargan `learning.json`, los bancos o `resources.json`, la pantalla sigue con 0.
- Estados: «Cargando el itinerario…», sin empezar (botón «Empezar el itinerario») y error con «Reintentar».
- Repintados sin perder el foco, lo escrito ni las listas abiertas (`form-keep.js`).
- Gráfica: `career-chart.js`, función pura (probada con node), sin `style=` (CSP), con título, descripción,
  leyenda, un trazo distinto por serie y la tabla con los mismos datos.
- `finance-store.js` lee, guarda y borra `pld:career-finance`; `account.js` lo usa para los avisos de §6.
- Pruebas: `tests/unit/career-chart.test.mjs`, `career-finance.test.mjs` y `e2e/career-ui.spec.js` (navegación,
  estados, plan, leer ≠ dominar, prioridad DAW, objetivo local, avisos de la cuenta, 320/768/1440 px, axe en
  claro y oscuro, inglés y sin conexión).

**Desviación de la propuesta (§4.5 de la auditoría):** la gráfica no enseña «la cobertura por puesto en el
tiempo», porque el documento no guarda ese historial (**UNKNOWN** cómo hacerlo sin otro bloque en `career`). Enseña
la evolución económica por año frente al objetivo. Guardar una foto mensual de la cobertura sería un cambio del
documento (Fase E o posterior, con su decisión).
