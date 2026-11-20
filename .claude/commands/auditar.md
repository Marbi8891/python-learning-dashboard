---
description: Auditoría del proyecto (pruebas + revisor-daw, red-teamer y buscador-mejoras) con registro, histórico y comparación
argument-hint: "[plan | safe-fix AUD-NNN] [categorías separadas por comas] [--depth quick|standard|deep]"
---

Eres el **Project Auditor** de este repositorio. Coordinas las pruebas y los agentes que ya existen y
unificas sus hallazgos en un registro con histórico. Todo está en [`docs/AUDITOR.md`](../../docs/AUDITOR.md).

Argumentos: $ARGUMENTS

- Vacío → modo **READ ONLY** sobre todas las categorías, con la profundidad de `project-auditor.toml`.
- `plan` → no audita: genera el plan de corrección con lo que ya hay en el registro.
- `safe-fix AUD-NNN` → corrige ese hallazgo solo si el auditor lo clasifica como SAFE FIX.
- Una lista de categorías (`security,bugs`) limita la auditoría. `--depth` cambia la profundidad.

`A` = `python scripts/audit/auditor.py` (usa el Python del `.venv` si existe). Fecha = la de hoy.

## Reglas que no se rompen

- READ ONLY es el modo por defecto: no modificas archivos del proyecto, solo escribes en
  `.claude/informes/` (fuera de Git; el repositorio es público y los hallazgos no se publican).
- No inventas hallazgos ni resultados. Una prueba solo «pasa» si lo dice el JSON de `A checks`.
- Diferencias hecho (`fact`), sospecha (`suspicion`) y recomendación (`recommendation`). Una opinión
  nunca es una vulnerabilidad.
- Nada de push, merge, despliegues, migraciones, borrados ni cambios de dependencias.
- Respeta la arquitectura actual (`docs/DECISIONS.md`): mejoras incrementales, nada de reescrituras.

## READ ONLY (y la base de los otros modos)

1. **Contexto:** `A context`. Devuelve la última auditoría, los archivos cambiados desde su commit y
   los hallazgos abiertos. Si `changed_files` es `[]`, no se ha pasado `frequency_days` y no se ha
   pedido un área, ejecuta solo el paso 2 y el 4 (sin agentes): ahorra coste sin perder las pruebas.
2. **Pruebas:** `A checks --depth <d> --out .claude/informes/audit/runs/<AAAAMMDDTHHMMZ>-checks.json`.
   Con `deep`, pregunta antes de añadir `--allow-writes` (las e2e crean archivos y arrancan servidores).
3. **Agentes** (si la profundidad no es `quick`), en paralelo y como mucho `limits.max_agents`. Lanza
   solo los que cubren las categorías pedidas:

   | Agente | Categorías | Guarda su informe en |
   |---|---|---|
   | `red-teamer` | security, dependencies, config-deploy | `.claude/informes/red-team-AAAA-MM-DD.md` |
   | `revisor-daw` | bugs, architecture, code-quality, testing, content, integration, docs | `.claude/informes/revision-AAAA-MM-DD.md` |
   | `buscador-mejoras` | performance, ux-accessibility | `.claude/informes/mejoras-AAAA-MM-DD.md` |

   A cada uno pásale: la fecha, sus categorías, la lista `changed_files` (céntrate en ella; si es
   `null`, todo el proyecto), los hallazgos abiertos de sus categorías que devolvió `context`, la ruta
   del JSON de pruebas y la lista de informes anteriores de `.claude/informes/`. Pídele que **añada al
   final** de su informe habitual un bloque ` ```json audit-findings ` con el esquema de
   `docs/AUDITOR.md` § «Esquema de un hallazgo», y que:
   - reutilice el `key` de un hallazgo abierto si vuelve a verlo (así no se duplica);
   - declare en `resolved` (con su evidencia) los abiertos que ya no se reproducen;
   - ponga su numeración propia (`RT-NNN`, `MJ-NNN`) en `ref`;
   - no incluya nada que no haya comprobado como `fact`.

   Guarda cada informe tal cual (si ya existe uno de hoy, `-2`, `-3`...).
4. **Registro e informe:**
   `A audit --scope <categorías|all> --depth <d> --checks <json del paso 2> <informes del paso 3>`.
   Escribe `latest-audit.md`, `history/<id>.md`, `runs/<id>.json` y actualiza `registry.json`.
5. **Muéstrame** solo: la puntuación y su variación, nuevos / resueltos / regresiones, los P0 y P1, las
   pruebas que fallan o no se han ejecutado, los hallazgos rechazados y la ruta del informe. No
   pegues el informe entero.

## PLAN

`A plan` (o `A plan --min-priority P1`). Muéstrame el resumen por prioridad y la ruta de
`plan-latest.md`. No cambias nada.

## SAFE FIX `AUD-NNN`

1. `A preflight-fix AUD-NNN`. Si no sale «Listo para corregir», **para**. Si el hallazgo es
   APPROVAL REQUIRED, aplica ese modo: explícame el problema, el impacto, la solución propuesta y los
   archivos que modificarías (los da `A plan`), y espera mi aprobación explícita.
2. Si está listo: `A preflight-fix AUD-NNN --create-branch` (crea `fix/audit-NNN-…` y comprueba que
   no hay cambios sin confirmar).
3. `A checks --only <las de «Verificar con» del plan> --out .claude/informes/audit/runs/antes.json`.
4. Haz el cambio mínimo y añade el test de regresión del hallazgo.
5. `A checks --only <las mismas> --out .claude/informes/audit/runs/despues.json` y
   `A compare-checks <antes> <despues>`. Si algo deja de pasar, deshaz **solo tus cambios** y dímelo.
6. Pasa las pruebas de `docs/TESTING.md` que tocan, revisa `git diff` y haz un commit en la rama con
   `git add` de archivos concretos. No subas la rama ni abras el PR hasta que te lo diga.

Nunca se corrigen solos: arquitectura principal, base de datos y migraciones, autenticación,
permisos, configuración de producción, secretos, infraestructura, CI, API pública ni eliminación de
funcionalidades. La lista exacta está en `[safe_fix]` de `project-auditor.toml`.
