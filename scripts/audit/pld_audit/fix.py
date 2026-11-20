"""Modos SAFE FIX y APPROVAL REQUIRED.

`classify` decide si un hallazgo se puede corregir sin aprobación. `preflight` comprueba Git antes
de tocar nada. Corregir lo hace después la persona o Claude Code, en la rama que se crea aquí, con
las pruebas antes y después (`auditor.py compare-checks`). Nada de esto hace push ni merge.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import severity_rank
from .config import Config, matches_any
from .findings import slug

SAFE = "SAFE FIX"
APPROVAL = "APPROVAL REQUIRED"
FORBIDDEN = "FORBIDDEN"
PROTECTED_BRANCHES = ("main", "master")


def classify(data: dict, cfg: Config) -> tuple[str, list[str]]:
    """Devuelve (modo, motivos). Basta un motivo para pedir aprobación."""
    files = [data["file"], *data.get("files", [])]
    forbidden = [f for f in files if matches_any(f, cfg.forbidden_paths)]
    if forbidden:
        return FORBIDDEN, [f"no se edita a mano: {', '.join(forbidden)}"]
    reasons = []
    if severity_rank(data["severity"]) < severity_rank(cfg.safe_fix_max_severity):
        reasons.append(f"severidad {data['severity']} > {cfg.safe_fix_max_severity}")
    if data["fix_risk"] not in cfg.safe_fix_allowed_risk:
        reasons.append(f"riesgo de la solución «{data['fix_risk']}»")
    if data["category"] in cfg.approval_categories:
        reasons.append(f"categoría «{data['category']}»")
    protected = [f for f in files if matches_any(f, cfg.approval_paths)]
    if protected:
        reasons.append(f"archivo protegido: {', '.join(protected)}")
    if data.get("source") == "checks":
        reasons.append("una prueba que falla se investiga antes de corregir")
    return (APPROVAL, reasons) if reasons else (SAFE, [])


@dataclass
class Preflight:
    ok: bool
    mode: str
    branch: str = ""
    problems: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def _git(root: Path, *args: str, runner=subprocess.run) -> subprocess.CompletedProcess:
    return runner(["git", *args], cwd=root, capture_output=True, text=True)


def branch_name(rec: dict, cfg: Config) -> str:
    number = rec["id"].split("-")[-1]
    return f"{cfg.branch_prefix}{number}-{slug(rec['data']['key'])[:40]}".rstrip("-")


def preflight(rec: dict, cfg: Config, create_branch: bool = False, runner=subprocess.run):
    mode, reasons = classify(rec["data"], cfg)
    result = Preflight(ok=False, mode=mode, reasons=reasons, branch=branch_name(rec, cfg))
    if cfg.mode != "safe-fix":
        result.problems.append(f"auditor.mode es «{cfg.mode}»: SAFE FIX está desactivado")
    if rec["status"] != "open":
        result.problems.append(f"{rec['id']} no está abierto ({rec['status']})")
    if mode != SAFE:
        result.problems.append(f"{rec['id']} es {mode}: " + "; ".join(reasons))

    status = _git(cfg.root, "status", "--porcelain", runner=runner)
    if status.returncode != 0:
        result.problems.append("no es un repositorio Git o git no responde")
        return result
    if status.stdout.strip():
        result.problems.append("hay cambios sin confirmar: no se tocan los cambios del usuario")
    current = _git(cfg.root, "branch", "--show-current", runner=runner).stdout.strip()
    exists = _git(cfg.root, "rev-parse", "--verify", "--quiet", result.branch, runner=runner)
    if exists.returncode == 0:
        result.problems.append(f"la rama {result.branch} ya existe")

    if result.problems:
        return result
    if create_branch:
        made = _git(cfg.root, "switch", "-c", result.branch, runner=runner)
        if made.returncode != 0:
            result.problems.append(f"no se pudo crear la rama: {made.stderr.strip()}")
            return result
    elif current in PROTECTED_BRANCHES:
        result.problems.append(f"estás en {current}: usa --create-branch")
        return result
    result.ok = True
    return result
