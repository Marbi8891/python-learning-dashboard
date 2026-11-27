# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 12:25 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta:** `c34b185931186802db5d7449bd454760320d3ff0` (**80 ahead / 0 behind main**)  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta definir el alcance, ejecutar CI sobre el SHA candidato exacto y completar smoke test manual, responsive y accesibilidad.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`. No pendiente.
- [ ] **#223 Academy:** draft; head `9d674df`, **17 ahead / 64 behind** Beta (merge base `5182b1ce`). CI #45890668077 y Deployment Check #45890668052 passed sobre el head actual de la PR; no hay approvals. Se solapa con #229 en HTML, router, precache e i18n. Demo local/sintética: no usar datos reales; faltan aislamiento multi-tenant, auth, persistencia backend y permisos. Mantener draft; actualizar sobre Beta y resolver solapamiento antes de CI de integración.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 32 behind** Beta (merge base `c31244a`). CI #45934058607 attempt 4 falla E2E (**286 pass / 1 fail**) en `e2e/learning-paths.spec.js:39`: tras reload, `#paths-view` vacío; expected “Mis Paths”, actual vacío. Artifact #15178416458 y logs revisados; causa aún no confirmada. Backend, cursos y WebKit pasaron; Deployment Check #45934058622 passed. Dos reviews COMMENTED, sin aprobación. No integra progreso/XP paralelo. Corregir, actualizar contra Beta y repetir CI.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, **16 ahead / 0 behind**. CI #45851158102 falla tests unitarios (**571 pass / 1 fail**) en `tests/unit/ai-academy-routing.test.mjs`: espera loader AI Academy ausente de main. Backend, cursos y WebKit passed; E2E skipped. Deployment Check #45851158126 passed. Es UI de planificación; no ejecuta Docker, scans ni métricas. Decidir alcance.
- [x] PR obsoletas **#207, #209, #101, #193, #203**: cerradas sin merge.

## CI y main
- [x] CI **#45981365281** passed en Beta SHA exacto `c34b185`: Backend, Cursos, E2E y WebKit. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45981365281
- [x] Main sigue en `be801c5`. CI monitor #45982659278 passed, pero no es suite completa.
- [ ] Los checks de PR #223/#229/#227 no validan una integración actualizada sobre Beta.
- [ ] CI de integración después de cualquier rebase/portado, sobre SHA exacto, antes de merge.

## Backlog de PR abiertas
GitHub devuelve **27 PR abiertas**. Checks de heads consultados:
- **#205 Tutor IA docs:** CI failed; Deployment check passed.
- **#201 Roadmaps:** CI failed; Deployment check passed.
- **#199 AI Academy:** CI y Deployment check failed.
- **#196 DAW Coach móvil:** CI y Deployment check failed.
- **#195 DAW Exam Coach:** CI failed; Deployment check passed.
- **#185 Python runtime isolation:** CI failed; Deployment check passed (head actual; run antiguo verde no cuenta).
- Dependabot **#128 axe-core:** CI failed; Deployment check passed.
- Dependabot **#127 Playwright** y **#126 Python 3.15:** ambos checks passed.
- Dependabot **#129–#133:** no revalidado en esta pasada.
No se investigaron todos los logs ni se integró ninguna de estas PR.

## Seguridad y calidad
- [x] CI workflow revisado: `contents: read`, checkout `persist-credentials: false`, `pip-audit`, `npm audit --audit-level=high`, Ruff, cobertura backend 100 % y pruebas PostgreSQL para migraciones, concurrencia, versionado y backups.
- [x] Pages workflow separado del deploy; permisos `contents: read`, `pages: write`, `id-token: write`.
- [ ] Revisar findings actuales de dependencias, secretos, configuración y privacidad del candidato.
- [ ] Smoke test de Pages, responsive y accesibilidad manual.
- [ ] Confirmar demo con datos sintéticos, sin progreso personal.

## Ramas y protección
- Inventario paginado: **106 ramas (100 + 6)**; todas devuelven `protected:false`.
- Rulesets: **[]**. Endpoint de branch protection detallado devuelve 403 a la integración; configuración no pudo inspeccionarse.
- `beta/programming-path-rebased`: **0 ahead / 51 behind** Beta; sin commits únicos, candidata redundante. No borrada.
- Comparaciones contra Beta:
  - `beta/academy-institutional-port`: 11/68
  - `beta/academy-institutional-rebased`: 17/64
  - `beta/ai-academy-port`: 16/74
  - `beta/hardening-rebased`: 19/71
  - `beta/port-hardening`: 22/75
  - `beta/port-pld003`: 14/75
  - `beta/programming-path-port`: 18/68
  - `beta/programming-path-rebased`: 0/51
Conservar ramas divergentes hasta revisar commits únicos.

## Tags y Release
- [x] `v1.0.0` anotado, sin firma; tag object `603274f`, target commit `fdf6409`. No mover ni reutilizar.
- [x] GitHub Releases: **[]**.
- [ ] Elegir tag nuevo sobre el SHA candidato validado y publicar Release con alcance, limitaciones y demo.

## Presentación
- [ ] README, instrucciones y CHANGELOG alineados con alcance final.
- [ ] Capturas sin datos personales; ES/EN, aviso legal y privacidad revisados.
- [ ] Ensayar walkthrough; no tocar progreso real.
- [ ] Smoke test de Pages, responsive y accesibilidad.
- [ ] Notas de versión y limitaciones.

## Limitaciones a declarar
Academy es demo local sintética, no servicio multi-tenant. Learning Paths reutiliza progreso existente, sin XP/store paralelo. Pentest Lab es planificación, no scanner ni laboratorio operativo.

## Registro
- 2026-11-27 12:25: Beta `c34b185`; CI #45981365281 passed en SHA exacto. Main `be801c5` intacta; monitor #45982659278 passed.
- Se actualiza este checklist y los bloques de auditoría de #223, #229 y #227 en lugar de añadir comentarios duplicados.
- No merges adicionales, branch deletions, force-pushes, tags, releases ni deployments.
