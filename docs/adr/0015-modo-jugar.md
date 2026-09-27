# ADR-0015: Modo «Jugar»: Mazmorra del Intérprete y Bug Rush

- **Estado:** Aceptada
- **Fecha:** 2026-09-27
- **Revisa:** el plan de entregas de ADR-0012 (el juego va antes de la entrega 3)

## Contexto

El autor quiere un juego que entretenga y a la vez enseñe el PCAP, construido sobre la app. Se valoraron tres conceptos:

- **A.** Roguelite de mazmorra.
- **B.** Arcade contrarreloj.
- **C.** Misiones de depuración, que necesitan Python en el móvil (entrega 5).

Se elige **A, con B como minijuego**.

## Decisión

Una pestaña nueva, **«Jugar»**, dentro de la misma app. No se hace una app aparte, para que el banco de preguntas, el progreso, la firma y la CI sean los mismos.

### La Mazmorra del Intérprete

- **Estructura:** 5 plantas, una por bloque, en el orden del examen. Cada planta tiene 3 salas, cada una con una pregunta, y un jefe de 3 preguntas con 45 s por pregunta.
- **Vidas:** la partida tiene 5 vidas propias. Fallar o agotar el tiempo quita una. Con 0 vidas se pierde la partida. Las vidas de la ruta no se tocan.
- **Monedas:**
  - se ganan 10 por sala, 15 por golpe al jefe y 25 por planta superada;
  - se gastan en dos comodines: *50/50*, que oculta dos opciones incorrectas (15 monedas), y *Curar* (40 monedas);
  - la puntuación es el total de monedas ganadas.
- **Qué aprende el jugador:**
  - las preguntas de cada planta salen de `practiceSet`: primero las falladas, luego las nuevas;
  - cada respuesta se guarda con `recordAnswer`, así que cuenta para la preparación y el repaso;
  - tras cada respuesta se muestra la explicación y se puede abrir la teoría sin perder la partida.
- **Se gana acertando, no siendo rápido.** El tiempo solo aprieta en los jefes.

### Bug Rush (90 s)

- **Mecánica:** aparece código y una respuesta propuesta. El jugador desliza, o toca «Sí»/«No», según sea la correcta o no.
- **Puntuación:** cada 5 aciertos seguidos sube el multiplicador, hasta ×4. Cada fallo resta 3 s y muestra la respuesta buena.
- **No cuenta para la preparación.** Un «sí/no» rápido no mide lo mismo que elegir entre cuatro opciones, y lo contaminaría. Solo da XP: 1 por cada 3 aciertos.

### Datos

- Las reglas viven en `pcap/Game.kt` (`DungeonRun`, `RushGame`, `GameRecords`), sin interfaz, y tienen tests.
- Los récords (partidas, plantas, puntuación y Bug Rush) se guardan en `app.game`, dentro del mismo documento JSON, y se fusionan quedándose con el máximo.
- La partida en curso vive en memoria: sobrevive a abrir la teoría o cambiar de pestaña, pero no a que Android cierre la app.

## Consecuencias

- **Plan de entregas revisado:**

  | Entrega | Contenido |
  |---|---|
  | 3 | Modo «Jugar» (este ADR) |
  | 4 | Ordenar código y completar el hueco, como salas nuevas de la mazmorra |
  | 5 | Simulacro, fichas y repaso |
  | 6 | Chaquopy |
  | 7 | Cuenta y sincronización |

- **ASSUMPTION:** antes de sincronizar, la fusión de la web (`mergePcap`) debe conservar el objeto `app`, que ahora incluye `game`. Ya estaba anotado para la entrega de sincronización.
- **VERIFY:** equilibrio de monedas y dificultad. Se ajustarán con partidas reales; las cifras están en constantes.
- **VERIFY:** la interfaz solo se compila en la CI.
