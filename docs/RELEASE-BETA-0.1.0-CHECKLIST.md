# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 15:54 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta audit snapshot:** `dee08c96ec3da7b79fa190612afc3b3116f1175b` (**85 ahead / 0 behind main**; CI #681 passed on this exact SHA). PR #237 head `326e4c86`; CI #683 passed on merge commit `7a320dc` (head + Beta base `dee08c96`). Deployment Check not verified. This checklist update on the PR branch will trigger another CI run.  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta definir alcance, validar CI sobre el SHA candidato exacto y completar smoke test manual, responsive y accesibilidad.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`. No pendiente.
- [ ] **#223 Academy:** draft; head `9d674df`, **17 ahead / 69 behind** Beta (merge base `5182b1ce`). CI #45890668077: Backend, Cursos, E2E and WebKit passed; Deployment Check #45890668052 passed. No reviews/approvals. Overlaps #229 in `frontend/index.html`, `frontend/js/app.js`, `frontend/precache.js`, and i18n. Local synthetic demo; no real tenant isolation, institutional auth, backend persistence or permission enforcement.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 37 behind** Beta (merge base `c31244a`). CI #45934058607: **286 passed, 1 failed** at `e2e/learning-paths.spec.js:39`; after reload `#paths-view` remains empty, expected “Mis Paths”. Backend, Cursos and WebKit passed; Deployment Check #45934058622 passed. Two COMMENTED reviews, no approval. Overlaps #223; read-only progress adapters, no parallel progress/XP store. Root cause not isolated.
- [ ] **#227 Pentest Lab:** draft against main; head `67ca9b2`, **16 ahead / 0 behind**. CI #45851158102 fails unit-test gate (**571/572 passed**) at `AI Academy is wired into app routing and view registry`; the assertion expects an AI Academy loader absent from main. Backend, Cursos and WebKit passed; Playwright did not start after the unit gate failed. Deployment Check #45851158126 passed. UI-only planning; no Docker execution, scans or live infrastructure metrics.
- [x] PR obsoletas **#207, #209, #101, #193, #203**: cerradas sin merge.

## CI y main
- [x] CI **#46010720561 (run #680)** passed on exact SHA `94efd96`: Backend, Cursos, E2E and WebKit. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46010720561.
- [x] CI **#46014073048 (run #681)** passed on exact SHA `dee08c96`: Backend, Cursos, E2E and WebKit. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46014073048.
- [x] Main sigue en `be801c5`. CI monitor #46012047656 passed; **no es una suite completa**.
- [ ] Los checks de #223/#229/#227 no validan una integración actualizada sobre Beta.
- [ ] CI de integración tras cualquier portado/rebase, en el SHA exacto antes de merge.

## Backlog de PR abiertas
GitHub devuelve **28 PR abiertas**, incluida #237. Checks consultados sobre sus heads:
- **#205 Tutor IA docs:** E2E failed; backend, cursos, WebKit y deployment passed (checks revisados en auditoría anterior; no revalidados en esta pasada).
- **#201 Roadmaps:** E2E failed; backend, cursos, WebKit y deployment passed.
- **#199 AI Academy:** Pages, E2E y WebKit failed; backend, cursos y configuración de Render passed.
- **#196 DAW Coach móvil:** Pages, E2E, backend y WebKit failed; cursos y configuración de Render passed.
- **#195 DAW Exam Coach:** E2E failed; backend, cursos, WebKit y deployment passed.
- **#185 Python runtime isolation:** E2E failed en el head actual; un run anterior verde no cuenta.
- Dependabot **#128 axe-core:** E2E y WebKit failed; backend, cursos y deployment passed.
- Dependabot **#126 Python 3.15, #127 Playwright y #129–#133:** todos los checks consultados passed.
No se investigaron los logs de todas las PR ni se integró ninguna de ellas.

## Seguridad y calidad
- [x] CI workflow: `contents: read`, checkout `persist-credentials: false`, `pip-audit`, `npm audit --audit-level=high`, Ruff, cobertura backend 100 % y pruebas PostgreSQL de migraciones, rate-limit, concurrencia, versionado y backup/restore.
- [x] Pages workflow separado: build y deploy en jobs distintos; checkout sin persistir credenciales.
- [ ] Hardening Pages propuesto en PR #237: `contents: read` a nivel workflow/build y `pages: write`, `id-token: write` solo en `deploy`. CI #683 pasó en merge commit `7a320dc`; PR sigue Draft, sin review. La corrección no está en Beta.
- [ ] Revisar findings actuales de dependencias, secretos, configuración y privacidad del candidato.
- [ ] Smoke test de Pages, responsive y accesibilidad manual.
- [ ] Confirmar demo con datos sintéticos, sin progreso personal.

## Ramas y protección
- Inventario paginado: **107 ramas (100 + 7)**; todas devuelven `protected:false` (lectura actual).
- Rulesets: **[]**. Endpoint detallado de branch protection devuelve 403 a la integración; no se pudo inspeccionar la configuración.
- `beta/programming-path-rebased`: **0 ahead / 52 behind** Beta; no tiene commits únicos, candidata redundante. No borrada.
- Comparaciones actuales contra Beta:
  - `beta/academy-institutional-port`: 11/73
  - `beta/academy-institutional-rebased`: 17/69
  - `beta/ai-academy-port`: 16/79
  - `beta/hardening-rebased`: 19/76
  - `beta/port-hardening`: 22/80
  - `beta/port-pld003`: 14/80
  - `beta/programming-path-port`: 18/73
  - `beta/programming-path-rebased`: 0/56
Conservar las ramas divergentes hasta revisar commits únicos.

## Tags y Release
- [x] `v1.0.0` anotado, sin firma; tag object `603274fb5a908260bea927d48de647883e2f948f`, target `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No mover ni reutilizar.
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
- 2026-11-27 15:54: Base Beta `dee08c96` (85 ahead / 0 behind main). CI #681 passed exact SHA `dee08c96`; main `be801c5` intacta. Monitor #46012047656 passed (not full suite). PR #223: 17/69 and CI green; #229: 32/37 with 286/1 E2E; #227: 16/0 main with 571/1 unit gate. Inventory 107 branches and 28 open PRs. PR #237 CI #683 passed on merge commit `7a320dc`; this checklist update will trigger another run.
- Checklist refrescado con el CI exacto #680 y comparaciones recalculadas. La descripción de PR y los checks de las candidatas se actualizarán en esta auditoría; no se repiten comentarios.
- No merges adicionales, branch deletions, force-pushes, tags, releases ni deployments.
