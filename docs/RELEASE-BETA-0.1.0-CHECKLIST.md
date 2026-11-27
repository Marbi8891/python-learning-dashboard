# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 14:45 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta audit snapshot:** `715c8c7e0fa42557ca470d26d8a5da0ef4fe0650` (**83 ahead / 0 behind main**; doc-only audit commit after CI target `2f16751`)  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta definir alcance, validar CI sobre el SHA candidato exacto y completar smoke test manual, responsive y accesibilidad.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`. No pendiente.
- [ ] **#223 Academy:** draft; head `9d674df`, **17 ahead / 67 behind** Beta (merge base `5182b1ce`). CI #45890668077 y Deployment Check #45890668052 passed en el head actual; no hay approvals. Se solapa con #229 en HTML, router, precache e i18n. Demo local/sintética; no usar datos reales. Faltan aislamiento multi-tenant, autenticación institucional, persistencia backend y enforcement de permisos. Mantener draft, actualizar sobre Beta y revisar conflictos antes de integración.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 35 behind** Beta (merge base `c31244a`). CI #45934058607 falla E2E (**286 pass / 1 fail**) tras reload: `#paths-view` queda vacío; esperaba “Mis Paths”. Revisé log y artifact #15178416458 en esta pasada. El fixture del head `88b9434` ya limpia localStorage solo una vez por tab con un marcador en sessionStorage, pero este run sigue fallando; causa de render/routing aún no aislada. Backend, cursos y WebKit pasaron; Deployment Check #45934058622 passed. Dos reviews COMMENTED, sin approval. Reutiliza progreso existente, sin store/XP paralelo. No integrar hasta corregir, actualizar sobre Beta y repetir CI.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, **16 ahead / 0 behind**. CI #45851158102 falla en tests unitarios (**571 pass / 1 fail**) en `tests/unit/ai-academy-routing.test.mjs`: espera loader de AI Academy ausente de main. Backend, cursos y WebKit passed; E2E se omitió. Deployment Check #45851158126 passed. Es UI de planificación; no ejecuta Docker, escaneos ni métricas reales. Decidir alcance y resolver baseline/test antes de integrarlo.
- [x] PR obsoletas **#207, #209, #101, #193, #203**: cerradas sin merge.

## CI y main
- [x] CI **#46002488588 (run #678)** passed en SHA exacto `2f16751`: Backend, Cursos, E2E y WebKit. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46002488588. El commit documental `715c8c7` posterior no tiene CI push verificable con el conector disponible.
- [x] Main sigue en `be801c5`. CI monitor #45991656306 passed; **no es una suite completa**.
- [ ] Los checks de #223/#229/#227 no validan una integración actualizada sobre Beta.
- [ ] CI de integración tras cualquier portado/rebase, en el SHA exacto antes de merge.

## Backlog de PR abiertas
GitHub devuelve **27 PR abiertas**. Checks consultados sobre sus heads:
- **#205 Tutor IA docs:** E2E failed; backend, cursos, WebKit y deployment passed.
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
- [ ] Reducir privilegios: `pages: write` e `id-token: write` están a nivel workflow, por lo que también los recibe `build`; moverlos al job `deploy`.
- [ ] Revisar findings actuales de dependencias, secretos, configuración y privacidad del candidato.
- [ ] Smoke test de Pages, responsive y accesibilidad manual.
- [ ] Confirmar demo con datos sintéticos, sin progreso personal.

## Ramas y protección
- Inventario paginado: **106 ramas (100 + 6)**; todas devuelven `protected:false`.
- Rulesets: **[]**. Endpoint detallado de branch protection devuelve 403 a la integración; no se pudo inspeccionar la configuración.
- `beta/programming-path-rebased`: **0 ahead / 52 behind** Beta; no tiene commits únicos, candidata redundante. No borrada.
- Comparaciones actuales contra Beta:
  - `beta/academy-institutional-port`: 11/69
  - `beta/academy-institutional-rebased`: 17/65
  - `beta/ai-academy-port`: 16/75
  - `beta/hardening-rebased`: 19/72
  - `beta/port-hardening`: 22/76
  - `beta/port-pld003`: 14/76
  - `beta/programming-path-port`: 18/69
  - `beta/programming-path-rebased`: 0/52
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
- 2026-11-27 14:45: Beta audit snapshot `715c8c7`; CI #46002488588 (run #678) passed en el código SHA `2f16751`. El commit `715c8c7` es documental y su CI push no se pudo verificar. Main `be801c5` intacta; monitor #45991656306 passed.
- Checklist consolidado con cifras de divergencia actuales y checks revalidados. No se repiten comentarios; se refrescan las descripciones existentes de las PR candidatas.
- No merges adicionales, branch deletions, force-pushes, tags, releases ni deployments.
