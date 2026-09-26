"""Banco de preguntas del PCAP (frontend/data/pcap.json).

Cada pregunta lleva un `check`: código que DEMUESTRA en Python real que la respuesta
marcada es la correcta. Si alguien cambia una pregunta y se equivoca, este test falla.
"""

import contextlib
import io
import json

import pytest

from app.config import DEFAULT_LESSONS_FILE

PCAP = json.loads((DEFAULT_LESSONS_FILE.parent / "pcap.json").read_text(encoding="utf-8"))
EXAM = PCAP["exam"]
BLOCKS = {block["slug"]: block for block in EXAM["blocks"]}
QUESTIONS = PCAP["questions"]
LESSON_MODULES = {
    module["slug"]
    for module in json.loads(DEFAULT_LESSONS_FILE.read_text(encoding="utf-8"))["modules"]
}


def bilingual(value):
    return isinstance(value, dict) and value.get("es", "").strip() and value.get("en", "").strip()


def option_text(option):
    return option if isinstance(option, str) else option["en"]


def test_exam_matches_official_format():
    assert (EXAM["questions"], EXAM["minutes"], EXAM["pass"]) == (40, 65, 70)
    assert sum(block["weight"] for block in EXAM["blocks"]) == 100
    assert sum(block["items"] for block in EXAM["blocks"]) == EXAM["questions"]
    assert set(BLOCKS) <= LESSON_MODULES, "cada bloque del examen tiene su módulo de lecciones"


@pytest.mark.parametrize("slug", list(BLOCKS))
def test_each_block_has_enough_questions_for_varied_exams(slug):
    count = sum(1 for q in QUESTIONS if q["block"] == slug)
    assert count >= 3 * BLOCKS[slug]["items"], f"{slug}: {count} preguntas"


def test_ids_are_unique():
    ids = [q["id"] for q in QUESTIONS] + [c["id"] for c in PCAP["cards"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("question", QUESTIONS, ids=[q["id"] for q in QUESTIONS])
def test_question_is_well_formed_and_its_answer_is_proven(question, tmp_path, monkeypatch):
    assert question["block"] in BLOCKS
    assert bilingual(question["q"]) and bilingual(question["explain"])
    options = question["options"]
    assert 4 <= len(options) <= 5
    assert all(isinstance(o, str) or bilingual(o) for o in options)
    texts = [option_text(o) for o in options]
    assert len(set(texts)) == len(texts)
    answer = question["answer"]
    assert answer and len(set(answer)) == len(answer) and all(0 <= i < len(options) for i in answer)

    monkeypatch.chdir(tmp_path)
    output, error = io.StringIO(), None
    if question.get("code"):
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            try:
                exec(compile(question["code"], "<pregunta>", "exec"), {"__name__": "__main__"})
            except Exception as exc:  # la respuesta puede ser «se lanza X»
                error = type(exc).__name__
    namespace = {
        "__output__": output.getvalue(),
        "__error__": error,
        "options": texts,
        "answer": answer,
    }
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(question["check"], "<check>", "exec"), namespace)


def test_share_of_choose_two_questions():
    multi = sum(1 for q in QUESTIONS if len(q["answer"]) > 1) / len(QUESTIONS)
    assert 0.1 <= multi <= 0.3


@pytest.mark.parametrize("card", PCAP["cards"], ids=[c["id"] for c in PCAP["cards"]])
def test_card_is_bilingual(card, tmp_path, monkeypatch):
    assert card["block"] in BLOCKS and bilingual(card["front"]) and bilingual(card["back"])
    if card.get("code"):
        monkeypatch.chdir(tmp_path)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                exec(compile(card["code"], "<ficha>", "exec"), {"__name__": "__main__"})
            except Exception:
                assert card.get("raises"), (
                    "el código de la ficha falla sin estar marcado con raises"
                )


def test_choose_two_questions_say_so_in_both_languages():
    for q in QUESTIONS:
        if len(q["answer"]) > 1:
            assert "(Elige" in q["q"]["es"] and "(Choose" in q["q"]["en"], q["id"]


def test_shared_options_are_code_not_english_prose():
    """Una opción en texto plano se ve igual en los dos idiomas: solo vale para código o salidas."""
    prose = ("is raised", "exception is", "none of", "nothing is")
    for q in QUESTIONS:
        for option in q["options"]:
            if isinstance(option, str):
                assert not any(word in option.lower() for word in prose), f"{q['id']}: {option!r}"
