"""Informe de auditoría en Markdown y puntuación heurística."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from . import SEVERITIES, severity_rank
from .fix import classify
from .registry import Diff, open_findings

SECTIONS = (
    ("Security Findings", {"security"}),
    ("Functional Bugs", {"bugs"}),
    ("Architecture Review", {"architecture", "integration", "config-deploy"}),
    ("Performance Review", {"performance"}),
    ("Code Quality", {"code-quality", "docs", "content"}),
    ("Testing Review", {"testing"}),
    ("UX and Accessibility", {"ux-accessibility"}),
    ("Dependencies", {"dependencies"}),
)
KIND_LABEL = {"fact": "Hecho", "suspicion": "Sospecha", "recommendation": "Recomendación"}
STATUS_ICON = {"passed": "✅ pasa", "failed": "❌ falla", "timeout": "⏱️ tiempo agotado"}
DEBT_CATEGORIES = {"architecture", "code-quality", "docs", "testing", "dependencies"}


@dataclass
class RunInfo:
    run_id: str
    date: str
    commit: str
    branch: str
    depth: str
    scope: list[str]
    sources: list[str]
    rejected: list[str] = field(default_factory=list)
    excluded: int = 0
    below_threshold: int = 0
    positives: list[str] = field(default_factory=list)


def score(open_recs: list[dict], checks, weights: dict[str, int]) -> tuple[int, list[str]]:
    """100 menos penalizaciones. Devuelve la puntuación y el desglose."""
    lines = []
    total = 0
    sev = Counter(r["data"]["severity"] for r in open_recs)
    for name in SEVERITIES:
        n = sev.get(name, 0)
        if n and weights[name.lower()]:
            total += n * weights[name.lower()]
            lines.append(f"{n} × {name} abierto: −{n * weights[name.lower()]}")
    failed = [c for c in checks if c.status in ("failed", "timeout")]
    not_run = [c for c in checks if c.status == "not_run"]
    if failed:
        total += len(failed) * weights["check_failed"]
        lines.append(
            f"{len(failed)} prueba(s) que fallan: −{len(failed) * weights['check_failed']}"
        )
    if not_run and weights["check_not_run"]:
        total += len(not_run) * weights["check_not_run"]
        lines.append(
            f"{len(not_run)} prueba(s) sin ejecutar (incertidumbre): "
            f"−{len(not_run) * weights['check_not_run']}"
        )
    return max(0, 100 - total), lines


def health_label(value: int) -> str:
    if value >= 90:
        return "sólido"
    if value >= 75:
        return "bueno, con puntos que atender"
    if value >= 50:
        return "con riesgos relevantes"
    return "en riesgo: no apto para producción"


def escape(text) -> str:
    """El texto de los agentes nunca se interpreta como HTML al abrir el informe."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _md(text) -> str:
    """Celda de tabla: sin HTML, sin saltos de línea y con `|` escapado."""
    return escape(text).replace("|", "\\|").replace("\n", " ")


def _fence(text: str) -> str:
    """Bloque de código que no se rompe aunque la evidencia contenga ```."""
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    ticks = "`" * max(3, longest + 1)
    return f"{ticks}text\n{text}\n{ticks}"


def _where(d: dict) -> str:
    where = f"`{d['file']}`"
    if d.get("line"):
        where += f" línea {d['line']}"
    if d.get("function"):
        where += f" (`{d['function']}`)"
    return where


def card(rec: dict, cfg, label: str = "") -> str:
    d = rec["data"]
    mode, reasons = classify(d, cfg)
    ref = f" · ref. {d['ref']}" if d.get("ref") else ""
    tag = f" · **{label}**" if label else ""
    previous = ""
    if rec.get("previous") and label == "cambiado":
        p = rec["previous"]
        previous = f"\n- **Antes:** {p['severity']} / {p['priority']}"
    evidence = (d.get("evidence") or "(recomendación sin evidencia de fallo)").strip()
    title, desc, impact = escape(d["title"]), escape(d["description"]), escape(d["impact"])
    fix, test = escape(d["fix"]), escape(d["regression_test"])
    why = f" ({'; '.join(reasons)})" if reasons else ""
    sources = ", ".join(d.get("sources", [d["source"]]))
    kind = KIND_LABEL[d["kind"]]
    return f"""#### {rec["id"]} · {title}{tag}

- **Severidad / prioridad:** {d["severity"]} / {d["priority"]} · **Tipo:** {kind}{previous}
- **Dónde:** {_where(d)}
- **Categoría:** {d["category"]} · **Fuente:** {sources}{ref}
- **Descripción:** {desc}
- **Evidencia:**

{_fence(evidence)}

- **Impacto:** {impact} · **Probabilidad:** {d["likelihood"]}
- **Solución recomendada:** {fix}
- **Esfuerzo:** {d["effort"]} · **Riesgo de la solución:** {d["fix_risk"]} · **Modo:** {mode}{why}
- **Test de regresión:** {test}
"""


def _section(title: str, cats: set[str], diff: Diff, open_recs: list[dict], cfg) -> str:
    detail = [(r, "nuevo") for r in diff.new if r["data"]["category"] in cats] + [
        (r, "regresión") for r in diff.regressions if r["data"]["category"] in cats
    ]
    detail += [(r, "cambiado") for r in diff.changed if r["data"]["category"] in cats]
    shown = {r["id"] for r, _ in detail}
    pending = [r for r in open_recs if r["data"]["category"] in cats and r["id"] not in shown]
    out = [f"## {title}\n"]
    if not detail and not pending:
        out.append("Sin hallazgos abiertos.\n")
        return "\n".join(out)
    detail.sort(key=lambda x: (x[0]["data"]["priority"], severity_rank(x[0]["data"]["severity"])))
    out += [card(r, cfg, label) for r, label in detail]
    if pending:
        out.append("Siguen abiertos sin cambios (detalle en informes anteriores):\n")
        out.append("| Id | Hallazgo | Severidad | Prioridad | Desde |\n|---|---|---|---|---|")
        out += [
            f"| {r['id']} | {_md(r['data']['title'])} | {r['data']['severity']} | "
            f"{r['data']['priority']} | {r['first_seen']} |"
            for r in pending
        ]
        out.append("")
    return "\n".join(out)


def _checks_table(checks) -> str:
    if not checks:
        return "No se ha ejecutado ninguna prueba en esta auditoría.\n"
    rows = ["| Prueba | Resultado | Tiempo | Detalle |", "|---|---|---|---|"]
    for c in checks:
        status = STATUS_ICON.get(c.status, "⚪ no ejecutada")
        detail = c.reason or (f"código {c.exit_code}" if c.status == "failed" else "")
        rows.append(f"| {_md(c.name)} (`{c.id}`) | {status} | {c.duration_s} s | {_md(detail)} |")
    count = Counter(c.status for c in checks)
    rows.append(
        f"\n**Total:** {count['passed']} pasan, {count['failed']} fallan, "
        f"{count['timeout']} agotan el tiempo y {count['not_run']} no se han ejecutado. "
        "Una prueba no ejecutada no cuenta como aprobada."
    )
    return "\n".join(rows) + "\n"


def _comparison(diff: Diff, previous: dict | None, value: int, open_recs) -> str:
    if previous is None:
        return "Primera auditoría registrada: no hay con qué comparar.\n"
    delta = value - previous["score"]
    sign = "+" if delta >= 0 else ""
    prev_open = previous.get("open_by_severity", {})
    now = Counter(r["data"]["severity"] for r in open_recs)
    debt_now = sum(1 for r in open_recs if r["data"]["category"] in DEBT_CATEGORIES)
    debt_before = previous.get("debt_open", 0)
    lines = [
        f"Comparado con {previous['run_id']} (commit `{previous.get('commit', '?')}`):\n",
        f"- **Puntuación:** {previous['score']} → {value} ({sign}{delta})",
        f"- **Nuevos:** {len(diff.new)} · **Resueltos:** {len(diff.resolved)} · "
        f"**Regresiones:** {len(diff.regressions)} · **Cambiados:** {len(diff.changed)} · "
        f"**Siguen igual:** {len(diff.unchanged)}",
        f"- **Deuda técnica abierta:** {debt_before} → {debt_now}",
        "- **Abiertos por severidad:** "
        + ", ".join(f"{s} {prev_open.get(s, 0)} → {now.get(s, 0)}" for s in SEVERITIES),
    ]
    if diff.resolved:
        lines.append("\nResueltos en esta auditoría:\n")
        lines += [
            f"- {r['id']} · {_md(r['data']['title'])} — {_md(r['resolution_evidence'])}"
            for r in diff.resolved
        ]
    if diff.not_redetected:
        lines.append(
            "\nNo re-detectados (siguen abiertos: sin evidencia no se dan por resueltos):\n"
        )
        lines += [
            f"- {r['id']} · {_md(r['data']['title'])} ({r['missed_runs']} auditoría(s) sin verlo)"
            for r in diff.not_redetected
        ]
    return "\n".join(lines) + "\n"


def render(
    info: RunInfo, diff: Diff, reg: dict, checks, cfg, previous: dict | None
) -> tuple[str, dict]:
    """Devuelve (Markdown, resumen de la ejecución para el registro)."""
    open_recs = open_findings(reg)
    value, breakdown = score(open_recs, checks, cfg.score)
    sev = Counter(r["data"]["severity"] for r in open_recs)
    criticals = [r for r in open_recs if r["data"]["severity"] == "CRITICAL"]
    summary = {
        "run_id": info.run_id,
        "date": info.date,
        "commit": info.commit,
        "branch": info.branch,
        "depth": info.depth,
        "scope": info.scope,
        "score": value,
        "open_by_severity": {s: sev.get(s, 0) for s in SEVERITIES},
        "debt_open": sum(1 for r in open_recs if r["data"]["category"] in DEBT_CATEGORIES),
        "checks": dict(Counter(c.status for c in checks)),
    }
    check_count = Counter(c.status for c in checks)
    failing = check_count["failed"] + check_count["timeout"]
    scope = ", ".join(info.scope) if info.scope else "ninguna (solo pruebas)"

    parts = [
        f"# Auditoría del proyecto · {info.run_id}\n",
        f"Commit `{info.commit}` en `{info.branch}` · profundidad `{info.depth}` · "
        f"modo `{cfg.mode}` · fuentes: {', '.join(info.sources) or 'solo pruebas'}.\n",
        "## Executive Summary\n",
        f"Estado: **{health_label(value)}** ({value}/100). Hay {len(open_recs)} hallazgo(s) "
        f"abiertos: {', '.join(f'{sev.get(s, 0)} {s}' for s in SEVERITIES)}. "
        f"En esta auditoría: {len(diff.new)} nuevo(s), {len(diff.resolved)} resuelto(s) y "
        f"{len(diff.regressions)} regresión(es). De las pruebas, {check_count['passed']} pasan, "
        f"{failing} fallan y {check_count['not_run']} no se han ejecutado. "
        f"Categorías revisadas por los agentes: {scope}."
        + (
            ""
            if info.sources
            else " **Sin revisión de agentes: la puntuación solo refleja las pruebas, no la "
            "calidad ni la seguridad del código.**"
        )
        + "\n",
        "## Project Health Score\n",
        f"**{value}/100** — evaluación heurística del auditor, no una métrica objetiva. Se parte "
        "de 100 y se resta por cada hallazgo abierto según su severidad, por cada prueba que falla "
        "y por cada prueba sin ejecutar (lo no comprobado resta porque es incertidumbre). Pesos en "
        "`project-auditor.toml` → `[score]`.\n",
    ]
    parts += [f"- {line}" for line in breakdown] or ["- Sin penalizaciones."]
    parts.append("\n## Comparación con la auditoría anterior\n")
    parts.append(_comparison(diff, previous, value, open_recs))
    parts.append("## Critical Findings\n")
    if criticals:
        parts.append(
            "| Id | Hallazgo | Dónde | Estado |\n|---|---|---|---|\n"
            + "\n".join(
                f"| {r['id']} | {_md(r['data']['title'])} | {_md(_where(r['data']))} | "
                f"{'nuevo' if r in diff.new else 'abierto desde ' + r['first_seen']} |"
                for r in criticals
            )
            + "\n\nEl detalle está en su sección.\n"
        )
    else:
        parts.append("Ningún hallazgo CRITICAL abierto.\n")
    for title, cats in SECTIONS:
        parts.append(_section(title, cats, diff, open_recs, cfg))
        if title == "Testing Review":
            parts.append("### Pruebas ejecutadas\n\n" + _checks_table(checks))

    debt = [r for r in open_recs if r["data"]["category"] in DEBT_CATEGORIES]
    parts.append("## Technical Debt\n")
    if debt:
        effort = Counter(r["data"]["effort"] for r in debt)
        parts.append(
            f"{len(debt)} hallazgo(s) de deuda abiertos (arquitectura, calidad, documentación, "
            f"pruebas y dependencias). Esfuerzo: {effort['S']} S, {effort['M']} M, "
            f"{effort['L']} L.\n"
        )
    else:
        parts.append("Sin deuda técnica registrada.\n")

    parts.append("## Recommended Actions\n")
    if open_recs:
        parts.append("| # | Id | Acción | Prioridad | Severidad | Esfuerzo | Modo |")
        parts.append("|---|---|---|---|---|---|---|")
        for i, r in enumerate(open_recs[:20], 1):
            d = r["data"]
            mode, _ = classify(d, cfg)
            parts.append(
                f"| {i} | {r['id']} | {_md(d['fix'])} | {d['priority']} | {d['severity']} | "
                f"{d['effort']} | {mode} |"
            )
        if len(open_recs) > 20:
            parts.append(f"\nY {len(open_recs) - 20} más: `auditor.py plan` los lista todos.")
        parts.append("")
    else:
        parts.append("Nada pendiente.\n")

    parts.append("## Positive Findings\n")
    positives = list(dict.fromkeys(info.positives))
    passed = [c.name for c in checks if c.status == "passed"]
    if passed:
        positives.append("Pruebas que pasan: " + ", ".join(passed) + ".")
    parts += [f"- {_md(p)}" for p in positives] or ["- Ninguno registrado."]

    parts.append("\n## Límites de esta auditoría\n")
    limits = []
    if info.rejected:
        limits.append(f"{len(info.rejected)} hallazgo(s) rechazados por no cumplir el esquema:")
        limits += [f"  - {_md(r)}" for r in info.rejected]
    if diff.conflicts:
        limits += [f"- Conflicto: {_md(c)}" for c in diff.conflicts]
    if info.excluded:
        limits.append(f"- {info.excluded} hallazgo(s) en rutas excluidas.")
    if info.below_threshold:
        limits.append(
            f"- {info.below_threshold} hallazgo(s) por debajo de la severidad mínima "
            f"({cfg.min_severity})."
        )
    not_run = [c for c in checks if c.status == "not_run"]
    if not_run:
        limits.append(
            "- No ejecutadas: " + "; ".join(f"`{c.id}` ({c.reason})" for c in not_run) + "."
        )
    limits.append(
        "- Los hallazgos de los agentes son revisión asistida por IA: los marcados como Sospecha "
        "necesitan confirmación antes de actuar."
    )
    parts += [line if line.startswith(("-", " ")) else f"- {line}" for line in limits]
    return "\n".join(parts) + "\n", summary
