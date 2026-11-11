"""Genera frontend/data/learning.json (conceptos y ejercicios) y comprueba las respuestas.

Nada se escribe «a ojo»: el script ejecuta con el mismo runner que usa el navegador
(frontend/py/runner.py) cada salida esperada, cada hueco, cada línea corregida y cada solución,
y comprueba que las soluciones equivocadas típicas fallan en el test que deben.

Uso:  python scripts/learning/build_learning.py           (genera)
      python scripts/learning/build_learning.py --check   (CI: falla si el JSON no está al día)
"""

from __future__ import annotations

import importlib.util
import json
import multiprocessing
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "frontend" / "data"
OUT = DATA / "learning.json"
# Ids estables (F1.0): el progreso del alumno se guarda por id de concepto, ejercicio y error.
# El registro solo crece; quitar o renombrar un id exige un plan de migración en el mismo PR.
LOCK = HERE / "ids.lock.json"
TIMEOUT_S = 5

sys.path.insert(0, str(HERE))
from concepts import AREAS, CONCEPTS, CURRICULUM_CE, DAW_COMPETENCIES, PATH  # noqa: E402
from exercises import E as BASE_EXERCISES  # noqa: E402
from poo_module import EXERCISES as POO_EXERCISES  # noqa: E402
from poo_module import MODULE, UNIT_FIELDS  # noqa: E402

E = [*BASE_EXERCISES, *POO_EXERCISES]

KINDS = {"choice", "output", "fill", "order", "bug", "code"}


def _load_runner():
    spec = importlib.util.spec_from_file_location("runner", ROOT / "frontend" / "py" / "runner.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize(text: str) -> str:
    """Misma regla que el navegador (learn/answers.js).

    Sin espacios al final de cada línea ni líneas vacías al final.
    """
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).rstrip("\n")


def _child(conn, action, payload):
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)  # los ejercicios de ficheros escriben en disco
        runner = _load_runner()
        if action == "run":
            result = runner.run_code(payload["code"], payload.get("stdin", ""))
            conn.send({"output": result["output"], "error": result["error"]})
        else:
            result = runner.check_exercise(payload["code"], payload["checks"])
            conn.send(
                {"passed": result["passed"], "case": result["case"], "message": result["message"]}
            )


def execute(action: str, **payload) -> dict:
    """Ejecuta en un proceso aparte, con tiempo límite (algunos códigos con errores no terminan)."""
    parent, child = multiprocessing.Pipe()
    process = multiprocessing.Process(target=_child, args=(child, action, payload))
    process.start()
    process.join(TIMEOUT_S)
    if process.is_alive():
        process.kill()
        process.join()
        return {"timeout": True, "output": "", "error": "timeout", "passed": False, "case": None}
    return parent.recv()


class Problems(list):
    def add(self, where: str, message: str) -> None:
        self.append(f"{where}: {message}")


def graph_requires(cid: str) -> list[str]:
    return next((c["requires"] for c in CONCEPTS if c["id"] == cid), [])


def check_concepts(problems: Problems) -> set[str]:
    lessons = {
        lesson["slug"]
        for module in json.loads((DATA / "lessons.json").read_text("utf-8"))["modules"]
        for lesson in module["lessons"]
    }
    uts = {
        m["slug"]
        for m in json.loads(
            (DATA / "courses" / "programacion" / "lessons.json").read_text("utf-8")
        )["modules"]
    }
    areas = {a["id"] for a in AREAS}
    ids = [c["id"] for c in CONCEPTS]
    if len(ids) != len(set(ids)):
        problems.add("conceptos", "ids repetidos")
    errors: set[str] = set()
    for concept in CONCEPTS:
        where = f"concepto {concept['id']}"
        if concept["area"] not in areas:
            problems.add(where, f"área desconocida {concept['area']}")
        for ref in concept["requires"] + concept.get("related", []):
            if ref not in ids:
                problems.add(where, f"referencia a un concepto inexistente: {ref}")
        for slug in concept.get("lessons", []):
            if slug not in lessons:
                problems.add(where, f"lección inexistente en lessons.json: {slug}")
        if not concept.get("lessons") and not concept.get("theory"):
            problems.add(where, "necesita teoría propia o una lección")
        if concept.get("ut") and concept["ut"] not in uts:
            problems.add(where, f"UT inexistente: {concept['ut']}")
        if concept["daw"] not in (1, 2, 3):
            problems.add(where, "daw debe ser 1, 2 o 3")
        if not concept["errors"]:
            problems.add(where, "sin errores típicos")
        for error in concept["errors"]:
            if not error["id"].startswith(f"{concept['id']}."):
                problems.add(where, f"el error {error['id']} no lleva el prefijo del concepto")
            if error["id"] in errors:
                problems.add(where, f"error repetido {error['id']}")
            errors.add(error["id"])
        example = concept["example"]
        result = execute("run", code=example["code"], stdin=example.get("stdin", ""))
        if result["error"]:
            problems.add(where, f"el ejemplo falla: {result['error']}")
        example["output"] = result["output"]
        lines = example["code"].count("\n") + 1
        for number, _ in example["lines"]:
            if not 1 <= number <= lines:
                problems.add(where, f"explicación de una línea inexistente: {number}")
    covered = [cid for comp in DAW_COMPETENCIES for cid in comp["concepts"]]
    if sorted(covered) != sorted(c["id"] for c in CONCEPTS if c["area"] != "poo"):
        problems.add(
            "DAW", "cada concepto (salvo el módulo de POO, aparte) va en una sola competencia"
        )
    if sum(comp["weight"] for comp in DAW_COMPETENCIES) != 100:
        problems.add("DAW", "los pesos de las competencias deben sumar 100")
    if sorted(PATH) != sorted(ids):
        problems.add("conceptos", "PATH debe contener cada concepto una vez")
    for position, cid in enumerate(PATH):
        for req in graph_requires(cid):
            if req in PATH and PATH.index(req) > position:
                problems.add("conceptos", f"en PATH, {cid} va antes que su prerrequisito {req}")
    # Prerrequisitos sin ciclos (la recomendación recorre el grafo)
    graph = {c["id"]: c["requires"] for c in CONCEPTS}
    state: dict[str, int] = {}

    def visit(node: str) -> None:
        if state.get(node) == 1:
            problems.add("conceptos", f"ciclo de prerrequisitos en {node}")
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for nxt in graph.get(node, []):
            visit(nxt)
        state[node] = 2

    for node in graph:
        visit(node)
    return errors


def check_exercise(ex: dict, concepts: set[str], errors: set[str], problems: Problems) -> None:
    where = f"ejercicio {ex['id']}"
    if ex["kind"] not in KINDS:
        problems.add(where, f"tipo desconocido {ex['kind']}")
        return
    if ex["concept"] not in concepts:
        problems.add(where, f"concepto inexistente {ex['concept']}")
    tags = (
        [o["error"] for o in ex.get("options", [])]
        + list(ex.get("traps", {}).values())
        + [ex.get("error")]
    )
    tags += [case.get("error") for case in ex.get("checks", [])]
    for tag in filter(None, tags):
        if tag not in errors:
            problems.add(where, f"error inexistente {tag}")

    kind = ex["kind"]
    if kind == "choice":
        if len(ex["options"]) < 2 or not 0 <= ex["answer"] < len(ex["options"]):
            problems.add(where, "opciones o respuesta no válidas")
        elif ex["options"][ex["answer"]]["error"]:
            problems.add(where, "la opción correcta no puede tener error")
    elif kind == "output":
        result = execute("run", code=ex["code"], stdin=ex["stdin"])
        if result.get("timeout") or result["error"]:
            problems.add(where, f"el código no termina bien: {result['error']}")
        elif normalize(result["output"]) != normalize(ex["expect"]):
            problems.add(where, f"salida real {result['output']!r} ≠ esperada {ex['expect']!r}")
        for trap in ex["traps"]:
            if normalize(trap) == normalize(ex["expect"]):
                problems.add(where, "una trampa coincide con la respuesta correcta")
    elif kind == "fill":
        if ex["code"].count("___") != 1:
            problems.add(where, "el código debe tener un único hueco ___")
        for answer in ex["accept"]:
            if ex["expect"] is None:
                continue
            result = execute("run", code=ex["code"].replace("___", answer))
            if result["error"] or normalize(result["output"]) != normalize(ex["expect"]):
                problems.add(
                    where, f"con {answer!r} la salida es {result['output']!r} ({result['error']})"
                )
        for trap in ex["traps"]:
            if trap in ex["accept"]:
                problems.add(where, "una trampa está entre las respuestas aceptadas")
    elif kind == "order":
        if len(ex["lines"]) < 3 and ex["pseudo"]:
            problems.add(where, "pocas líneas para ordenar")
        if ex["expect"] is not None:
            result = execute("run", code="\n".join(ex["lines"]))
            if result["error"] or normalize(result["output"]) != normalize(ex["expect"]):
                problems.add(
                    where, f"el código ordenado da {result['output']!r} ({result['error']})"
                )
    elif kind == "bug":
        lines = ex["code"].split("\n")
        if not 1 <= ex["line"] <= len(lines):
            problems.add(where, "línea fuera de rango")
            return
        fixed = lines[: ex["line"] - 1] + ([ex["fix"]] if ex["fix"] else []) + lines[ex["line"] :]
        good = execute("run", code="\n".join(fixed), stdin=ex["stdin"])
        if (
            good.get("timeout")
            or good["error"]
            or normalize(good["output"]) != normalize(ex["expect"])
        ):
            problems.add(where, f"la versión corregida da {good['output']!r} ({good['error']})")
        bad = execute("run", code=ex["code"], stdin=ex["stdin"])
        if (
            not bad.get("timeout")
            and not bad["error"]
            and normalize(bad["output"]) == normalize(ex["expect"])
        ):
            problems.add(where, "la versión con el error ya da la salida correcta")
    elif kind == "code":
        result = execute("check", code=ex["solution"], checks=ex["checks"])
        if not result["passed"]:
            problems.add(
                where,
                f"la solución no supera los tests: caso {result['case']}: {result['message']}",
            )
        for wrong, expected_case in ex["_wrong"]:
            result = execute("check", code=wrong, checks=ex["checks"])
            if result["passed"] or result["case"] != expected_case:
                problems.add(
                    where,
                    f"una solución equivocada debería fallar en el caso {expected_case}: {result}",
                )


MAPPING_STATUS = {"verified", "proposed", "unassigned"}
CHOICE_OPTIONS = 4  # preguntas tipo test del módulo de POO: siempre cuatro opciones
MIN_UNIT_EXERCISES = 8


def _same_text(ex: dict) -> str:
    """Enunciado y código normalizados, para detectar preguntas repetidas."""
    return " ".join(f"{ex['q']} {ex.get('code') or ''}".lower().split())


def check_units(problems: Problems) -> list[dict]:
    """Módulo de POO: cada unidad tiene todos sus apartados y sus ejercicios están completos.

    Devuelve el índice del módulo con `available` en las unidades que ya tienen concepto.
    """
    catalog = json.loads((DATA / "curriculum" / "daw-cyl.json").read_text("utf-8"))
    criteria = {
        ce["id"]
        for module in catalog["modules"]
        for ra in module.get("learningOutcomes", [])
        for ce in ra["criteria"]
    }
    sources = {source["id"] for source in catalog["sources"]}
    by_id = {c["id"]: c for c in CONCEPTS}
    exercises = {e["id"]: e for e in E}
    units = MODULE["units"]
    if [u["number"] for u in units] != list(range(1, len(units) + 1)):
        problems.add("módulo POO", "las unidades deben ir numeradas 1, 2, 3… sin huecos")
    numbers = {u["id"]: u["number"] for u in units}
    for concept in CONCEPTS:
        if concept["area"] == "poo" and concept["id"] not in numbers:
            problems.add(f"concepto {concept['id']}", "es del área poo pero no está en MODULE")
    seen_texts: dict[str, str] = {}
    for ex in E:
        if by_id.get(ex["concept"], {}).get("area") != "poo":
            continue
        text = _same_text(ex)
        if text in seen_texts:
            problems.add(f"ejercicio {ex['id']}", f"repite el enunciado de {seen_texts[text]}")
        seen_texts.setdefault(text, ex["id"])
    for unit in units:
        concept = by_id.get(unit["id"])
        if concept is None:
            continue  # unidad aún no publicada: el índice la muestra «en preparación»
        cid = concept["id"]
        where = f"unidad {unit['number']} ({cid})"
        if concept.get("unit") != {"module": MODULE["id"], "number": unit["number"]}:
            problems.add(where, "el campo unit no coincide con el índice del módulo")
        for name in UNIT_FIELDS:
            if not concept.get(name):
                problems.add(where, f"falta el apartado {name}")
        own = [e for e in E if e["concept"] == cid]
        if len(own) < MIN_UNIT_EXERCISES:
            problems.add(where, f"necesita al menos {MIN_UNIT_EXERCISES} ejercicios")
        used: list[str] = []
        section_ids = set()
        for section in concept.get("sections", []):
            swhere = f"{where}, lección {section.get('id')}"
            if not section.get("id", "").startswith(f"{cid}.") or section["id"] in section_ids:
                problems.add(swhere, f"id de lección repetido o sin el prefijo {cid}.")
            section_ids.add(section.get("id"))
            if not section.get("title") or not section.get("theory"):
                problems.add(swhere, "falta el título o la teoría")
            if not section.get("examples"):
                problems.add(swhere, "sin ejemplos")
            for example in section.get("examples", []):
                result = execute("run", code=example["code"], stdin=example.get("stdin", ""))
                if result.get("timeout") or result["error"]:
                    problems.add(swhere, f"un ejemplo falla: {result['error']}")
                example["output"] = result["output"]
                lines = example["code"].count("\n") + 1
                for number, _ in example["lines"]:
                    if not 1 <= number <= lines:
                        problems.add(swhere, f"explicación de una línea inexistente: {number}")
            if len(section.get("quiz", [])) != 3:
                problems.add(swhere, "el mini-quiz debe tener 3 preguntas")
            used += section.get("quiz", [])
        for group in ("guided", "autonomous"):
            for eid in concept.get(group, []):
                if exercises.get(eid, {}).get("kind") != "code":
                    problems.add(where, f"{group}: {eid} debe ser un ejercicio de escribir código")
        used += concept.get("guided", []) + concept.get("autonomous", [])
        used += concept.get("selfcheck", [])
        used += concept.get("pass", {}).get("required", [])
        for eid in used:
            if exercises.get(eid, {}).get("concept") != cid:
                problems.add(where, f"{eid} no existe o no es un ejercicio de esta unidad")
        for ex in own:
            ewhere = f"ejercicio {ex['id']}"
            if ex["id"] not in used:
                problems.add(ewhere, "no aparece en ninguna lección, práctica ni autoevaluación")
            if ex["kind"] == "choice" and len(ex["options"]) != CHOICE_OPTIONS:
                problems.add(ewhere, f"una pregunta tipo test lleva {CHOICE_OPTIONS} opciones")
            if ex["kind"] == "code":
                starter = execute("check", code=ex["starter"], checks=ex["checks"])
                if starter["passed"]:
                    problems.add(ewhere, "el código inicial ya supera los tests")
                result = execute("run", code=ex["solution"])
                if result["output"].strip():
                    ex["expect"] = result["output"]  # «Resultado esperado»: el de la solución real
        score = concept.get("pass", {}).get("minScore")
        if not isinstance(score, (int, float)) or not 0 < score <= 1:
            problems.add(where, "pass.minScore debe estar entre 0 y 1")
        for mapping in concept.get("curriculum", []):
            mwhere = f"{where}, {mapping.get('ce')}"
            if mapping.get("status") not in MAPPING_STATUS:
                problems.add(mwhere, f"estado no válido (usa {sorted(MAPPING_STATUS)})")
            if mapping.get("source", "").split("#")[0] not in sources:
                problems.add(mwhere, "fuente desconocida en daw-cyl.json")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(mapping.get("reviewed", ""))):
                problems.add(mwhere, "falta la fecha de revisión (AAAA-MM-DD)")
            if mapping.get("status") != "unassigned" and mapping.get("ce") not in criteria:
                problems.add(mwhere, "CE inexistente en daw-cyl.json")
            unreviewed = mapping.get("by") in (None, "", "plataforma")
            if mapping.get("status") == "verified" and unreviewed:
                problems.add(mwhere, "una correspondencia verified necesita quién la validó")
    return [{**u, "available": u["id"] in by_id} for u in units]


def current_ids(concepts: list[dict], exercises: list[dict]) -> dict[str, list[str]]:
    return {
        "concepts": [c["id"] for c in concepts],
        "exercises": [e["id"] for e in exercises],
        "errors": [error["id"] for c in concepts for error in c["errors"]],
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


def check_lock(now: dict, problems: Problems) -> None:
    for kind, ids in locked_ids().items():
        lost = [i for i in ids if i not in now.get(kind, [])]
        if lost:
            problems.add(f"ids.lock.json ({kind})", f"ya no existen (hace falta migración): {lost}")


def knowledge_model(exercises: list[dict], problems: Problems) -> list[dict]:
    """Añade a cada concepto su módulo, RA, CE, dificultad e importancia (F1.4).

    - `ce` sale de CURRICULUM_CE y se comprueba contra el catálogo oficial (daw-cyl.json).
    - `module` y `ra` se derivan de los CE; `difficulty` es el nivel medio de sus ejercicios (1-3);
      `importance` es la importancia para DAW que ya tenía (`daw`, 1-3), con nombre explícito.
    """
    catalog = json.loads((DATA / "curriculum" / "daw-cyl.json").read_text("utf-8"))
    criteria = {
        ce["id"]
        for module in catalog["modules"]
        for ra in module.get("learningOutcomes", [])
        for ce in ra["criteria"]
    }
    ids = {c["id"] for c in CONCEPTS}
    for cid in sorted(set(CURRICULUM_CE) ^ ids):
        problems.add(f"concepto {cid}", "falta o sobra en CURRICULUM_CE")
    enriched = []
    for concept in CONCEPTS:
        ce = CURRICULUM_CE.get(concept["id"], [])
        for unknown in [c for c in ce if c not in criteria]:
            problems.add(f"concepto {concept['id']}", f"CE inexistente en daw-cyl.json: {unknown}")
        levels = [e["level"] for e in exercises if e["concept"] == concept["id"]]
        outcomes = sorted({c.rsplit("-", 1)[0] for c in ce}, key=lambda r: int(r.split("RA")[1]))
        enriched.append(
            {
                **concept,
                "module": sorted({c.split("-")[0] for c in ce})[0] if ce else None,
                "ra": outcomes,
                "ce": ce,
                "difficulty": round(sum(levels) / len(levels), 1) if levels else 1,
                "importance": concept["daw"],
            }
        )
    return enriched


def build() -> dict:
    problems = Problems()
    errors = check_concepts(problems)
    concepts = {c["id"] for c in CONCEPTS}
    ids = [e["id"] for e in E]
    if len(ids) != len(set(ids)):
        problems.add("ejercicios", "ids repetidos")
    for ex in E:
        check_exercise(ex, concepts, errors, problems)
    for concept in concepts:
        if not any(e["concept"] == concept for e in E):
            problems.add(f"concepto {concept}", "sin ejercicios")
    check_lock(current_ids(CONCEPTS, E), problems)
    units = check_units(problems)
    concepts_out = knowledge_model(E, problems)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    exercises = [{k: v for k, v in e.items() if not k.startswith("_")} for e in E]
    return {
        "version": 1,
        "areas": AREAS,
        "path": PATH,
        "daw": DAW_COMPETENCIES,
        "modules": [{**MODULE, "units": units}],
        "concepts": concepts_out,
        "exercises": exercises,
    }


def main() -> None:
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text("utf-8") != text:
            print(
                "learning.json no está al día: ejecuta python scripts/learning/build_learning.py",
                file=sys.stderr,
            )
            sys.exit(1)
        locked = locked_ids()
        if merged_lock(locked, current_ids(data["concepts"], data["exercises"])) != locked:
            print(
                "Hay ids nuevos sin registrar en ids.lock.json: "
                "ejecuta python scripts/learning/build_learning.py",
                file=sys.stderr,
            )
            sys.exit(1)
        print(
            f"learning.json al día: {len(data['concepts'])} conceptos, "
            f"{len(data['exercises'])} ejercicios comprobados"
        )
        return
    OUT.write_text(text, "utf-8", newline="\n")  # LF también en Windows
    lock = merged_lock(locked_ids(), current_ids(data["concepts"], data["exercises"]))
    LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=1) + "\n", "utf-8", newline="\n")
    print(
        f"Escrito {OUT.relative_to(ROOT)}: {len(data['concepts'])} conceptos, "
        f"{len(data['exercises'])} ejercicios"
    )


if __name__ == "__main__":
    main()
