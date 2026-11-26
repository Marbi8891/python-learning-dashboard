# Auditoría PLD Beta 0.1.0 — 26/11/2026

> **Estado actualizado después del snapshot inicial:** consulta `docs/RELEASE-BETA-0.1.0-CHECKLIST.md` y `docs/BETA_INTEGRATION_LOG.md` para el estado actual. Este inventario de PR/funciones es una fotografía inicial, no una lista viva.

- Programming Path (#224) ya se integró en `release/beta-0.1.0`; CI del head fuente y Deployment check pasaron.
- Hardening PLD-001/003/004 y AI Academy (#211, #216, #219) ya están integrados en Beta.
- PRs obsoletas #207, #209, #101, #193 y #203 cerradas sin merge.
- PR #223 sigue abierta, desfasada de la Beta; su test de ruta se corrigió en head, pero no hay CI para ese commit y necesita rebase/port.
- PR #227 sigue en `main`, fuera de Beta; se añadió la traducción que faltaba, CI nuevo pendiente y el alcance no está decidido.
- `main` no se ha modificado.


## Alcance y reglas

- Repositorio: `Marbi8891/python-learning-dashboard`.
- Rama base auditada: `main` (`be801c5afa1c27ba6d5f24695236fe8ee67bdcee`).
- Rama de trabajo: `release/beta-0.1.0`, creada desde el mismo SHA. No se modifica `main`.
- La publicación de GitHub Pages ocurre al integrar cambios en `main`; por tanto, la Beta se prepara y valida en esta rama, sin desplegar automáticamente la web pública.
- No editar a mano JSON generado en `frontend/data/`; cambiar scripts y regenerar con los builders.
- No aceptar integraciones que dupliquen lecciones, progreso, bancos, recursos, runtime o sistemas de estado. Reutilizar el sistema existente.
- No integrar PRs directamente sin revisar el diff, sus pruebas y conflictos con las demás líneas de trabajo.

## Arquitectura observada en main

- Frontend: aplicación estática HTML/CSS/JavaScript ES Modules, con carga diferida de áreas y routing/hash.
- Runtime Python: Pyodide servido desde la propia web y ejecutado en Web Worker.
- Backend: FastAPI, routers, esquemas Pydantic y capa de persistencia/sincronización de documentos de estado.
- Persistencia: modo local y cuenta/backend; el estado compartido usa documentos versionados y mecanismos de sincronización.
- Contenido: JSON en `frontend/data/`, scripts de construcción en `scripts/`, IDs estables/locks y pruebas de consistencia.
- QA: Node unit tests, Playwright E2E, pruebas Python/pytest, Ruff, scripts de artefacto/precache, accesibilidad axe y workflows de CI/deployment.
- Infraestructura: Docker Compose, Render config, GitHub Pages, service worker/PWA y CSP.

## Inventario funcional de main (confirmado en el árbol)

### Integrado en main — 🟢

- Aplicación principal, portada, navegación, cursos y aprendizaje de Python.
- Práctica adaptativa, quizzes, gamificación y progreso.
- DAW: currículo oficial y contenidos/cursos de programación, POO, JavaScript, Java, SQL, Entornos, Marcas, Bases de Datos y otros módulos existentes.
- PCAP: banco, preparación y simulacros verificados en backend.
- Ciberseguridad: curso y estado/progreso asociado.
- Excel Academy: catálogo y motor/formación profesional, con módulos integrados.
- Career / Mi Carrera en IA: base de carrera, roadmap, competencias y módulos de la interfaz #176/#178 ya integrados.
- Cuenta, sincronización, documentos de estado, certificados y recursos.
- NEXARO AI: PR #190 está fusionada. La integración es opcional y su configuración por defecto mantiene el servicio desactivado. La conexión real con un NEXARO desplegado debe validarse por separado.
- Seguridad, accesibilidad, PWA, Pyodide local, CI y despliegue.

### PRs abiertas candidatas — 🔵, no integradas todavía

| PR | Área | Estado / riesgo inicial |
|---|---|---|
| #209 | PLD ACADEMY institucional | MVP frontend demo. CI reportó fallos en la última ejecución observada; sin multitenancy, auth institucional ni persistencia server-side. No usar datos reales. |
| #207 | Programming Path | 28 prácticas y mapa curricular; reutiliza Career. Requiere CI actualizado y revisar solapamiento de recursos/scripts de Career. |
| #205 | Documentación Tutor IA | Docs solamente; debe conciliarse con la decisión vigente de tutor IA y NEXARO. |
| #203 | Retirada/limpieza de Tutor IA | Elimina interfaz y módulos; conflicto funcional con #190/#180/#193/#205. No integrar hasta resolver una decisión de producto. |
| #201 | Roadmaps hub | UI ligera, pero su progreso es local y necesita reconciliarse con el Learning Engine/Career antes de integrarse. |
| #199 | AI Academy | Integrada en Beta vía #216; catálogo y curso inicial. Contenido parcial, progreso local propio pendiente de unificación. |
| #196 | DAW Coach mobile | PWA independiente; potencial duplicación del Coach/Second Brain. Requiere revisar integración y precache/service worker. |
| #195 | DAW Exam Coach | Workspace local-first; potencial solapamiento con preparación DAW y progreso. |
| #193 | Tutor IA spec | Documentación, no código. |
| #180 | Widget/servicio tutor NEXARO local | Prototipo con requisitos pendientes de CORS/rutas/auth y compatibilidad; solapa #190. |
| #175 | Demo Edition | Cambios amplios (45 archivos): modo demo, hub de cursos y laboratorio. CI reportado fallido en la rama al último snapshot; revisar logs y la base de cambios. |
| #186 | Versionado de documentos de estado | Corrección de sincronización; revisar como prioridad de estabilidad antes de integrar features que escriben estado. |
| #185 | Aislamiento de runtime Python | Corrección de seguridad/fiabilidad; prioridad alta y revisar tests. |
| #184 | Concurrencia de simulacros verificados | Corrección de backend; prioridad alta. |
| #183 | Pages deployment job | Corrección del pipeline de despliegue; revisar el estado CI y mantener fuera de main hasta aprobación. |
| #146 | DevOps Academy MVP | Contenido y curso; candidato posterior, necesita revisión curricular y progreso común. |
| #101 | Career Roadmap Backend Junior | Amplio contenido de Career; candidato, verificar coherencia con Career ya integrado y con #207. |
| #102 | Aviso marca Python | Docs/legal; revisión necesaria antes de la beta pública. |
| #157 | Trazabilidad académica/uso IA | Documentación; candidato de gobernanza. |
| #95 | Memoria de proyecto | Documento académico; validar que corresponde al estado actual. |

## Prioridad de revisión e integración

### P0 — Estabilidad y seguridad

1. #186 versionado/sync (PLD-003).
2. #185 aislamiento de ejecución Python (PLD-004).
3. #184 concurrencia de simulacros (PLD-001).
4. #183 pipeline Pages.
5. Revisar el estado CI y compatibilidad de cada fix. Integrar uno por uno en Beta, ejecutar regresión y documentar el SHA.

### P1 — Consolidación de Learning Hub

1. #201 Roadmaps como navegación sobre rutas existentes; rehacer/adapter progreso para el sistema compartido, no mantener store independiente.
2. #207 Programming Path: validar datos generados, IDs y recursos; integrar como prácticas vinculadas al contenido existente.
3. #199 AI Academy: validar rutas, catálogo y contenido; separar contenido authored de outlines y completar progresivamente.
4. #146 DevOps Academy, #101 Career y recursos: evitar duplicados; resolver referencias y fuente única.

### P2 — Experiencias

1. #175 Demo Edition: validar y adaptar demo sin tocar estado real ni llamar API; proteger por modo demo y revisar tests.
2. #195/#196 DAW Coach/Exam Coach: consolidar en una experiencia DAW, reutilizando el currículo, progreso, conceptos, revisión y biblioteca existentes.
3. #209 ACADEMY institucional: mantener como demo visual hasta implementar tenancy, auth/roles, backend, aislamiento de datos, auditoría y controles de privacidad.

### P3 — IA y documentación

- Definir una decisión única de producto para tutor: NEXARO opcional (integración #190) frente a asistente determinista y módulos retirados por #203.
- No habilitar proveedor ni enviar datos de estudiantes sin configuración, consentimiento/privacidad y límites de datos.
- Integrar documentación (#205/#193/#157/#102) tras comprobarla contra código real.

## Definition of Beta 0.1.0

- Todas las áreas principales accesibles desde una navegación coherente.
- Currículos/rutas conectados a contenidos reales existentes.
- Un único sistema de progreso, XP, mastery, evaluación y sincronización.
- Contenido completo y trazable; enlaces a recursos externos comprobados, con licencias respetadas.
- Demo separada de cuentas reales.
- Tests unitarios, backend, E2E, accesibilidad, responsive, PWA/precache y seguridad en verde.
- Sin despliegue desde esta rama; publicar requiere revisión y aprobación manual de merge.

## Estado de trabajo

- [x] Confirmar repositorio y permisos.
- [x] Confirmar `main` SHA y que beta parte de ese mismo commit.
- [x] Inventariar árbol y arquitectura de alto nivel.
- [x] Inventariar PRs recientes y cambios/solapamientos.
- [x] Revisar diffs prioritarios y snapshots CI de fixes/features.
- [x] Integrar #183 (Pages workflow) en Beta.
- [x] Integrar #185 (PLD-004) en Beta vía PR #211.
- [ ] Port/rebase #186 (PLD-003): PR #212 bloqueada por conflictos.
- [ ] Port/rebase #184 (PLD-001): pendiente.
- [x] Integrar AI Academy (#216) tras CI verde.
- [x] Integrar fixes P0 PLD-001/003/004 vía #219 tras CI verde.
- [ ] Consolidar catálogo/rutas/Academies.
- [ ] Consolidar DAW Coach y preparación.
- [ ] Integrar Demo Edition.
- [ ] Integrar Academy institucional en modo demo.
- [ ] Ejecutar regresión completa y crear release candidate.

## Observaciones

Este documento es una auditoría inicial basada en la estructura de `main`, metadata de PR y snapshots de CI disponibles el 26/11/2026. No sustituye la revisión del diff ni la ejecución local de los tests. Los estados CI pueden cambiar; comprobar el run más reciente antes de integrar cada PR.
