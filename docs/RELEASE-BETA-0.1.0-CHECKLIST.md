# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 11:16 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee` (sin cambios)  
**Beta antes de esta actualización:** `9d55399f243bfd22cbbcd74c5d2077616690c5c4` (**79 ahead / 0 behind main**)  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta decidir el alcance, validar CI sobre el SHA candidato exacto y completar smoke test manual y accesibilidad.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] **#223 Academy:** draft; head `9d674df`, **17 ahead / 63 behind** Beta `9d55399` (merge base `5182b1ce`). CI #45890668077 y Deployment Check #45890668052 pasaron en su head, no en una integración actualizada. Sin reviews. Solapa con #229 en HTML, router, precache e i18n. Demo local sintética; sin aislamiento multi-tenant, auth institucional, persistencia backend ni permisos reales.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 31 behind** Beta `9d55399` (merge base `c31244a`). CI #45934058607 (attempt 4) falla E2E: **286 pasan, 1 falla** en `e2e/learning-paths.spec.js:39`. Tras reload, `#paths-view` queda vacío; se espera “Mis Paths”. En esta pasada descargué e inspeccioné el artifact #15178416458; el estado vacío se confirma, pero la causa no. Backend, cursos y WebKit pasaron; Deployment Check #45934058622 pasó. Dos reviews COMMENTED, sin aprobación. Mantener draft hasta diagnosticar, corregir, actualizar contra Beta y validar CI.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, **16 ahead / 0 behind**. CI #45851158102 falla en tests unitarios: **571/572 pasan**; falla `AI Academy is wired into app routing and view registry` (`tests/unit/ai-academy-routing.test.mjs:8`) por loader/registro ausente en main. Backend, cursos y WebKit pasaron; E2E se omitió. Deployment Check #45851158126 pasó. Sin reviews. UI de planificación; no ejecuta Docker ni escaneos. Decidir alcance antes de integrar.
- [x] PR obsoletas **#207, #209, #101, #193 y #203**: cerradas sin merge.

## CI y main
- [x] CI **#45971319534** pasó los cuatro jobs sobre Beta exacta `9d55399`: backend, cursos, E2E y WebKit. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45971319534
- [ ] Este checklist crea un nuevo commit; comprobar CI en el SHA nuevo antes de publicar.
- [ ] Main `be801c5` intacta. Último CI monitor #45972604250 passed, pero no es suite completa. Último fallo completo conocido: routing de AI Academy (569/570).
- [ ] Los checks de #223/#229/#227 no validan la integración sobre Beta actual; actualizar y rerun antes de merge.

## PR abiertas fuera de candidatas
GitHub devuelve **27 PR abiertas**. Runs de los heads consultados:
- **#205, #201:** CI failed; Deployment check passed.
- **#199, #196:** CI y Deployment check failed.
- **#195:** CI failed; Deployment check passed.
- **#185:** CI más reciente failed; Deployment check passed. Hay un CI anterior green, no es el head actual.
- Dependabot **#128:** CI failed; Deployment check passed.
- Dependabot **#127, #126, #129–#133:** CI y Deployment check passed.
No se revisaron los logs de todos estos fallos en esta pasada; los checks corresponden a sus heads.

## Seguridad y calidad
- [x] Workflow CI revisado: permisos `contents: read`, checkout con `persist-credentials: false`, `pip-audit`, `npm audit --audit-level=high`, Ruff, cobertura backend 100 % y pruebas PostgreSQL de migraciones, concurrencia y copias.
- [x] Pages workflow separado; permisos `contents: read`, `pages: write`, `id-token: write`.
- [ ] Revisar findings actuales de dependencias, secretos, configuración y privacidad del candidato.
- [ ] Accesibilidad y responsive manuales; smoke test de Pages.
- [ ] Confirmar demo con datos sintéticos, sin cuentas/progreso real.

## Ramas y protección
- Inventario paginado: **106 ramas** (100 + 6).
- Main y Beta: `protected:false`; rulesets **[]**, verificado por API en esta pasada.
- `beta/programming-path-rebased`: **0 ahead / 50 behind** Beta; sin commits únicos, candidata redundante. No borrada: no hay acción de delete branch disponible.
- Comparaciones de ramas beta-port contra `9d55399`:
  - `beta/academy-institutional-port`: 11/67
  - `beta/academy-institutional-rebased`: 17/63
  - `beta/ai-academy-port`: 16/73
  - `beta/hardening-rebased`: 19/70
  - `beta/port-hardening`: 22/74
  - `beta/port-pld003`: 14/74
  - `beta/programming-path-port`: 18/67
  - `beta/programming-path-rebased`: 0/50
Conservar ramas divergentes hasta revisar commits únicos.

## Tags y Release
- [x] `v1.0.0` anotado, sin firma; último dato verificado: apunta a `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No mover ni reutilizar.
- [x] GitHub Releases: **[]**, revalidado en esta pasada.
- [ ] Elegir tag nuevo sobre el commit candidato validado y publicar Release con alcance, límites y demo.

## Presentación
- [ ] README, instrucciones y CHANGELOG alineados con el alcance final.
- [ ] Capturas sin datos personales; ES/EN, aviso legal y privacidad revisados.
- [ ] Demo walkthrough sin tocar progreso real.
- [ ] Smoke test manual de Pages, responsive y accesibilidad.
- [ ] Notas de versión y limitaciones.

## Limitaciones a declarar
Academy es demo local sintética, no servicio multi-tenant. Learning Paths reutiliza progreso existente, sin XP/store paralelo. Pentest Lab es planificación, no scanner ni laboratorio operativo.

## Registro breve
- 10:05: Beta `80f21c5`; CI #45966922239 passed.
- 11:16: Beta `9d55399`; CI #45971319534 passed en SHA exacto; main sigue en `be801c5`.
- Artifact E2E de #229 descargado de nuevo; el DOM vacío tras reload se confirma, causa sin confirmar. Logs de #227 muestran el test de routing de AI Academy como fallo.
- No se realizaron merges adicionales, branch deletions, force-pushes, tags, releases ni deployments. Main sin cambios.
