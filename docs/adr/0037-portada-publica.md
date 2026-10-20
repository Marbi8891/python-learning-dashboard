# ADR-0037: Portada pública dentro de la app

- **Estado:** Propuesta (pendiente de que el autor la apruebe en el PR).
- **Fecha:** 2026-10-19
- **Relacionada:** ADR-0007 (estética), ADR-0010 (PWA), ADR-0031 (núcleo educativo por conceptos)

## Contexto

La raíz de la web llevaba en la primera visita a `#/bienvenida`, un mapa dentro de la app con el
menú lateral, y después a `#/aprender`. No había una página que presentara el producto a quien
llega desde un enlace: qué es, qué funciones tiene, qué está en desarrollo y cómo está hecho.

La web se publica en GitHub Pages bajo `/python-learning-dashboard/` y todas sus rutas son de hash.

## Decisión

1. **Una ruta más de la misma app**, `#/portada`, en lugar de una página HTML aparte o de mover la
   app a otra URL. Así no cambia ningún enlace profundo (`index.html#/…`), la CSP, el service
   worker ni la publicación en el subdirectorio.
2. **A pantalla completa**: con la portada a la vista se ocultan el menú lateral, la barra superior
   y el asistente (`body[data-page="landing"]`); tiene su propia cabecera y pie.
3. **Secciones con ruta propia** (`#/portada/funcionalidades`, `#/portada/como-funciona`…): un
   ancla `#seccion` cambiaría el hash y el router la trataría como ruta desconocida.
4. **La raíz lleva siempre a la portada** (decisión de la persona del 20/10/2026; antes solo en la
   primera visita y después a `#/aprender`). «Empezar a aprender» y el menú llevan a `#/aprender`; el logo de la
   cabecera (escritorio y móvil) lleva a la portada. `#/bienvenida` se mantiene como presentación guiada.
5. **Contenido verificable**: el texto es fijo o sale de `learning.json`, `lessons.json` y
   `DAW_COURSES`. La demostración usa el concepto «bucles» y el ejercicio `buc-01` reales, con la
   misma relación respuesta trampa → error del temario. Lo que es un ejemplo (la conversación y el
   progreso) se dice en la página. CodeFeed aparece como propuesta, sin vídeos ni botones.
6. **Sin dependencias nuevas**: `js/landing.js` y `css/landing.css` reutilizan los tokens de
   diseño, el resaltado de highlight.js ya incluido y el Python del navegador (Pyodide) solo si se
   pulsa «Ejecutar».

## Consecuencias

- Quien vuelve a la raíz sigue yendo a «¿Qué estudio ahora?»; la portada está enlazada en el pie
  del menú lateral.
- El contenido de la portada lo pinta JavaScript, como el resto de la app: sin JavaScript solo se ve
  el aviso de `<noscript>`.
- Si se publica CodeFeed, la sección debe cambiar de «En desarrollo» a enlazar la función real.
