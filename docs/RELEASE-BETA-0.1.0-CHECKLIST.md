# PLD Beta 0.1.0 — checklist de lanzamiento

**Auditoría:** 2026-11-27 23:54 CET
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta:** `dee08c96ec3da7b79fa190612afc3b3116f1175b` — 85 ahead / 0 behind main; CI #681 pasó en este SHA.  
**PR #237 (head before this checklist refresh):** `08fb83a84573b737b98ef11f412052392907cdd0` — 11 ahead / 0 behind Beta; CI run [46075563491](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46075563491) passed 4/4 and Deployment Check [46075563479](https://github.com/Marbi8891/python-learning-dashboard/actions/runs/46075563479) passed 3/3 on this exact SHA. Draft, no reviews; no merge or production deployment. The checklist refresh creates a new head; its checks must be verified separately.
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No publicar Beta ni crear tag hasta validar el SHA candidato exacto, completar smoke test manual, responsive y accesibilidad, y decidir el alcance de las funcionalidades incluidas. CI y Deployment Check de #237 no realizan un despliegue real de Pages.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`. No pendiente.
- [ ] **#223 Academy:** Draft; 17 ahead / 69 behind Beta. CI #648 (#45890668077) pasó 4/4 y Deployment Check #331 (#45890668052) pasó 3/3 en el head `9d674df` (estados verificados). Se solapa con #229 en HTML, router, precache e i18n. Demo local con datos sintéticos; sin aislamiento multi-tenant, autenticación institucional, persistencia backend ni enforcement de permisos. Actualizar sobre Beta, resolver conflictos y revisar conjuntamente con #229.
- [ ] **#229 Learning Paths:** Draft; 32 ahead / 37 behind Beta. CI #664 (#45934058607) falla (286 E2E pass / 1 fail tras reload); `#paths-view` queda vacío y no muestra “Mis Paths”. Deployment Check #335 (#45934058622) pasó 3/3. Dos reviews COMMENTED, sin approval. Reutiliza progreso existente; no crea store/XP paralelo. Causa raíz del reload no aislada; no integrar hasta corregir y validar el head actualizado.
- [ ] **#227 Pentest Lab:** Draft contra `main`; 16 ahead / 0 behind main y 16 ahead / 85 behind Beta. CI #623 (#45851158102) falla el gate unitario (571/572); el test de AI Academy routing espera un loader ausente en main. E2E no se ejecutó tras el gate. Deployment Check #310 (#45851158126) pasó 3/3. Es una UI de planificación; no ejecuta Docker, escaneos ni métricas reales. Decidir alcance y corregir el baseline/test antes de integrar.
- [x] PR obsoletas **#207, #209, #101, #193 y #203**: cerradas sin merge.
- [x] #224 merged.

## CI y cambios
- [x] CI #681 (#46014073048) pasó en el SHA exacto de Beta `dee08c96`: Backend, Cursos, E2E y WebKit.
- [x] CI #689 (#46062856041) pasó 4/4 en el head previo de #237 `f6ad6363` (Backend, Cursos, E2E, WebKit).
- [x] Deployment Check #343 (#46062855991) pasó 3/3 en el head previo `f6ad6363` (workflows, Docker health check y artefacto Pages).
- [x] CI #687/#341 también pasaron en el head previo `301e191c`; son resultados históricos, no el head actual.
- [x] #237 limita `contents: read` al build y `pages: write`/`id-token: write` al job deploy; checkout usa `persist-credentials: false`. No está integrado en Beta.
- [x] CI #690 (#46072044202) y Deployment Check #344 (#46072044260) pasaron en el head actual `db1a2066`; jobs verificados individualmente. No es un despliegue de Pages.
- [ ] Los checks de #223/#229/#227 no validan integración actualizada sobre Beta.
- [ ] Main: el último monitor conocido pasó, pero es un job `report`, no una suite completa; no revalidado en esta pasada.


## Backlog
GitHub devuelve **28 PR abiertas**. Solo #237, #223, #229 y #227 se inspeccionaron en esta pasada; el resto no se revalidó individualmente.
- #205 Tutor IA docs, #201 Roadmaps, #199 AI Academy, #196 DAW Coach móvil, #195 DAW Exam Coach, #185 Python runtime isolation y Dependabot #128 axe-core: última auditoría registró fallos; confirmar checks actuales antes de actuar.
- Dependabot #126–#127 y #129–#133: último registro indicaba checks verdes; no revalidados ahora.
No se cerraron ni integraron otras PR.

## Ramas y protección
- Inventario paginado: **107 ramas (100 + 7)**; la API de branches marca `protected:false` en las 107, incluidas `main` y Beta.
- Rulesets: lista vacía (verificada en esta pasada).
- La API detallada de branch protection devuelve 403; no se pudo inspeccionar configuración adicional. La evidencia disponible indica que `main` y Beta no tienen protección activa.
- `beta/programming-path-rebased`: 0 ahead / 56 behind Beta; sin commits únicos por delante, posible redundancia. No borrada.
- Comparaciones verificadas contra Beta:
  - `beta/academy-institutional-port`: 11/73
  - `beta/academy-institutional-rebased`: 17/69
  - `beta/ai-academy-port`: 16/79
  - `beta/hardening-rebased`: 19/76
  - `beta/port-hardening`: 22/80
  - `beta/port-pld003`: 14/80
  - `beta/programming-path-port`: 18/73
  - `beta/programming-path-rebased`: 0/56
Conservar ramas divergentes hasta revisar commits únicos.


## Seguridad y calidad
- [x] CI Beta #681 incluye Ruff, pip-audit, npm audit (nivel high), cobertura backend 100 % y pruebas PostgreSQL de migraciones, rate-limit, concurrencia, versionado y backup/restore.
- [x] Pages build/deploy separados; checkout sin persistir credenciales.
- [x] Hardening de permisos propuesto en #237; CI #690 y Deployment Check #344 pasaron en el head actual `db1a2066`.
- [ ] Revisión de findings de dependencias, secretos, configuración y privacidad sobre el candidato final.
- [ ] Smoke test Pages, responsive y accesibilidad manual.
- [ ] Verificar que la demo usa solo datos sintéticos.
## Tags y Release
- [x] Tag `v1.0.0` revalidado: tag anotado, sin firma (`verified:false`, reason `unsigned`), target `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No mover ni reutilizar.
- [x] GitHub Releases: `[]`, confirmado en esta pasada.
- [ ] Elegir un tag nuevo solo sobre el SHA candidato validado y publicar Release con alcance, limitaciones y demo.


## Presentación
- [ ] README, instrucciones y CHANGELOG ajustados al alcance de Beta.
- [ ] Capturas sin datos personales; ES/EN, privacidad y avisos revisados.
- [ ] Ensayar walkthrough.
- [ ] Smoke test, responsive y accesibilidad.
- [ ] Notas de versión y limitaciones.

## Limitaciones a declarar
Academy es demo local sintética, no servicio multi-tenant. Learning Paths reutiliza progreso existente. Pentest Lab es una interfaz de planificación, no un scanner ni un laboratorio operativo.


## Registro
- 2026-11-27 15:54: Base Beta `dee08c96` (85 ahead / 0 behind main). CI #681 passed exact SHA; main `be801c5` intact. Monitor passed (not full suite). PR #223: 17/69; #229: 32/37, 286/1 E2E; #227: 16/0 main, 571/1 unit gate. Inventory 107 branches and 28 open PRs. PR #237 had CI #683 passed on prior merge SHA, #684 in progress on `8cbd010`, Deployment Check #338 passed. Branch protection not verified.
- 2026-11-27 19:27 CET: PR #237 head `21a09dc` (5/0 contra Beta), CI #685 attempt 2 passed (Backend, Cursos, E2E, WebKit), Deployment Check #339 passed. First attempt failed WebKit recovery-link test; retry passed.
- 2026-11-27 20:14 CET: PR #237 head `8bbcf857` (6/0). CI #686 passed exact SHA (4/4); Deployment Check #340 passed exact SHA (3/3). Checklist actualizado en esta rama. PR sigue Draft, sin review; no merge ni deploy. Search devolvió 27 PR abiertas, inventario 107 ramas (100+7, última página vacía), rulesets vacíos; branch protection 403. Tag `v1.0.0` confirmado y Releases vacías.
- No merges adicionales, branch deletions, force-pushes, tags, releases ni deployments.

- 2026-11-27 21:15 CET: se confirmó CI #687 (4/4) y Deployment Check #341 (3/3) en head #237 `301e191c`. PR abierta, Draft y sin reviews. Se recalcularon comparaciones de ramas, se confirmó 27 PR abiertas y 107 ramas; PR obsoletas #207/#209/#101/#193/#203 cerradas sin merge y #224 merged. Main intacta. Esta actualización documental crea un nuevo head; los checks de ese nuevo head quedan pendientes de verificación.

- Corrección 21:15 CET: la búsqueda paginada actual devuelve 28 PR abiertas (no 27); el total anterior correspondía a una consulta incompleta/estado anterior.


- 2026-11-27 22:40 CET: PR #237 head `f6ad6363` verificado; CI #689 y Deployment Check #343 pasaron 4/4 y 3/3 en ese SHA. La PR sigue Draft, sin reviews. Checklist actualizado y crea un nuevo commit; sus checks aún no se verifican. API de branches devuelve 107/107 `protected:false`; rulesets `[]`. Releases vacías y tag `v1.0.0` confirmado anotado sin firma. Se revalidaron estados de #223 (CI #648/DC #331 verde), #229 (CI #664 fallida 286/1; DC #335 verde) y #227 (CI #623 fallida 571/572; DC #310 verde). No hubo merge, borrado ni despliegue.

- 2026-11-27 23:14 CET: #237 head `db1a2066` (10 ahead / 0 behind Beta). CI #690 pasó 4/4 y Deployment Check #344 pasó 3/3; jobs inspeccionados. PR sigue Draft, sin reviews. Se revalidaron #223 (CI #648/DC #331 verdes), #229 (CI #664 falla E2E; DC #335 verde) y #227 (CI #623 falla gate unitario; DC #310 verde). Branch inventory: 107 (100 + 7 + página vacía); comparaciones de ocho ramas portadas recalculadas. No cambios en main/Beta, merges, borrados, tags, releases ni deployments.


- 2026-11-27 23:54 CET: refreshed the checklist based on verified PR head `08fb83a` (CI 4/4, Deployment Check 3/3); this documentation commit is branch-only and its own checks are pending. Branch inventory: 107, all API-marked unprotected; `main` and Beta `protected:false`, rulesets empty. Open PR count 28. Obsolete #207/#209/#101/#193/#203 closed unmerged; #224 merged. #223 current head checks green (historical head), #229 CI fails 286/1 E2E, #227 CI fails 571/572 unit gate. Beta checklist remains at the 15:11 snapshot; no merge, branch deletion, tag, release or deployment.
