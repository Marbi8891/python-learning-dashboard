# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 10:05 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta antes de esta actualización:** `80f21c5d3f23da06286d8ba29c48670e97685a36` (**78 ahead / 0 behind main**)  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta aprobar el alcance, validar CI en el commit candidato exacto y completar smoke test manual y accesibilidad.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] **#223 Academy:** draft; head `9d674df`, **17 ahead / 62 behind** Beta `80f21c5` (merge base `5182b1ce`). CI #45890668077 y Deployment Check #45890668052 pasaron en el head, no en una integración actualizada. Sin reviews. Solapa con #229 en HTML, router, precache e i18n. Demo local con datos sintéticos; sin multi-tenant, auth institucional, persistencia backend ni permisos reales.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 30 behind** Beta `80f21c5` (merge base `c31244a`). CI #45934058607, attempt 4, falla E2E: **286 pasan, 1 falla** en `e2e/learning-paths.spec.js:39`. Tras reload, `#paths-view` queda vacío; la aserción espera “Mis Paths”. Logs/artifact #15178416458 inspeccionados; causa no confirmada. Backend, cursos y WebKit passed; Deployment Check #45934058622 passed. Dos reviews COMMENTED, ninguna aprobación. No integrar hasta diagnóstico, corrección, actualización contra Beta y CI verde.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, **16 ahead / 0 behind**. CI #45851158102 falla en el job `e2e`, en el paso de tests unitarios: falla `AI Academy is wired into app routing and view registry` (`tests/unit/ai-academy-routing.test.mjs:8`), porque espera loader/registro ausente en main. Backend, cursos y WebKit passed; Deployment Check #45851158126 passed. Sin reviews. UI-only; no ejecuta Docker ni escaneos. Decidir alcance y resolver baseline antes de integrar.
- [x] PR obsoletas **#207, #209, #101, #193 y #203**: cerradas sin merge.

## CI y main
- [x] CI push **#45966922239** pasó los cuatro jobs sobre el head exacto de Beta `80f21c5`: backend, cursos, E2E y WebKit. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45966922239
- [ ] Este checklist genera un commit nuevo; validar CI en el nuevo SHA antes de publicar.
- [ ] Main `be801c5` permanece intacta. En esta consulta sus check-runs son CI monitors/report, no una suite completa. Último fallo completo conocido: test de routing AI Academy (569/570).
- [ ] CI de #223/#229/#227 no valida integración contra Beta actual; actualizar branches y correr checks antes de merge.

## PR abiertas fuera de candidatas
GitHub devuelve **27 PR abiertas**. Checks consultados en los heads actuales:
- **#205:** E2E failed; resto de checks consultados green.
- **#201:** E2E failed; resto green.
- **#199:** Pages, E2E y WebKit failed.
- **#196:** Pages, E2E, backend y WebKit failed.
- **#195:** E2E failed; resto green.
- **#185:** hay runs E2E failed y success asociados; confirmar cuál es el último antes de considerar integración.
- Dependabot **#128:** E2E y WebKit failed.
- Dependabot **#127, #126, #129–#133:** todos los checks consultados green en sus heads actuales.
Los checks son de sus ramas y no sustituyen una validación contra main actualizado.

## Seguridad y calidad
- [x] Workflow CI revisado: permisos `contents: read`, checkout con `persist-credentials: false`, `pip-audit`, `npm audit --audit-level=high`, Ruff, cobertura backend 100 % y tests PostgreSQL/concurrencia/migraciones/copias.
- [x] Pages workflow separado: build y deploy en jobs distintos; permisos `contents: read`, `pages: write`, `id-token: write`.
- [ ] Revisar findings actuales de dependencias, secretos, defaults inseguros y privacidad del candidato.
- [ ] Accesibilidad y responsive manuales.
- [ ] Confirmar demo sin cuentas/progreso real.

## Ramas y protección
- Inventario paginado: **106 ramas** (100 página 1, 6 página 2).
- API de ramas devuelve `protected:false` para las ramas listadas; rulesets **[]**. Endpoint de protección detallada de main devuelve 403 a la integración.
- `beta/programming-path-rebased`: **0 ahead / 49 behind** Beta; no tiene commits únicos, candidata redundante. No borrada: no hay acción de delete branch disponible.
- Otras ramas beta-port respecto a Beta:
  - `beta/academy-institutional-port`: 11/66
  - `beta/academy-institutional-rebased`: 17/62
  - `beta/ai-academy-port`: 16/72
  - `beta/hardening-rebased`: 19/69
  - `beta/port-hardening`: 22/73
  - `beta/port-pld003`: 14/73
  - `beta/programming-path-port`: 18/66
  - `beta/programming-path-rebased`: 0/49
Conservar ramas divergentes hasta revisar commits únicos.

## Tags y Release
- [x] `v1.0.0` anotado, **sin firma**, apunta a `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No mover ni reutilizar.
- [x] API de Releases devuelve **[]**.
- [ ] Elegir tag nuevo sobre commit candidato validado y publicar Release con alcance, límites y demo.

## Presentación
- [ ] README, instrucciones y CHANGELOG alineados con alcance final.
- [ ] Capturas sin datos personales.
- [ ] ES/EN, aviso legal y privacidad revisados.
- [ ] Demo walkthrough sin tocar progreso real.
- [ ] Smoke test manual de Pages.
- [ ] Notas de versión y limitaciones.

## Limitaciones a declarar
Academy es demo local sintética, no servicio institucional multi-tenant. Learning Paths lee progreso existente; no debe duplicar XP/progreso. Pentest Lab es planificación, no scanner/laboratorio operativo.

## Registro
- 2026-11-27 10:05: Beta `80f21c5`; 78 ahead / 0 behind main; CI #45966922239 pasó todos los jobs sobre ese SHA.
- PR #223: 17/62; PR #229: 32/30; PR #227: 16/0 frente a main.
- PR #229 falla la aserción tras reload; logs/artifact inspeccionados, causa sin confirmar. #227 falla en test de routing AI Academy en main.
- PR obsoletas #207, #209, #101, #193 y #203 cerradas sin merge.
- 27 PR abiertas; estados de checks de PR y Dependabot reconsultados.
- 106 ramas; main y Beta listadas sin protección; rulesets vacíos.
- No se realizaron merges, branch deletions, force-pushes, tags, releases ni deployments. Main sin cambios.
