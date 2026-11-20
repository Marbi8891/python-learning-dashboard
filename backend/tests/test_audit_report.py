"""Project Auditor (scripts/audit): informe, puntuación, plan y la CLI de punta a punta.

Los informes de agentes de scripts/audit/fixtures/ son EJEMPLOS FICTICIOS.
"""

import json
import shutil
import sys

import pytest

from app.config import DEFAULT_LESSONS_FILE

REPO = DEFAULT_LESSONS_FILE.parents[2]
AUDIT = REPO / "scripts" / "audit"
sys.path.insert(0, str(AUDIT))
import auditor  # noqa: E402
from pld_audit import checks, plan, registry, report  # noqa: E402

FIXTURES = AUDIT / "fixtures"


@pytest.fixture
def project(tmp_path):
    """Copia de la configuración real con una prueba que pasa y otra que falla."""
    text = (REPO / "project-auditor.toml").read_text(encoding="utf-8")
    text = text[: text.index("[[checks]]")]
    text += """
[[checks]]
id = "ok"
name = "Siempre pasa"
category = "testing"
cmd = ["{python}", "-c", "print('bien')"]

[[checks]]
id = "ko"
name = "Siempre falla"
category = "testing"
cmd = ["{python}", "-c", "import sys; print('roto'); sys.exit(3)"]

[[checks]]
id = "lejos"
name = "Necesita deep"
category = "ux-accessibility"
depth = "deep"
cmd = ["{python}", "-c", "pass"]
"""
    (tmp_path / "project-auditor.toml").write_text(text, encoding="utf-8")
    for name in ("ejemplo-1-revision.md", "ejemplo-1-red-team.md", "ejemplo-2-revision.md"):
        shutil.copy(FIXTURES / name, tmp_path / name)
    return tmp_path


def run(project, *args):
    return auditor.main(["--config", str(project / "project-auditor.toml"), *args])


def out_dir(project):
    return project / ".claude" / "informes" / "audit"


def test_two_audits_end_to_end(project, capsys):
    assert run(project, "checks", "--out", str(project / "c1.json")) == 0
    c1 = json.loads((project / "c1.json").read_text(encoding="utf-8"))
    assert {c["id"]: c["status"] for c in c1["checks"]} == {
        "ok": "passed",
        "ko": "failed",
        "lejos": "not_run",
    }
    assert run(project, "checks", "--strict", "--out", str(project / "c1b.json")) == 1

    assert (
        run(
            project,
            "audit",
            "--scope",
            "all",
            "--run-id",
            "R1",
            "--checks",
            str(project / "c1.json"),
            str(project / "ejemplo-1-revision.md"),
            str(project / "ejemplo-1-red-team.md"),
        )
        == 0
    )
    out = out_dir(project)
    first = (out / "latest-audit.md").read_text(encoding="utf-8")
    assert first == (out / "history" / "R1.md").read_text(encoding="utf-8")
    for heading in (
        "Executive Summary",
        "Project Health Score",
        "Critical Findings",
        "Security Findings",
        "Functional Bugs",
        "Architecture Review",
        "Performance Review",
        "Code Quality",
        "Testing Review",
        "UX and Accessibility",
        "Dependencies",
        "Technical Debt",
        "Recommended Actions",
        "Positive Findings",
    ):
        assert f"## {heading}" in first, heading
    assert "evaluación heurística" in first and "Primera auditoría" in first
    assert "AUD-003 · Falta límite de intentos" in first and "ref. RT-900" in first
    assert "Sospecha" in first and "APPROVAL REQUIRED" in first  # seguridad pide aprobación
    assert "Falla la prueba «Siempre falla»" in first and "roto" in first
    assert "1 hallazgo(s) rechazados" in first and "necesita evidencia" in first
    assert "`lejos` (necesita profundidad «deep»; esta ejecución: «standard»)" in first
    assert "funciones puras con tests" in first  # hallazgo positivo del agente
    reg = registry.load(out / "registry.json")
    assert [r["id"] for r in registry.open_findings(reg)] == [
        "AUD-003",  # P1 HIGH (empate con AUD-004: decide el id)
        "AUD-004",
        "AUD-001",
        "AUD-002",
    ]

    # Segunda auditoría: la prueba ya pasa, un bug cambia, uno nuevo y una resolución.
    c2 = dict(c1)
    c2["checks"] = [dict(c, status="passed") if c["id"] == "ko" else c for c in c1["checks"]]
    (project / "c2.json").write_text(json.dumps(c2), encoding="utf-8")
    assert (
        run(
            project,
            "audit",
            "--scope",
            "bugs,code-quality,ux-accessibility,security",
            "--run-id",
            "R2",
            "--checks",
            str(project / "c2.json"),
            str(project / "ejemplo-2-revision.md"),
        )
        == 0
    )
    second = (out / "latest-audit.md").read_text(encoding="utf-8")
    assert "Comparado con R1" in second
    assert "**Nuevos:** 1 · **Resueltos:** 2 · **Regresiones:** 0 · **Cambiados:** 1" in second
    assert "AUD-001 · El temporizador del simulacro no se detiene al salir · **cambiado**" in second
    assert "**Antes:** MEDIUM / P2" in second
    assert "AUD-005 · Imagen de portada sin texto alternativo · **nuevo**" in second
    assert "&lt;img&gt; decorativa sin alt." in second and "<img>" not in second
    assert "AUD-002 · Función de render de 180 líneas (1 auditoría(s) sin verlo)" in second
    assert "la prueba «ko» ha pasado en R2" in second
    assert (
        "Siguen abiertos sin cambios"
        not in second.split("## Code Quality")[0].split("## Functional Bugs")[1]
    )
    assert "| AUD-002 | Función de render de 180 líneas | LOW | P3 | R1 |" in second
    assert second.count("#### AUD-002") == 0  # no se repite el detalle de lo que no cambia
    assert (out / "history" / "R1.md").exists() and (out / "runs" / "R2.json").exists()
    reg = registry.load(out / "registry.json")
    assert [r["run_id"] for r in reg["runs"]] == ["R1", "R2"]
    assert reg["runs"][1]["score"] > reg["runs"][0]["score"]

    capsys.readouterr()
    assert run(project, "context", "--since", "HEAD") == 0
    context = json.loads(capsys.readouterr().out)
    assert context["last_audit"]["run_id"] == "R2"
    assert {f["id"] for f in context["open_findings"]} == {"AUD-001", "AUD-002", "AUD-005"}

    assert run(project, "plan", "--min-priority", "P2") == 0
    text = (out / "plan-latest.md").read_text(encoding="utf-8")
    assert text.index("## P1") < text.index("## P2") and "AUD-002" not in text
    assert "SAFE FIX" in text and "auditor.py checks --only" in text

    assert run(project, "preflight-fix", "AUD-404") == 2
    assert run(project, "preflight-fix", "AUD-001") == 1  # modo read-only
    assert "desactivado" in capsys.readouterr().out


def test_tests_only_audit_says_the_code_was_not_reviewed(project):
    assert run(project, "checks", "--out", str(project / "c.json")) == 0
    assert run(project, "audit", "--scope", "", "--checks", str(project / "c.json")) == 0
    text = (out_dir(project) / "latest-audit.md").read_text(encoding="utf-8")
    assert "Sin revisión de agentes" in text and "ninguna (solo pruebas)" in text


def test_cli_rejects_bad_input(project, capsys):
    assert run(project, "checks", "--only", "nope") == 2
    assert run(project, "audit", "--scope", "magia") == 2
    (project / "project-auditor.toml").write_text('[auditor]\nmode = "x"', encoding="utf-8")
    assert run(project, "plan") == 2
    assert "Configuración no válida" in capsys.readouterr().err


def test_compare_checks_cli(project, capsys):
    def write(name, status):
        res = checks.CheckResult("a", "A", "testing", "HIGH", status, "x").to_dict()
        (project / name).write_text(json.dumps({"checks": [res]}), encoding="utf-8")

    write("antes.json", "passed")
    write("despues.json", "failed")
    before, after = str(project / "antes.json"), str(project / "despues.json")
    assert run(project, "compare-checks", before, after) == 1
    assert "a: passed → failed" in capsys.readouterr().out
    assert run(project, "compare-checks", before, before) == 0
    assert "Ninguna prueba" in capsys.readouterr().out


def test_run_ids_do_not_collide(tmp_path):
    from datetime import UTC, datetime

    now = datetime(2026, 11, 20, 15, 0, tzinfo=UTC)
    assert auditor.new_run_id(tmp_path, now) == "20261120T1500Z"
    (tmp_path / "history").mkdir()
    (tmp_path / "history" / "20261120T1500Z.md").write_text("")
    assert auditor.new_run_id(tmp_path, now) == "20261120T1500Z-2"


def test_score_and_label():
    weights = {
        "critical": 25,
        "high": 10,
        "medium": 4,
        "low": 1,
        "info": 0,
        "check_failed": 10,
        "check_not_run": 2,
    }
    recs = [{"data": {"severity": s}} for s in ("CRITICAL", "HIGH", "INFO")]
    res = [
        checks.CheckResult("a", "A", "testing", "HIGH", "failed", "x"),
        checks.CheckResult("b", "B", "testing", "HIGH", "not_run", "x"),
    ]
    value, lines = report.score(recs, res, weights)
    assert value == 100 - 25 - 10 - 10 - 2 and len(lines) == 4
    assert report.score([{"data": {"severity": "CRITICAL"}}] * 9, [], weights)[0] == 0
    assert [report.health_label(v) for v in (95, 80, 60, 10)] == [
        "sólido",
        "bueno, con puntos que atender",
        "con riesgos relevantes",
        "en riesgo: no apto para producción",
    ]


def test_plan_with_nothing_open(project):
    from pld_audit import config

    cfg = config.load(project / "project-auditor.toml")
    assert "Nada pendiente" in plan.render(registry.empty(), cfg)


def test_agent_text_cannot_inject_html_or_break_the_evidence_block(project):
    from pld_audit import config

    cfg = config.load(project / "project-auditor.toml")
    data = {
        "title": "<script>alert(1)</script>",
        "severity": "LOW",
        "priority": "P3",
        "category": "bugs",
        "file": "a.js",
        "description": "<b>x</b>",
        "evidence": "antes\n```\n<img src=x onerror=alert(1)>\n```",
        "impact": "i",
        "likelihood": "low",
        "fix": "f",
        "effort": "S",
        "fix_risk": "low",
        "regression_test": "t",
        "kind": "fact",
        "key": "k",
        "source": "revisor",
    }
    text = report.card({"id": "AUD-001", "data": data}, cfg)
    assert "<script>" not in text and "&lt;script&gt;" in text and "&lt;b&gt;" in text
    assert "````text\nantes\n```\n<img" in text and text.rstrip().count("````") == 2
