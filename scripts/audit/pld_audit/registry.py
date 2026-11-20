"""Registro de hallazgos entre auditorías.

Un hallazgo se identifica por su huella (categoría + archivo + causa raíz), no por su redacción.
Reglas de estado:

- new: huella que no estaba en el registro (recibe un id AUD-NNN que ya no cambia).
- unchanged / changed: seguía abierto; changed si cambia la severidad, la prioridad o la evidencia.
- regression: estaba resuelto y vuelve a aparecer.
- resolved: SOLO con evidencia. O un agente lo declara resuelto con evidencia, o la prueba que lo
  generó vuelve a pasar. Que un agente no lo repita no lo resuelve (los modelos no son
  deterministas): queda abierto como «no re-detectado» para verificarlo.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import severity_rank

VERSION = 1


@dataclass
class Diff:
    new: list[dict] = field(default_factory=list)
    changed: list[dict] = field(default_factory=list)
    regressions: list[dict] = field(default_factory=list)
    unchanged: list[dict] = field(default_factory=list)
    resolved: list[dict] = field(default_factory=list)
    not_redetected: list[dict] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


def empty() -> dict:
    return {"version": VERSION, "next_id": 1, "findings": {}, "runs": []}


def load(path: Path) -> dict:
    if not path.exists():
        return empty()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != VERSION:
        raise ValueError(f"{path}: versión de registro {data.get('version')} no soportada")
    return data


def save(path: Path, data: dict) -> None:
    """Escritura atómica: o queda el registro nuevo entero o el anterior."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".registry-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def dedupe(findings: list[dict]) -> list[dict]:
    """El mismo problema visto por dos agentes es un hallazgo: se queda la severidad mayor."""
    by_fp: dict[str, dict] = {}
    for f in findings:
        prev = by_fp.get(f["fingerprint"])
        if prev is None:
            by_fp[f["fingerprint"]] = {**f, "sources": [f["source"]]}
            continue
        sources = sorted(set(prev["sources"]) | {f["source"]})
        winner = f if severity_rank(f["severity"]) < severity_rank(prev["severity"]) else prev
        by_fp[f["fingerprint"]] = {**winner, "sources": sources}
    return list(by_fp.values())


def _event(rec: dict, run_id: str, event: str) -> None:
    rec["history"].append({"run": run_id, "event": event, "severity": rec["data"]["severity"]})


def by_id(reg: dict, finding_id: str) -> dict | None:
    for rec in reg["findings"].values():
        if rec["id"] == finding_id:
            return rec
    return None


def apply_run(
    reg: dict,
    run_id: str,
    findings: list[dict],
    resolved_claims: list[dict],
    scope: set[str],
    check_results=(),
) -> Diff:
    diff = Diff()
    seen: set[str] = set()

    for f in dedupe(findings):
        fp = f["fingerprint"]
        seen.add(fp)
        rec = reg["findings"].get(fp)
        if rec is None:
            rec = {
                "id": f"AUD-{reg['next_id']:03d}",
                "fingerprint": fp,
                "status": "open",
                "first_seen": run_id,
                "last_seen": run_id,
                "resolved_in": None,
                "resolution_evidence": None,
                "missed_runs": 0,
                "data": f,
                "history": [],
            }
            reg["next_id"] += 1
            reg["findings"][fp] = rec
            _event(rec, run_id, "new")
            diff.new.append(rec)
            continue
        old = rec["data"]
        rec.update(last_seen=run_id, missed_runs=0, data=f)
        if rec["status"] == "resolved":
            rec.update(status="open", resolved_in=None, resolution_evidence=None)
            _event(rec, run_id, "regression")
            diff.regressions.append(rec)
        elif any(old.get(k) != f.get(k) for k in ("severity", "priority", "evidence")):
            rec["previous"] = {k: old.get(k) for k in ("severity", "priority")}
            _event(rec, run_id, "changed")
            diff.changed.append(rec)
        else:
            diff.unchanged.append(rec)

    def resolve(rec: dict, evidence: str) -> None:
        rec.update(status="resolved", resolved_in=run_id, resolution_evidence=evidence)
        _event(rec, run_id, "resolved")
        diff.resolved.append(rec)

    for claim in resolved_claims:
        rec = by_id(reg, claim["id"])
        if rec is None:
            diff.conflicts.append(f"{claim['source']}: {claim['id']} no existe en el registro")
        elif rec["fingerprint"] in seen:
            diff.conflicts.append(
                f"{claim['source']}: {claim['id']} se declara resuelto pero se ha vuelto a detectar"
            )
        elif rec["status"] == "open":
            resolve(rec, f"{claim['evidence']} ({claim['source']})")

    passed = {r.id for r in check_results if r.status == "passed"}
    for rec in reg["findings"].values():
        if rec["status"] != "open" or rec["fingerprint"] in seen:
            continue
        data = rec["data"]
        if data["source"] == "checks":
            check_id = data["key"].removeprefix("check-")
            if check_id in passed:
                resolve(rec, f"la prueba «{check_id}» ha pasado en {run_id}")
        elif data["category"] in scope:
            rec["missed_runs"] += 1
            diff.not_redetected.append(rec)
    return diff


def open_findings(reg: dict) -> list[dict]:
    recs = [r for r in reg["findings"].values() if r["status"] == "open"]
    return sorted(
        recs,
        key=lambda r: (r["data"]["priority"], severity_rank(r["data"]["severity"]), r["id"]),
    )
