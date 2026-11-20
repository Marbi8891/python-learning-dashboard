"""Esquema de un hallazgo, validación y huella estable.

Los agentes devuelven sus hallazgos en un bloque de su informe Markdown:

    ```json audit-findings
    {"findings": [...], "resolved": [{"id": "AUD-003", "evidence": "..."}], "positives": ["..."]}
    ```

Un hallazgo que no cumple el esquema no se descarta en silencio: se rechaza con su motivo y el
informe lo cuenta.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

from . import PRIORITIES, SEVERITIES
from .config import normalize_path

KINDS = ("fact", "suspicion", "recommendation")
LEVELS = ("high", "medium", "low")
EFFORTS = ("S", "M", "L")

_ALIASES = {
    "severity": {
        "critica": "CRITICAL",
        "crítica": "CRITICAL",
        "alta": "HIGH",
        "media": "MEDIUM",
        "baja": "LOW",
        "informativa": "INFO",
        "info": "INFO",
    },
    "kind": {
        "hecho": "fact",
        "sospecha": "suspicion",
        "recomendacion": "recommendation",
        "recomendación": "recommendation",
    },
    "level": {"alta": "high", "media": "medium", "baja": "low"},
    "effort": {"s": "S", "m": "M", "l": "L", "bajo": "S", "medio": "M", "alto": "L"},
}

REQUIRED = (
    "title",
    "severity",
    "priority",
    "category",
    "file",
    "description",
    "impact",
    "likelihood",
    "fix",
    "effort",
    "fix_risk",
    "regression_test",
    "kind",
    "key",
)

_BLOCK = re.compile(r"```json[ \t]+audit-findings[ \t]*\n(.*?)```", re.DOTALL)


@dataclass
class Batch:
    findings: list[dict] = field(default_factory=list)
    resolved: list[dict] = field(default_factory=list)
    positives: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    excluded: int = 0
    below_threshold: int = 0


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fingerprint(category: str, file: str, key: str) -> str:
    """Misma categoría + archivo + causa raíz = mismo hallazgo, aunque cambie la redacción."""
    raw = f"{category}|{normalize_path(file)}|{slug(key)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _alias(kind: str, value):
    if not isinstance(value, str):
        return value
    return _ALIASES[kind].get(value.strip().lower(), value.strip())


def validate(raw: dict, categories: tuple[str, ...], source: str) -> tuple[dict | None, str]:
    """Devuelve (hallazgo normalizado, '') o (None, motivo del rechazo)."""
    if not isinstance(raw, dict):
        return None, "no es un objeto"
    item = dict(raw)
    item.setdefault("source", source)
    item["severity"] = _alias("severity", item.get("severity"))
    if isinstance(item["severity"], str):
        item["severity"] = item["severity"].upper()
    item["kind"] = _alias("kind", item.get("kind"))
    item["likelihood"] = _alias("level", item.get("likelihood"))
    item["fix_risk"] = _alias("level", item.get("fix_risk"))
    item["effort"] = _alias("effort", item.get("effort"))
    if isinstance(item.get("priority"), str):
        item["priority"] = item["priority"].strip().upper()

    label = item.get("title") or item.get("key") or "(sin título)"
    missing = [k for k in REQUIRED if not isinstance(item.get(k), str) or not item[k].strip()]
    if missing:
        return None, f"«{label}»: faltan {', '.join(missing)}"
    checks = (
        ("severity", SEVERITIES),
        ("priority", PRIORITIES),
        ("category", categories),
        ("kind", KINDS),
        ("likelihood", LEVELS),
        ("fix_risk", LEVELS),
        ("effort", EFFORTS),
    )
    for key, allowed in checks:
        if item[key] not in allowed:
            return None, f"«{label}»: {key} «{item[key]}» no es válido"
    if item["kind"] != "recommendation" and not str(item.get("evidence", "")).strip():
        return None, f"«{label}»: un hecho o una sospecha necesita evidencia"
    if item["kind"] == "recommendation" and item["severity"] in ("CRITICAL", "HIGH"):
        return None, f"«{label}»: una recomendación no puede ser {item['severity']}"
    if item["kind"] == "suspicion" and item["severity"] == "CRITICAL":
        return None, f"«{label}»: una sospecha sin confirmar no puede ser CRITICAL"
    line = item.get("line")
    if line is not None and (not isinstance(line, int) or isinstance(line, bool) or line < 1):
        return None, f"«{label}»: line tiene que ser un entero ≥ 1"
    item["file"] = normalize_path(item["file"])
    item["fingerprint"] = fingerprint(item["category"], item["file"], item["key"])
    return item, ""


def extract_blocks(text: str) -> list[dict]:
    """Bloques ```json audit-findings``` de un informe (o el archivo entero si es JSON)."""
    stripped = text.strip()
    if stripped.startswith(("{", "[")):
        payloads = [stripped]
    else:
        payloads = _BLOCK.findall(text)
    blocks = []
    for payload in payloads:
        data = json.loads(payload)
        blocks.append({"findings": data} if isinstance(data, list) else data)
    return blocks


def parse_report(text: str, source: str, cfg) -> Batch:
    """Valida los hallazgos de un informe aplicando exclusiones y severidad mínima."""
    batch = Batch()
    try:
        blocks = extract_blocks(text)
    except json.JSONDecodeError as exc:
        batch.rejected.append(f"{source}: bloque audit-findings con JSON no válido ({exc})")
        return batch
    if not blocks:
        batch.rejected.append(f"{source}: no tiene bloque ```json audit-findings```")
    threshold = SEVERITIES.index(cfg.min_severity)
    for block in blocks:
        for raw in block.get("findings", []):
            item, reason = validate(raw, cfg.categories, source)
            if item is None:
                batch.rejected.append(f"{source}: {reason}")
            elif cfg.is_excluded(item["file"]):
                batch.excluded += 1
            elif SEVERITIES.index(item["severity"]) > threshold:
                batch.below_threshold += 1
            else:
                batch.findings.append(item)
        for res in block.get("resolved", []):
            ok = isinstance(res, dict) and res.get("id") and str(res.get("evidence", "")).strip()
            if ok:
                batch.resolved.append({**res, "source": source})
            else:
                batch.rejected.append(f"{source}: resolución sin id o sin evidencia: {res!r}")
        batch.positives += [p for p in block.get("positives", []) if isinstance(p, str)]
    return batch


def from_checks(results, cfg) -> list[dict]:
    """Cada prueba que falla es un hallazgo verificado (kind=fact) de su categoría."""
    found = []
    for r in results:
        if r.status not in ("failed", "timeout"):
            continue
        item = {
            "title": f"Falla la prueba «{r.name}»",
            "severity": r.severity,
            "priority": "P0" if r.severity == "CRITICAL" else "P1",
            "category": r.category,
            "file": "project-auditor.toml",
            "function": r.id,
            "description": f"`{r.command}` terminó en {r.status} ({r.reason or r.exit_code}).",
            "evidence": r.output_tail or "(sin salida)",
            "impact": "Una prueba del proyecto no pasa: el cambio no está terminado (CLAUDE.md).",
            "likelihood": "high",
            "fix": "Leer la salida, reproducirla en local y corregir la causa sin tocar la prueba.",
            "effort": "M",
            "fix_risk": "medium",
            "regression_test": f"La propia prueba `{r.id}`.",
            "kind": "fact",
            "key": f"check-{r.id}",
            "source": "checks",
        }
        valid, _ = validate(item, cfg.categories, "checks")
        found.append(valid)
    return found
