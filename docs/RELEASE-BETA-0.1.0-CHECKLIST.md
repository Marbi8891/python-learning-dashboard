# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27, 07:43 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta:** `960086f65ee812d941b7c454a3f68f60ab134ec6` (75 commits ahead, 0 behind main)  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación

No crear tag ni publicar Release hasta que el alcance esté aprobado, CI pase sobre el commit exacto candidato y se complete la revisión manual de demo y accesibilidad.

## PR candidatas

- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] **#223 Academy:** draft; head `9d674df`, 17 ahead / 59 behind Beta (merge base `5182b1ce`). CI #45890668077 y Deployment Check #45890668052 passed en su head; sin reviews. Actualizar contra Beta, revisar conflictos y repetir checks. Demo localStorage con datos sintéticos; no tiene aislamiento multi-tenant, auth institucional, persistencia backend ni permisos reales.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, 32 ahead / 27 behind Beta (merge base `c31244a`). CI #45934058607 falló E2E en la persistencia tras reload: `#paths-view` queda vacío y no muestra “Mis Paths” (286 tests pasaron, 1 falló). Deployment Check #45934058622 passed. Reintento de jobs fallidos solicitado; attempt 4 está en curso: backend, cursos y WebKit passed; E2E sigue running. Solo reviews COMMENTED, sin aprobación. No integrar aún.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, 16 ahead / 0 behind. CI #45851158102 falló en `ai-academy-routing.test.mjs` por loader de AI Academy ausente en main; no es una prueba propia de Pentest Lab. Deployment Check #45851158126 passed; sin reviews. UI-only: no ejecuta Docker ni scans. Decidir alcance y corregir el bloqueo de baseline antes de integrar.
- [x] PR obsoletas #207, #209, #101, #193 y #203 cerradas sin merge.

## CI y estado de main

- [x] CI #45949035755 passed sobre **Beta exacta `960086f`**: backend, cursos, E2E y WebKit. Backend incluye Ruff, pip-audit, cobertura 100%, PostgreSQL y pruebas de concurrencia. E2E incluye unit tests y npm audit de vulnerabilidades altas. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45949035755
- [x] CI #45948792247 passed sobre `18406e9` (commit anterior).
- [ ] Main `be801c5` no ha cambiado. Las últimas ejecuciones consultadas son CI monitor y están verdes; no equivalen a suite completa. Último fallo completo conocido en la auditoría previa: routing de AI Academy (569/570). No se reejecutó la suite completa de main en esta pasada.
- [ ] La CI exacta de #223/#229/#227 no valida integración contra la Beta actual. Actualizar branches y correr checks antes de merge.

## Seguridad y calidad

- [x] Revisión previa de workflows: CI con `contents: read`, checkout `persist-credentials: false`, `pip-audit` y `npm audit --audit-level=high`.
- [ ] Revisar findings actuales de dependencias, secretos, defaults inseguros y avisos de privacidad en el candidato.
- [ ] Revisar accesibilidad y responsive manualmente.
- [ ] Confirmar que la demo no toca cuentas ni progreso real.
- [ ] Verificar Dependabot antes de integrar: #128 tiene fallo de accesibilidad reportado (`label-content-name-mismatch`); #185 tenía un check fallido en la última revisión. No se revalidaron todos los heads en esta pasada.

## Ramas y protección

- Main sigue intacta.
- Inventario de ramas paginado: **106 ramas**; todas las devueltas indican `protected:false`.
- Main y Beta no están protegidas. Rulesets: lista vacía. Endpoint de protección detallada devuelve 403 al conector; no se modificó configuración.
- `beta/programming-path-rebased`: 0 commits únicos ahead / 46 behind Beta; candidata redundante. No se borró (sin herramienta de eliminación disponible).
- Las demás ramas beta-port tienen commits propios; conservar hasta revisar sus cambios. No se borraron ramas ni se hizo force-push.

## Tags y Release

- [x] Tag existente `v1.0.0`, anotado, **sin firma**; apunta al commit `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No mover ni reutilizar.
- [x] GitHub Releases: ninguna publicada.
- [ ] Aprobar nombre de tag nuevo y crearlo sobre el commit exacto validado.
- [ ] Publicar Release con alcance, limitaciones conocidas y enlace a demo.

## Presentación

- [ ] README, instrucciones y changelog corresponden al alcance final.
- [ ] Capturas actualizadas, sin datos personales.
- [ ] Textos ES/EN, avisos legales y privacidad revisados.
- [ ] Demo walkthrough sin tocar progreso real.
- [ ] Smoke test manual de Pages.
- [ ] Notas de versión y lista de limitaciones.

## Limitaciones que deben declararse

Academy es una demo local con datos sintéticos, no un servicio institucional multi-tenant. Learning Paths consulta el progreso existente; no debe crear un almacén paralelo de XP/progreso. Pentest Lab es una interfaz de planificación, no un scanner/laboratorio operativo. En la release se deben indicar las pruebas que se ejecutaron sobre el commit exacto.

## Registro de esta auditoría

- Confirmado head Beta `960086f`, 75 ahead / 0 behind main; CI #45949035755 verde sobre este SHA exacto.
- #223 y #229 continúan divergentes y en draft; #227 permanece contra main y con fallo de test base.
- Se solicitó re-run de jobs fallidos de #229; attempt 4 está en curso al cerrar esta revisión.
- PR #207, #209, #101, #193 y #203 verificadas cerradas sin merge.
- No se hicieron merges, branch deletions, force-pushes, tags, releases ni deployments. Main sin cambios.
