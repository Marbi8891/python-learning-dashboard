# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 08:51 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta:** `d51f96ce5b723764da9dcae02bd137fb0a0ee87c` (**76 ahead / 0 behind main**)  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta aprobar el alcance, validar CI en el commit exacto candidato y completar smoke test manual y accesibilidad.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] **#223 Academy:** draft; head `9d674df`, **17 ahead / 60 behind** Beta (merge base `5182b1ce`). CI #648 y Deployment Check #331 pasaron en su head, sin reviews. Se solapa con #229 en `frontend/index.html`, `frontend/js/app.js`, `frontend/precache.js` y `frontend/i18n/en.json`. Actualizar y revisar antes de integrar. Demo local con datos sintéticos; sin multi-tenant, auth institucional, persistencia backend ni permisos reales.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 28 behind** Beta (merge base `c31244a`). CI #664 falló E2E en intento 4: la selección funciona antes del reload, pero después `#paths-view` queda vacío y no muestra “Mis Paths”. Artifact #15178416458 inspeccionado; el trace confirma la vista vacía, pero la causa no está confirmada. Backend, cursos y WebKit pasaron; Deployment Check #335 passed. Reviews COMMENTED, sin aprobación. No integrar hasta corregir y repetir CI.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, **16 ahead / 0 behind**. CI #623 falla en `ai-academy-routing.test.mjs` porque el test espera un loader de AI Academy ausente en main; backend, cursos y WebKit pasaron, E2E se omitió. Deployment Check #310 passed; sin reviews. UI-only, no ejecuta Docker ni scans. Decidir alcance antes de integrar.
- [x] PR obsoletas #207, #209, #101, #193 y #203 cerradas sin merge.

## CI y main
- [x] CI #45953880076 (run #672, attempt 2) passed los cuatro jobs sobre **Beta exacta `d51f96c`**: backend, cursos, E2E y WebKit. El intento 1 falló WebKit en la prueba de recuperación de contraseña (enlace mailto); el reintento pasó. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45953880076
- [x] CI #45949035755 passed sobre el head previo `960086f`.
- [ ] Main `be801c5` permanece intacta. No se ejecutó suite completa de main en esta pasada; el último fallo completo conocido fue routing de AI Academy (569/570). Los CI monitors verdes no sustituyen la suite completa.
- [ ] Las CI de #223/#229/#227 no validan integración contra el Beta actual; actualizar branches y correr checks antes de merge.

## PR abiertas fuera de las candidatas Beta
19 PR abiertas en el inventario:
- Fallos de CI en heads consultados: **#205** (#529), **#201** (#519), **#199** (#516 y Deployment #203), **#196** (#490 y Deployment #177), **#195** (#494), **#185** (#592). No se investigaron logs de todos estos fallos en esta pasada.
- Checks verdes en los heads consultados: **#186** (#470), **#184** (#471), **#183** (#462), **#180** (#454), **#175** (#477), **#157** (#410), **#146** (#359), **#102** (#297), **#95** (#281), **#63** (#208). Los runs pueden ser antiguos; revisar head/base antes de integrar.

## Seguridad y calidad
- [x] En CI observado: `pip-audit`, `npm audit --audit-level=high`, Ruff, cobertura backend 100 %, tests PostgreSQL y concurrencia.
- [ ] Revisar findings actuales de dependencias, secretos, defaults inseguros y privacidad en el candidato.
- [ ] Accesibilidad y responsive manuales.
- [ ] Confirmar demo sin cuentas/progreso real.
- [ ] Dependabot #128 (fallo `label-content-name-mismatch`) y #185/#592 requieren revisar sus heads y logs actuales; no revalidado en esta pasada.

## Ramas y protección
- Inventario paginado: **106 ramas** (100 en página 1, 6 en página 2).
- Main y Beta: `protected:false`; rulesets: `[]`. No se cambió la configuración.
- `beta/programming-path-rebased`: **0 ahead / 47 behind** Beta; no tiene commits únicos, candidata redundante. No se borró, no hay herramienta de eliminación disponible.
- Otras ramas beta-port divergentes respecto a Beta: academy-institutional-port 11/64; ai-academy-port 16/70; hardening-rebased 19/67; port-hardening 22/71; port-pld003 14/71; programming-path-port 18/64. Conservar hasta revisar sus commits únicos.

## Tags y Release
- [x] Tag `v1.0.0` verificado; objeto anotado apunta a commit `fdf64098556f0e835e08ad5ce58c230a21b5f591`, **sin firma**. No mover ni reutilizar.
- [x] GitHub Releases: ninguna publicada.
- [ ] Elegir tag nuevo y crearlo sobre el commit exacto validado.
- [ ] Publicar Release con alcance, limitaciones y demo.

## Presentación
- [ ] README, instrucciones y changelog alineados con alcance final.
- [ ] Capturas sin datos personales.
- [ ] ES/EN, aviso legal y privacidad revisados.
- [ ] Demo walkthrough sin tocar progreso real.
- [ ] Smoke test manual de Pages.
- [ ] Notas de versión y limitaciones.

## Limitaciones a declarar
Academy es demo local sintética, no servicio institucional multi-tenant. Learning Paths lee progreso existente; no debe duplicar XP/progreso. Pentest Lab es planificación, no scanner/laboratorio operativo.

## Registro
- 2026-11-27 08:51: Beta head `d51f96c`; 76 ahead / 0 behind main. CI #45953880076 attempt 2 passed en SHA exacto.
- #223 y #229 divergentes, draft y sin approvals; #227 draft contra main con fallo de baseline.
- Se reintentó WebKit fallido de CI Beta; reintento passed.
- Artifact E2E de #229 inspeccionado; el fallo de reload sigue reproducible y sin causa confirmada.
- PR obsoletas #207, #209, #101, #193 y #203 cerradas sin merge.
- No se realizaron merges, branch deletions, force-pushes, tags, releases ni deployments. Main sin cambios.
