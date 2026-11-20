# Revisión, segunda auditoría (EJEMPLO FICTICIO)

```json audit-findings
{
  "findings": [
    {
      "title": "El temporizador del simulacro no se detiene al salir",
      "severity": "HIGH", "priority": "P1", "category": "bugs",
      "file": "./frontend/js/ejemplo/simulacro.js", "line": 44, "function": "startTimer",
      "description": "Ahora además se duplica al volver a entrar.",
      "evidence": "simulacro.js:44 dos setInterval activos tras volver a entrar",
      "impact": "El tiempo baja al doble de velocidad.", "likelihood": "alta",
      "fix": "Guardar el id y llamar a clearInterval al salir.", "effort": "S",
      "fix_risk": "low", "regression_test": "Unitario: entrar dos veces, un único timer.",
      "kind": "fact", "key": "timer-not-cleared"
    },
    {
      "title": "Imagen de portada sin texto alternativo",
      "severity": "LOW", "priority": "P2", "category": "ux-accessibility",
      "file": "frontend/ejemplo.html", "line": 12,
      "description": "<img> decorativa sin alt.",
      "evidence": "ejemplo.html:12 <img src=portada.webp>",
      "impact": "Un lector de pantalla lee el nombre del archivo.", "likelihood": "alta",
      "fix": "Añadir alt=\"\" por ser decorativa.", "effort": "S", "fix_risk": "low",
      "regression_test": "La e2e de axe (regla image-alt).", "kind": "fact",
      "key": "portada-sin-alt"
    }
  ],
  "resolved": [
    {"id": "AUD-003", "evidence": "ejemplo.py:10 ahora usa Depends(rate_limit); test_ejemplo_429 pasa"}
  ]
}
```
