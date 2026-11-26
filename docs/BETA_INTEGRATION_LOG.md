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

- Estado: integrado en Beta mediante PR #219; PR de port #212 se cerró sin merge como supersedido.
- Un write sin versión no sobrescribe progreso existente; cliente lee/mergea y maneja 409/428.
- Añade regresiones de concurrencia en PostgreSQL y documentación del contrato de sincronización.
- CI final de #219 en verde: backend, E2E, WebKit, cursos y deployment check.
- PR original #186 sigue dirigido a `main`; no se ha integrado allí.

### BETA-004 — Verified exam concurrency (PLD-001, #184)

- Estado: integrado en Beta mediante PR #219.
- Serializa el inicio de simulacros verificados por usuario; protege el límite diario y evita más de un simulacro abierto.
- Añade pruebas de concurrencia PostgreSQL y documentación.
- CI final de #219 en verde: backend, E2E, WebKit, cursos y deployment check.
- PR original #184 sigue dirigido a `main`; no se ha integrado allí.

## CI de features candidatas (snapshot histórico)

- #199 AI Academy: los fallos de los snapshots previos quedaron resueltos al port; integrada en Beta vía #216. La validación de #216 fue verde.
- #207 Programming Path: PR original cerrada como supersedida por #224; su port rebased se integró en Beta y CI de #224 fue verde.
- #209 PLD ACADEMY: PR original cerrada como supersedida por #223. La nueva PR #223 tiene E2E fallido en el último run y necesita rebase/CI.
- #175 Demo Edition: PR reporta pruebas locales verdes, pero el estado de CI debe comprobarse antes de portarla.
- Estos snapshots antiguos no son evidencia del CI actual de Beta.

## Próximo orden

1. Actualizar/portar PR #223 PLD ACADEMY sobre el head actual de Beta y ejecutar CI completo; corregir el E2E de viewport pendiente.
2. Decidir el alcance de #227 Pentest Lab; corregir las pruebas y validar el prototipo UI-only si se decide incluir.
3. Ejecutar CI en el commit final de Beta, smoke test del runtime y revisar accesibilidad/precache/Pages.
4. Preparar release notes y pedir aprobación antes de publicar o integrar a `main`.

### Integración BETA-005 — AI Academy (#199)

- Estado: integrada en Beta vía PR #216, squash merge.
- Añade catálogo de 20 cursos y 5 rutas, navegación, pantalla de catálogo/detalle, índice de módulos y 8 lecciones authored en AI Fundamentals.
- Corrige el literal mal cerrado del curso ai-19 y el test de routing duplicado; regenera `frontend/precache.js` usando el recorrido de directorios exacto del builder.
- Validación final: CI completa en verde (backend, cursos, E2E, WebKit) y Deployment check en verde (artefacto Pages, Docker, workflows/Render).
- Merge commit Beta: `d92519c7a7687a35031d747b41594b3386080d7a`.
- Limitación de contenido: la mayoría de los cursos son outlines; solo Fundamentals tiene lecciones desarrolladas. El checklist de AI Academy usa almacenamiento local propio, pendiente de adaptarse al progreso compartido.

### Integración BETA-006 — PLD-001 + PLD-003 + PLD-004 (#219)

- Estado: integrada en Beta vía PR #219, squash merge.
- PLD-003: versión de documentos sincronizados; un write sin versión no sobrescribe progreso existente; cliente lee/mergea y maneja 428/409; PostgreSQL concurrency regression.
- PLD-001: serializa el inicio de simulacros verificados por usuario; protege límite diario y evita dos simulacros abiertos; PostgreSQL concurrency regression.
- PLD-004: aislamiento de ejecución Python ya integrado en #211 y conservado.
- CI final: backend (100% coverage, Ruff), E2E, WebKit, cursos, Docker, Pages artifact y deployment workflows en verde.
- Merge commit: `648ed43fea067902339528638d3733301e1f60ac`.
- PR #219 es el port rebaseado sobre la Beta actual; PRs originales #184/#186 no se modificaron.

## Integraciones pendientes

### PR #223 — PLD ACADEMY institucional

- Port rebased previo sobre Beta, incluyendo hardening #219; ahora su base está desfasada tras el merge de #224.
- Añade landing pública, workspace demo local, grupos, actividades, analítica, role preview y tour.
- Se corrigió el test de persistencia para seguir el CTA desde la landing al workspace en head commit `230dfa2015eed29425f6e282004e04aae85d60a0`.
- Último CI del head anterior: backend/cursos/WebKit y Deployment check verdes; E2E falló en la persistencia (expectativa de ruta) y un test de viewport PCAP. No hay CI disponible para el head corregido.
- El conector no dispone de operación de rebase/update-branch. Requiere rebase/port manual antes de merge.
- No usar con datos reales; faltan tenancy/auth/permisos/persistencia/auditoría.

### PR #227 — Pentest Lab dashboard

- PR separada contra `main`; no está en Beta y el alcance está pendiente de decisión.
- UI-only: no ejecuta scans ni Docker labs; infraestructura se muestra desconectada.
- Se añadió la traducción faltante de “Pentest Lab” en head commit `67ca9b23ace5676e635164a3b0b3356428121038`; CI no ha corrido en ese head.
- El run anterior falló unit test de traducciones y WebKit por un test de recuperación de cuenta (`mailto:`). Repetir y resolver antes de integrar.

### BETA-007 — Programming Path (#224)

- Estado: integrado en `release/beta-0.1.0` mediante merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597` el 26/11/2026.
- Añade 17 módulos de mapa curricular y 28 prácticas con tareas, entregables, criterios y evidencias.
- Reutiliza el documento Career/store y IDs de recursos/lecciones existentes; no duplica progreso ni bancos.
- CI del head #224 verde: backend, E2E, WebKit, cursos y Deployment check.
- Post-merge CI sobre el merge commit no confirmado; runtime/progress smoke test pendiente.
