"""Genera frontend/data/curriculum/daw-cyl.json: el catálogo del ciclo de DAW en Castilla y León.

Junta tres fuentes y deja constancia de cada una:
- La Orden EDU/1311/2024 (BOCYL): módulos, horas, curso y horas semanales en Castilla y León.
- El Real Decreto 405/2023 (BOE): ECTS, resultados de aprendizaje, criterios de evaluación y
  contenidos básicos de los módulos técnicos, extraídos literalmente por extract_boe.py.
- La plataforma: cada pregunta de frontend/data/courses/<curso>/bank.json lleva el código del módulo
  que trabaja (campo `module`, lo pone scripts/courses/). De ahí salen los cursos y el número de
  preguntas de cada módulo. Es una relación con el módulo, no con criterios concretos, porque esa
  relación aún no la ha revisado nadie.

Lo que no tiene fuente comprobada se queda en `null` con `status: "pendiente"`. No se inventa nada.

Uso:  python scripts/curriculum/build_curriculum.py           (genera)
      python scripts/curriculum/build_curriculum.py --check   (CI: falla si el JSON no está al día)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "frontend" / "data"
OUT = DATA / "curriculum" / "daw-cyl.json"
RD_405 = HERE / "rd_405_2023_daw.json"
TOTAL_HOURS = 2000
WEEKLY_HOURS = 30  # por curso, anexo II de la orden

SOURCES = [
    {
        "id": "orden-edu-1311-2024",
        "title": "Orden EDU/1311/2024, de 26 de noviembre (BOCYL núm. 234, 2/12/2024)",
        "what": "Duración, curso y horas semanales de cada módulo (anexos I y II)",
        "url": "https://bocyl.jcyl.es/boletines/2024/12/02/pdf/BOCYL-D-02122024-27.pdf",
    },
    {
        "id": "rd-405-2023",
        "title": "Real Decreto 405/2023, de 29 de mayo (artículo tercero, anexo I)",
        "what": "ECTS, resultados de aprendizaje, criterios de evaluación y contenidos básicos",
        "url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-13221",
    },
    {
        "id": "rd-500-2024",
        "title": "Real Decreto 500/2024, de 21 de mayo (artículo séptimo)",
        "what": "Suprime FOL, EIE y FCT, añade los módulos transversales y renombra el proyecto",
        "url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-10685",
    },
    {
        "id": "rd-659-2023",
        "title": "Real Decreto 659/2023, de 18 de julio (anexos V, VII, VIII y X)",
        "what": "Resultados de aprendizaje de los módulos transversales (sin extraer todavía)",
        "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2023-16889",
    },
]

# Orden EDU/1311/2024: (código, nombre, horas, curso, horas semanales). Código None = optativo.
CYL_MODULES = [
    ("0373", "Lenguajes de marcas y sistemas de gestión de información", 102, 1, 3),
    ("0483", "Sistemas informáticos", 170, 1, 5),
    ("0484", "Bases de datos", 170, 1, 5),
    ("0485", "Programación", 272, 1, 8),
    ("0487", "Entornos de desarrollo", 68, 1, 2),
    ("0179", "Inglés profesional (GS)", 68, 1, 2),
    ("1709", "Itinerario personal para la empleabilidad I", 102, 1, 3),
    (None, "Módulo optativo I", 34, 1, 2),
    ("1665", "Digitalización aplicada a los sectores productivos (GS)", 34, 2, 1),
    ("0612", "Desarrollo web en entorno cliente", 231, 2, 7),
    ("0613", "Desarrollo web en entorno servidor", 264, 2, 8),
    ("0614", "Despliegue de aplicaciones web", 99, 2, 3),
    ("0615", "Diseño de interfaces web", 165, 2, 5),
    ("1708", "Sostenibilidad aplicada al sistema productivo", 34, 2, 1),
    ("1710", "Itinerario personal para la empleabilidad II", 68, 2, 2),
    (None, "Módulo optativo II", 54, 2, 3),
    # La tabla del anexo I no indica curso ni horas semanales para el proyecto
    ("0616", "Proyecto intermodular de desarrollo de aplicaciones web", 65, None, None),
]

# Dónde están los RA de los módulos que no vienen en el RD 405/2023 (RD 500/2024, art. séptimo)
PENDING_OUTCOMES = {
    "0179": "rd-659-2023#anexo-X",
    "1709": "rd-659-2023#anexo-V",
    "1710": "rd-659-2023#anexo-V",
    "1665": "rd-659-2023#anexo-VII",
    "1708": "rd-659-2023#anexo-VIII",
    "0616": None,
}

NOTES = {
    "0616": "La tabla del anexo I no indica el curso. Por la suma de horas (1.014 en 2º) sería 2º: "
    "pendiente de confirmar.",
    "optativo-1": "34 horas con 2 horas semanales: no cuadra con un curso completo. Pendiente de "
    "confirmar con el centro qué optativo se imparte.",
    "optativo-2": "Pendiente de confirmar con el centro qué optativo se imparte.",
}


class Problems(list):
    def add(self, where: str, what: str) -> None:
        self.append(f"{where}: {what}")


def module_id(code: str | None, name: str) -> str:
    return code or ("optativo-1" if name.endswith(" I") else "optativo-2")


def outcomes_of(code: str, official: dict) -> list[dict]:
    return [
        {
            "id": f"{code}-RA{o['number']}",
            "number": o["number"],
            "text": o["text"],
            "criteria": [
                {"id": f"{code}-RA{o['number']}-{c['letter']}", **c} for c in o["criteria"]
            ],
        }
        for o in official["learningOutcomes"]
    ]


def questions_by_module(problems: Problems) -> dict[str, dict[str, list[str]]]:
    """Código de módulo -> {curso: ids de sus preguntas}, leído de los bancos de los cursos.

    El panel del alumno usa los ids para calcular el progreso por módulo sin descargar los
    bancos."""
    found: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for bank in sorted((DATA / "courses").glob("*/bank.json")):
        course_id = bank.parent.name
        for q in json.loads(bank.read_text("utf-8"))["questions"]:
            if not q.get("module"):
                problems.add(f"{course_id}/{q['id']}", "pregunta sin módulo")
            else:
                found[q["module"]][course_id].append(q["id"])
    return found


def build() -> dict:
    rd = json.loads(RD_405.read_text("utf-8"))
    official = {m["code"]: m for m in rd["modules"]}
    source_ids = {s["id"] for s in SOURCES}
    problems = Problems()
    tagged = questions_by_module(problems)
    modules = []

    for code, name, hours, course, weekly in CYL_MODULES:
        mid = module_id(code, name)
        module = {
            "id": mid,
            "code": code,
            "name": name,
            "course": course,
            "hours": hours,
            "weeklyHours": weekly,
            "source": "orden-edu-1311-2024#anexo-I",
        }
        if code in official:
            rd_module = official[code]
            if rd_module["name"].casefold() != name.casefold():
                problems.add(code, f"el nombre del BOE es «{rd_module['name']}»")
            module |= {
                "ects": rd_module["ects"],
                "stateMinHours": rd_module["stateMinHours"],
                "learningOutcomes": outcomes_of(code, rd_module),
                "contents": rd_module["contents"],
                "contribution": rd_module["contribution"],
                "outcomesSource": "rd-405-2023#anexo-I",
                "status": "oficial",
            }
        else:
            module |= {
                "ects": None,
                "stateMinHours": None,
                "learningOutcomes": [],
                "contents": [],
                "contribution": None,
                "outcomesSource": PENDING_OUTCOMES.get(code),
                "status": "pendiente",
            }
        by_course = tagged.get(code, {})
        # Primero el curso con más preguntas del módulo; a igualdad, por nombre
        module["platformCourses"] = sorted(by_course, key=lambda c: (-len(by_course[c]), c))
        module["platformQuestions"] = sum(len(ids) for ids in by_course.values())
        module["platformQuestionIds"] = {c: by_course[c] for c in module["platformCourses"]}
        if mid in NOTES:
            module["note"] = NOTES[mid]
        modules.append(module)

    codes = {m["code"] for m in modules}
    for code in sorted(set(tagged) - codes):
        problems.add(f"módulo {code}", "lo usan preguntas de los cursos, pero no está en la orden")
    _validate(modules, official, source_ids, problems)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    return {
        "version": 1,
        "cycle": {
            "id": "daw",
            "name": "Técnico Superior en Desarrollo de Aplicaciones Web",
            "region": "Castilla y León",
            "hours": TOTAL_HOURS,
        },
        "notice": "Las actividades de la plataforma son prácticas y no son evaluaciones oficiales "
        "del centro.",
        "sources": SOURCES,
        "modules": modules,
    }


def _validate(modules, official, source_ids, problems) -> None:
    codes = [m["code"] for m in modules if m["code"]]
    if len(codes) != len(set(codes)):
        problems.add("módulos", "hay códigos repetidos")
    if missing := set(official) - set(codes):
        problems.add("RD 405/2023", f"módulos sin entrada en la orden: {sorted(missing)}")
    if (total := sum(m["hours"] for m in modules)) != TOTAL_HOURS:
        problems.add("horas", f"suman {total}, no {TOTAL_HOURS}")
    for course in (1, 2):
        weekly = sum(m["weeklyHours"] or 0 for m in modules if m["course"] == course)
        if weekly != WEEKLY_HOURS:
            problems.add(f"{course}º curso", f"{weekly} horas semanales, no {WEEKLY_HOURS}")
    for m in modules:
        where = m["code"] or m["id"]
        for ref in (m["source"], m["outcomesSource"]):
            if ref and ref.split("#")[0] not in source_ids:
                problems.add(where, f"fuente desconocida {ref}")
        if m["status"] == "oficial":
            if not m["learningOutcomes"]:
                problems.add(where, "sin resultados de aprendizaje")
            for ra in m["learningOutcomes"]:
                if not ra["text"] or not ra["criteria"]:
                    problems.add(ra["id"], "sin texto o sin criterios")


def main() -> None:
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    official = [m for m in data["modules"] if m["status"] == "oficial"]
    outcomes = sum(len(m["learningOutcomes"]) for m in official)
    criteria = sum(len(ra["criteria"]) for m in official for ra in m["learningOutcomes"])
    summary = (
        f"{len(data['modules'])} módulos ({len(official)} con RA oficiales), "
        f"{outcomes} RA y {criteria} CE"
    )
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text("utf-8") != text:
            print(
                "daw-cyl.json no está al día: python scripts/curriculum/build_curriculum.py",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"daw-cyl.json al día: {summary}")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, "utf-8", newline="\n")  # LF también en Windows
    print(f"Escrito {OUT.relative_to(ROOT)}: {summary}")


if __name__ == "__main__":
    main()
