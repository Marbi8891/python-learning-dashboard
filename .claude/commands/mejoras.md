---
description: Busca mejoras en el proyecto con el agente buscador-mejoras y guarda el informe
argument-hint: "[área opcional, p. ej. accesibilidad o curso de Java]"
---

Usa el subagente `buscador-mejoras` para buscar mejoras en este proyecto.

- Área: $ARGUMENTS (si está vacío, todo el proyecto).
- Pásale la fecha de hoy y la lista de informes que ya hay en `.claude/informes/`.

Cuando termine:

1. Guarda su informe, tal cual, en `.claude/informes/mejoras-AAAA-MM-DD.md` con la fecha de hoy
   (si ya existe uno de hoy, añade `-2`, `-3`...). Esa carpeta no se sube a Git.
2. Muéstrame el resumen y los primeros pasos recomendados, y dime la ruta del informe.
3. No implementes ninguna mejora hasta que yo elija cuál.
