"""Ejecuta las pruebas configuradas y registra lo que pasó de verdad.

Cada prueba acaba en uno de estos estados, y solo `passed` cuenta como aprobada:

- passed: terminó con código 0.
- failed: terminó con otro código.
- timeout: superó su tiempo máximo.
- not_run: no se ejecutó (falta un programa, un módulo o una ruta; está desactivada, la
  profundidad no la incluye o escribe archivos y no se permitió). Siempre con el motivo.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import DEPTHS, Check, Config

STATUSES = ("passed", "failed", "timeout", "not_run")

_SECRET = re.compile(
    r"(?i)\b(password|passwd|secret|token|api[_-]?key|authorization)\b(\s*[=:]\s*|\s+)(\S+)"
)


@dataclass
class CheckResult:
    id: str
    name: str
    category: str
    severity: str
    status: str
    command: str
    reason: str = ""
    exit_code: int | None = None
    duration_s: float = 0.0
    output_tail: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CheckResult:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


def redact(text: str) -> str:
    """Oculta valores que parecen secretos antes de guardar la salida de una prueba."""
    return _SECRET.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTADO]", text)


def tail(text: str, lines: int) -> str:
    return "\n".join(text.splitlines()[-lines:])


def project_python(root: Path) -> str:
    for candidate in (root / ".venv" / "bin" / "python", root / ".venv" / "Scripts" / "python.exe"):
        if candidate.exists():
            return str(candidate)
    return sys.executable


def _module_available(python: str, module: str, cwd: Path) -> bool:
    code = f"import importlib.util,sys; sys.exit(importlib.util.find_spec({module!r}) is None)"
    try:
        return subprocess.run([python, "-c", code], cwd=cwd, capture_output=True).returncode == 0
    except OSError:
        return False


def missing_requirement(check: Check, root: Path, python: str) -> str:
    for program in check.requires:
        if shutil.which(program) is None:
            return f"falta el programa «{program}»"
    for path in check.requires_paths:
        if not (root / path).exists():
            return f"falta «{path}»"
    for module in check.requires_modules:
        if not _module_available(python, module, root):
            return f"falta el módulo de Python «{module}» en {python}"
    return ""


def select_reason(check: Check, depth: str, only: set[str] | None, allow_writes: bool) -> str:
    """Motivo por el que una prueba no entra en esta ejecución ('' si entra)."""
    if only is not None and check.id not in only:
        return "no seleccionada (--only)"
    if not check.enabled:
        return "desactivada en la configuración"
    if DEPTHS.index(check.depth) > DEPTHS.index(depth):
        return f"necesita profundidad «{check.depth}»; esta ejecución: «{depth}»"
    if check.writes_files and not allow_writes:
        return "crea archivos o arranca servidores: hace falta --allow-writes"
    return ""


Runner = Callable[..., subprocess.CompletedProcess]


def run_check(
    check: Check, cfg: Config, python: str, runner: Runner = subprocess.run
) -> CheckResult:
    cmd = [part.replace("{python}", python) for part in check.cmd]
    result = CheckResult(
        id=check.id,
        name=check.name,
        category=check.category,
        severity=check.severity,
        status="not_run",
        command=" ".join(cmd),
    )
    missing = missing_requirement(check, cfg.root, python)
    if missing:
        result.reason = missing
        return result
    timeout = check.timeout_s or cfg.check_timeout_s
    start = time.monotonic()
    try:
        proc = runner(
            cmd,
            cwd=cfg.root / check.cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env={**os.environ, "NO_COLOR": "1", "FORCE_COLOR": "0"},
        )
    except subprocess.TimeoutExpired as exc:
        result.status = "timeout"
        result.reason = f"superó {timeout} s"
        output = "".join(
            part.decode("utf-8", "replace") if isinstance(part, bytes) else part
            for part in (exc.stdout or "", exc.stderr or "")
        )
        result.output_tail = redact(tail(output, cfg.max_output_lines))
    except OSError as exc:
        result.reason = f"no se pudo ejecutar: {exc}"
    else:
        result.exit_code = proc.returncode
        result.status = "passed" if proc.returncode == 0 else "failed"
        output = (proc.stdout or "") + (proc.stderr or "")
        result.output_tail = redact(tail(output, cfg.max_output_lines))
    result.duration_s = round(time.monotonic() - start, 2)
    return result


def run_checks(
    cfg: Config,
    depth: str | None = None,
    only: set[str] | None = None,
    allow_writes: bool = False,
    runner: Runner = subprocess.run,
    progress: Callable[[CheckResult], None] | None = None,
) -> list[CheckResult]:
    depth = depth or cfg.depth
    python = project_python(cfg.root)
    results = []
    for check in cfg.checks:
        reason = select_reason(check, depth, only, allow_writes)
        if reason:
            res = CheckResult(
                id=check.id,
                name=check.name,
                category=check.category,
                severity=check.severity,
                status="not_run",
                command=" ".join(check.cmd),
                reason=reason,
            )
        else:
            res = run_check(check, cfg, python, runner)
        results.append(res)
        if progress:
            progress(res)
    return results


def compare(before: list[CheckResult], after: list[CheckResult]) -> list[str]:
    """Pruebas que pasaban antes de un cambio y ya no pasan (para SAFE FIX)."""
    prev = {r.id: r.status for r in before}
    broken = []
    for r in after:
        if prev.get(r.id) == "passed" and r.status != "passed":
            broken.append(f"{r.id}: passed → {r.status}")
    for check_id, status in prev.items():
        if status == "passed" and check_id not in {r.id for r in after}:
            broken.append(f"{check_id}: passed → ausente")
    return broken
