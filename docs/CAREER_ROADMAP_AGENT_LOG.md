# Career Roadmap · Registro de trabajo

Registro persistente del módulo Career Roadmap. Antes de cada sesión: leer este archivo y comprobar el
estado real del repositorio (`git log`, PR abiertos). La arquitectura está en
[`CAREER_ROADMAP_ARCHITECTURE.md`](CAREER_ROADMAP_ARCHITECTURE.md).

## Estado de los sprints

| Sprint | Estado | PR |
|---|---|---|
| 0 · Auditoría y arquitectura | Hecho y fusionado; D1-D4 aprobadas por el autor (04/11/2026, «OK D1-D4») | #100 |
| 1 · Catálogo, documento `career` y cálculo | Hecho, pendiente de revisión | #101 |
| 2 · Vistas y navegación | Sin empezar: espera aprobación | — |
| 3-9 | Sin empezar | — |

## Agentes

Los agentes `career-*` del prompt **no existen** y no se crean (DEC-014). Se reutilizan `revisor-daw`,
`buscador-mejoras`, `mejorador-web` y `red-teamer`.

## Decisiones

| Id | Decisión | Registro |
|---|---|---|
| D1 | Documento `career` + catálogo estático generado | DEC-011 |
| D2 | IA pospuesta; nunca de pago | DEC-012 |
| D3 | Full Stack, Data/ML y Ciberseguridad como esqueleto | DEC-013 |
| D4 | Sin agentes `career-*` | DEC-014 |
| — | Dominio de competencia por agregación de fuentes | DEC-015 |

## Sprint 0 (04/11/2026)

- Base auditada: `main` en `d0c88c6`. Solo documentación.

## Sprint 1 (04/11/2026)

**Hecho**

- `scripts/career/roadmaps.py` (datos), `build_career.py` (validación y generación con `--check`),
  `ids.lock.json`. Generados `frontend/data/career/index.json` y `python-backend-junior.json`:
  8 fases, 54 unidades (24 pendientes de contenido propio), 24 competencias, 8 proyectos.
- `frontend/js/career/career-data.js`: limpieza, fusión, inscripción, unidades, entregas, dominio de
  competencias, estados de fase y siguiente actividad. `career-store.js`: guardado, sincronización y
  señales del motor 2.0 y de los cursos. Se inicia en `app.js` y se sube antes de cerrar sesión (`account.js`).
- `pcap-store.js` exporta `blockCoverage` para no duplicar la regla de cobertura.
- Backend: `"career"` en `COURSES`. CI: paso `build_career.py --check`.
- Docs: `CAREER_ROADMAP_API.md`, `CAREER_ROADMAP_DATA_MODEL.md`, `CAREER_ROADMAP_ADAPTIVE_ENGINE.md`,
  DEC-011..015, `TESTING.md`, índice.

**Pruebas**

| Prueba | Resultado |
|---|---|
| `ruff check` y `ruff format --check` | OK |
| `pytest --cov=app --cov-fail-under=100` | 658 pasan, cobertura 100 % (nuevos: `test_career_catalog.py`, caso `career` en `test_course_state.py`) |
| `build_career.py --check` | OK |
| `npm run test:unit` | 175 pasan (11 nuevos en `career-data.test.mjs`) |
| e2e (chromium, contenedor) | 180 pasan; 18 fallan porque el contenedor no llega a `cdn.jsdelivr.net` (Pyodide), igual que en `main`. La CI de GitHub sí los ejecuta |

**Pendiente / problemas conocidos**

- Todavía no hay interfaz: el documento `career` solo cambia desde las vistas del Sprint 2.
- `phase.assessment` está vacío hasta el Sprint 5.
- Los proyectos son autoevaluados.

## Próximas acciones

1. El autor revisa el PR #101 y aprueba el Sprint 2.
2. Sprint 2: ruta `#/carrera`, vistas Resumen, Ruta, Competencias, Proyectos, Evaluaciones y Preparación;
   e2e, axe y capturas en 320/768/1440 px. Revisión con `revisor-daw` y `mejorador-web`.
