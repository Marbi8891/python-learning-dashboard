# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 20:14 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta audit snapshot:** `dee08c96ec3da7b79fa190612afc3b3116f1175b` (**85 ahead / 0 behind main**; CI #681 passed en ese SHA).  
**PR #237 head:** `8bbcf8578255a7de96f72960df18c27670fedb2b` (**6 ahead / 0 behind Beta**); CI #686 passed (Backend, Cursos, E2E, WebKit) y Deployment Check #340 passed (workflow, artefacto Pages, Docker health check). Sigue Draft, sin reviews ni approvals.  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta definir alcance, validar CI sobre el SHA candidato exacto y completar smoke test manual, responsive y accesibilidad. La CI y Deployment Check de PR #237 no hacen un despliegue real de Pages.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`. No pendiente.
- [ ] **#223 Academy:** draft; head `9d674df`, **17 ahead / 69 behind** Beta (merge base `5182b1ce`). CI #45890668077 y Deployment Check #45890668052 passed en ese head, no revalidados ahora. No reviews/approvals. Se solapa con #229 en `frontend/index.html`, `frontend/js/app.js`, `frontend/precache.js` e i18n. Demo local/sintética; no tiene aislamiento multi-tenant real, autenticación institucional, persistencia backend ni enforcement de permisos.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 37 behind** Beta (merge base `c31244a`). CI #45934058607: **286 passed, 1 failed** en `e2e/learning-paths.spec.js:39`; tras reload `#paths-view` queda vacío, esperaba “Mis Paths”. Backend, Cursos y WebKit pasaron; Deployment Check #45934058622 passed. Dos reviews COMMENTED, sin approval; una revisión retractó un finding falso de markup y la otra confirmó los problemas de render duplicado/async y listener, pero el CI sigue fallando. Solapamiento con #223; reutiliza progreso, sin store/XP paralelo. Causa del fallo de reload no aislada.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, **16 ahead / 0 behind main**; contra Beta **16 / 85**. CI #45851158102 falla gate unitario (**571/572 passed**) en `AI Academy is wired into app routing and view registry`; assertion espera loader de AI Academy que no existe en main. Backend, Cursos y WebKit pasaron; Playwright no se inició. Deployment Check #45851158126 passed. UI de planificación, no ejecuta Docker, escaneos ni métricas reales. Decidir alcance antes de integrar.
- [x] PR obsoletas **#207, #209, #101, #193, #203**: cerradas sin merge.
- [x] #224 está merged; no debe tratarse como candidata pendiente.

## CI y main
- [x] CI **#46010720561 (run #680)** passed en SHA `94efd96`: Backend, Cursos, E2E y WebKit.
- [x] CI **#46014073048 (run #681)** passed en SHA `dee08c96`: Backend, Cursos, E2E y WebKit.
- [x] Main sigue en `be801c5`. Monitor #46012047656 passed; **no es una suite completa**.
- [x] PR #237: CI **#46049729874 (run #686)** passed en head exacto `8bbcf857`, 4/4 jobs.
- [x] PR #237: Deployment Check **#46049729866 (run #340)** passed en head exacto `8bbcf857`, 3/3 jobs.
- [ ] Los checks de #223/#229/#227 no validan una integración actualizada sobre Beta.
- [ ] CI de integración tras cualquier portado/rebase, en el SHA exacto antes de merge.

## Backlog de PR abiertas
GitHub devuelve **27 PR abiertas**. Esta pasada revalidó las PR candidatas y #237; el resto no se revalidó individualmente.
- **#205 Tutor IA docs:** última auditoría E2E failed.
- **#201 Roadmaps:** última auditoría E2E failed.
- **#199 AI Academy:** última auditoría Pages, E2E y WebKit failed.
- **#196 DAW Coach móvil:** última auditoría Pages, E2E, backend y WebKit failed.
- **#195 DAW Exam Coach:** última auditoría E2E failed.
- **#185 Python runtime isolation:** última auditoría E2E failed en head actual.
- Dependabot **#128 axe-core:** última auditoría E2E y WebKit failed.
- Dependabot **#126 Python 3.15, #127 Playwright y #129–#133:** checks consultados en auditorías anteriores pasaron; no revalidados ahora.
No se investigaron logs de todas las PR ni se integró ninguna.

## Seguridad y calidad
- [x] CI workflow: `contents: read`, checkout `persist-credentials: false`, `pip-audit`, `npm audit --audit-level=high`, Ruff, cobertura backend 100 % y pruebas PostgreSQL de migraciones, rate-limit, concurrencia, versionado y backup/restore (según CI #681).
- [x] Pages workflow separado: build y deploy en jobs distintos; checkout sin persistir credenciales.
- [x] Hardening Pages propuesto en PR #237: `contents: read` a nivel workflow/build y `pages: write`, `id-token: write` solo en `deploy`. CI #686 y Deployment Check #340 passed en el head exacto. No está integrado en Beta ni se probó un despliegue real de Pages.
- [ ] Revisar findings actuales de dependencias, secretos, configuración y privacidad del candidato.
- [ ] Smoke test de Pages, responsive y accesibilidad manual.
- [ ] Confirmar demo con datos sintéticos, sin progreso personal.

## Ramas y protección
- Inventario paginado: **107 ramas (100 + 7)**; página final vacía.
- Rulesets: **[]** verificado mediante API.
- Endpoint de branch protection para main y Beta devuelve **403 Resource not accessible by integration**; no se puede verificar la protección efectiva.
- `beta/programming-path-rebased`: **0 ahead / 56 behind** Beta; no tiene commits únicos por delante, candidata redundante. No borrada.
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
- [x] GitHub Releases: **[]** verificado.
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
- 2026-11-27 15:54: Base Beta `dee08c96` (85 ahead / 0 behind main). CI #681 passed exact SHA; main `be801c5` intact. Monitor passed (not full suite). PR #223: 17/69; #229: 32/37, 286/1 E2E; #227: 16/0 main, 571/1 unit gate. Inventory 107 branches and 28 open PRs. PR #237 had CI #683 passed on prior merge SHA, #684 in progress on `8cbd010`, Deployment Check #338 passed. Branch protection not verified.
- 2026-11-27 19:27 CET: PR #237 head `21a09dc` (5/0 contra Beta), CI #685 attempt 2 passed (Backend, Cursos, E2E, WebKit), Deployment Check #339 passed. First attempt failed WebKit recovery-link test; retry passed.
- 2026-11-27 20:14 CET: PR #237 head `8bbcf857` (6/0). CI #686 passed exact SHA (4/4); Deployment Check #340 passed exact SHA (3/3). Checklist actualizado en esta rama. PR sigue Draft, sin review; no merge ni deploy. Search devolvió 27 PR abiertas, inventario 107 ramas (100+7, última página vacía), rulesets vacíos; branch protection 403. Tag `v1.0.0` confirmado y Releases vacías.
- No merges adicionales, branch deletions, force-pushes, tags, releases ni deployments.
