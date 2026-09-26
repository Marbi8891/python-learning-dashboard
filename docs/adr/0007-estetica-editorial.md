# ADR-0007: Estética editorial de academia

- **Estado:** Aceptada
- **Fecha:** 2026-09-26

## Contexto

Se quiere que la web transmita la calidad de una academia de pago, sin cambiar el nombre (Python Learning Dashboard) ni añadir complejidad al backend.

## Opciones

- **A. Editorial oscuro** (tipo MasterClass): tinta casi negra, serif en titulares, dorado como acento.
- **B. Tech vibrante** (degradados, brillos).
- **C. Claro corporativo** (tipo campus universitario).

## Decisión

Opción A, elegida por el autor.

1. **Paleta:** tinta `#0c0d10`, marfil `#eeeae2`, dorado `#d4af6a` para la acción principal y el foco, y verde `#4fd18b` solo para el progreso. El tema claro es papel crema con botones en tinta. Todos los contrastes se calcularon (≥ 4,5:1) y axe-core los audita en los dos temas.
2. **Tipografía:** Fraunces (serif, licencia OFL) para titulares, alojada en el propio sitio como Inter y JetBrains Mono (sin Google Fonts: RGPD). Solo dos archivos (≈ 40 KB).
3. **Portada = ficha del curso:** nivel, duración estimada, qué aprenderás, temario desplegable con el estado de cada lección, qué incluye y requisitos. El texto del curso vive en `lessons.json` (`course` y `summary` de cada módulo), la fuente única (ADR-0002); el backend lo ignora.
4. **Duración estimada calculada**, no inventada: palabras de la teoría a 120 palabras/min + 5 min de ejemplo + 8 de ejercicio + 2 de quiz, redondeado a 5. Los retos se suman aparte (10 min por estrella). Se muestra siempre con «≈».
5. **«Mi aprendizaje» (`#/perfil`):** nivel, cifras, progreso por módulo, actividad de 12 semanas, logros e historial por lección. Todo se deriva del estado que ya existía (ADR-0005); no hay datos nuevos que guardar.
6. **Sin reclamos falsos:** ni testimonios, ni número de alumnos, ni precios. La estética es de academia de pago; el contenido no finge serlo.

## Consecuencias

- Un quiz con 0 aciertos ahora cuenta como hecho (antes no se guardaba y la guía no avanzaba).
- Las páginas completas (portada y perfil) comparten la función `showPage`; añadir otra es añadir una entrada a `VIEWS`.
