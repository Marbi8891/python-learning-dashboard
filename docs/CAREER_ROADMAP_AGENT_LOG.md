# Career Roadmap · Registro de trabajo

Registro persistente del módulo Career Roadmap. Antes de cada sesión: leer este archivo y comprobar el
estado real del repositorio (`git log`, PR abiertos). La arquitectura está en
[`CAREER_ROADMAP_ARCHITECTURE.md`](CAREER_ROADMAP_ARCHITECTURE.md).

## Estado de los sprints

| Sprint | Estado | PR |
|---|---|---|
| 0 · Auditoría y arquitectura | Entregado, espera aprobación del autor | este PR |
| 1-9 | Sin empezar | — |

## Agentes

Los agentes `career-*` que pide el prompt **no existen** en `.claude/agents/` (04/11/2026). Existen
`revisor-daw`, `buscador-mejoras`, `mejorador-web` y `red-teamer`. La auditoría del Sprint 0 la hizo la
sesión principal. Qué hacer con ellos: decisión D4.

## Decisiones

| Id | Estado | Recomendación |
|---|---|---|
| D1 Persistencia | Pendiente | Documento `career` + catálogo estático generado |
| D2 IA (Sprint 7) | Pendiente | Posponer; nunca de pago |
| D3 Itinerarios B-D | Pendiente | Esqueleto con recursos externos |
| D4 Agentes `career-*` | Pendiente | Reutilizar los cuatro existentes |

## Sprint 0 (04/11/2026)

- Base auditada: `main` en `d0c88c6`.
- Archivos creados: `docs/CAREER_ROADMAP_ARCHITECTURE.md`, este registro. Índice en `docs/README.md`.
- Sin cambios funcionales: no hace falta ejecutar pruebas de código.
- Dependencias externas: PR #96 (Bases de datos) conviene fusionarlo antes del Sprint 3.

## Próximas acciones

1. El autor decide D1-D4 y aprueba el Sprint 1.
2. Sprint 1: generador del catálogo, itinerario A enlazado a contenido existente y documento `career`.
