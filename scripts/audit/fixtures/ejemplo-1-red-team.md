# Red team (EJEMPLO FICTICIO para tests y documentación)

```json audit-findings
{
  "findings": [
    {
      "title": "Falta límite de intentos en el endpoint de ejemplo",
      "severity": "Alta", "priority": "P1", "category": "security",
      "file": "backend/app/routers/ejemplo.py", "line": 10, "ref": "RT-900",
      "description": "POST /api/v1/ejemplo no aplica rate_limit.",
      "evidence": "ejemplo.py:10 @router.post sin Depends(rate_limit)",
      "impact": "Fuerza bruta contra la cuenta.", "likelihood": "media",
      "fix": "Añadir la dependencia de límite de intentos existente.", "effort": "S",
      "fix_risk": "low", "regression_test": "Test que hace N+1 intentos y espera 429.",
      "kind": "sospecha", "key": "no-rate-limit-ejemplo"
    },
    {
      "title": "Hallazgo sin evidencia (se rechaza)",
      "severity": "HIGH", "priority": "P1", "category": "security",
      "file": "backend/app/main.py", "description": "x", "impact": "x",
      "likelihood": "low", "fix": "x", "effort": "S", "fix_risk": "low",
      "regression_test": "x", "kind": "fact", "key": "sin-evidencia"
    }
  ]
}
```
