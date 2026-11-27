# PLD Beta 0.1.0 — checklist de lanzamiento

**Actualizado:** 2026-11-27 09:31 CET  
**Main:** `be801c5afa1c27ba6d5f24695236fe8ee67bdcee`  
**Beta (head antes de esta actualización):** `22fdc1d21634340f78f5557ac8737014bddf02e8` (**77 ahead / 0 behind main**)  
**Demo:** https://marbi8891.github.io/python-learning-dashboard/

## Gate de publicación
No crear tag ni publicar Release hasta aprobar el alcance, validar CI en el commit candidato exacto y completar smoke test manual y accesibilidad.

## PR candidatas
- [x] **#224 Programming Path:** merged en Beta; merge commit `1c104b3816f82a55bc883b18e8896a5b011c6597`.
- [ ] **#223 Academy:** draft; head `9d674df`, branch `beta/academy-institutional-rebased`, **17 ahead / 61 behind** Beta (merge base `5182b1ce`). CI #648 y Deployment Check #331 pasaron en su head, no en una integración actualizada. Sin approvals. Se solapa con #229 en HTML, router, precache e i18n. Demo local con datos sintéticos; sin multi-tenant, auth institucional, persistencia backend ni permisos reales.
- [ ] **#229 Learning Paths:** draft; head `88b9434`, **32 ahead / 29 behind** Beta (merge base `c31244a`). CI #45934058607, attempt 4, failed E2E: **286 pasan, 1 falla** en `e2e/learning-paths.spec.js:39`; tras reload, `#paths-view` queda vacío. Artifact #15178416458 descargado e inspeccionado: selección guardada, pero la vista no se renderiza; causa sin confirmar. Backend, cursos y WebKit passed; Deployment Check #45934058622 passed. No approvals. No integrar hasta diagnóstico, corrección, actualización contra Beta y CI verde.
- [ ] **#227 Pentest Lab:** draft contra main; head `67ca9b2`, **16 ahead / 0 behind**. CI #45851158102 falla en unit tests: **571/572 pasan**; falla `AI Academy is wired into app routing and view registry` (`tests/unit/ai-academy-routing.test.mjs:8`). Es un test de routing/baseline, no del Pentest Lab; E2E se omitió. Backend, cursos y WebKit passed; Deployment Check #45851158126 passed. Sin approvals. UI-only; no ejecuta Docker ni escaneos. Decidir alcance y resolver baseline antes de integrar.
- [x] PR obsoletas **#207, #209, #101, #193 y #203**: cerradas sin merge (verificado).

## CI y main
- [x] CI run **#45961952646** pasó los cuatro jobs sobre el head exacto de Beta `22fdc1d`: backend, WebKit, cursos y E2E. https://github.com/Marbi8891/python-learning-dashboard/actions/runs/45961952646
- [ ] Este checklist generará un commit nuevo; su CI aún no existe/no se ha verificado. Validar el nuevo head antes de publicar.
- [ ] Main `be801c5` permanece intacta. No se ejecutó suite completa de main en esta pasada; el último fallo completo conocido fue routing de AI Academy (569/570). Los CI monitors no sustituyen una suite completa.
- [ ] CI de #223/#229/#227 no valida la integración contra Beta actual; actualizar ramas y correr checks antes de merge.

## PR abiertas fuera de candidatas
El buscador devolvió **27 PR abiertas**. Runs anteriores, no revalidados en esta pasada:
- CI fallida conocida: **#205** (#529), **#201** (#519), **#199** (#516; Deployment #203), **#196** (#490; Deployment #177), **#195** (#494), **#185** (#592).
- Últimos checks consultados en verde: **#186** (#470), **#184** (#471), **#183** (#462), **#180** (#454), **#175** (#477), **#157** (#410), **#146** (#359), **#102** (#297), **#95** (#281), **#63** (#208). Los runs pueden ser antiguos; verificar head/base antes de integrar.
- Dependabot #128 tenía un finding de accesibilidad `label-content-name-mismatch`; estado actual no revalidado.

## Seguridad y calidad
- [x] Workflow CI revisado: permisos `contents: read`, checkout con `persist-credentials: false`, `pip-audit`, `npm audit --audit-level=high`, Ruff, cobertura backend 100 % y tests PostgreSQL/concurrencia.
- [x] Pages workflow separado: build y deploy en jobs distintos; permisos `contents: read`, `pages: write`, `id-token: write`.
- [ ] Revisar findings actuales de dependencias, secretos, defaults inseguros y privacidad en el candidato.
- [ ] Accesibilidad y responsive manuales.
- [ ] Confirmar demo sin cuentas/progreso real.

## Ramas y protección
- Inventario paginado: **106 ramas** (100 en página 1, 6 en página 2).
- Protección de main/Beta no revalidada por endpoint en esta pasada. Última comprobación disponible: `protected:false`, rulesets vacíos.
- `beta/programming-path-rebased`: **0 ahead / 48 behind** Beta; sin commits únicos, candidata redundante. No se borró; no hay herramienta de eliminación disponible.
- Otras ramas beta-port respecto a Beta: academy-institutional-port **11/65**; academy-institutional-rebased **17/61**; ai-academy-port **16/71**; hardening-rebased **19/68**; port-hardening **22/72**; port-pld003 **14/72**; programming-path-port **18/65**. Conservar hasta revisar commits únicos.

## Tags y Release
- [x] Tag `v1.0.0` verificado anteriormente; anotado, sin firma, apunta a `fdf64098556f0e835e08ad5ce58c230a21b5f591`. No mover ni reutilizar.
- [x] Última verificación: no hay GitHub Releases publicadas.
- [ ] Elegir tag nuevo sobre el commit exacto validado y publicar Release con alcance, limitaciones y demo.

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
- 2026-11-27 09:31: Beta `22fdc1d`; 77 ahead / 0 behind main; CI #45961952646 pasó todos los jobs sobre ese SHA.
- PR #223 compare actual: 17/61; PR #229: 32/29; #227: 16/0 frente a main.
- Artifact de #229 reexaminado; fallo de reload confirmado, causa no confirmada. Logs de #227 identifican el test de routing AI Academy como fallo.
- PR obsoletas #207, #209, #101, #193 y #203 cerradas sin merge.
- Comentarios de auditoría añadidos a #223, #229 y #227.
- No se realizaron merges, branch deletions, force-pushes, tags, releases ni deployments. Main sin cambios.
