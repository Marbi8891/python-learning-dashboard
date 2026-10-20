# Documentación legal

Trabajo de **LegalDocs AI** (`.claude/agents/legaldocs-ai.md`). Nada de esta carpeta se publica en la web:
los documentos publicados siguen siendo `frontend/privacidad.html` y `frontend/aviso-legal.html`, y solo
cambian cuando el titular aprueba una versión concreta y fusiona su PR.

| Archivo | Para qué |
|---|---|
| [PROMPT_MAESTRO.md](PROMPT_MAESTRO.md) | Instrucciones completas del agente (secciones 1-24) |
| [PRUEBAS_AGENTE.md](PRUEBAS_AGENTE.md) | Batería de aceptación del agente y registro de ejecuciones |
| [expediente/DIAGNOSTICO.md](expediente/DIAGNOSTICO.md) | Diagnóstico jurídico del proyecto |
| [expediente/MATRIZ.md](expediente/MATRIZ.md) | Matriz de trazabilidad |
| [expediente/borradores/](expediente/borradores/) | Propuestas de texto en estado BORRADOR |
| [expediente/HISTORIAL.md](expediente/HISTORIAL.md) | Versiones y aprobaciones |

Para usarlo: `claude --agent legaldocs-ai "Actualiza el expediente legal tras el último cambio"` o, en una
sesión normal, `@agent-legaldocs-ai revisa la política de privacidad`.

No es asesoramiento jurídico ni certifica el cumplimiento de ninguna norma.
