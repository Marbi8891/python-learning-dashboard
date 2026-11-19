"""Generador de cursos: ejercicios de fórmulas de Excel y cursos sin módulo oficial (academia).

Ejecuta el motor de fórmulas con Node, como en CI:
    python -m unittest discover -s scripts/courses/tests
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from course_builder import Block, Lesson, Q, build  # noqa: E402

IVA = {
    "grid": {"B1": "Base", "B2": 100, "B3": 250, "B4": 80, "D1": "IVA", "E1": 0.21},
    "cell": "D2",
    "expect": 21,
    "checks": [
        {"type": "value"},
        {"type": "fill", "to": "D4", "expect": [52.5, 16.8]},
        {"type": "references", "must": ["B2", "$E$1"]},
        {"type": "noConstants"},
    ],
    "hints": ["Si copias =B2*E1 hacia abajo, ¿qué pasa con E1?"],
    "solution": {"formula": "=B2*$E$1", "explain": "$E$1 no cambia al copiarla."},
    "mistakes": [{"error": "=B2*E1", "fix": "Al copiarla, E1 pasa a E2, que está vacía."}],
}

CONTAR = {
    "grid": {"A2": "F-001", "A3": 120, "A5": "pendiente", "A6": 80},
    "formula": "=CONTAR(A2:A6)",
    "input": "number",
    "answer": 2,
}


def lesson(questions: list[Q]) -> Lesson:
    return Lesson(
        slug="xl-prueba",
        title="Unidad de prueba",
        theory="Teoría.",
        example="",
        exercise="Ejercicio.",
        starter="",
        hint="Pista.",
        faq=[],
        challenge=("Reto", 1, "Enunciado.", "", "Pista."),
        questions=questions,
        quiz=[],
        sources=[],
    )


def build_course(questions: list[Q]) -> dict[str, dict]:
    blocks = [Block("m01", "Módulo de prueba", "Resumen.", 100, [lesson(questions)])]
    files = build("excel", blocks, runner=lambda code: "", examples=lambda code: None, module=None)
    return {name: json.loads(text) for name, text in files.items()}


class ExcelBuilderTest(unittest.TestCase):
    def test_formula_exercises_are_checked_and_published(self) -> None:
        course = build_course(
            [
                Q(id="xl-iva", q="IVA", explain="$E$1 absoluta.", kind="formula", excel=IVA),
                Q(id="xl-contar", q="¿Qué da?", explain=".", kind="formula-result", excel=CONTAR),
            ]
        )
        bank = course["bank.json"]
        self.assertEqual(bank["engine"], "1.1.0")
        first, second = bank["questions"]
        self.assertEqual(first["kind"], "formula")
        self.assertEqual(first["excel"]["solution"]["formula"], "=B2*$E$1")
        self.assertEqual(second["kind"], "formula-result")
        # Sin módulo oficial: ni módulo ni mapa del currículo de DAW
        for question in bank["questions"]:
            self.assertNotIn("module", question)
            self.assertNotIn("curriculum", question)
        self.assertNotIn("curriculum", course["lessons.json"]["modules"][0]["lessons"][0])

    def test_wrong_author_answer_stops_the_build(self) -> None:
        wrong = {**CONTAR, "answer": 4}  # CONTARA daría 4; CONTAR da 2
        with self.assertRaisesRegex(AssertionError, "el motor da 2"):
            build_course([Q(id="xl-mal", q="?", explain=".", kind="formula-result", excel=wrong)])

    def test_mistake_that_passes_stops_the_build(self) -> None:
        # Sin la comprobación de copia, el error frecuente =B2*E1 pasaría por bueno
        weak = {**IVA, "checks": [{"type": "value"}]}
        with self.assertRaisesRegex(AssertionError, "pasa todas las comprobaciones"):
            build_course([Q(id="xl-debil", q="?", explain=".", kind="formula", excel=weak)])

    def test_formula_kind_without_data_is_rejected(self) -> None:
        with self.assertRaisesRegex(AssertionError, "faltan los datos del ejercicio"):
            build_course([Q(id="xl-vacio", q="?", explain=".", kind="formula")])


if __name__ == "__main__":
    unittest.main()
