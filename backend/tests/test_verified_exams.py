"""Simulacros del PCAP verificados por el servidor (#109).

El servidor elige las preguntas, apunta la hora, corrige con el banco y no deja inventar la nota,
repetir la recompensa, entregar fuera de tiempo ni tocar los simulacros de otra cuenta.
"""

from collections import Counter
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import verified_exams as exams
from app.models import VerifiedExam
from app.rate_limit import write_limiter
from tests.conftest import login, register

URL = "/api/v1/verified/pcap-exams"


def start(client, headers):
    response = client.post(URL, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def right_answers(question_ids, how_many):
    """Las `how_many` primeras bien y el resto mal (o sin contestar)."""
    questions = exams.bank()["questions"]
    answers = {}
    for n, qid in enumerate(question_ids):
        good = questions[qid]["answer"]
        if n < how_many:
            answers[qid] = list(good)
        elif len(questions[qid]["options"]) > 1:
            answers[qid] = [next(i for i in range(len(questions[qid]["options"])) if i not in good)]
    return answers


def submit(client, headers, exam_id, answers):
    return client.post(f"{URL}/{exam_id}/answers", json={"answers": answers}, headers=headers)


def test_the_server_picks_the_real_exam_blueprint(client, auth_headers):
    exam = start(client, auth_headers)
    blueprint = exams.bank()["exam"]
    assert exam["exam_code"] == blueprint["code"]
    assert len(exam["question_ids"]) == blueprint["questions"] == len(set(exam["question_ids"]))
    blocks = Counter(exams.bank()["questions"][qid]["block"] for qid in exam["question_ids"])
    assert blocks == {b["slug"]: b["items"] for b in blueprint["blocks"]}
    started = datetime.fromisoformat(exam["started_at"])
    assert datetime.fromisoformat(exam["deadline"]) - started == timedelta(
        minutes=blueprint["minutes"]
    )


def test_the_server_grades_and_the_client_cannot_choose_the_score(client, auth_headers):
    exam = start(client, auth_headers)
    answers = right_answers(exam["question_ids"], 30)
    response = submit(client, auth_headers, exam["id"], answers)
    assert response.status_code == 200
    result = response.json()
    assert (result["correct"], result["total"], result["score"]) == (30, 40, 75)
    assert result["status"] == "finished" and result["passed"] is True
    # Un campo «score» inventado no cuenta: el esquema solo acepta respuestas
    forged = client.post(
        f"{URL}/{start(client, auth_headers)['id']}/answers",
        json={"answers": {}, "score": 100},
        headers=auth_headers,
    )
    assert forged.json()["score"] == 0  # nada contestado: 0, aunque diga 100


def test_repeating_a_submission_does_not_grade_twice(client, auth_headers):
    exam = start(client, auth_headers)
    answers = right_answers(exam["question_ids"], 20)
    first = submit(client, auth_headers, exam["id"], answers).json()
    again = submit(client, auth_headers, exam["id"], answers)
    assert again.status_code == 200 and again.json() == first
    better = submit(client, auth_headers, exam["id"], right_answers(exam["question_ids"], 40))
    assert better.status_code == 409  # no se puede volver a entregar con otras respuestas
    summary = client.get("/api/v1/verified", headers=auth_headers).json()
    assert [e["score"] for e in summary["exams"]] == [50]
    assert summary["best_score"] == 50 and summary["passed"] is False


def test_impossible_answers_are_rejected(client, auth_headers):
    exam = start(client, auth_headers)
    qid = exam["question_ids"][0]
    options = len(exams.bank()["questions"][qid]["options"])
    other = next(q for q in exams.bank()["questions"] if q not in exam["question_ids"])
    cases = {
        "pregunta de otro simulacro": {other: [0]},
        "id inventado": {"no-existe": [0]},
        "opción fuera de rango": {qid: [options]},
        "opción repetida": {qid: [0, 0]},
    }
    for case, answers in cases.items():
        response = submit(client, auth_headers, exam["id"], answers)
        assert response.status_code == 422, case
    assert submit(client, auth_headers, exam["id"], {qid: [-1]}).status_code == 422  # esquema
    too_many = list(range(len(exams.bank()["questions"][qid]["answer"]) + 1))
    assert submit(client, auth_headers, exam["id"], {qid: too_many}).status_code == 422
    # Tras los rechazos sigue en curso y se puede entregar bien
    assert submit(client, auth_headers, exam["id"], {}).json()["status"] == "finished"


def test_a_late_submission_is_not_graded(client, auth_headers):
    exam = start(client, auth_headers)
    late = datetime.now(UTC) - timedelta(minutes=exams.bank()["exam"]["minutes"]) - exams.GRACE
    with Session(client.engine) as db:
        db.execute(
            update(VerifiedExam).where(VerifiedExam.id == exam["id"]).values(started_at=late)
        )
        db.commit()
    response = submit(client, auth_headers, exam["id"], right_answers(exam["question_ids"], 40))
    assert response.status_code == 409
    assert submit(client, auth_headers, exam["id"], {}).status_code == 409  # ya no está en curso
    assert client.get("/api/v1/verified", headers=auth_headers).json()["exams"] == []


def test_starting_another_abandons_the_open_one(client, auth_headers):
    first = start(client, auth_headers)
    start(client, auth_headers)
    assert submit(client, auth_headers, first["id"], {}).status_code == 409
    with Session(client.engine) as db:
        statuses = list(db.scalars(select(VerifiedExam.status).order_by(VerifiedExam.id)))
    assert statuses == ["abandoned", "open"]


def test_only_a_few_verified_exams_a_day(client, auth_headers, monkeypatch):
    monkeypatch.setattr(exams.get_settings(), "verified_exams_per_day", 2)
    start(client, auth_headers)
    start(client, auth_headers)
    assert client.post(URL, headers=auth_headers).status_code == 429


def test_an_account_deleted_before_starting_gets_401(client, auth_headers):
    """La cuenta desaparece entre la autenticación y el bloqueo de su fila (PLD-001)."""
    from app.models import User
    from app.routers.verified import start_exam

    with Session(client.engine) as db:
        user = db.scalar(select(User))
        db.delete(user)
        db.flush()
        with pytest.raises(HTTPException) as error:
            start_exam(user, db)
        assert error.value.status_code == 401
        db.rollback()


def test_nobody_can_see_or_submit_another_users_exam(client, auth_headers):
    exam = start(client, auth_headers)
    register(client, email="eva@example.com", name="Eva")
    write_limiter.reset()
    eva = {
        "Authorization": f"Bearer {login(client, email='eva@example.com').json()['access_token']}"
    }
    assert submit(client, eva, exam["id"], {}).status_code == 404
    assert submit(client, eva, 999_999, {}).status_code == 404  # igual que uno que no existe
    assert client.get("/api/v1/verified", headers=eva).json()["exams"] == []
    assert submit(client, auth_headers, exam["id"], {}).status_code == 200  # el suyo sigue abierto


def test_it_needs_an_account(client):
    assert client.post(URL).status_code == 401
    assert client.get("/api/v1/verified").status_code == 401


def test_export_and_delete_include_verified_exams(client, auth_headers):
    exam = start(client, auth_headers)
    submit(client, auth_headers, exam["id"], {})
    export = client.get("/api/v1/users/me/export", headers=auth_headers).json()
    assert [e["score"] for e in export["verified_exams"]] == [0]
    from tests.conftest import PASSWORD

    response = client.post(
        "/api/v1/users/me/delete", json={"password": PASSWORD}, headers=auth_headers
    )
    assert response.status_code == 204
    with Session(client.engine) as db:
        assert db.scalars(select(VerifiedExam)).all() == []


def test_two_simultaneous_submissions_grade_once(client, auth_headers, monkeypatch):
    """Si otra petición entrega entre la lectura y la escritura, esta no corrige otra vez."""
    exam = start(client, auth_headers)
    answers = right_answers(exam["question_ids"], 10)
    real_grade = exams.grade

    def other_request_finishes_first(question_ids, given):
        with Session(client.engine) as db:
            db.execute(
                update(VerifiedExam)
                .where(VerifiedExam.id == exam["id"])
                .values(status="finished", answers=answers, correct=10, score=25)
            )
            db.commit()
        return real_grade(question_ids, given)

    monkeypatch.setattr(exams, "grade", other_request_finishes_first)
    same = submit(client, auth_headers, exam["id"], answers)
    assert same.status_code == 200 and same.json()["score"] == 25
    with Session(client.engine) as db:
        db.execute(update(VerifiedExam).values(status="open"))
        db.commit()
    other = submit(client, auth_headers, exam["id"], right_answers(exam["question_ids"], 40))
    assert other.status_code == 409  # la otra ya entregó con otras respuestas
