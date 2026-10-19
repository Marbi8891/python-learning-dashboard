# ADR-0036: Tutor de Python adaptativo con plan pedagógico determinista

- **Estado:** Propuesta (pendiente de que el autor la apruebe en el PR).
- **Fecha:** 2026-10-19
- **Relacionada:** ADR-0003 (los ejercicios se ejecutan en el navegador), ADR-0031 (núcleo
  educativo por conceptos), ADR-0034 (agentes A2A y Python Tutor)

## Contexto

El Python Tutor de ADR-0034 respondía bien con un modelo, pero dependía casi por completo de él:

- el nivel salía solo del número de lecciones completadas (≈ % global de avance);
- cada consulta era independiente: no sabía qué pista había dado ni si el alumno había entendido;
- el análisis del código se limitaba a buscar el tipo de error en el texto;
- con el modelo simulado (el que usa hoy la web publicada, porque no se quiere gastar en APIs de
  pago) las respuestas eran una guía genérica marcada como «Modo de desarrollo»;
- la web no distinguía una respuesta de IA de una preparada, no permitía cancelar ni reintentar y
  podía mostrar la respuesta tardía de una conversación ya cerrada.

## Decisión

1. **Plan pedagógico determinista antes del modelo** (`PythonTutorAgent.plan()`): tipo de
   consulta, concepto, nivel, análisis del código, pista que toca, si se permite la solución y
   pregunta de comprobación. El modelo recibe ese plan como guía; sin modelo, el plan es la
   respuesta. Así el tutor sin IA es útil por sí solo y un modelo pequeño (Ollama) se equivoca
   menos.
2. **Reutilizar el contenido revisado del curso** (`frontend/data/learning.json`: 22 conceptos,
   ejemplos con salida verificada en CI, errores típicos y ejercicios de predicción) en lugar de
   escribir otro temario. `services/curriculum.py` lo carga una vez y tolera que falte.
3. **Nivel por evidencias**, no por el % global: conceptos demostrados en Aprender y lecciones con
   el ejercicio superado, corregido por las dificultades del concepto de la pregunta y por las
   comprobaciones de la conversación. Si no hay evidencias, se dice.
4. **Análisis del código con `ast`, sin ejecutarlo nunca en el backend**, separando hechos de
   hipótesis. Ejecutar sigue siendo cosa del navegador (Pyodide): la web añade «Ejecutar en tu
   navegador» a los ejemplos.
5. **Memoria de conversación acotada y en memoria** (`ConversationStore`, clave sesión +
   `contextId`): extractos de 6 turnos, pistas, comprobación pendiente, aciertos y fallos;
   5 conversaciones por alumno, 2 horas sin uso. No se guardan conversaciones completas ni en la
   base de datos: el autor no ha decidido guardarlas.
6. **Respuestas preparadas sin gasto** para saludo, petición ambigua, fuera de tema y corrección
   de la comprobación: no llaman al modelo ni consumen cupo.
7. **Transparencia del origen**: `source` (`model`, `simulated`, `prepared`) en los metadatos del
   artefacto y `reason` en los fallos; la web lo dice en cada respuesta. Si el proveedor falla, se
   entrega la guía preparada. Reintentar es siempre manual.
8. **Contratos intactos**: mismas rutas REST y A2A, mismo `TutorQuery` (un campo opcional nuevo,
   `gradual`), metadatos solo añadidos; Agent Card 0.2.0.
9. **Evaluación en dos capas**: 20 casos versionados (`tests/tutor_eval/casos.json`) con criterios
   exactos que la CI comprueba sin modelo, y criterios de modelo y rúbrica que aplica
   `scripts/a2a/eval_tutor.py` con un modelo real, fuera de la CI.

## Alternativas descartadas

- **Dejarlo todo al modelo con un prompt más largo:** con Ollama 7B la adaptación y las pistas
  graduadas no son fiables, y con el modelo simulado no habría tutor.
- **Guardar las conversaciones en la base de datos:** daría continuidad entre reinicios, pero es un
  dato personal nuevo sin decisión explícita del autor.
- **Ejecutar el código del alumno en el backend para ver la salida real:** riesgo de seguridad
  innecesario; el navegador ya lo hace.
- **Un clasificador con modelo (o embeddings):** más coste y dependencias para lo que resuelven
  reglas comprobables.

## Consecuencias

- Sin dependencias nuevas, sin proveedores de pago y sin infraestructura nueva.
- El tutor sin IA de la web publicada mejora sin cambiar la configuración de Render.
- Las reglas de clasificación son heurísticas en español: una pregunta rara puede caer en el tipo
  equivocado. Los casos de evaluación lo vigilan y se amplían cuando aparezca un fallo.
- La memoria de conversación se pierde al reiniciar y no se comparte entre instancias (hoy hay
  una).
- La calidad con un modelo real no está medida en CI: hay que pasar `eval_tutor.py` con Ollama y
  revisar la rúbrica antes de activar un modelo en producción.
