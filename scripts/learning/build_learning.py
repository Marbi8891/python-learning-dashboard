"""Genera frontend/data/learning.json (conceptos y ejercicios) y comprueba las respuestas.

Ver ADR-0031.

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
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "frontend" / "data"
OUT = DATA / "learning.json"
TIMEOUT_S = 5

sys.path.insert(0, str(HERE))
from concepts import AREAS, CONCEPTS, PATH  # noqa: E402
from exercises import E  # noqa: E402

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
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    exercises = [{k: v for k, v in e.items() if not k.startswith("_")} for e in E]
    return {
        "version": 1,
        "areas": AREAS,
        "path": PATH,
        "concepts": CONCEPTS,
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
        print(
            f"learning.json al día: {len(data['concepts'])} conceptos, "
            f"{len(data['exercises'])} ejercicios comprobados"
        )
        return
    OUT.write_text(text, "utf-8")
    print(
        f"Escrito {OUT.relative_to(ROOT)}: {len(data['concepts'])} conceptos, "
        f"{len(data['exercises'])} ejercicios"
    )


if __name__ == "__main__":
    main()
