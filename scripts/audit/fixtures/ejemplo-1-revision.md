# Revisión (EJEMPLO FICTICIO para tests y documentación)

Este informe es inventado: los hallazgos no describen el código real del proyecto.

```json audit-findings
{
  "findings": [
    {
      "title": "El temporizador del simulacro no se detiene al salir de la vista",
      "severity": "MEDIUM", "priority": "P2", "category": "bugs",
      "file": "frontend/js/ejemplo/simulacro.js", "line": 42, "function": "startTimer",
      "description": "setInterval se crea al entrar y no se limpia al cambiar de vista.",
      "evidence": "simulacro.js:42 setInterval(tick, 1000) sin clearInterval en unmount",
      "impact": "El contador sigue corriendo y descuenta tiempo de otro intento.",
      "likelihood": "media", "fix": "Guardar el id y llamar a clearInterval al salir.",
      "effort": "S", "fix_risk": "low",
      "regression_test": "Unitario: salir de la vista y comprobar que no hay timers activos.",
      "kind": "hecho", "key": "timer-not-cleared"
    },
    {
      "title": "Función de render de 180 líneas",
      "severity": "LOW", "priority": "P3", "category": "code-quality",
      "file": "frontend/js/ejemplo/panel.js", "function": "renderPanel",
      "description": "Mezcla cálculo de datos y construcción del DOM.",
      "impact": "Difícil de probar y de cambiar.", "likelihood": "low",
      "fix": "Extraer el cálculo a una función pura con su test.", "effort": "M",
      "fix_risk": "low", "regression_test": "Unitario de la función extraída.",
      "kind": "recommendation", "key": "render-panel-too-long"
    }
  ],
  "positives": ["La lógica del repaso espaciado está aislada en funciones puras con tests."]
}
```
