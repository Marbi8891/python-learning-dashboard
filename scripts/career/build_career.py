"""Genera el catálogo de itinerarios profesionales: frontend/data/career/*.json.

El catálogo es estático (lo sirve GitHub Pages y funciona sin backend ni conexión). El progreso de
cada alumno va aparte, en su documento `career` (frontend/js/career/career-data.js).

Validaciones (cualquiera falla → no se genera y --check falla):
- ids con formato de id, únicos dentro de su tipo y registrados en ids.lock.json, que solo crece;
- prerrequisitos de módulos que existen y sin ciclos;
- toda referencia existe: conceptos (learning.json), bloques de los cursos de DAW
  (courses/<curso>/bank.json), recursos (resources.json), competencias, criterios, listas, bandas;
- cada competencia tiene una fuente evaluable (concepto, bloque o evaluación) y alguna unidad
  que la trabaja;
- cada unidad tiene nivel, objetivos, competencias y, si no está pendiente, algo que estudiar;
- cada módulo está en alguna etapa y tiene su evaluación;
- objetivos de los puestos entre 0 y 1, URL de repositorio https.

Uso:  python scripts/career/build_career.py           (genera)
      python scripts/career/build_career.py --check   (CI: falla si no está al día o no es válido)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "frontend" / "data"
OUT = DATA / "career"
LOCK = HERE / "ids.lock.json"

sys.path.insert(0, str(HERE))
import applied_ai  # noqa: E402
import programming_path  # noqa: E402

ROADMAPS = [applied_ai, programming_path]
ID = re.compile(r"^[a-z0-9][a-z0-9.-]{0,60}$")
LINK_KINDS = ("concept", "block", "resource")
EVALUABLE = ("concepts", "blocks", "assessments")


class Problems(list):
    def add(self, where: str, what: str) -> None:
        self.append(f"{where}: {what}")


def known_references() -> dict[str, set[str]]:
    learning = json.loads((DATA / "learning.json").read_text("utf-8"))
    resources = json.loads((DATA / "resources.json").read_text("utf-8"))
    blocks = set()
    for bank in sorted((DATA / "courses").glob("*/bank.json")):
        course = bank.parent.name
        blocks |= {
            f"{course}:{b['slug']}" for b in json.loads(bank.read_text("utf-8"))["exam"]["blocks"]
        }
    return {
        "concept": {c["id"] for c in learning["concepts"]},
        "block": blocks,
        "resource": {r["id"] for r in resources["resources"]},
    }


def text(value, where: str, problems: Problems) -> None:
    if not (
        isinstance(value, dict)
        and all(isinstance(value.get(k), str) and value[k].strip() for k in ("es", "en"))
    ):
        problems.add(where, "texto sin «es» y «en»")


def unique(ids: list[str], kind: str, problems: Problems) -> None:
    seen = set()
    for i in ids:
        if not isinstance(i, str) or not ID.fullmatch(i):
            problems.add(kind, f"id con formato inválido: {i!r}")
        if i in seen:
            problems.add(kind, f"id repetido: {i}")
        seen.add(i)


def cycles(modules: list[dict]) -> list[str]:
    graph = {m["id"]: m["requires"] for m in modules}
    state: dict[str, int] = {}
    found = []

    def visit(node: str, path: list[str]) -> None:
        state[node] = 1
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                found.append(" → ".join([*path, node, nxt]))
            elif nxt in graph and state.get(nxt) is None:
                visit(nxt, [*path, node])
        state[node] = 2

    for node in graph:
        if state.get(node) is None:
            visit(node, [])
    return found


def build(module, refs: dict[str, set[str]], problems: Problems) -> dict:
    """Valida un itinerario y devuelve el JSON que se publica."""
    rid = module.ID
    levels = [lv["id"] for lv in module.LEVELS]
    skills = {s["id"]: s for s in module.SKILLS}
    criteria = {c["id"]: c for p in module.PROJECTS for c in p["criteria"]}
    modules = {m["id"]: m for m in module.MODULES}
    checklists = module.CHECKLISTS
    bands = {b["id"] for b in module.SALARY_BANDS}

    unique([s["id"] for s in module.SKILLS], f"{rid} competencias", problems)
    unique([m["id"] for m in module.MODULES], f"{rid} módulos", problems)
    unique([u["id"] for m in module.MODULES for u in m["units"]], f"{rid} unidades", problems)
    unique([p["id"] for p in module.PROJECTS], f"{rid} proyectos", problems)
    unique([c["id"] for p in module.PROJECTS for c in p["criteria"]], f"{rid} criterios", problems)
    unique([r["id"] for r in module.ROLES], f"{rid} puestos", problems)
    unique([s["id"] for s in module.STAGES], f"{rid} etapas", problems)
    unique([i for items in checklists.values() for i, _ in items], f"{rid} listas", problems)

    text(module.TITLE, f"{rid} título", problems)
    for s in module.SKILLS:
        where = f"{rid} competencia {s['id']}"
        text(s["title"], where, problems)
        if s["category"] not in module.CATEGORIES:
            problems.add(where, f"categoría desconocida {s['category']}")
        src = s["sources"]
        if not any(src[k] for k in EVALUABLE):
            problems.add(
                where, "sin fuente evaluable (concepto, bloque o evaluación): leer no puede subirla"
            )
        for c in src["concepts"]:
            if c not in refs["concept"]:
                problems.add(where, f"concepto inexistente {c}")
        for b in src["blocks"]:
            if b not in refs["block"]:
                problems.add(where, f"bloque inexistente {b}")
        for a in src["assessments"]:
            if a not in modules:
                problems.add(where, f"evaluación inexistente {a}")
        for c in src["criteria"]:
            if c not in criteria:
                problems.add(where, f"criterio inexistente {c}")
            elif s["id"] not in criteria[c]["skills"]:
                problems.add(where, f"el criterio {c} no declara esta competencia")
        for c in src["checklists"]:
            if c not in checklists:
                problems.add(where, f"lista inexistente {c}")

    for c in criteria.values():
        for s in c["skills"]:
            if s not in skills:
                problems.add(f"{rid} criterio {c['id']}", f"competencia inexistente {s}")
            elif c["id"] not in skills[s]["sources"]["criteria"]:
                problems.add(
                    f"{rid} criterio {c['id']}", f"la competencia {s} no lo declara como fuente"
                )
        if c["module"] not in modules:
            problems.add(f"{rid} criterio {c['id']}", f"módulo inexistente {c['module']}")

    for p in module.PROJECTS:
        text(p["title"], f"{rid} proyecto {p['id']}", problems)
        if p["repo"] is not None and not str(p["repo"]).startswith("https://"):
            problems.add(f"{rid} proyecto {p['id']}", "el repositorio debe ser https")

    trained = set()
    for m in module.MODULES:
        where = f"{rid} módulo {m['id']}"
        text(m["title"], where, problems)
        for r in m["requires"]:
            if r not in modules or r == m["id"]:
                problems.add(where, f"prerrequisito inválido {r}")
        if m["assessment"]["id"] != m["id"] or not 0 < m["assessment"]["pass"] <= 1:
            problems.add(where, "evaluación mal definida")
        for c in m["project"]["criteria"]:
            if c not in criteria:
                problems.add(where, f"criterio inexistente {c}")
        for c in m["project"]["checklists"]:
            if c not in checklists:
                problems.add(where, f"lista inexistente {c}")
        if not m["units"]:
            problems.add(where, "sin unidades")
        for u in m["units"]:
            uw = f"{rid} unidad {u['id']}"
            if not u["id"].startswith(f"{m['id']}."):
                problems.add(uw, f"debe empezar por «{m['id']}.»")
            text(u["title"], uw, problems)
            if u["level"] not in levels:
                problems.add(uw, f"nivel desconocido {u['level']}")
            if not u["objectives"] or not all(
                isinstance(o, str) and o.strip() for o in u["objectives"]
            ):
                problems.add(uw, "sin objetivos")
            if not u["skills"]:
                problems.add(uw, "sin competencias")
            for s in u["skills"]:
                if s not in skills:
                    problems.add(uw, f"competencia inexistente {s}")
                trained.add(s)
            for link in u["links"]:
                if link["kind"] not in LINK_KINDS or link["id"] not in refs[link["kind"]]:
                    problems.add(uw, f"enlace inexistente {link['kind']}:{link['id']}")
            if not u["pending"] and not u["links"]:
                problems.add(uw, "marcada con contenido pero no enlaza a nada")
    for s in skills:
        if s not in trained:
            problems.add(f"{rid} competencia {s}", "ninguna unidad la trabaja")
    for cycle in cycles(module.MODULES):
        problems.add(f"{rid} módulos", f"ciclo de prerrequisitos {cycle}")

    staged = set()
    for st in module.STAGES:
        text(st["title"], f"{rid} etapa {st['id']}", problems)
        if not (isinstance(st["months"], int) and 1 <= st["months"] <= 24):
            problems.add(f"{rid} etapa {st['id']}", "duración fuera de 1-24 meses")
        for m in st["modules"]:
            if m not in modules:
                problems.add(f"{rid} etapa {st['id']}", f"módulo inexistente {m}")
            staged.add(m)
    for m in modules:
        if m not in staged:
            problems.add(f"{rid} módulo {m}", "no está en ninguna etapa del plan")

    for r in module.ROLES:
        where = f"{rid} puesto {r['id']}"
        text(r["title"], where, problems)
        if r["band"] not in bands:
            problems.add(where, f"banda inexistente {r['band']}")
        for s, target in r["skills"].items():
            if s not in skills:
                problems.add(where, f"competencia inexistente {s}")
            if not (isinstance(target, (int, float)) and 0 < target <= 1):
                problems.add(where, f"objetivo fuera de (0, 1] en {s}")

    for b in module.SALARY_BANDS:
        if not (isinstance(b["min"], int) and (b["max"] is None or b["max"] > b["min"])):
            problems.add(f"{rid} banda {b['id']}", "importes inválidos")

    return {
        "id": rid,
        "version": module.VERSION,
        "title": module.TITLE,
        "specialization": module.SPECIALIZATION,
        "levels": module.LEVELS,
        "categories": [{"id": k, "title": v} for k, v in module.CATEGORIES.items()],
        "salary": {
            "source": module.SALARY_SOURCE,
            "bands": module.SALARY_BANDS,
            "defaultTarget": module.DEFAULT_TARGET,
        },
        "stages": module.STAGES,
        "modules": module.MODULES,
        "skills": module.SKILLS,
        "projects": module.PROJECTS,
        "checklists": {
            name: [{"id": i, "title": {"es": t, "en": t}} for i, t in items]
            for name, items in checklists.items()
        },
        "roles": module.ROLES,
    }


def current_ids(roadmap: dict) -> dict[str, list[str]]:
    rid = roadmap["id"]
    return {
        f"{rid}:modules": [m["id"] for m in roadmap["modules"]],
        f"{rid}:units": [u["id"] for m in roadmap["modules"] for u in m["units"]],
        f"{rid}:skills": [s["id"] for s in roadmap["skills"]],
        f"{rid}:projects": [p["id"] for p in roadmap["projects"]],
        f"{rid}:criteria": [c["id"] for p in roadmap["projects"] for c in p["criteria"]],
        f"{rid}:roles": [r["id"] for r in roadmap["roles"]],
        f"{rid}:stages": [s["id"] for s in roadmap["stages"]],
        f"{rid}:checklists": [i["id"] for items in roadmap["checklists"].values() for i in items],
        "roadmaps": [rid],
    }


def locked_ids() -> dict[str, list[str]]:
    return json.loads(LOCK.read_text("utf-8")) if LOCK.exists() else {}


def merged_lock(locked: dict, now: dict) -> dict:
    """El registro solo crece: lo nuevo se añade al final y lo registrado no se toca."""
    result = {kind: list(values) for kind, values in locked.items()}
    for kind, values in now.items():
        known = result.setdefault(kind, [])
        known.extend(v for v in values if v not in known)
    return result


def outputs(problems: Problems) -> tuple[dict[Path, str], dict[str, list[str]]]:
    refs = known_references()
    files: dict[Path, str] = {}
    ids: dict[str, list[str]] = {}
    index = []
    for module in ROADMAPS:
        roadmap = build(module, refs, problems)
        for kind, values in current_ids(roadmap).items():
            ids.setdefault(kind, []).extend(values)
        files[OUT / f"{roadmap['id']}.json"] = dump(roadmap)
        index.append(
            {
                "id": roadmap["id"],
                "version": roadmap["version"],
                "title": roadmap["title"],
                "modules": len(roadmap["modules"]),
                "units": sum(len(m["units"]) for m in roadmap["modules"]),
                "skills": len(roadmap["skills"]),
            }
        )
    files[OUT / "index.json"] = dump({"version": 1, "roadmaps": index})
    for kind, values in locked_ids().items():
        lost = [i for i in values if i not in ids.get(kind, [])]
        if lost:
            problems.add(f"ids.lock.json ({kind})", f"ya no existen (los ids no se borran): {lost}")
    return files, ids


def dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=1) + "\n"


def main(argv: list[str]) -> int:
    problems = Problems()
    files, ids = outputs(problems)
    if problems:
        print("El catálogo de itinerarios no es válido:", *problems, sep="\n  ", file=sys.stderr)
        return 1
    if "--check" in argv:
        stale = [
            p for p, content in files.items() if not p.exists() or p.read_text("utf-8") != content
        ]
        locked = locked_ids()
        if stale:
            print(
                "No está al día: ejecuta python scripts/career/build_career.py",
                *map(str, stale),
                sep="\n  ",
                file=sys.stderr,
            )
            return 1
        if merged_lock(locked, ids) != locked:
            print(
                "Hay ids nuevos sin registrar en ids.lock.json: "
                "ejecuta python scripts/career/build_career.py",
                file=sys.stderr,
            )
            return 1
        print(f"Catálogo de itinerarios al día: {len(files) - 1} itinerario(s)")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for path, content in files.items():
        path.write_text(content, "utf-8", newline="\n")
    LOCK.write_text(dump(merged_lock(locked_ids(), ids)), "utf-8", newline="\n")
    print(f"Generado {OUT} ({len(files) - 1} itinerario(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
