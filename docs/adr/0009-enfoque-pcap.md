# ADR-0009: Enfoque en el examen PCAP

- **Estado:** Aceptada
- **Fecha:** 2026-09-27

## Contexto

El objetivo de la web pasa a ser preparar la certificación **PCAP-31-03** (Python Institute): 40 preguntas, 65 minutos, aprobado con 70 %, cinco bloques con peso fijo (Módulos y paquetes 12 %, Excepciones 14 %, Strings 18 %, POO 34 %, Miscelánea 22 %). No se ha encontrado ninguna versión posterior del examen (VERIFY en pythoninstitute.org antes de presentarse).

## Opciones

- **A. Ruta PCAP completa:** reorganizar el temario por los bloques del examen y añadir la zona de examen.
- **B. Curso actual + sección PCAP aparte.**
- **C. Solo un simulador.**

## Decisión

A, elegida por el autor, con las cuatro herramientas de examen (simulacro, práctica por bloque, fichas y panel) y preguntas en español o inglés a elección del alumno.

1. **Temario:** módulo 0 de bases (lo que el PCAP da por sabido), un módulo por bloque (su `slug` coincide con el del bloque) y «Después del PCAP» como extra. Las lecciones existentes se reubican; no se borra ninguna, así que el progreso guardado se conserva.
2. **Banco de preguntas** en `frontend/data/pcap.json`, separado de las lecciones: 126 preguntas (al menos el triple de las que pide cada bloque en un simulacro) y 48 fichas. Cada pregunta lleva un `check` en Python que **demuestra** la respuesta y que la CI ejecuta; se evitan detalles que cambian entre versiones de Python (textos de error, orden de sets, valores de `random` o `platform`).
3. **Originalidad:** todas las preguntas se han escrito para este proyecto. No se usan preguntas reales ni «dumps».
4. **Simulacro** con el reparto oficial (5/6/7/14/8), temporizador que corrige al llegar a cero, marcado para revisar y revisión con explicaciones al final. Las de «elige dos» solo puntúan si se aciertan las dos, como en el examen.
5. **Preparación estimada** = acierto de cada bloque (último intento de cada pregunta respondida) ponderado por su peso. «Listo» exige ≥ 80 %, todos los bloques con ≥ 5 preguntas y ≥ 60 %, y el último simulacro ≥ 75 %. Es orientativo y la web lo dice.
6. **Gamificación** dentro del sistema de ADR-0005 (XP derivados, no acumulados): 5 XP por pregunta distinta acertada alguna vez y 50 XP por simulacro aprobado (máximo 4), racha de aciertos en la práctica y 7 logros de examen.
7. **Almacenamiento:** el estado del examen se guarda en el navegador (`pld:pcap`), como el del juego. Sincronizarlo con la cuenta queda como mejora futura (tabla y migración propias).

## Consecuencias

- La interfaz de la zona de examen está en español; solo cambian de idioma las preguntas, opciones, explicaciones y fichas.
- La zona PCAP se pinta a sí misma y no se repinta con los cambios de progreso, para no perder un simulacro en curso.
