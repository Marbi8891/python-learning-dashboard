"""Plan de corrección (modo PLAN): qué hacer, en qué orden y cómo verificarlo. No cambia nada."""

from __future__ import annotations

from . import PRIORITIES
from .fix import APPROVAL, FORBIDDEN, SAFE, classify
from .registry import open_findings
from .report import escape

MODE_HELP = {
    SAFE: "Se puede corregir en una rama propia con `auditor.py preflight-fix` y pruebas antes y "
    "después.",
    APPROVAL: "Necesita aprobación explícita antes de tocar nada.",
    FORBIDDEN: "No se edita el archivo afectado: se cambia su generador o lo hace la persona.",
}


def verification(data: dict, cfg) -> list[str]:
    ids = [c.id for c in cfg.checks if c.category == data["category"] and c.enabled]
    return ids or [c.id for c in cfg.checks if c.category == "testing"]


def render(reg: dict, cfg, min_priority: str = "P3") -> str:
    limit = PRIORITIES.index(min_priority)
    recs = [r for r in open_findings(reg) if PRIORITIES.index(r["data"]["priority"]) <= limit]
    out = [
        "# Plan de corrección\n",
        f"{len(recs)} hallazgo(s) abiertos con prioridad hasta {min_priority}, ordenados por "
        "prioridad y severidad. Este plan no cambia ningún archivo.\n",
    ]
    if not recs:
        out.append("Nada pendiente.")
        return "\n".join(out) + "\n"
    for priority in PRIORITIES[: limit + 1]:
        group = [r for r in recs if r["data"]["priority"] == priority]
        if not group:
            continue
        out.append(f"## {priority}\n")
        for r in group:
            d = r["data"]
            mode, reasons = classify(d, cfg)
            files = ", ".join(f"`{f}`" for f in [d["file"], *d.get("files", [])])
            out.append(
                f"### {r['id']} · {escape(d['title'])}\n\n"
                f"- **Severidad:** {d['severity']} · **Esfuerzo:** {d['effort']} · "
                f"**Riesgo de la solución:** {d['fix_risk']}\n"
                f"- **Modo:** {mode}{' — ' + '; '.join(reasons) if reasons else ''}. "
                f"{MODE_HELP[mode]}\n"
                f"- **Archivos que se modificarían:** {files}\n"
                f"- **Qué hacer:** {escape(d['fix'])}\n"
                f"- **Test de regresión:** {escape(d['regression_test'])}\n"
                f"- **Verificar con:** "
                f"`auditor.py checks --only {','.join(verification(d, cfg))}`\n"
            )
    return "\n".join(out) + "\n"
