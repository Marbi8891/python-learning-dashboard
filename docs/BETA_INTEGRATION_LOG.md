# Registro de integración — PLD Beta 0.1.0

## 26/11/2026

### Integración BETA-001 — Pages deployment (#183)

- Estado: integrada en `release/beta-0.1.0`.
- Archivo: `.github/workflows/pages.yml`.
- Cambio: separar `build` (construcción y subida de artefacto) de `deploy` (publicación), siguiendo el workflow propuesto en #183.
- Verificación fuente: checks de #183 en verde.
- Seguridad de despliegue: workflow conserva el trigger de publicación solo en `main`; esta rama Beta no publica.
- Commit: `cfe992872bd816af25afa4cfc30586f8edb092a6`.

### Integración BETA-002 — Python runtime isolation (PLD-004, #185)

- Estado: integrada en Beta mediante PR #211, squash merge.
- Cambios: restauración del estado del intérprete entre ejecuciones; reinicio de Worker cuando la restauración no se puede garantizar; pruebas de regresión y documentación.
- Checks del commit fuente #185: backend, E2E, WebKit, cursos, Pages artefacto, Docker y Render workflows en verde.
- PR original #185 continúa sin modificar y dirigido a `main`.
- Merge commit de Beta: `fb7201c39f056360533a0cbc7b7b2aa66a9a7eef`.

### BETA-003 — State document versioning (PLD-003, #186)

- Estado: bloqueada para integración automática.
- Se creó PR de integración #212 hacia Beta, pero GitHub reporta `mergeable_state=dirty`.
- La rama fuente está 8 commits detrás de `main` y diverge desde `525f1b89`; además, solapa documentación/Changelog con la integración PLD-004.
- Checks del commit fuente #186: backend, E2E, WebKit, cursos, Docker, Pages artefacto y Render workflows en verde.
- No se fuerza el merge. Se necesita rebase/port manual sobre el estado Beta, preservando cambios recientes y #185, y repetir CI.
- PR #212 es una PR de integración a Beta; no cambia el destino de la PR original #186.

### BETA-004 — Verified exam concurrency (PLD-001, #184)

- Estado: pendiente de port/rebase.
- Checks del commit fuente #184 estaban en verde (backend, E2E, WebKit, cursos, artefacto Pages, Docker y Render).
- Cambia `verified.py`, añade prueba PostgreSQL, actualiza tests/docs/CI. Solapa `CHANGELOG.md` y `docs/TESTING.md` con PLD-004 y tiene una base antigua; se revisará después de PLD-003.
- No se integró aún.

## CI de features candidatas (snapshot revisado)

- #199 AI Academy: fallan artefacto Pages, E2E y WebKit; backend/cursos/Render/Docker pasan.
- #207 Programming Path: fallan backend (Ruff format) y E2E; artefacto Pages, WebKit, cursos, Docker y Render pasan.
- #209 PLD ACADEMY institucional: fallan artefacto Pages, backend (cobertura) y E2E; WebKit, cursos, Docker y Render pasan.
- #175 Demo Edition: PR reporta pruebas locales verdes, pero el estado de CI del branch debe comprobarse de nuevo antes de portarlo.
- Estos resultados son snapshots de runs asociados a los SHAs de PR; no son prueba de que el CI actual de Beta haya ejecutado esas pruebas.

## Próximo orden

1. Rebase/adaptar PLD-003 (#186) y ejecutar CI contra Beta.
2. Portar PLD-001 (#184), integrando sin duplicar los tests de CI y changelog.
3. Revisar la estrategia de merge de los PRs de features; actualizar branches base y corregir CI.
4. Consolidar Learning Hub, Programming Path, AI Academy, DAW Coach y Demo Edition en el orden de dependencias.

### Integración BETA-005 — AI Academy (#199)

- Estado: integrada en Beta vía PR #216, squash merge.
- Añade catálogo de 20 cursos y 5 rutas, navegación, pantalla de catálogo/detalle, índice de módulos y 8 lecciones authored en AI Fundamentals.
- Corrige el literal mal cerrado del curso ai-19 y el test de routing duplicado; regenera `frontend/precache.js` usando el recorrido de directorios exacto del builder.
- Validación final: CI completa en verde (backend, cursos, E2E, WebKit) y Deployment check en verde (artefacto Pages, Docker, workflows/Render).
- Merge commit Beta: `d92519c7a7687a35031d747b41594b3386080d7a`.
- Limitación de contenido: la mayoría de los cursos son outlines; solo Fundamentals tiene lecciones desarrolladas. El checklist de AI Academy usa almacenamiento local propio, pendiente de adaptarse al progreso compartido.
