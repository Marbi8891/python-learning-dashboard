# PLD Beta 0.1.0 — checklist de lanzamiento

**Auditoría:** 2026-11-27 21:15 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta:** `dee08c96ec3da7b79fa190612afc3b3116f1175b` — 85 ahead / 0 behind main; CI #681 pasó en este SHA.  
**PR #237:** head `301e191c76d40afaa1e420d2a283b8de5813bab8` — 7 ahead / 0 behind Beta; CI #687 pasó (4/4 jobs) y Deployment Check #341 pasó (3/3) en este SHA. La PR sigue Draft, sin reviews ni approvals.  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No publicar Beta ni crear tag hasta validar el SHA candidato exacto, completar smoke test manual, responsive y accesibilidad, y decidir el alcance de las funcionalidades incluidas. CI y Deployment Check de #237 no realizan un despliegue real de Pages.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`. No pendiente.
- [ ] **#223 Academy:** Draft; 17 commits ahead / 69 behind Beta. Los checks verdes de su head son de una auditoría anterior y no se revalidaron ahora. Se solapa con #229 en HTML, router, precache e i18n. Demo local con datos sintéticos; sin aislamiento multi-tenant, autenticación institucional, persistencia backend ni enforcement de permisos. Actualizar sobre Beta, resolver conflictos y revisar conjuntamente con #229.
- [ ] **#229 Learning Paths:** Draft; 32 ahead / 37 behind Beta. Última CI conocida: 286 E2E pass / 1 fail tras reload; `#paths-view` queda vacío y no muestra “Mis Paths”. Deployment Check anterior pasó. Dos reviews COMMENTED, sin approval. Reutiliza progreso existente; no crea store/XP paralelo. Causa raíz del reload no aislada; no integrar hasta corregir y validar el head actualizado.
- [ ] **#227 Pentest Lab:** Draft contra `main`; 16 ahead / 0 behind main y 16 ahead / 85 behind Beta. Última CI conocida: 571/572 unit tests; falla el test de AI Academy routing por loader ausente en main. E2E no se ejecutó tras el gate unitario. Deployment Check anterior pasó. Es una UI de planificación; no ejecuta Docker, escaneos ni métricas reales. Decidir alcance y corregir el baseline/test antes de integrar.
- [x] PR obsoletas **#207, #209, #101, #193 y #203**: cerradas sin merge.
- [x] #224 merged.

## CI y cambios
- [x] CI #681 (#46014073048) pasó en el SHA exacto de Beta `dee08c96`: Backend, Cursos, E2E y WebKit.
- [x] CI #687 (#46055498436) pasó en el head de #237 `301e191c`: 4/4 jobs.
- [x] Deployment Check #341 (#46055498425) pasó en `301e191c`: 3/3 jobs (artefacto Pages, workflow/configuración y Docker health check).
- [x] #237 limita `contents: read` al build y `pages: write`/`id-token: write` al job deploy; checkout usa `persist-credentials: false`. No está integrado en Beta.
- [ ] La actualización documental que sigue a esta auditoría generará otro head/checks; no se considerarán verdes hasta que se puedan verificar.
- [ ] Los checks de #223/#229/#227 no validan integración actualizada sobre Beta.
- [ ] Main: último monitor conocido pasó, pero es un job `report`, no suite completa; no revalidado en esta pasada.

## Backlog
GitHub devuelve **27 PR abiertas**. Solo #237, #223, #229 y #227 se inspeccionaron en esta pasada; el resto no se revalidó individualmente.
- #205 Tutor IA docs, #201 Roadmaps, #199 AI Academy, #196 DAW Coach móvil, #195 DAW Exam Coach, #185 Python runtime isolation y Dependabot #128 axe-core: última auditoría registró fallos; confirmar checks actuales antes de actuar.
- Dependabot #126–#127 y #129–#133: último registro indicaba checks verdes; no revalidados ahora.
No se cerraron ni integraron otras PR.

## Ramas y protección
- Inventario paginado: **107 ramas (100 + 7)**.
- Rulesets: lista vacía en la API.
- Endpoint detallado de branch protection para main/Beta devuelve 403; no se puede confirmar protección efectiva.
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
- [x] Hardening de permisos propuesto en #237 y CI/Deployment Check verdes en head `301e191c`.
- [ ] Revisión de findings de dependencias, secretos, configuración y privacidad sobre el candidato final.
- [ ] Smoke test Pages, responsive y accesibilidad manual.
- [ ] Verificar que la demo usa solo datos sintéticos.

## Tags y Release
Último registro: tag `v1.0.0` anotado sin firma, target `fdf64098556f0e835e08ad5ce58c230a21b5f591`; GitHub Releases vacío. No se pudo revalidar en esta pasada porque los endpoints de tags/releases no están disponibles mediante el conector y el acceso web falló. No mover ni reutilizar el tag.

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
