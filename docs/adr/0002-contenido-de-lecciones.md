# ADR-0002: Contenido de las lecciones, fuente única y política de fuentes

- **Estado:** Aceptada
- **Fecha:** 2026-09-25

## Contexto

La teoría se basa en el tutorial oficial de Python, *Python para todos* (PY4E) y documentación de librerías. El frontend se publica en GitHub Pages y todavía no hay backend desplegado. Aun así, el backend también debe servir las lecciones.

## Decisión

1. **Fuente única:** `frontend/data/lessons.json`.
   - El frontend lo lee directamente, así que funciona en Pages sin backend.
   - El backend lo carga en la base de datos con `python -m app.seed`. La ruta se puede cambiar con `LESSONS_FILE`.
2. **Texto propio:** las explicaciones están redactadas para este proyecto, sin copiar las fuentes. Cada lección enlaza a sus fuentes en `sources`.
3. **Validación:** un test comprueba que todas las lecciones tienen teoría, ejemplo, ejercicio y al menos una fuente con URL `https`.
4. **Formato:** Markdown mínimo (párrafos, listas, `código`, **negrita**, *cursiva*). Se renderiza escapando siempre el HTML, así que el contenido no puede inyectar código.

## Consecuencias

- Añadir o corregir una lección solo requiere editar un archivo.
- El backend depende de la carpeta `frontend/` para cargar el contenido. Es aceptable en un monorepo y se puede cambiar con `LESSONS_FILE`.
- Hay que respetar las licencias: la documentación de Python exige atribución, y PY4E tiene una licencia Creative Commons no comercial (VERIFY: comprobar la licencia exacta antes de cualquier uso comercial). Por eso se enlaza y no se copia.
- El progreso se guarda por ahora en `localStorage` (cada navegador el suyo). Pasará al backend cuando haya usuarios (ADR-0001, fase 3).
