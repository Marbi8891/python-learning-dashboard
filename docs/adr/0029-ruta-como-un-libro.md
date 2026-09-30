# ADR-0029: La Ruta como un libro

- **Estado:** Aceptada e implementada (app 0.15.0)
- **Fecha:** 2026-09-30
- **Sustituye a:** [ADR-0028](0028-ruta-sin-ruido-visual.md) (camino con línea). La lógica de la ruta no cambia: las unidades, las lecciones, las vidas y el desbloqueo siguen igual.

## Contexto

Tras el camino «sin ruido» (ADR-0028), el autor pidió un rediseño completo de la Ruta **tipo libro**:

- arriba, el nombre del tema;
- un desplegable con todas las lecciones de ese tema.

## Decisión

1. **Cada tema es una página** (`HorizontalPager`) que se pasa deslizando, o con «‹ Anterior» y «Siguiente ›» del pie, que muestra «3 / 12». El libro se abre en la página del tema que toca (`Book.openingPage`).
2. **Cabecera fija** con «TEMA 3 DE 12» y el título del tema de la página visible. Cambia sola al pasar de página. Tiene dos desplegables:
    - **Lecciones:** el botón «4 lecciones · 2 hechas ▾» abre la lista de las lecciones del tema, cada una con su estado (✓ hecha y repetible, ▶ la que toca, · bloqueada) y su número de preguntas. Tocar una la abre.
    - **Índice:** todos los temas del curso; tocar uno lleva a su página con una animación.
3. **La página** está pensada para leerse como un libro:
    - el número del capítulo grande en serif;
    - el título, el estado y el progreso (barra fina animada);
    - una **entradilla**: el primer párrafo de la teoría del tema en serif (`Book.intro`, cortado en una frase si es largo);
    - «Leer la teoría completa ›».
4. **Una sola acción principal por página:**
    - «Continuar · Lección N de M» si el tema está en curso;
    - «Repasar este tema» si ya está hecho;
    - si está bloqueado, una frase que explica qué hacer.

   Debajo, «Practicar este tema (sin gastar vidas)».
5. Se mantienen la barra de estado en texto (ADR-0028) y el aviso de quedarse sin vidas.

**Código:**

- `pcap/Book.kt` tiene la entradilla y la página de apertura, sin Android y con tests (`BookTest`, que comprueba que todos los temas de todos los cursos tienen entradilla);
- la interfaz está en `ui/PathScreen.kt`.

## Alternativas descartadas

| Opción | Por qué no |
| --- | --- |
| Lista vertical de temas plegables | Se parece más a un índice que a un libro; la página por tema da foco y espacio a la lectura. |
| Las lecciones siempre visibles en la página | El autor pidió un desplegable, y así la página queda limpia para la entradilla. |
| Página de teoría completa dentro del pager | Duplicaría la pantalla de Teoría; la entradilla invita a leerla sin repetirla. |

## Consecuencias

- **DONE:** el dominio Kotlin compila y pasan 65 tests, 4 nuevos.
- **VERIFY:**
  - la interfaz solo se compila en la CI;
  - hay que probar en el móvil el deslizamiento entre páginas, los dos desplegables, TalkBack (la cabecera del tema es un encabezado y el pie dice «Página 3 de 12») y los temas claro y oscuro.
