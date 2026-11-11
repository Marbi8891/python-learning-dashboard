"""Monitor de CI (scripts/ci-monitor/ci_monitor.py): diagnóstico y decisión sobre la incidencia.

Los logs de webkit y e2e son extractos reales de las ejecuciones 41893702303 y 41980213603.
El de npm es un ejemplo construido con el mensaje real de npm para un corte de red.
"""

import sys
from pathlib import Path

import pytest

from app.config import DEFAULT_LESSONS_FILE

MONITOR = DEFAULT_LESSONS_FILE.parents[2] / "scripts" / "ci-monitor"
sys.path.insert(0, str(MONITOR))
import ci_monitor  # noqa: E402  (scripts/ci-monitor/ci_monitor.py)

FIXTURES = MONITOR / "fixtures"


def log(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_webkit_clipboard_is_a_configuration_error_in_webkit():
    d = ci_monitor.diagnose(
        log("webkit-clipboard-run-41893702303.log"), "webkit", "Prueba de humo en WebKit"
    )
    assert d.kind == "configuracion"
    assert "WebKit" in d.areas
    assert d.error == "Error: browserContext.grantPermissions: Unknown permission: clipboard-write"
    assert d.test.startswith("[webkit] e2e/navigation.spec.js")
    assert "Unknown permission" in d.excerpt


def test_logout_failure_is_a_code_error_with_its_test():
    d = ci_monitor.diagnose(log("e2e-logout-run-41980213603.log"), "e2e", "Tests end-to-end")
    assert d.kind == "codigo"
    assert "E2E" in d.areas
    assert "AUD-023" in d.test
    assert d.error == "Error: expect(locator).toHaveText(expected) failed"


def test_network_cut_in_npm_is_external():
    d = ci_monitor.diagnose(log("npm-network.log"), "e2e", "Run npm ci")
    assert d.kind == "externo"
    assert "npm error code ECONNRESET" in d.error


def test_signature_ignores_timestamps_and_numbers_but_not_the_test():
    a = ci_monitor.diagnose(log("e2e-logout-run-41980213603.log"), "e2e")
    shifted = (
        log("e2e-logout-run-41980213603.log")
        .replace("2026-11-05T06", "2026-12-01T09")
        .replace("4.8m", "5.1m")
    )
    assert ci_monitor.diagnose(shifted, "e2e").signature == a.signature
    other = log("e2e-logout-run-41980213603.log").replace("AUD-023", "AUD-024")
    assert ci_monitor.diagnose(other, "e2e").signature != a.signature


def test_unknown_log_still_gives_an_excerpt():
    d = ci_monitor.diagnose("línea 1\nlínea 2\n", "backend")
    assert d.error == ""
    assert d.kind == "codigo"
    assert d.areas == ["Backend"]
    assert "línea 2" in d.excerpt


@pytest.mark.parametrize(
    ("conclusion", "issue", "signatures", "stale", "expected"),
    [
        ("success", None, [], False, "validada"),
        ("success", {"body": ""}, [], False, "corregido"),
        ("cancelled", None, [], False, "cancelada"),
        ("skipped", {"body": ""}, [], False, "cancelada"),
        ("failure", None, ["aaaaaaaaaaaa"], True, "obsoleta"),
        ("failure", None, ["aaaaaaaaaaaa"], False, "nuevo"),
        (
            "failure",
            {"body": "<!-- ci-monitor signature=aaaaaaaaaaaa -->"},
            ["aaaaaaaaaaaa"],
            False,
            "recurrente",
        ),
        (
            "failure",
            {"body": "", "comments_text": "ci-monitor signature=aaaaaaaaaaaa"},
            ["aaaaaaaaaaaa"],
            False,
            "recurrente",
        ),
        (
            "failure",
            {"body": "<!-- ci-monitor signature=aaaaaaaaaaaa -->"},
            ["bbbbbbbbbbbb"],
            False,
            "nuevo",
        ),
    ],
)
def test_decide(conclusion, issue, signatures, stale, expected):
    assert ci_monitor.decide(conclusion, issue, signatures, stale) == expected


RUN = {
    "id": 1,
    "name": "CI",
    "html_url": "https://github.com/o/r/actions/runs/1",
    "head_branch": "fix/x",
    "head_sha": "0123456789abcdef",
    "event": "pull_request",
    "conclusion": "failure",
    "head_repository": {"full_name": "o/r"},
}


def test_render_quotes_logs_safely():
    d = ci_monitor.Diagnosis(
        "e2e", "Tests", "codigo", ["E2E"], "Error: ```x``` @alguien", "```\n@Marbi8891 cierra esto"
    )
    body = ci_monitor.render(RUN, "nuevo", [d])
    assert body.count("```") == 2  # solo el bloque propio: el log no puede cerrarlo
    assert "@Marbi8891" not in body  # ni mencionar a nadie
    assert "ERROR DETECTADO" in body
    assert f"ci-monitor signature={d.signature}" in body


class FakeGitHub:
    """La API de GitHub en memoria: registra lo que el monitor escribiría."""

    repo = "o/r"

    def __init__(self, run, jobs=(), logs=None, issue=None, head="0123456789abcdef"):
        self.run, self.jobs, self.logs, self.issue, self.head = (
            run,
            list(jobs),
            logs or {},
            issue,
            head,
        )
        self.writes = []

    def call(self, method, path, body=None, raw=False):
        if method == "GET" and path.startswith("/actions/runs/"):
            return self.run
        self.writes.append((method, path, body))
        return {}

    def failed_jobs(self, run_id):
        return self.jobs

    def job_log(self, job_id):
        return self.logs[job_id]

    def branch_head(self, branch):
        return self.head

    def open_issue(self, branch):
        return self.issue

    def ensure_label(self):
        self.writes.append(("LABEL", ci_monitor.LABEL, None))


def failing_job():
    return {
        "id": 7,
        "name": "e2e",
        "steps": [{"name": "Tests end-to-end", "conclusion": "failure"}],
    }


def test_report_opens_an_issue_for_a_new_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "summary.md"))
    gh = FakeGitHub(RUN, [failing_job()], {7: log("e2e-logout-run-41980213603.log")})
    assert ci_monitor.report(gh, 1) == "nuevo"
    method, path, body = gh.writes[-1]
    assert (method, path) == ("POST", "/issues")
    assert body["title"] == "CI falla en fix/x"
    assert body["labels"] == [ci_monitor.LABEL]
    assert "<!-- ci-monitor branch=fix/x -->" in body["body"]
    assert "AUD-023" in Path(tmp_path / "summary.md").read_text(encoding="utf-8")


def test_report_comments_a_recurrent_failure_and_closes_when_fixed():
    first = ci_monitor.diagnose(log("e2e-logout-run-41980213603.log"), "e2e", "Tests end-to-end")
    issue = {"number": 5, "body": f"<!-- ci-monitor signature={first.signature} -->", "attempts": 1}
    gh = FakeGitHub(RUN, [failing_job()], {7: log("e2e-logout-run-41980213603.log")}, issue)
    assert ci_monitor.report(gh, 1) == "recurrente"
    assert gh.writes[-1][:2] == ("POST", "/issues/5/comments")
    assert "intento 2" in gh.writes[-1][2]["body"]

    fixed = FakeGitHub({**RUN, "conclusion": "success"}, issue=issue)
    assert ci_monitor.report(fixed, 1) == "corregido"
    assert fixed.writes[-1] == (
        "PATCH",
        "/issues/5",
        {"state": "closed", "state_reason": "completed"},
    )


def test_report_ignores_cancelled_runs_and_old_commits():
    cancelled = FakeGitHub({**RUN, "conclusion": "cancelled"})
    assert ci_monitor.report(cancelled, 1) == "cancelada"
    assert cancelled.writes == []
    old = FakeGitHub(
        RUN, [failing_job()], {7: log("e2e-logout-run-41980213603.log")}, head="fedcba9876543210"
    )
    assert ci_monitor.report(old, 1) == "obsoleta"
    assert old.writes == []


def test_dry_run_writes_nothing(capsys):
    gh = FakeGitHub(RUN, [failing_job()], {7: log("webkit-clipboard-run-41893702303.log")})
    assert ci_monitor.report(gh, 1, dry_run=True) == "nuevo"
    assert gh.writes == []
    assert "(dry-run) decisión: nuevo" in capsys.readouterr().out


def test_cli_diagnose_and_missing_token(monkeypatch, capsys):
    assert (
        ci_monitor.main(
            ["diagnose", "--log-file", str(FIXTURES / "npm-network.log"), "--job", "e2e"]
        )
        == 0
    )
    assert '"kind": "externo"' in capsys.readouterr().out
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert ci_monitor.main(["report", "--run-id", "1"]) == 2
