# Itinerario «AI Engineer & AI Product Developer»

Ruta profesional de 8 módulos hacia Applied AI Engineering + AI Product Development, que convive con
DAW. Decisión: [DEC-012](DECISIONS.md). Auditoría y propuesta: [AI_CAREER_PATH_AUDIT.md](AI_CAREER_PATH_AUDIT.md).

## 1. Estado por fases

| Fase | Estado |
|---|---|
| A · Auditoría y propuesta | Aprobada el 18/11/2026 (D1-D6 y D8; D7 pendiente) |
| **B · Modelo de datos y arquitectura** | **Implementada en `feature/ai-career-path`, pendiente de revisión** |
| C · Pantalla «Mi Carrera en IA» | Sin empezar. Espera la aprobación de la Fase B (la decisión de §6 ya está tomada) |
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
  Todavía no hay pantalla ni entrada de menú.
- **PWA:** los 3 módulos y los 2 JSON nuevos están en `precache.js`, así que funcionan sin conexión.

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

Para la Fase C:
- Botón «Borrar mis datos económicos» y la exportación a mano.
- Cuando haya datos económicos, el aviso tras cerrar sesión no puede decir solo «Tus datos se han borrado
  de este navegador»: tiene que decir que los económicos se quedan aquí.
- Borrar la cuenta tampoco los borra (no están en ella): la pantalla de borrado debe decirlo y ofrecer
  borrarlos.

## 7. Limitaciones conocidas

- Sin pantalla: la ruta solo se puede usar desde código hasta la Fase C.
- Ningún banco de evaluación todavía (`bank: null`): hasta la Fase D ningún módulo se puede completar.
  Es intencionado: sin evaluación no hay competencia.
- Los objetivos de las unidades y los títulos de los criterios solo están en español (el inglés repite el texto).
- Los umbrales (0,7, 180 días, 7 días de prioridad DAW) son hipótesis iniciales, como DEC-009.
- `nextActivities` no está conectado al planificador ni al plan de «Hoy» (Fase E).
- Las evidencias las declara el alumno; el navegador no puede verificar un PR. Por eso una competencia
  nunca sube solo con evidencias.
- **Fallo previo encontrado (no es de esta fase):** si `flush()` coincide con la subida inicial que
  sigue en vuelo tras iniciar sesión, las dos subidas llevan la misma versión. La segunda recibe 409 y
  `doc-sync` relee y fusiona; esa fusión llama a `save*()` y vuelve a marcar el almacén como pendiente,
  así que `flush()` devuelve `false` aunque el servidor lo tenga todo. Afecta a todos los almacenes con
  este patrón (`planner-store.js` incluido) y explica fallos intermitentes ya presentes en `main` al
  cerrar sesión justo después de entrar: `account.spec.js:194` falló 2 de 10 veces y `security.spec.js:40`
  1 de 10, con 3 workers, el 18/11/2026. Propuesta: una sola subida a la vez en `uploader.js`
  (`flush` espera a la que está en curso), en su propia rama `fix/…`.
