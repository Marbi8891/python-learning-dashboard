# ADR-0006: Experiencia del alumno (portada, guía, errores explicados y apariencia)

- **Estado:** Aceptada
- **Fecha:** 2026-09-26

## Contexto

La app tenía todo el contenido, pero un principiante no sabía por dónde empezar, tenía que bajar hasta la consola en cada ejemplo y los errores de Python aparecían en inglés.

## Decisiones

1. **Portada (`#/inicio`):** saludo, botón «Continuar donde lo dejaste» (primera lección pendiente), resumen de progreso, cómo funciona una lección y tarjetas de módulo con su barra. Es la ruta por defecto; las URL de lección siguen funcionando igual.
2. **Guía por lección Aprende → Practica → Comprueba** con un único botón grande «Siguiente paso» que dice qué hacer a continuación. El estado se deriva de datos existentes (lección leída, completada y quiz respondido); solo se añade `read` al estado local del juego, sin XP.
3. **Consola al lado** a partir de 1280 px de ancho (el T480 tiene 1366 px): rejilla de dos columnas con la consola fija (`position: sticky`). En pantallas más estrechas queda debajo, como antes.
4. **Errores explicados:** `runner.py` (el mismo motor en el navegador y en los tests) traduce los errores más habituales a una explicación en español con la línea del alumno y un botón «Ir a la línea N». El traceback original se mantiene: aprender a leerlo también es parte del curso.
5. **Apariencia:** tema automático (sigue al sistema), claro u oscuro, y tres tamaños de letra. Se guarda en `localStorage` (`pld:prefs`) y se aplica antes de pintar la página para evitar parpadeos. El código se muestra siempre sobre fondo oscuro, como en PyCharm.

## Consecuencias

- La auditoría WCAG (axe-core) se ejecuta en los dos temas.
- Los colores dejan de estar escritos en cada hoja de estilos: todos salen de variables en `base.css`.
- El tamaño de letra usa `zoom` en el área de estudio; la barra lateral mantiene su tamaño para no ocupar más espacio.
