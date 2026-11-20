"""Project Auditor (scripts/audit): configuración, pruebas, hallazgos, registro y SAFE FIX."""

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import DEFAULT_LESSONS_FILE

REPO = DEFAULT_LESSONS_FILE.parents[2]
sys.path.insert(0, str(REPO / "scripts" / "audit"))
from pld_audit import checks, config, findings, fix, registry  # noqa: E402

CATEGORIES = ("security", "bugs", "code-quality", "testing", "dependencies", "ux-accessibility")


def make_config(tmp_path: Path, extra: str = "", mode: str = "read-only") -> config.Config:
    cats = ", ".join(f'"{c}"' for c in CATEGORIES)
    (tmp_path / "project-auditor.toml").write_text(
        f"""
[auditor]
mode = "{mode}"
categories = [{cats}]
exclude = ["node_modules/**"]
min_severity = "LOW"
[safe_fix]
approval_categories = ["security"]
approval_paths = ["backend/app/routers/**"]
forbidden_paths = ["frontend/data/**/*.json", "**/.env"]
{extra}
""",
        encoding="utf-8",
    )
    return config.load(tmp_path / "project-auditor.toml")


def finding(**overrides) -> dict:
    base = {
        "title": "Temporizador sin limpiar",
        "severity": "MEDIUM",
        "priority": "P2",
        "category": "bugs",
        "file": "frontend/js/a.js",
        "line": 3,
        "description": "d",
        "evidence": "a.js:3 setInterval",
        "impact": "i",
        "likelihood": "medium",
        "fix": "clearInterval",
        "effort": "S",
        "fix_risk": "low",
        "regression_test": "t",
        "kind": "fact",
        "key": "timer",
    }
    base.update(overrides)
    return base


def valid(**overrides) -> dict:
    item, reason = findings.validate(finding(**overrides), CATEGORIES, "revisor")
    assert item is not None, reason
    return item


# --- Configuración -------------------------------------------------------------------------


def test_the_project_configuration_is_valid_and_covers_docs_testing():
    cfg = config.load(REPO / "project-auditor.toml")
    ids = {c.id for c in cfg.checks}
    assert cfg.mode == "read-only"  # el modo predeterminado no modifica nada
    assert {"ruff-lint", "backend-tests", "frontend-unit", "npm-audit", "pip-audit"} <= ids
    assert cfg.output_dir.startswith(".claude/informes")  # fuera de Git: el repo es público
    for check in cfg.checks:
        assert not any("--fix" in part for part in check.cmd), check.id
        if "build_" in " ".join(check.cmd) or "_course.py" in " ".join(check.cmd):
            assert "--check" in check.cmd, f"{check.id} sobrescribiría JSON generados"
    e2e = next(c for c in cfg.checks if c.id == "e2e")
    assert e2e.writes_files and e2e.depth == "deep"


@pytest.mark.parametrize(
    ("snippet", "message"),
    [
        ('[auditor]\nmode = "yolo"\ncategories = ["bugs"]', "auditor.mode"),
        ("[auditor]\ncategories = []", "al menos una categoría"),
        (
            '[auditor]\ncategories = ["bugs"]\n[[checks]]\nid = "a"\nname = "A"\n'
            'category = "nope"\ncmd = ["x"]',
            "no está en auditor.categories",
        ),
        (
            '[auditor]\ncategories = ["bugs"]\n'
            + '[[checks]]\nid = "a"\nname = "A"\ncategory = "bugs"\ncmd = ["x"]\n' * 2,
            "ids repetidos",
        ),
        ('[auditor]\ncategories = ["bugs"]\n[score]\nbonus = 3', "clave desconocida"),
        ('[auditor]\ncategories = ["bugs"]\n[limits]\nmax_agents = 0', "entero positivo"),
        (
            '[auditor]\ncategories = ["bugs"]\n[[checks]]\nid = "a"\nname = "A"\n'
            'category = "bugs"\ncmd = []',
            "sin shell",
        ),
        ("[auditor\n", "TOML no válido"),
    ],
)
def test_invalid_configuration_says_what_is_wrong(tmp_path, snippet, message):
    path = tmp_path / "project-auditor.toml"
    path.write_text(snippet, encoding="utf-8")
    with pytest.raises(config.ConfigError, match=message):
        config.load(path)


def test_missing_configuration_file(tmp_path):
    with pytest.raises(config.ConfigError, match="no existe"):
        config.load(tmp_path / "nada.toml")


@pytest.mark.parametrize(
    ("path", "patterns", "expected"),
    [
        ("node_modules/x/y.js", ("node_modules/**",), True),
        ("node_modules", ("node_modules/**",), True),
        ("./frontend\\data\\a.json", ("frontend/data/**/*.json",), True),
        ("backend/.env", ("**/.env",), True),
        ("frontend/js/app.js", ("frontend/data/**",), False),
    ],
)
def test_path_matching(path, patterns, expected):
    assert config.matches_any(path, patterns) is expected


# --- Pruebas -------------------------------------------------------------------------------


def fake_runner(returncode=0, output="ok", raises=None):
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        if raises:
            raise raises
        return subprocess.CompletedProcess(cmd, returncode, stdout=output, stderr="")

    run.calls = calls
    return run


def checks_config(tmp_path, body: str) -> config.Config:
    return make_config(tmp_path, extra=body)


def test_checks_record_passed_failed_and_the_python_placeholder(tmp_path):
    cfg = checks_config(
        tmp_path,
        '[[checks]]\nid = "t"\nname = "T"\ncategory = "testing"\ncmd = ["{python}", "-V"]',
    )
    runner = fake_runner(0, "token=abc123 listo")
    [res] = checks.run_checks(cfg, runner=runner)
    assert res.status == "passed" and res.exit_code == 0
    assert "{python}" not in runner.calls[0][0][0]
    assert "shell" not in runner.calls[0][1]  # lista de argumentos, sin shell
    assert "abc123" not in res.output_tail and "[REDACTADO]" in res.output_tail

    [res] = checks.run_checks(cfg, runner=fake_runner(3, "\n".join(map(str, range(100)))))
    assert res.status == "failed" and res.exit_code == 3
    assert res.output_tail.splitlines()[-1] == "99" and len(res.output_tail.splitlines()) == 40


def test_checks_timeout_and_unexecutable(tmp_path):
    cfg = checks_config(
        tmp_path, '[[checks]]\nid = "t"\nname = "T"\ncategory = "testing"\ncmd = ["x"]'
    )
    timeout = subprocess.TimeoutExpired(["x"], 1, output=b"parcial")
    [res] = checks.run_checks(cfg, runner=fake_runner(raises=timeout))
    assert res.status == "timeout" and "parcial" in res.output_tail
    [res] = checks.run_checks(cfg, runner=fake_runner(raises=FileNotFoundError("x")))
    assert res.status == "not_run" and "no se pudo ejecutar" in res.reason


def test_checks_that_cannot_run_are_never_reported_as_passed(tmp_path):
    cfg = checks_config(
        tmp_path,
        """
[[checks]]
id = "prog"
name = "P"
category = "testing"
cmd = ["x"]
requires = ["programa-que-no-existe-pld"]
[[checks]]
id = "path"
name = "R"
category = "testing"
cmd = ["x"]
requires_paths = ["no-existe"]
[[checks]]
id = "mod"
name = "M"
category = "testing"
cmd = ["x"]
requires_modules = ["modulo_que_no_existe_pld"]
[[checks]]
id = "deep"
name = "D"
category = "testing"
cmd = ["x"]
depth = "deep"
[[checks]]
id = "writes"
name = "W"
category = "testing"
cmd = ["x"]
writes_files = true
[[checks]]
id = "off"
name = "O"
category = "testing"
cmd = ["x"]
enabled = false
""",
    )
    runner = fake_runner()
    results = {r.id: r for r in checks.run_checks(cfg, depth="standard", runner=runner)}
    assert all(r.status == "not_run" and r.reason for r in results.values())
    assert "programa" in results["prog"].reason and "módulo" in results["mod"].reason
    assert "deep" in results["deep"].reason and "--allow-writes" in results["writes"].reason
    assert runner.calls == []

    only = checks.run_checks(cfg, only={"deep"}, depth="deep", runner=runner)
    assert [r.status for r in only if r.id == "deep"] == ["passed"]
    assert all(r.reason == "no seleccionada (--only)" for r in only if r.id != "deep")


def test_compare_detects_checks_that_stop_passing():
    def r(check_id, status):
        return checks.CheckResult(check_id, check_id, "testing", "HIGH", status, "cmd")

    before = [r("a", "passed"), r("b", "failed"), r("c", "passed")]
    after = [r("a", "failed"), r("b", "passed")]
    assert checks.compare(before, after) == ["a: passed → failed", "c: passed → ausente"]
    assert checks.compare(before, before) == []


def test_project_python_prefers_the_virtualenv(tmp_path):
    assert checks.project_python(tmp_path) == sys.executable
    venv = tmp_path / ".venv" / "bin"
    venv.mkdir(parents=True)
    (venv / "python").write_text("")
    assert checks.project_python(tmp_path) == str(venv / "python")


# --- Hallazgos -----------------------------------------------------------------------------


def test_spanish_labels_are_normalized():
    item = valid(severity="Alta", kind="sospecha", likelihood="baja", effort="medio", priority="p1")
    assert (item["severity"], item["kind"], item["likelihood"]) == ("HIGH", "suspicion", "low")
    assert (item["effort"], item["priority"]) == ("M", "P1")


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"fix": ""}, "faltan fix"),
        ({"severity": "GRAVE"}, "severity"),
        ({"category": "magia"}, "category"),
        ({"evidence": ""}, "necesita evidencia"),
        ({"kind": "recommendation", "severity": "HIGH"}, "una recomendación no puede"),
        ({"kind": "suspicion", "severity": "CRITICAL"}, "sospecha sin confirmar"),
        ({"line": 0}, "line"),
    ],
)
def test_invalid_findings_are_rejected_with_a_reason(overrides, reason):
    item, why = findings.validate(finding(**overrides), CATEGORIES, "revisor")
    assert item is None and reason in why
    assert findings.validate("texto", CATEGORIES, "x") == (None, "no es un objeto")


def test_recommendations_do_not_need_evidence():
    assert valid(kind="recommendation", severity="LOW", evidence="")["kind"] == "recommendation"


def test_fingerprint_ignores_wording_and_path_style_but_not_the_root_cause():
    a = valid()
    b = valid(title="Otra redacción", file="./frontend\\js\\a.js", line=9, key="Timer")
    c = valid(key="otro-problema")
    assert a["fingerprint"] == b["fingerprint"] != c["fingerprint"]


def test_parse_report_applies_exclusions_threshold_and_reports_problems(tmp_path):
    cfg = make_config(tmp_path)
    text = (
        "texto\n```json audit-findings\n"
        '{"findings": ['
        '{"title": "x"},'
        '{"title": "a", "severity": "MEDIUM", "priority": "P2", "category": "bugs", '
        '"file": "node_modules/x.js", "description": "d", "evidence": "e", "impact": "i", '
        '"likelihood": "low", "fix": "f", "effort": "S", "fix_risk": "low", '
        '"regression_test": "t", "kind": "fact", "key": "k"},'
        '{"title": "b", "severity": "INFO", "priority": "P3", "category": "bugs", '
        '"file": "a.js", "description": "d", "evidence": "e", "impact": "i", '
        '"likelihood": "low", "fix": "f", "effort": "S", "fix_risk": "low", '
        '"regression_test": "t", "kind": "fact", "key": "k2"}],'
        '"resolved": [{"id": "AUD-001"}, {"id": "AUD-002", "evidence": "ya no está"}],'
        '"positives": ["bien", 3]}\n```\n'
    )
    batch = findings.parse_report(text, "revisor", cfg)
    assert batch.findings == [] and batch.excluded == 1 and batch.below_threshold == 1
    assert len(batch.rejected) == 2  # el hallazgo incompleto y la resolución sin evidencia
    assert batch.resolved == [{"id": "AUD-002", "evidence": "ya no está", "source": "revisor"}]
    assert batch.positives == ["bien"]

    assert "no tiene bloque" in findings.parse_report("nada", "x", cfg).rejected[0]
    bad = findings.parse_report("```json audit-findings\n{no json\n```", "x", cfg)
    assert "JSON no válido" in bad.rejected[0]
    as_json = findings.parse_report(f"[{__import__('json').dumps(finding())}]", "x", cfg)
    assert len(as_json.findings) == 1


def test_failing_checks_become_verified_findings(tmp_path):
    cfg = make_config(tmp_path)
    res = [
        checks.CheckResult("unit", "Unit", "testing", "HIGH", "failed", "node", exit_code=1),
        checks.CheckResult("dep", "Dep", "dependencies", "CRITICAL", "timeout", "npm"),
        checks.CheckResult("ok", "Ok", "testing", "HIGH", "passed", "x"),
        checks.CheckResult("nr", "Nr", "testing", "HIGH", "not_run", "x"),
    ]
    found = findings.from_checks(res, cfg)
    assert [(f["key"], f["kind"], f["priority"]) for f in found] == [
        ("check-unit", "fact", "P1"),
        ("check-dep", "fact", "P0"),
    ]


# --- Registro ------------------------------------------------------------------------------


def test_registry_lifecycle_new_unchanged_changed_and_regression():
    reg = registry.empty()
    d1 = registry.apply_run(reg, "r1", [valid(), valid(key="b")], [], {"bugs"})
    assert [r["id"] for r in d1.new] == ["AUD-001", "AUD-002"]

    d2 = registry.apply_run(reg, "r2", [valid(), valid(key="b", severity="HIGH")], [], {"bugs"})
    assert [r["id"] for r in d2.unchanged] == ["AUD-001"]
    assert [r["id"] for r in d2.changed] == ["AUD-002"]
    assert d2.changed[0]["previous"]["severity"] == "MEDIUM"

    claim = {"id": "AUD-002", "evidence": "e", "source": "s"}
    d3 = registry.apply_run(reg, "r3", [valid()], [claim], {"bugs"})
    assert [r["id"] for r in d3.resolved] == ["AUD-002"]
    assert registry.by_id(reg, "AUD-002")["resolved_in"] == "r3"

    d4 = registry.apply_run(reg, "r4", [valid(), valid(key="b")], [], {"bugs"})
    assert [r["id"] for r in d4.regressions] == ["AUD-002"]  # mismo id, no uno nuevo
    assert registry.by_id(reg, "AUD-002")["status"] == "open"
    assert [e["event"] for e in registry.by_id(reg, "AUD-002")["history"]] == [
        "new",
        "changed",
        "resolved",
        "regression",
    ]


def test_absence_alone_never_resolves_a_finding():
    reg = registry.empty()
    registry.apply_run(reg, "r1", [valid(), valid(key="s", category="security")], [], {"bugs"})
    diff = registry.apply_run(reg, "r2", [], [], {"bugs"})
    assert diff.resolved == []
    assert [r["id"] for r in diff.not_redetected] == ["AUD-001"]  # security estaba fuera
    assert registry.by_id(reg, "AUD-001")["missed_runs"] == 1
    assert all(r["status"] == "open" for r in reg["findings"].values())


def test_resolution_claims_are_checked():
    reg = registry.empty()
    registry.apply_run(reg, "r1", [valid()], [], {"bugs"})
    claims = [
        {"id": "AUD-001", "evidence": "e", "source": "revisor"},
        {"id": "AUD-404", "evidence": "e", "source": "revisor"},
    ]
    diff = registry.apply_run(reg, "r2", [valid()], claims, {"bugs"})
    assert diff.resolved == []
    assert "se ha vuelto a detectar" in diff.conflicts[0]
    assert "no existe" in diff.conflicts[1]


def test_dedupe_keeps_the_most_severe_and_all_sources():
    a = valid(severity="MEDIUM")
    b = {**valid(severity="HIGH"), "source": "red-team"}
    [merged] = registry.dedupe([a, b])
    assert merged["severity"] == "HIGH" and merged["sources"] == ["red-team", "revisor"]


def test_check_findings_resolve_only_when_the_check_passes(tmp_path):
    cfg = make_config(tmp_path)
    failed = checks.CheckResult("unit", "Unit", "testing", "HIGH", "failed", "x")
    reg = registry.empty()
    registry.apply_run(reg, "r1", findings.from_checks([failed], cfg), [], set(), [failed])
    not_run = checks.CheckResult("unit", "Unit", "testing", "HIGH", "not_run", "x")
    assert registry.apply_run(reg, "r2", [], [], {"testing"}, [not_run]).resolved == []
    passed = checks.CheckResult("unit", "Unit", "testing", "HIGH", "passed", "x")
    diff = registry.apply_run(reg, "r3", [], [], set(), [passed])
    assert [r["id"] for r in diff.resolved] == ["AUD-001"]
    assert "ha pasado" in diff.resolved[0]["resolution_evidence"]


def test_registry_round_trip_and_version(tmp_path):
    path = tmp_path / "audit" / "registry.json"
    assert registry.load(path) == registry.empty()
    reg = registry.empty()
    registry.apply_run(reg, "r1", [valid()], [], {"bugs"})
    registry.save(path, reg)
    assert registry.load(path) == reg
    assert [p.name for p in path.parent.iterdir()] == ["registry.json"]  # sin temporales
    path.write_text('{"version": 99}', encoding="utf-8")
    with pytest.raises(ValueError, match="no soportada"):
        registry.load(path)


# --- SAFE FIX ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("overrides", "mode", "reason"),
    [
        ({}, fix.SAFE, None),
        ({"severity": "HIGH"}, fix.APPROVAL, "severidad"),
        ({"fix_risk": "medium"}, fix.APPROVAL, "riesgo"),
        ({"category": "security"}, fix.APPROVAL, "categoría"),
        ({"file": "backend/app/routers/auth.py"}, fix.APPROVAL, "archivo protegido"),
        ({"files": ["frontend/data/lessons.json"]}, fix.FORBIDDEN, "no se edita a mano"),
        ({"source": "checks"}, fix.APPROVAL, "se investiga"),
    ],
)
def test_classify(tmp_path, overrides, mode, reason):
    cfg = make_config(tmp_path)
    got, reasons = fix.classify({**valid(), **overrides}, cfg)
    assert got == mode
    assert (reason is None and reasons == []) or any(reason in r for r in reasons)


def fake_git(outputs: dict):
    calls = []

    def run(cmd, **kwargs):
        calls.append(cmd[1:])
        code, out = outputs.get(cmd[1], (0, ""))
        return SimpleNamespace(returncode=code, stdout=out, stderr="error")

    run.calls = calls
    return run


def record(**overrides):
    reg = registry.empty()
    registry.apply_run(reg, "r1", [valid(**overrides)], [], {"bugs"})
    return registry.by_id(reg, "AUD-001")


def test_preflight_creates_a_branch_only_when_everything_is_safe(tmp_path):
    cfg = make_config(tmp_path, mode="safe-fix")
    git = fake_git({"rev-parse": (1, ""), "branch": (0, "main")})
    result = fix.preflight(record(), cfg, create_branch=True, runner=git)
    assert result.ok and result.branch == "fix/audit-001-timer"
    assert ["switch", "-c", "fix/audit-001-timer"] in git.calls

    git = fake_git({"rev-parse": (1, ""), "branch": (0, "main")})
    on_main = fix.preflight(record(), cfg, runner=git)
    assert not on_main.ok and "--create-branch" in on_main.problems[0]


def test_preflight_refuses_and_never_touches_git(tmp_path):
    cfg = make_config(tmp_path, mode="safe-fix")
    dirty = fake_git({"status": (0, " M a.js"), "rev-parse": (0, "abc")})
    result = fix.preflight(record(severity="HIGH"), cfg, create_branch=True, runner=dirty)
    assert not result.ok
    text = " ".join(result.problems)
    assert "APPROVAL REQUIRED" in text and "sin confirmar" in text and "ya existe" in text
    assert not any(call[0] == "switch" for call in dirty.calls)

    read_only = make_config(tmp_path)
    git = fake_git({"rev-parse": (1, "")})
    assert "desactivado" in fix.preflight(record(), read_only, runner=git).problems[0]
    no_repo = fix.preflight(record(), cfg, runner=fake_git({"status": (128, "")}))
    assert "no es un repositorio" in no_repo.problems[-1]
    fails = fake_git({"rev-parse": (1, ""), "switch": (1, "")})
    assert "no se pudo crear" in fix.preflight(record(), cfg, True, fails).problems[0]

    reg = registry.empty()
    registry.apply_run(reg, "r1", [valid()], [], {"bugs"})
    registry.apply_run(reg, "r2", [], [{"id": "AUD-001", "evidence": "e", "source": "s"}], {"bugs"})
    closed = fix.preflight(registry.by_id(reg, "AUD-001"), cfg, runner=fake_git({}))
    assert "no está abierto" in closed.problems[0]
