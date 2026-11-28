# PLD Beta 0.1.0 — checklist de lanzamiento

**Auditoría:** 2026-11-28 08:06 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta:** `dee08c96ec3da7b79fa190612afc3b3116f1175b` — 85 commits ahead / 0 behind main. CI #681 pasó 4/4 en este SHA.  
**PR #237:** head `1fc3a508b6d9922b1d5b8211e39c586721e19b22`, 18 ahead / 0 behind Beta; CI #698 pasó 4/4 y Deployment Check #352 pasó 3/3 en este SHA. Draft, sin reviews ni aprobaciones. No se desplegó Pages.  
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
- [x] **PR #237 CI #698:** 4/4 passed sobre `1fc3a508`. (Backend, Cursos, E2E, WebKit). [Run](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46118164927)
- [x] **PR #237 Deployment Check #352:** 3/3 passed en `1fc3a508` (workflows/configuración, artefacto Pages, Docker health). [Run](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46118164917)
- [x] Los jobs de #237 fueron inspeccionados. Backend: Ruff, formato, pip-audit, cobertura SQLite 100 %, migraciones PostgreSQL, rate limits/concurrencia, versionado y backup/restore. E2E: tests unitarios frontend, npm audit high y Playwright Chromium. WebKit smoke pasó. Cursos pasó sus validaciones.
- [x] **Main CI monitor #429:** éxito en `be801c5`; solo ejecutó el job `report`, no es suite completa. [Run](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46099434032)
- [ ] Checks de #223/#229/#227 no corresponden a una integración actualizada sobre Beta.

## PR abiertas y ramas

- GitHub devuelve **28 PR abiertas**. Se revalidaron #237, #223, #224, #229, #227 y las cinco PR obsoletas; el resto del backlog no se auditó individualmente.
- **107 ramas** (100 + 7, paginación completa). La búsqueda de ramas usada en esta pasada solo devuelve nombres y no expone el estado de protección.
- Última comprobación directa a las 07:45 CET: `main` y Beta `protected:false`, rulesets vacíos y checks obligatorios desactivados; el endpoint detallado de protección devolvió 403. No revalidado ahora. Configurar desde GitHub Settings.
- `beta/programming-path-rebased` comparada ahora: 0 commits ahead / 56 behind Beta; candidata redundante, no borrada. Las demás ramas de portado no se recalcularon.
- No se cerraron ni fusionaron otras PR, ni se eliminaron ramas.

## Seguridad y cambios de Pages

- [x] #237 cambia solo `.github/workflows/pages.yml` y este checklist.
- [x] Build con `contents: read`; deploy con `pages: write` y `id-token: write`. Checkout usa `persist-credentials: false`.
- [x] Build y deploy separados. Checks validan configuración y artefacto, no una publicación real.
- [ ] Revisar findings, secretos, privacidad y configuración en el SHA candidato final.
- [ ] Smoke test manual, responsive y accesibilidad.

## Tags y Release

- [x] Última comprobación registrada a las 06:35: GitHub Releases vacía. No revalidable en esta pasada (el conector no expone el endpoint).
- [x] Última comprobación registrada a las 06:35: `v1.0.0` anotado, sin firma (`verified:false`, reason `unsigned`); tag object `603274fb5a908260bea927d48de647883e2f948f`, target `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No revalidado en esta pasada; no mover ni reutilizar.
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

- **2026-11-28 06:35 CET:** revalidado `main` `be801c5` y Beta `dee08c96` (85/0); CI Beta #681 pasa 4/4. PR #237 head `697e75fd` pasa CI #696 (4/4) y Deployment Check #350 (3/3); jobs revisados. #237 sigue Draft, sin reviews, y no hubo despliegue Pages. Se confirmaron 28 PR abiertas y 107 ramas. Branch endpoints de `main` y Beta muestran `protected:false`; rulesets `[]`. Releases `[]`; tag `v1.0.0` sigue anotado, sin firma. El checklist de la rama Beta sigue en snapshot antiguo (84 commits ahead/27 PR). Este refresh documental en la rama de auditoría inicia sus propios checks, pendientes de verificación. Main y Beta no se modifican.
- **2026-11-28 03:33 CET:** head #237 `5fe412f`, CI #694 4/4 y Deployment Check #348 3/3; el refresh anterior dejó checks pendientes para su nuevo head.
- No se han hecho merges, branch deletions, force-pushes, tags, releases ni deployments en esta auditoría.

- **2026-11-28 08:06 CET:** revalidado main `be801c5` y Beta `dee08c96` (85 ahead / 0 behind); Beta CI #681 pasó 4/4 en el SHA exacto. PR #237 head `1fc3a508`, CI #698 pasó 4/4 y Deployment Check #352 pasó 3/3 en ese SHA; jobs inspeccionados. PR #237 sigue Draft, sin reviews y no hubo Pages deployment. PR #223 CI #648/DC #331 passed en `9d674df`; #229 CI #664 failure (286/1) y DC #335 passed en `88b9434`; #227 CI #623 failure (571/572) y DC #310 passed en `67ca9b2`. #224 merged; #207/#209/#101/#193/#203 cerradas sin merge. Search paginado de ramas confirma 107 (100 + 7); la herramienta de ramas no expone protección en esta pasada, por lo que la última evidencia directa de 07:45 (`protected:false`, rulesets vacíos) queda como histórica, no revalidada. Release/tag tampoco revalidable hoy; última evidencia 06:35. Checklist refrescado en esta rama de auditoría; este nuevo commit documental inicia sus propios checks y no se atribuyen resultados del SHA anterior. Main y Beta sin cambios.
