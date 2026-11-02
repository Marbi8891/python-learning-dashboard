---
description: Inspecciona la web o aplica una mejora pequeña del frontend con el agente mejorador-web
argument-hint: "[MW-NNN | MJ-NNN | descripción de la mejora] (vacío: solo inspeccionar y proponer)"
---

Usa el subagente `mejorador-web`.

- Tarea: $ARGUMENTS
- Si la tarea está vacía, pídele **solo inspección**: que no cambie nada y devuelva candidatas MW-NNN.
- Si es un MJ-NNN, pásale el informe de `.claude/informes/mejoras-*.md` donde aparece.
- Pásale la fecha de hoy y la lista de informes que ya hay en `.claude/informes/`.

Cuando termine:

1. Si solo ha inspeccionado, guarda su respuesta tal cual en `.claude/informes/mejoras-web-AAAA-MM-DD.md`
   (si ya existe uno de hoy, añade `-2`, `-3`...). Esa carpeta no se sube a Git.
2. Muéstrame el resumen: las candidatas, o la rama, el commit, el antes y después y las pruebas.
3. No subas la rama, no abras el PR y no fusiones nada hasta que yo lo diga.
