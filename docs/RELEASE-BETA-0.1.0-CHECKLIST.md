# PLD Beta 0.1.0 — checklist de lanzamiento

**Auditoría:** 2026-11-28 05:37 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta:** `dee08c96ec3da7b79fa190612afc3b3116f1175b` — 85 commits ahead / 0 behind main. CI #681 pasó 4/4 en este SHA.  
**PR #237:** head `1bed20e7c8c2ac698c7af67a603d118d1376f55a`, 15 ahead / 0 behind Beta; CI #695 pasó 4/4 y Deployment Check #349 pasó 3/3 en este SHA. Draft, sin reviews ni aprobaciones. No se desplegó Pages.  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación

No crear tag ni publicar Beta hasta:
- validar CI en el SHA candidato exacto;
- decidir alcance de las funciones candidatas;
- completar smoke test de Pages, responsive y accesibilidad;
- revisar privacidad, datos de demo, README, CHANGELOG y notas de versión.

Los checks de CI y Deployment Check no realizan un despliegue real de Pages.

## PR candidatas

- [x] **#224 Programming Path:** fusionada en Beta. Merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`. El progreso y documentos existentes se reutilizan; no se crea un store paralelo.
- [ ] **#223 Academy:** Draft; 17 ahead / 69 behind Beta (merge base `5182b1ce`). CI #648 y Deployment Check #331 pasaron 4/4 y 3/3 en el head `9d674df`. Sin approvals. Demo local con datos sintéticos; no incluye autenticación institucional, aislamiento multi-tenant, persistencia backend ni enforcement real de permisos. Se solapa con #229 en HTML, router, precache e i18n. Actualizar sobre Beta y resolver conflictos antes de considerar integración.
- [ ] **#229 Learning Paths:** Draft; 32 ahead / 37 behind Beta (merge base `c31244a`). CI #664 falla: 286 E2E pasan y 1 falla al recargar; `#paths-view` queda vacío y no muestra “Mis Paths”. Deployment Check #335 pasó 3/3. Dos reviews COMMENTED, sin aprobación. Lee el progreso existente, sin store/XP paralelo. Causa raíz pendiente; no integrar hasta corregir, actualizar sobre Beta y repetir CI.
- [ ] **#227 Pentest Lab:** Draft contra main; 16 ahead / 0 behind main, 16 ahead / 85 behind Beta. CI #623 falla 571/572 tests unitarios: el test de routing de AI Academy espera un loader ausente de main; Playwright no se ejecutó. Deployment Check #310 pasó 3/3. Es una UI de planificación, no ejecuta Docker ni escaneos. Decidir alcance y corregir el test/base antes de integrarlo.
- [x] PR obsoletas #207, #209, #101, #193 y #203: cerradas sin merge.

## CI verificada

- [x] **Beta CI #681:** 4/4 passed sobre `dee08c96` (Backend, Cursos, E2E, WebKit). [Run](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46014073048)
- [x] **PR #237 CI #695:** 4/4 passed sobre `1bed20e7` (Backend, Cursos, E2E, WebKit). [Run](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46098793354)
- [x] **PR #237 Deployment Check #349:** 3/3 passed en el mismo SHA (workflows/configuración, artefacto Pages, Docker health). [Run](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46098793370)
- [x] Los jobs de #237 fueron inspeccionados. Backend: Ruff, formato, pip-audit, cobertura SQLite 100 %, migraciones PostgreSQL, rate limits/concurrencia, versionado y backup/restore. E2E: tests unitarios frontend, npm audit high y Playwright Chromium. WebKit smoke pasó. Cursos pasó sus validaciones.
- [x] **Main CI monitor #429:** éxito en `be801c5`; solo ejecutó el job `report`, no es suite completa. [Run](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46099434032)
- [ ] Checks de #223/#229/#227 no corresponden a una integración actualizada sobre Beta.

## PR abiertas y ramas

- GitHub devuelve **28 PR abiertas**. En esta pasada se revalidaron #237, #223, #224, #229, #227 y las cinco PR obsoletas; el resto del backlog no se auditó individualmente.
- **107 ramas** (100 en página 1 + 7 en página 2); la API marca `protected:false` en todas, incluidas main y Beta.
- Rulesets: lista vacía. Endpoint detallado de branch protection devuelve 403 a esta integración. Evidencia disponible: main y Beta sin protección activa. Configurar desde GitHub Settings.
- `beta/programming-path-rebased` fue comparada a las 03:33: 0 commits ahead / 56 behind Beta; candidata redundante, no borrada. Las otras ramas portadas no se recalcularon en esta pasada.
- No se cerraron ni fusionaron otras PR, ni se eliminaron ramas.

## Seguridad y cambios de Pages

- [x] #237 cambia solo `.github/workflows/pages.yml` y este checklist.
- [x] Build con `contents: read`; deploy con `pages: write` y `id-token: write`. Checkout usa `persist-credentials: false`.
- [x] Build y deploy separados. Checks validan configuración y artefacto, no una publicación real.
- [ ] Revisar findings, secretos, privacidad y configuración en el SHA candidato final.
- [ ] Smoke test manual, responsive y accesibilidad.

## Tags y Release

- [x] GitHub Releases: lista vacía.
- [x] `v1.0.0` existe como tag anotado, sin firma (`verified:false`, reason `unsigned`). Tag object `603274fb5a908260bea927d48de647883e2f948f`, target `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No mover ni reutilizar.
- [ ] Crear un tag nuevo solo sobre el SHA candidato validado y publicar Release con alcance, limitaciones y demo.

## Presentación

- [ ] README, instrucciones y CHANGELOG alineados con el alcance final.
- [ ] Capturas sin datos personales; revisar ES/EN, privacidad y avisos.
- [ ] Ensayar walkthrough.
- [ ] Smoke test, responsive y accesibilidad.
- [ ] Notas de versión y limitaciones.

## Limitaciones que deben declararse

Academy es una demo local con datos sintéticos, no una plataforma institucional multi-tenant. Learning Paths reutiliza progreso existente. Pentest Lab es un panel de planificación, no un scanner ni un laboratorio operativo.

## Registro reciente

- **2026-11-28 05:37 CET:** revalidado main `be801c5`, Beta `dee08c96` (85/0), 28 PR abiertas y 107 ramas. CI #681 y #695 pasan 4/4; Deployment Check #349 pasa 3/3. Main monitor #429 pasa, pero solo es `report`. PR #237 sigue Draft, sin reviews; el checklist de la rama Beta sigue en snapshot del 27/11 15:11 y está desactualizado (84 commits ahead y 27 PR abiertas en su texto). Este refresh es solo en la rama de auditoría; no se modifica Beta ni main. Los checks del nuevo commit documental quedan pendientes.
- **2026-11-28 03:33 CET:** head #237 `5fe412f`, CI #694 4/4 y Deployment Check #348 3/3; el refresh anterior dejó checks pendientes para su nuevo head.
- No se han hecho merges, branch deletions, force-pushes, tags, releases ni deployments en esta auditoría.
