# Career Roadmap · Modelo de datos

Dos partes: el **catálogo** (igual para todos, generado) y el **documento de progreso** de cada alumno.
No hay tablas nuevas ni migraciones (DEC-011).

## Catálogo (`frontend/data/career/`)

Se escribe en `scripts/career/roadmaps.py` y se genera con `python scripts/career/build_career.py`.
Nadie edita a mano los JSON generados.

```
Roadmap        id, status (complete | skeleton), title{es,en}, description, level, months, objectives[]
├─ Skill       id, title, category, target (1-3), requires[skill], sources{concepts[], blocks[], projects[]}
├─ Phase       id, title, description, objectives[], requires[phase], skills[skill], assessment, project
│  └─ Unit     id, title, links[{kind, ref, title, url?}], pending
└─ Project     id, phase, skills[], title, description, criteria[{id, text}]
```

| Entidad del prompt | Dónde está |
|---|---|
| Roadmap, RoadmapPhase, LearningUnit, Skill, Project | Catálogo |
| Assessment | `phase.assessment` (vacío hasta el Sprint 5) |
| UserRoadmap, UserUnitProgress, ProjectSubmission | Documento `career` |
| UserPhaseProgress, UserSkill, LearningEvidence, Recommendation | Se **calculan** en `career-data.js`; no se guardan |
| AssessmentAttempt | Documento `career` (Sprint 5) |

### Enlaces de una unidad

| `kind` | `ref` | Contenido |
|---|---|---|
| `concept` | id de `learning.json` | Concepto del motor adaptativo |
| `pcap` | slug de `lessons.json` | Lección del curso PCAP |
| `lesson` | `<curso>/<slug>` | Lección de un curso de DAW |
| `block` | `<curso>:<bloque>` | Bloque de preguntas de un curso de DAW |
| `resource` | id de `resources.json` | Recurso externo con licencia revisada |

Una unidad sin enlaces queda `pending: true` («contenido pendiente»): no se inventa contenido.

### Validaciones del generador

Ids `[a-z0-9-]`, únicos y estables (`scripts/career/ids.lock.json` solo crece); prerrequisitos de fases
y competencias que existen y sin ciclos; cada enlace y cada fuente existe; cada competencia tiene alguna
fuente y está en alguna fase; cada proyecto es de la fase que lo declara y tiene criterios; textos en
español e inglés; `months` entre 1 y 36.

### Itinerario Python Backend Developer Junior

8 fases, 54 unidades (24 pendientes de contenido propio), 24 competencias en 7 categorías y 8 proyectos.

| Fase | Requiere | Unidades (pendientes) | Proyecto |
|---|---|---|---|
| Python Fundamentals | — | 7 (0) | Mini proyecto de consola |
| Professional Python | Fundamentals | 8 (3) | Gestor de tareas con persistencia |
| Databases & SQL | Fundamentals | 7 (1) | Gestión de clientes y operaciones |
| Backend Development | Professional Python, Databases | 7 (5) | API REST con usuarios, roles y CRUD |
| Software Testing | Backend | 5 (3) | Batería de pruebas de la API |
| Frontend Development | Fundamentals | 7 (3) | Interfaz web para la API |
| DevOps & Deployment | Backend | 6 (3) | Despliegue completo |
| Career Preparation | Testing, Frontend, DevOps | 7 (5) | Proyecto final |

## Documento de progreso (`pld:career` y `/api/v1/course-state/career`)

```json
{
  "v": 1,
  "active": "python-backend-junior", "activeAt": "ISO",
  "roadmaps": {
    "python-backend-junior": {
      "enrolledAt": "ISO", "months": null, "monthsAt": null,
      "units": { "fund-control": { "done": true, "at": "ISO" } },
      "projects": { "api-rest": { "repo": "https://github.com/…", "checks": { "crud": true }, "at": "ISO" } }
    }
  }
}
```

- **Limpieza** (`cleanCareer`): ids con formato, fechas ISO, `done` booleano, criterios solo `true`,
  `repo` solo `https:` sin usuario ni contraseña (si no, vacío), como mucho 10 itinerarios y 300
  unidades o proyectos por itinerario. Conserva los campos que no conoce (DEC-007).
- **Fusión** (`mergeCareer`): gana lo cambiado más tarde (cada unidad, cada proyecto, los meses y el
  itinerario activo); la fecha de inicio es la más antigua. Una unidad desmarcada se guarda con fecha
  para que otro dispositivo no la vuelva a marcar.
- **Duración:** `months` es solo un ritmo orientativo; nunca bloquea.
- **Datos personales:** solo los enlaces que pone el alumno. Entra en la exportación y se borra con la cuenta.
