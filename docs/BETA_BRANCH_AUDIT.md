# Inventario de ramas — 26/11/2026

Repositorio: `Marbi8891/python-learning-dashboard`. Se obtuvieron 100 ramas en la consulta (página adicional vacía). `main` es la rama por defecto. Este inventario clasifica nombres, no declara que todas las ramas estén actualizadas ni sean mergeables.

## Ramas de Beta creadas durante la auditoría

- `release/beta-0.1.0`: rama de integración.
- `beta/ai-academy-port`: port de AI Academy, PR #216.
- `beta/port-hardening`: port de PLD-003 + PLD-001, PR #217.
- `beta/port-pld003`: port anterior PLD-003, PR #214 cerrada como supersedida.
- `beta/hardening-rebased`: port actualizado PLD-001/003/004, PR #219.
- `beta/academy-institutional-port`: port PLD ACADEMY, PR #220.
- `beta/programming-path-port`: port Programming Path, PR #221.

## Ramas asociadas a PRs abiertas

| Rama | PR | Área |
|---|---:|---|
| `feature/pld-academy-institutional-mvp` | #209 | ACADEMY institucional |
| `feature/programming-path` | #207 | Programming Path |
| `feat/pld-ai-tutor-docs` | #205 | Tutor IA docs |
| `fix/assistant-docs-coherence-2026-11-24` | #203 | Retirada Tutor IA / coherencia |
| `feat/roadmaps-learning-hub` | #201 | Roadmaps |
| `feature/ai-academy-curriculum` | #199 | AI Academy |
| `feature/daw-coach-mobile` | #196 | DAW Coach móvil |
| `feature/daw-exam-coach` | #195 | DAW Exam Coach |
| `feature/pld-ai-tutor-spec` | #193 | Especificación tutor |
| `fix/state-document-versioning` | #186 | PLD-003 sincronización |
| `fix/python-runtime-isolation` | #185 | PLD-004 runtime |
| `fix/verified-exams-concurrency` | #184 | PLD-001 simulacros |
| `fix/pages-deploy-job` | #183 | GitHub Pages |
| `feature/nexaro-local-ai-connection` | #180 | Tutor NEXARO local |
| `feat/demo-edition` | #175 | Demo Edition |
| `docs/academic-development-traceability` | #157 | Gobernanza académica |
| `feature/devops-academy-mvp` | #146 | DevOps Academy |
| `dependabot/docker/backend/main/python-3.15-slim` | #126 | Dependencias |
| `dependabot/npm_and_yarn/main/axe-core/playwright-4.14.0` | #128 | Dependencias |
| `dependabot/npm_and_yarn/main/playwright/test-1.65.0` | #127 | Dependencias |
| `dependabot/pip/backend/main/alembic-gte-1.20.1-and-lt-2.0` | #130 | Dependencias |
| `dependabot/pip/backend/main/fastapi-gte-0.162.2-and-lt-1.0` | #133 | Dependencias |
| `dependabot/pip/backend/main/pytest-cov-gte-7.1.0` | #131 | Dependencias |
| `dependabot/pip/backend/main/ruff-gte-0.17.4` | #129 | Dependencias |
| `dependabot/pip/backend/main/sqlalchemy-gte-2.1.8-and-lt-3.0` | #132 | Dependencias |
| `chore/brand-transition-and-trademark-notice` | #102 | Marca/legal |
| `feature/ai-career-path` | #101 | Career Backend Junior |
| `docs/resultado-pagable` | #95 | Memoria académica |
| (rama no identificada en la consulta) | #63 | Aviso legal |

## Ramas de trabajo / experimentación / infraestructura sin PR abierta en la consulta

- `develop`
- `chore/docker-local-hardening`
- `ci/dependabot-deployment-check`
- `config/google-oauth-client-id`
- `docs/plan-mejora-auditoria`
- `docs/product-strategy-2026-2027`
- `feat/adaptive-study-budget`
- `feat/claude-seo-agent`
- `feat/cybersecurity-course`
- `feat/google-oauth-login`
- `feat/hitos-verificados`
- `feat/mapa-ra-ce`
- `feat/nexaro-ai-integration`
- `feat/panel-cobertura-ce`
- `feat/panel-criterios-ra`
- `feat/pld-monetization-foundation`
- `feat/project-auditor`
- `feat/tutor-ia`
- `feat/video-factory`
- `feature/adaptive-python-tutor`
- `feature/ai-career-path-ui`
- `feature/devops-learning-path`
- `feature/nexaro-local-ai-connection` (también #180)
- `feature/qa-staging-environment`
- `feature/student-dashboard-1edvld`
- `fix/ciberseguridad-progreso`
- `fix/contraste-rediseno`
- `fix/e2e-my-account`
- `fix/google-auth-format-ci`
- `fix/google-borrado-y-carga-diferida`
- `fix/panel-foco-repintado`
- `fix/subida-unica`
- `fix/sync-cursos-dos-sesiones`
- `ops/health-db-copias`
- `sec/limite-peticiones-bd`
- `security/appsec-hardening-oxxazk`
- `ui/pro-redesign`

## Ramas Claude / sesiones de trabajo

- `claude/cierre-mvp-rbk6ai`
- `claude/legaldocs-ai-22dtoa`
- `claude/portada-7jjf1y`
- `claude/project-thread-0deakf`
- `claude/project-thread-0pnjhl`
- `claude/project-thread-3qo18t`
- `claude/project-thread-5d6v00`
- `claude/project-thread-6vnj5k`
- `claude/project-thread-8qjuz7`
- `claude/project-thread-74qvea`
- `claude/project-thread-agb5v1`
- `claude/project-thread-crudrw`
- `claude/project-thread-g2kykr`
- `claude/project-thread-g4eg9k`
- `claude/project-thread-go8idr`
- `claude/project-thread-jxx9sq`
- `claude/project-thread-kwg81i`
- `claude/project-thread-ntfevu`
- `claude/project-thread-nybdey`
- `claude/project-thread-s35m36`
- `claude/project-thread-tr7z7w`
- `claude/project-thread-xl5vtb`
- `claude/project-thread-y4a9jv`
- `claude/project-thread-ykfasf`
- `claude/project-thread-ynuprv`
- `claude/readme-xb5v7f`
- `claude/recuperacion-contrasena`
- `claude/tutor-hibrido-3s4dln`

## Recomendación de limpieza (no ejecutada)

No borrar ramas durante la Beta sin comprobar último commit, PR asociada, si contiene trabajo único y si está desplegada. La prioridad es identificar ramas que ya se integraron, PR cerradas y experimentos abandonados; conservar las ramas fuente de PRs abiertas y los puntos de recuperación.
