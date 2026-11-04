"""Genera frontend/data/career/*.json (Career Roadmap) a partir de scripts/career/roadmaps.py.

El script valida el catálogo antes de escribir nada:
- ids con formato correcto, únicos y estables (ids.lock.json solo crece: el progreso del alumno se
  guarda por id de fase, unidad, competencia, proyecto y criterio);
- prerrequisitos de fases y competencias que existen y no forman ciclos;
- cada enlace de una unidad apunta a contenido que existe (conceptos, lecciones, bloques, recursos);
- cada competencia tiene al menos una fuente de evidencias y está en alguna fase;
- textos en español e inglés.

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
VERSION = 1

sys.path.insert(0, str(HERE))
from roadmaps import CATEGORIES, ROADMAPS  # noqa: E402

ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,48}$")
LEVELS = {"junior", "mid", "senior"}
STATUSES = {"complete", "skeleton"}
DAW_COURSES = ("programacion", "sql", "entornos", "marcas", "js", "java")


def _json(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def text(value: dict) -> str:
    return value if isinstance(value, str) else value.get("es", "")


class Problems(list):
    def add(self, where: str, message: str) -> None:
        self.append(f"{where}: {message}")


def platform_content() -> dict[str, dict[str, dict]]:
    """Todo lo que una unidad o una competencia puede enlazar, con su título."""
    learning = _json(DATA / "learning.json")
    pcap = _json(DATA / "lessons.json")
    resources = _json(DATA / "resources.json")
    content: dict[str, dict[str, dict]] = {
        "concept": {c["id"]: {"title": c["title"]} for c in learning["concepts"]},
        "pcap": {
            lesson["slug"]: {"title": lesson["title"]}
            for module in pcap["modules"]
            for lesson in module["lessons"]
        },
        "resource": {
            r["id"]: {"title": r["title"], "url": r["url"]} for r in resources["resources"]
        },
        "lesson": {},
        "block": {},
    }
    for course in DAW_COURSES:
        lessons = _json(DATA / "courses" / course / "lessons.json")
        for module in lessons["modules"]:
            for lesson in module["lessons"]:
                content["lesson"][f"{course}/{lesson['slug']}"] = {"title": text(lesson["title"])}
        bank = _json(DATA / "courses" / course / "bank.json")
        for block in bank["exam"]["blocks"]:
            content["block"][f"{course}:{block['slug']}"] = {"title": text(block["title"])}
    return content


def check_text(value, where: str, problems: Problems) -> None:
    if not (
        isinstance(value, dict) and value.get("es", "").strip() and value.get("en", "").strip()
    ):
        problems.add(where, "falta el texto en español o en inglés")


def check_id(value, where: str, problems: Problems) -> None:
    if not isinstance(value, str) or not ID.match(value):
        problems.add(where, f"id no válido: {value!r}")


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    """Devuelve un ciclo de prerrequisitos si lo hay (búsqueda en profundidad)."""
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt) :] + [nxt]
            if nxt in graph and state.get(nxt) is None:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in graph:
        if state.get(node) is None:
            found = visit(node)
            if found:
                return found
    return None


def unique(items: list[dict], where: str, problems: Problems) -> dict[str, dict]:
    seen: dict[str, dict] = {}
    for item in items:
        check_id(item.get("id"), where, problems)
        if item.get("id") in seen:
            problems.add(where, f"id repetido: {item['id']}")
        seen[item.get("id")] = item
    return seen


def build_roadmap(rm: dict, content: dict, problems: Problems) -> dict:
    where = f"itinerario {rm.get('id')}"
    check_id(rm.get("id"), where, problems)
    for field in ("title", "description"):
        check_text(rm.get(field), f"{where} · {field}", problems)
    if rm.get("level") not in LEVELS:
        problems.add(where, f"nivel desconocido: {rm.get('level')}")
    if rm.get("status") not in STATUSES:
        problems.add(where, f"estado desconocido: {rm.get('status')}")
    if not (isinstance(rm.get("months"), int) and 1 <= rm["months"] <= 36):
        problems.add(where, "months debe ser un entero entre 1 y 36")
    for i, objective in enumerate(rm.get("objectives", [])):
        check_text(objective, f"{where} · objetivo {i + 1}", problems)

    skills = unique(rm["skills"], f"{where} · competencias", problems)
    phases = unique(rm["phases"], f"{where} · fases", problems)
    projects = unique(rm["projects"], f"{where} · proyectos", problems)

    for sid, skill in skills.items():
        sw = f"{where} · competencia {sid}"
        check_text(skill.get("title"), sw, problems)
        if skill.get("category") not in CATEGORIES:
            problems.add(sw, f"categoría desconocida: {skill.get('category')}")
        if skill.get("target") not in (1, 2, 3):
            problems.add(sw, "target debe ser 1, 2 o 3")
        for req in skill.get("requires", []):
            if req not in skills:
                problems.add(sw, f"prerrequisito que no existe: {req}")
        sources = skill.get("sources", {})
        if not any(sources.get(kind) for kind in ("concepts", "blocks", "projects")):
            problems.add(sw, "sin fuentes de evidencias")
        for kind, known in (("concepts", "concept"), ("blocks", "block")):
            for ref in sources.get(kind, []):
                if ref not in content[known]:
                    problems.add(sw, f"{kind}: no existe {ref}")
        for ref in sources.get("projects", []):
            if ref not in projects:
                problems.add(sw, f"projects: no existe {ref}")
            elif sid not in projects[ref].get("skills", []):
                problems.add(sw, f"el proyecto {ref} no la declara en sus competencias")
    cycle = find_cycle({sid: s.get("requires", []) for sid, s in skills.items()})
    if cycle:
        problems.add(where, f"ciclo de prerrequisitos entre competencias: {' → '.join(cycle)}")

    in_phase: set[str] = set()
    unit_ids: set[str] = set()
    out_phases = []
    for pid, phase in phases.items():
        pw = f"{where} · fase {pid}"
        for field in ("title", "description"):
            check_text(phase.get(field), f"{pw} · {field}", problems)
        for i, objective in enumerate(phase.get("objectives", [])):
            check_text(objective, f"{pw} · objetivo {i + 1}", problems)
        if not phase.get("objectives"):
            problems.add(pw, "sin objetivos")
        for req in phase.get("requires", []):
            if req not in phases:
                problems.add(pw, f"prerrequisito que no existe: {req}")
        for sid in phase.get("skills", []):
            if sid not in skills:
                problems.add(pw, f"competencia que no existe: {sid}")
            in_phase.add(sid)
        if phase.get("assessment") is not None:
            problems.add(
                pw, "las evaluaciones de fase llegan en el Sprint 5 (assessment debe ser None)"
            )
        project = phase.get("project")
        if project is not None and (project not in projects or projects[project]["phase"] != pid):
            problems.add(pw, f"proyecto que no existe o es de otra fase: {project}")
        units = []
        if not phase.get("units"):
            problems.add(pw, "sin unidades")
        for unit in phase.get("units", []):
            uw = f"{pw} · unidad {unit.get('id')}"
            check_id(unit.get("id"), uw, problems)
            if unit.get("id") in unit_ids:
                problems.add(uw, "id repetido en el itinerario")
            unit_ids.add(unit.get("id"))
            check_text(unit.get("title"), uw, problems)
            links = []
            for kind, ref in unit.get("links", []):
                if kind not in content:
                    problems.add(uw, f"tipo de enlace desconocido: {kind}")
                elif ref not in content[kind]:
                    problems.add(uw, f"{kind}: no existe {ref}")
                else:
                    links.append({"kind": kind, "ref": ref, **content[kind][ref]})
            units.append(
                {"id": unit["id"], "title": unit["title"], "links": links, "pending": not links}
            )
        out_phases.append(
            {
                "id": pid,
                "title": phase["title"],
                "description": phase["description"],
                "objectives": phase["objectives"],
                "requires": phase.get("requires", []),
                "skills": phase.get("skills", []),
                "units": units,
                "assessment": phase.get("assessment"),
                "project": project,
            }
        )
    for sid in skills:
        if sid not in in_phase:
            problems.add(f"{where} · competencia {sid}", "no está en ninguna fase")
    cycle = find_cycle({pid: p.get("requires", []) for pid, p in phases.items()})
    if cycle:
        problems.add(where, f"ciclo de prerrequisitos entre fases: {' → '.join(cycle)}")

    for prid, project in projects.items():
        jw = f"{where} · proyecto {prid}"
        for field in ("title", "description"):
            check_text(project.get(field), f"{jw} · {field}", problems)
        if project.get("phase") not in phases:
            problems.add(jw, f"fase que no existe: {project.get('phase')}")
        elif phases[project["phase"]].get("project") != prid:
            problems.add(jw, "su fase no lo tiene como proyecto")
        for sid in project.get("skills", []):
            if sid not in skills:
                problems.add(jw, f"competencia que no existe: {sid}")
        criteria = unique(project.get("criteria", []), f"{jw} · criterios", problems)
        if not criteria:
            problems.add(jw, "sin criterios de evaluación")
        for cid, criterion in criteria.items():
            check_text(criterion.get("text"), f"{jw} · criterio {cid}", problems)

    return {
        "version": VERSION,
        "id": rm["id"],
        "status": rm["status"],
        "title": rm["title"],
        "description": rm["description"],
        "level": rm["level"],
        "months": rm["months"],
        "objectives": rm["objectives"],
        "categories": list(CATEGORIES),
        "skills": [
            {
                "id": s["id"],
                "title": s["title"],
                "category": s["category"],
                "target": s["target"],
                "requires": s.get("requires", []),
                "sources": {k: s["sources"].get(k, []) for k in ("concepts", "blocks", "projects")},
            }
            for s in rm["skills"]
        ],
        "phases": out_phases,
        "projects": rm["projects"],
    }


def current_ids(roadmaps: list[dict]) -> dict[str, list[str]]:
    ids: dict[str, list[str]] = {
        "roadmaps": [],
        "phases": [],
        "units": [],
        "skills": [],
        "projects": [],
        "criteria": [],
    }
    for rm in roadmaps:
        ids["roadmaps"].append(rm["id"])
        ids["phases"] += [f"{rm['id']}/{p['id']}" for p in rm["phases"]]
        ids["units"] += [f"{rm['id']}/{u['id']}" for p in rm["phases"] for u in p["units"]]
        ids["skills"] += [f"{rm['id']}/{s['id']}" for s in rm["skills"]]
        ids["projects"] += [f"{rm['id']}/{p['id']}" for p in rm["projects"]]
        ids["criteria"] += [
            f"{rm['id']}/{p['id']}/{c['id']}" for p in rm["projects"] for c in p["criteria"]
        ]
    return ids


def locked_ids() -> dict[str, list[str]]:
    return _json(LOCK) if LOCK.exists() else {}


def merged_lock(locked: dict, now: dict) -> dict:
    """El registro solo crece: lo nuevo se añade al final y lo registrado no se toca."""
    result = {kind: list(values) for kind, values in locked.items()}
    for kind, values in now.items():
        known = result.setdefault(kind, [])
        known.extend(v for v in values if v not in known)
    return result


def build() -> tuple[dict[str, dict], dict[str, list[str]], Problems]:
    problems = Problems()
    content = platform_content()
    files: dict[str, dict] = {}
    seen: set[str] = set()
    for rm in ROADMAPS:
        if rm.get("id") in seen:
            problems.add("ROADMAPS", f"itinerario repetido: {rm['id']}")
        seen.add(rm.get("id"))
        files[f"{rm['id']}.json"] = build_roadmap(rm, content, problems)
    files["index.json"] = {
        "version": VERSION,
        "default": ROADMAPS[0]["id"],
        "roadmaps": [
            {
                "id": data["id"],
                "status": data["status"],
                "title": data["title"],
                "description": data["description"],
                "level": data["level"],
                "months": data["months"],
                "phases": len(data["phases"]),
                "skills": len(data["skills"]),
            }
            for data in (files[f"{rm['id']}.json"] for rm in ROADMAPS)
        ],
    }
    ids = current_ids([files[f"{rm['id']}.json"] for rm in ROADMAPS])
    for kind, values in locked_ids().items():
        lost = [v for v in values if v not in ids.get(kind, [])]
        if lost:
            problems.add(f"ids.lock.json ({kind})", f"ya no existen (hace falta migración): {lost}")
    return files, ids, problems


def dump(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def main() -> None:
    files, ids, problems = build()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    if "--check" in sys.argv:
        stale = [
            n
            for n, d in files.items()
            if not (OUT / n).exists() or (OUT / n).read_text("utf-8") != dump(d)
        ]
        extra = (
            sorted(p.name for p in OUT.glob("*.json") if p.name not in files)
            if OUT.exists()
            else []
        )
        locked = locked_ids()
        if stale or extra or merged_lock(locked, ids) != locked:
            print(
                f"frontend/data/career no está al día ({stale + extra or 'ids.lock.json'}): "
                "ejecuta python scripts/career/build_career.py",
                file=sys.stderr,
            )
            sys.exit(1)
        units = sum(len(p["units"]) for d in files.values() for p in d.get("phases", []))
        print(f"career al día: {len(files) - 1} itinerario(s), {units} unidades comprobadas")
        return
    OUT.mkdir(exist_ok=True)
    for name, data in files.items():
        (OUT / name).write_text(dump(data), "utf-8", newline="\n")
    LOCK.write_text(dump(merged_lock(locked_ids(), ids)), "utf-8", newline="\n")
    print(f"Generados {len(files)} archivos en {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
