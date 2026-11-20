"""Lectura y validación de project-auditor.toml."""

from __future__ import annotations

import fnmatch
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from . import PRIORITIES, SEVERITIES

MODES = ("read-only", "plan", "safe-fix")
DEPTHS = ("quick", "standard", "deep")
FIX_RISKS = ("low", "medium", "high")


class ConfigError(ValueError):
    """La configuración no es válida: se dice qué campo y por qué."""


@dataclass(frozen=True)
class Check:
    id: str
    name: str
    category: str
    cmd: tuple[str, ...]
    cwd: str = "."
    depth: str = "quick"
    timeout_s: int | None = None
    enabled: bool = True
    requires: tuple[str, ...] = ()
    requires_modules: tuple[str, ...] = ()
    requires_paths: tuple[str, ...] = ()
    writes_files: bool = False
    severity: str = "HIGH"


@dataclass(frozen=True)
class Config:
    root: Path
    mode: str = "read-only"
    output_dir: str = ".claude/informes/audit"
    min_severity: str = "LOW"
    depth: str = "standard"
    frequency_days: int = 7
    categories: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    max_agents: int = 3
    check_timeout_s: int = 900
    max_output_lines: int = 40
    score: dict[str, int] = field(default_factory=dict)
    safe_fix_max_severity: str = "MEDIUM"
    safe_fix_allowed_risk: tuple[str, ...] = ("low",)
    branch_prefix: str = "fix/audit-"
    approval_categories: tuple[str, ...] = ()
    approval_paths: tuple[str, ...] = ()
    forbidden_paths: tuple[str, ...] = ()
    checks: tuple[Check, ...] = ()

    @property
    def out(self) -> Path:
        return self.root / self.output_dir

    def is_excluded(self, path: str) -> bool:
        return matches_any(path, self.exclude)


DEFAULT_SCORE = {
    "critical": 25,
    "high": 10,
    "medium": 4,
    "low": 1,
    "info": 0,
    "check_failed": 10,
    "check_not_run": 2,
}


def normalize_path(path: str) -> str:
    p = path.strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    """Glob sencillo: `*` y `**` cruzan carpetas; `dir/**` también cubre `dir`."""
    p = normalize_path(path)
    for pattern in patterns:
        pat = normalize_path(pattern)
        # `a/**/b` también cubre `a/b` (cero carpetas intermedias).
        if fnmatch.fnmatchcase(p, pat) or fnmatch.fnmatchcase(p, pat.replace("/**/", "/")):
            return True
        if pat.endswith("/**") and (p == pat[:-3] or p.startswith(pat[:-2])):
            return True
        if pat.startswith("**/") and fnmatch.fnmatchcase(p.rsplit("/", 1)[-1], pat[3:]):
            return True
    return False


def _choice(value, allowed, name):
    if value not in allowed:
        raise ConfigError(f"{name}: «{value}» no es válido (se espera {', '.join(allowed)})")
    return value


def _str_list(data, key, where):
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ConfigError(f"{where}.{key}: tiene que ser una lista de textos")
    return tuple(value)


def _positive_int(data, key, default, where):
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ConfigError(f"{where}.{key}: tiene que ser un entero positivo")
    return value


def _parse_check(raw: dict, index: int, categories: tuple[str, ...]) -> Check:
    where = f"checks[{index}]"
    for key in ("id", "name", "category"):
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            raise ConfigError(f"{where}.{key}: obligatorio")
    if raw["category"] not in categories:
        raise ConfigError(f"{where}.category: «{raw['category']}» no está en auditor.categories")
    cmd = _str_list(raw, "cmd", where)
    if not cmd:
        raise ConfigError(f"{where}.cmd: obligatorio (lista de argumentos, sin shell)")
    timeout = raw.get("timeout_s")
    if timeout is not None:
        timeout = _positive_int(raw, "timeout_s", None, where)
    return Check(
        id=raw["id"],
        name=raw["name"],
        category=raw["category"],
        cmd=cmd,
        cwd=raw.get("cwd", "."),
        depth=_choice(raw.get("depth", "quick"), DEPTHS, f"{where}.depth"),
        timeout_s=timeout,
        enabled=bool(raw.get("enabled", True)),
        requires=_str_list(raw, "requires", where),
        requires_modules=_str_list(raw, "requires_modules", where),
        requires_paths=_str_list(raw, "requires_paths", where),
        writes_files=bool(raw.get("writes_files", False)),
        severity=_choice(raw.get("severity", "HIGH"), SEVERITIES, f"{where}.severity"),
    )


def parse(data: dict, root: Path) -> Config:
    aud = data.get("auditor", {})
    limits = data.get("limits", {})
    fix = data.get("safe_fix", {})
    categories = _str_list(aud, "categories", "auditor")
    if not categories:
        raise ConfigError("auditor.categories: hace falta al menos una categoría")

    score = dict(DEFAULT_SCORE)
    for key, value in data.get("score", {}).items():
        if key not in DEFAULT_SCORE:
            raise ConfigError(f"score.{key}: clave desconocida")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ConfigError(f"score.{key}: tiene que ser un entero ≥ 0")
        score[key] = value

    allowed_risk = _str_list(fix, "allowed_fix_risk", "safe_fix") or ("low",)
    for risk in allowed_risk:
        _choice(risk, FIX_RISKS, "safe_fix.allowed_fix_risk")
    approval_categories = _str_list(fix, "approval_categories", "safe_fix")
    for cat in approval_categories:
        _choice(cat, categories, "safe_fix.approval_categories")

    checks = tuple(_parse_check(raw, i, categories) for i, raw in enumerate(data.get("checks", [])))
    ids = [c.id for c in checks]
    duplicated = sorted({i for i in ids if ids.count(i) > 1})
    if duplicated:
        raise ConfigError(f"checks: ids repetidos: {', '.join(duplicated)}")

    return Config(
        root=root,
        mode=_choice(aud.get("mode", "read-only"), MODES, "auditor.mode"),
        output_dir=aud.get("output_dir", ".claude/informes/audit"),
        min_severity=_choice(aud.get("min_severity", "LOW"), SEVERITIES, "auditor.min_severity"),
        depth=_choice(aud.get("depth", "standard"), DEPTHS, "auditor.depth"),
        frequency_days=_positive_int(aud, "frequency_days", 7, "auditor"),
        categories=categories,
        exclude=_str_list(aud, "exclude", "auditor"),
        max_agents=_positive_int(limits, "max_agents", 3, "limits"),
        check_timeout_s=_positive_int(limits, "check_timeout_s", 900, "limits"),
        max_output_lines=_positive_int(limits, "max_output_lines", 40, "limits"),
        score=score,
        safe_fix_max_severity=_choice(
            fix.get("max_severity", "MEDIUM"), SEVERITIES, "safe_fix.max_severity"
        ),
        safe_fix_allowed_risk=allowed_risk,
        branch_prefix=fix.get("branch_prefix", "fix/audit-"),
        approval_categories=approval_categories,
        approval_paths=_str_list(fix, "approval_paths", "safe_fix"),
        forbidden_paths=_str_list(fix, "forbidden_paths", "safe_fix"),
        checks=checks,
    )


def load(path: Path) -> Config:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"no existe {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path.name}: TOML no válido: {exc}") from exc
    return parse(data, path.parent)


__all__ = ["Check", "Config", "ConfigError", "PRIORITIES", "load", "matches_any", "parse"]
