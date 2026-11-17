"""Contrasta los casos de referencia del motor de fórmulas con LibreOffice (opcional, en local).

Crea un .xlsx con los datos y la fórmula de cada caso de `tests/fixtures/excel/reference-cases.json`
con fuente «libreoffice», lo recalcula con LibreOffice sin interfaz y compara el resultado con el
esperado. No forma parte de CI: necesita LibreOffice y openpyxl (pip install openpyxl).

Uso:  python scripts/excel/oracle_libreoffice.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from openpyxl import Workbook, load_workbook

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests" / "fixtures" / "excel" / "reference-cases.json"

# Español → inglés, como guarda Excel las fórmulas en un .xlsx
NAMES = {
    "SUMA": "SUM",
    "PROMEDIO": "AVERAGE",
    "MIN": "MIN",
    "MAX": "MAX",
    "CONTARA": "COUNTA",
    "CONTAR": "COUNT",
    "PRODUCTO": "PRODUCT",
    "REDONDEAR": "ROUND",
}
WORDS = {
    "VERDADERO": "TRUE",
    "FALSO": "FALSE",
    "#¡DIV/0!": "#DIV/0!",
    "#N/D": "#N/A",
    "#¡REF!": "#REF!",
}
ERRORS = {
    "#DIV/0!": "#¡DIV/0!",
    "#N/A": "#N/D",
    "#VALUE!": "#¡VALOR!",
    "#REF!": "#¡REF!",
    "#NAME?": "#¿NOMBRE?",
    "#NUM!": "#¡NUM!",
}


def to_english(formula: str) -> str:
    """Traduce fuera de los textos entre comillas: nombres, booleanos, «;» y la coma decimal."""
    out, i, text = [], 0, formula
    while i < len(text):
        ch = text[i]
        if ch == '"':
            j = i + 1
            while j < len(text):
                if text[j] == '"' and text[j + 1 : j + 2] == '"':
                    j += 2
                    continue
                if text[j] == '"':
                    break
                j += 1
            out.append(text[i : j + 1])
            i = j + 1
            continue
        if ch == "," and i > 0 and text[i - 1].isdigit() and text[i + 1 : i + 2].isdigit():
            out.append(".")
        elif ch == ";":
            out.append(",")
        else:
            longest = sorted(WORDS, key=len, reverse=True)
            word = next((w for w in longest if text.startswith(w, i)), None)
            if word:
                out.append(WORDS[word])
                i += len(word)
                continue
            name = next(
                (n for n in sorted(NAMES, key=len, reverse=True) if text.startswith(n + "(", i)),
                None,
            )
            if name and (i == 0 or not text[i - 1].isalpha()):
                out.append(NAMES[name])
                i += len(name)
                continue
            out.append(ch)
        i += 1
    return "".join(out)


def split(key: str, default: str) -> tuple[str, str]:
    sheet, _, cell = key.rpartition("!")
    return (sheet or default), cell.upper()


def main() -> None:
    soffice = shutil.which("soffice")
    if soffice is None:
        sys.exit("Hace falta LibreOffice (soffice)")
    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    selected = [c for c in cases if c["source"] == "libreoffice"]
    with tempfile.TemporaryDirectory() as tmp:
        book = Workbook()
        book.remove(book.active)
        for index, case in enumerate(selected):
            default = f"C{index}"
            sheets = {default: book.create_sheet(default)}
            for key, value in case.get("grid", {}).items():
                sheet, cell = split(key, default)
                name = default if sheet == default else f"{sheet}{index}"[:31]
                if name not in sheets:
                    sheets[name] = book.create_sheet(name)
                raw = value.get("f") if isinstance(value, dict) else value
                sheets[name][cell] = raw
            formula = to_english(case["formula"])
            for key in case.get("grid", {}):
                sheet, _ = split(key, default)
                if sheet != default:
                    quoted = f"'{sheet}'!" if " " in sheet else f"{sheet}!"
                    renamed = f"'{sheet}{index}'!" if " " in sheet else f"{sheet}{index}!"
                    formula = formula.replace(quoted, renamed)
                    formula = formula.replace(quoted.lower(), renamed)
            sheets[default]["Z200"] = formula
        source = Path(tmp) / "casos.xlsx"
        book.save(source)
        out = Path(tmp) / "out"
        subprocess.run(
            [soffice, "--headless", "--convert-to", "xlsx", "--outdir", str(out), str(source)],
            check=True,
            capture_output=True,
        )
        result = load_workbook(out / "casos.xlsx", data_only=True)
        failures = 0
        for index, case in enumerate(selected):
            got = result[f"C{index}"]["Z200"].value
            want = case["expect"]
            if isinstance(want, dict):
                ok = isinstance(got, str) and ERRORS.get(got, got) == want["error"]
            elif isinstance(want, bool):
                ok = got is want
            elif isinstance(want, (int, float)):
                ok = isinstance(got, (int, float)) and not isinstance(got, bool)
                ok = ok and abs(got - want) <= 1e-9 * max(1, abs(want))
            else:
                ok = (got or "") == want
            if not ok:
                failures += 1
                print(f"DIFERENCIA {case['id']}: {case['formula']}", end=" ")
                print(f"→ LibreOffice {got!r}, esperado {want!r}")
        print(f"{len(selected) - failures} de {len(selected)} casos coinciden con LibreOffice")
        sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
