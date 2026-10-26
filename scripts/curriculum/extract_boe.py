"""Extrae del BOE los módulos técnicos de DAW, con sus RA y CE literales.

Lee el XML oficial del Real Decreto 405/2023 (artículo tercero, que reescribe el anexo I del
Real Decreto 686/2010) y escribe scripts/curriculum/rd_405_2023_daw.json. Ese JSON es la fuente
de build_curriculum.py y se guarda en el repositorio, así la CI no necesita red.

El texto se copia tal cual, erratas incluidas: los textos legales no tienen derechos de autor
(art. 13 de la Ley de Propiedad Intelectual) y no se deben retocar.

Uso:
  1. Descarga el XML: https://www.boe.es/diario_boe/xml.php?id=BOE-A-2023-13221
  2. python scripts/curriculum/extract_boe.py ruta/al/BOE-A-2023-13221.xml
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "rd_405_2023_daw.json"
BOE_ID = "BOE-A-2023-13221"
START = "Artículo tercero."  # actualización del Real Decreto 686/2010 (DAW)
END = "Disposición final primera."

MODULE = re.compile(r"^El módulo profesional (\d{4})\. (.+) queda redactado como sigue:$")
OUTCOME = re.compile(r"^(\d+)\. (.+)$")
CRITERION = re.compile(r"^([a-zñ])\) (.+)$")
BULLET = re.compile(r"^[−–-] ?(.+)$")


def paragraphs(xml_path: Path) -> list[str]:
    """Párrafos del artículo tercero, en orden y sin espacios sobrantes.

    NFC: algunos párrafos escriben las tildes como carácter combinado («o» + U+0301). Es el
    mismo texto, pero así todas las comparaciones funcionan igual."""
    root = ET.parse(xml_path).getroot()
    if root.findtext("metadatos/identificador") != BOE_ID:
        sys.exit(f"El XML no es el {BOE_ID}")
    texts = [
        unicodedata.normalize("NFC", " ".join("".join(p.itertext()).split()))
        for p in root.iter("p")
    ]
    start = next(i for i, t in enumerate(texts) if t.startswith(START))
    end = next(i for i, t in enumerate(texts) if i > start and t.startswith(END))
    return texts[start:end]


def parse_module(code: str, name: str, lines: list[str]) -> dict:
    module = {"code": code, "name": name, "ects": None, "stateMinHours": None}
    outcomes, contents, contribution = [], [], None
    section = None
    for line in lines:
        if match := re.match(r"^Equivalencia en créditos ECTS: (\d+)\.$", line):
            module["ects"] = int(match[1])
        elif match := re.match(r"^Duración: (\d+) horas\.$", line):
            module["stateMinHours"] = int(match[1])
            section = None
        elif line.startswith("Resultados de aprendizaje y criterios de evaluación"):
            section = "outcomes"
        elif line in ("Contenidos básicos:", "Contenidos."):  # 0615 usa «Contenidos.»
            section = "contents"
        elif line == "Orientaciones pedagógicas.":
            section = "guidance"
        elif section == "outcomes":
            if line == "Criterios de evaluación:":
                continue
            if (match := CRITERION.match(line)) and outcomes:
                outcomes[-1]["criteria"].append({"letter": match[1], "text": match[2]})
            elif match := OUTCOME.match(line):
                outcomes.append({"number": int(match[1]), "text": match[2], "criteria": []})
            else:
                sys.exit(f"{code}: línea inesperada en los resultados de aprendizaje: {line!r}")
        elif section == "contents":
            if match := BULLET.match(line):
                contents[-1]["items"].append(match[1])
            else:
                contents.append({"title": line.rstrip(":"), "items": []})
        elif section == "guidance" and line.startswith("La formación del módulo contribuye"):
            contribution = line
    module["learningOutcomes"] = outcomes
    module["contents"] = contents
    module["contribution"] = contribution
    return module


def extract(xml_path: Path) -> dict:
    lines = paragraphs(xml_path)
    starts = [(i, m) for i, line in enumerate(lines) if (m := MODULE.match(line))]
    modules = []
    for n, (i, match) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        modules.append(parse_module(match[1], match[2], lines[i + 1 : end]))
    return {
        "source": {
            "id": "rd-405-2023",
            "title": "Real Decreto 405/2023, de 29 de mayo (artículo tercero, anexo I)",
            "boe": BOE_ID,
            "url": f"https://www.boe.es/diario_boe/txt.php?id={BOE_ID}",
        },
        "modules": modules,
    }


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    data = extract(Path(sys.argv[1]))
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    OUT.write_text(text, "utf-8", newline="\n")  # LF también en Windows
    for module in data["modules"]:
        criteria = sum(len(o["criteria"]) for o in module["learningOutcomes"])
        print(
            f"{module['code']} {module['name']}: {len(module['learningOutcomes'])} RA, "
            f"{criteria} CE, {len(module['contents'])} bloques de contenidos"
        )


if __name__ == "__main__":
    main()
