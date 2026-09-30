# ADR-0028: Rediseño de la Ruta: fluida y sin ruido visual

- **Estado:** Aceptada e implementada (app 0.14.0)
- **Fecha:** 2026-09-30
- **Sustituye en lo visual a:** la pantalla de ruta de [ADR-0012](0012-app-estilo-duolingo.md). La lógica no cambia: las unidades, las lecciones, las vidas y el desbloqueo siguen igual.

## Contexto

El autor pidió rediseñar la pantalla «Ruta» para que se viera **fluida y sin ruido visual**. La versión anterior tenía:

- tarjetas de unidad con el fondo de color y cuatro líneas de texto (bloque, peso en el examen, lecciones y acierto);
- emojis de colores en la barra de estado (🔥 ⚡ ♥) y un candado en cada unidad bloqueada;
- un zigzag marcado sin nada que uniera los nodos, y la etiqueta «EMPEZAR» encima del actual.

## Decisión

1. **Un solo acento:** solo la lección que toca usa el color principal. Las completadas llevan un verde suave y las bloqueadas son un círculo de contorno con el número en gris.
2. **Una línea fina (3 dp) une las lecciones** de cada unidad y se colorea hasta donde has llegado. Se dibuja por detrás, recortada en el borde de cada círculo. Para saber dónde está la lección anterior sin medir nada, cada fila tiene un alto fijo (84 dp).
3. **Una curva suave** en lugar del zigzag: desplazamientos de 0, 34 y 48 dp, frente a los 64 dp de antes.
4. **Cabecera de unidad fina y fija arriba** (`stickyHeader`):
    - «UNIDAD 3» en pequeño, el título, «3/4», «Teoría» y una barra de progreso de 3 dp que se rellena con animación;
    - el peso en el examen y el acierto siguen en la descripción de TalkBack, pero no ocupan la pantalla.
5. **Barra de estado en texto:** «5 días de racha · 12/20 XP hoy · 4 vidas», sin iconos. Solo cambia de color lo que importa: la meta cumplida en verde y 0 vidas en rojo.
6. **Movimiento suave:**
    - un pulso lento alrededor de la lección que toca (si el sistema desactiva las animaciones, se queda quieto);
    - las barras de progreso animadas;
    - el botón **«Ir a mi lección»**, que solo aparece cuando tu lección no está en pantalla y te lleva hasta ella con un desplazamiento animado.

## Alternativas descartadas

| Opción | Por qué no |
| --- | --- |
| Tarjeta «Hoy» fija encima del camino | Añade un bloque más de información en la pantalla principal; lo mismo está en «Mi cuenta» (ADR-0027). |
| Lista de unidades plegable | Más densa y menos visual; pierde la sensación de avanzar por un camino. |
| Dibujar todo el camino en un único Canvas | Más control, pero se pierden la accesibilidad por elemento y el reciclado de la lista. |

## Consecuencias

- La información que se quita de la vista sigue disponible: el acierto y el peso de cada unidad los lee TalkBack, y el detalle completo está en Examen o Práctica y en «Mi cuenta».
- **VERIFY:** la interfaz solo se compila en la CI. Hay que probar en el móvil, en tema claro y oscuro, la fluidez del desplazamiento, que la cabecera fija no tape la lección actual y el botón «Ir a mi lección».
