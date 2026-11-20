"""Project Auditor de Python Learning Dashboard (docs/AUDITOR.md).

    python scripts/audit/auditor.py checks [--depth quick|standard|deep] [--only a,b]
    python scripts/audit/auditor.py context [--since REF]
    python scripts/audit/auditor.py audit --scope all|cat,cat --checks FILE informe.md ...
    python scripts/audit/auditor.py plan [--min-priority P1]
    python scripts/audit/auditor.py preflight-fix AUD-NNN [--create-branch]
    python scripts/audit/auditor.py compare-checks antes.json despues.json

Solo `preflight-fix --create-branch` cambia algo del repositorio (crea una rama). El resto
escribe únicamente en la carpeta de salida (.claude/informes/audit/, fuera de Git).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pld_audit import checks as checks_mod  # noqa: E402
from pld_audit import config as config_mod  # noqa: E402
from pld_audit import findings as findings_mod  # noqa: E402
from pld_audit import fix as fix_mod  # noqa: E402
from pld_audit import plan as plan_mod  # noqa: E402
from pld_audit import registry as registry_mod  # noqa: E402
from pld_audit import report as report_mod  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def git(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    except OSError:
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def new_run_id(out: Path, now: datetime | None = None) -> str:
    base = (now or datetime.now(UTC)).strftime("%Y%m%dT%H%MZ")
    run_id, n = base, 2
    while (out / "history" / f"{run_id}.md").exists() or (out / "runs" / f"{run_id}.json").exists():
        run_id, n = f"{base}-{n}", n + 1
    return run_id


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_checks(path: Path | None) -> list:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [checks_mod.CheckResult.from_dict(item) for item in data["checks"]]


def cmd_checks(cfg, args) -> int:
    only = set(args.only.split(",")) if args.only else None
    unknown = (only or set()) - {c.id for c in cfg.checks}
    if unknown:
        print(f"Pruebas desconocidas: {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2

    def progress(r):
        icon = report_mod.STATUS_ICON.get(r.status, "⚪ no ejecutada")
        extra = f" — {r.reason}" if r.reason else ""
        print(f"{icon:<20} {r.id:<22} {r.duration_s:>7} s{extra}", flush=True)

    results = checks_mod.run_checks(cfg, args.depth, only, args.allow_writes, progress=progress)
    out = Path(args.out) if args.out else cfg.out / "runs" / f"{new_run_id(cfg.out)}-checks.json"
    payload = {
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": git(cfg.root, "rev-parse", "--short", "HEAD") or "?",
        "depth": args.depth or cfg.depth,
        "checks": [r.to_dict() for r in results],
    }
    write(out, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"\nResultados: {out}")
    failed = [r for r in results if r.status in ("failed", "timeout")]
    return 1 if args.strict and failed else 0


def cmd_context(cfg, args) -> int:
    """Lo que necesita un agente, y nada más: hallazgos abiertos y archivos cambiados."""
    reg = registry_mod.load(cfg.out / "registry.json")
    last = reg["runs"][-1] if reg["runs"] else None
    since = args.since or (last["commit"] if last else "")
    changed = None
    if since:
        names = git(cfg.root, "diff", "--name-only", f"{since}..HEAD")
        known = git(cfg.root, "rev-parse", "--verify", "--quiet", f"{since}^{{commit}}")
        if known:
            changed = [f for f in names.splitlines() if f and not cfg.is_excluded(f)]
    open_recs = [
        {
            "id": r["id"],
            "title": r["data"]["title"],
            "severity": r["data"]["severity"],
            "category": r["data"]["category"],
            "file": r["data"]["file"],
            "key": r["data"]["key"],
            "ref": r["data"].get("ref"),
        }
        for r in registry_mod.open_findings(reg)
        if r["data"]["source"] != "checks"
    ]
    print(
        json.dumps(
            {
                "last_audit": last and {k: last[k] for k in ("run_id", "commit", "score")},
                "changed_since": since or None,
                "changed_files": changed,
                "open_findings": open_recs,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_audit(cfg, args) -> int:
    scope = list(cfg.categories) if args.scope == "all" else [s for s in args.scope.split(",") if s]
    bad = [s for s in scope if s not in cfg.categories]
    if bad:
        print(f"Categorías desconocidas: {', '.join(bad)}", file=sys.stderr)
        return 2
    check_results = load_checks(Path(args.checks) if args.checks else None)

    found, resolved, positives, rejected = [], [], [], []
    excluded = below = 0
    sources = []
    for path in map(Path, args.reports):
        batch = findings_mod.parse_report(path.read_text(encoding="utf-8"), path.stem, cfg)
        sources.append(path.stem)
        found += batch.findings
        resolved += batch.resolved
        positives += batch.positives
        rejected += batch.rejected
        excluded += batch.excluded
        below += batch.below_threshold
    found += findings_mod.from_checks(check_results, cfg)

    reg_path = cfg.out / "registry.json"
    reg = registry_mod.load(reg_path)
    previous = reg["runs"][-1] if reg["runs"] else None
    run_id = args.run_id or new_run_id(cfg.out)
    diff = registry_mod.apply_run(reg, run_id, found, resolved, set(scope), check_results)
    info = report_mod.RunInfo(
        run_id=run_id,
        date=datetime.now(UTC).isoformat(timespec="seconds"),
        commit=git(cfg.root, "rev-parse", "--short", "HEAD") or "?",
        branch=git(cfg.root, "branch", "--show-current") or "?",
        depth=args.depth or cfg.depth,
        scope=scope,
        sources=sources,
        rejected=rejected,
        excluded=excluded,
        below_threshold=below,
        positives=positives,
    )
    markdown, summary = report_mod.render(info, diff, reg, check_results, cfg, previous)
    reg["runs"].append(summary)

    write(cfg.out / "history" / f"{run_id}.md", markdown)
    write(cfg.out / "latest-audit.md", markdown)
    run_record = {"summary": summary, "checks": [c.to_dict() for c in check_results]}
    write(cfg.out / "runs" / f"{run_id}.json", json.dumps(run_record, ensure_ascii=False, indent=2))
    registry_mod.save(reg_path, reg)

    print(f"Auditoría {run_id}: {summary['score']}/100")
    print(
        f"Nuevos {len(diff.new)} · resueltos {len(diff.resolved)} · "
        f"regresiones {len(diff.regressions)} · cambiados {len(diff.changed)} · "
        f"rechazados {len(rejected)}"
    )
    print(f"Informe: {cfg.out / 'latest-audit.md'}")
    return 0


def cmd_plan(cfg, args) -> int:
    reg = registry_mod.load(cfg.out / "registry.json")
    text = plan_mod.render(reg, cfg, args.min_priority)
    write(cfg.out / "plan-latest.md", text)
    print(text)
    print(f"Plan: {cfg.out / 'plan-latest.md'}")
    return 0


def cmd_preflight(cfg, args) -> int:
    reg = registry_mod.load(cfg.out / "registry.json")
    rec = registry_mod.by_id(reg, args.id)
    if rec is None:
        print(f"{args.id} no está en el registro", file=sys.stderr)
        return 2
    result = fix_mod.preflight(rec, cfg, create_branch=args.create_branch)
    print(f"{rec['id']} · {rec['data']['title']}")
    print(f"Modo: {result.mode}" + (f" ({'; '.join(result.reasons)})" if result.reasons else ""))
    if not result.ok:
        print("No se puede corregir ahora:")
        for problem in result.problems:
            print(f"  - {problem}")
        return 1
    print(f"Listo para corregir en la rama {result.branch}.")
    print("Antes y después: auditor.py checks --out <antes|despues>.json y compare-checks.")
    return 0


def cmd_compare(cfg, args) -> int:
    broken = checks_mod.compare(load_checks(Path(args.before)), load_checks(Path(args.after)))
    if broken:
        print("El cambio rompe pruebas que pasaban:")
        for line in broken:
            print(f"  - {line}")
        return 1
    print("Ninguna prueba que pasaba ha dejado de pasar.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="auditor.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--config", default=str(ROOT / "project-auditor.toml"))
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("checks", help="ejecuta las pruebas configuradas")
    p.add_argument("--depth", choices=config_mod.DEPTHS)
    p.add_argument("--only", help="ids separados por comas")
    p.add_argument("--allow-writes", action="store_true", help="permite pruebas que crean archivos")
    p.add_argument("--out", help="archivo JSON de resultados")
    p.add_argument("--strict", action="store_true", help="código 1 si alguna falla")
    p.set_defaults(func=cmd_checks)

    p = sub.add_parser("context", help="contexto mínimo para los agentes")
    p.add_argument("--since", help="ref de Git (por defecto, el commit de la última auditoría)")
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("audit", help="incorpora los informes y genera el informe")
    p.add_argument("--scope", required=True, help="all o categorías separadas por comas")
    p.add_argument("--checks", help="JSON de `checks`")
    p.add_argument("--depth", choices=config_mod.DEPTHS)
    p.add_argument("--run-id")
    p.add_argument("reports", nargs="*", help="informes de los agentes (.md o .json)")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("plan", help="plan de corrección")
    p.add_argument("--min-priority", choices=config_mod.PRIORITIES, default="P3")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("preflight-fix", help="comprueba si un hallazgo admite SAFE FIX")
    p.add_argument("id")
    p.add_argument("--create-branch", action="store_true")
    p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("compare-checks", help="detecta pruebas que dejan de pasar")
    p.add_argument("before")
    p.add_argument("after")
    p.set_defaults(func=cmd_compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = config_mod.load(Path(args.config))
    except config_mod.ConfigError as exc:
        print(f"Configuración no válida: {exc}", file=sys.stderr)
        return 2
    return args.func(cfg, args)


if __name__ == "__main__":
    sys.exit(main())
