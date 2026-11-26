# Proceso de desarrollo de Python Learning Dashboard

> Documento de seguimiento académico. Debe completarse con hechos y evidencias del desarrollo real. No se deben inventar fechas, horas, autorías, pruebas ni decisiones retrospectivas.

## 1. Propósito

Este documento describe cómo se ha organizado y dirigido el desarrollo de Python Learning Dashboard (PLD), qué decisiones se han tomado, qué herramientas se han utilizado y cómo se ha comprobado el resultado.

PLD es una aplicación web educativa para aprender Python y apoyar el estudio de contenidos de DAW y la preparación del PCAP.

- Repositorio: https://github.com/Marbi8891/python-learning-dashboard
- Demo: https://marbi8891.github.io/python-learning-dashboard/
- Memoria académica: [../memoria/memoria.md](../memoria/memoria.md)
- Decisiones de arquitectura: [../DECISIONS.md](../DECISIONS.md)
- Pruebas: [../TESTING.md](../TESTING.md)

## 2. Forma de trabajo

El trabajo se organiza en iteraciones pequeñas. Para cada cambio se procura:

1. Identificar una necesidad o un error concreto.
2. Revisar cómo está resuelto actualmente y qué partes pueden verse afectadas.
3. Comparar alternativas cuando la decisión tenga consecuencias técnicas.
4. Implementar el cambio, manualmente o con asistencia de herramientas, dejando claro qué ayuda se ha utilizado.
5. Revisar el código y comprobar que encaja con la arquitectura existente.
6. Ejecutar las pruebas adecuadas y revisar el resultado.
7. Documentar la decisión, las limitaciones y los siguientes pasos.

Este flujo describe el método de trabajo que se quiere mantener. Para afirmar que se siguió en una tarea concreta debe existir evidencia en el commit, la incidencia, la prueba o el registro de trabajo correspondiente.

## 3. Responsabilidades y uso de herramientas

El alumno es responsable de definir el problema, establecer prioridades, decidir si acepta una propuesta, revisar los cambios y comprobar el funcionamiento de la aplicación.

Las herramientas de IA generativa se han utilizado como apoyo en tareas de análisis, programación, depuración, pruebas y documentación. Su participación se detalla en [USO-DE-INTELIGENCIA-ARTIFICIAL.md](USO-DE-INTELIGENCIA-ARTIFICIAL.md).

No se atribuirá al alumno la escritura manual de código que haya sido generado por una herramienta. Tampoco se considerará validado un cambio por el mero hecho de que una herramienta lo haya propuesto.

## 4. Evidencias que se conservarán

| Evidencia | Qué permite comprobar | Dónde consultarla |
|---|---|---|
| Historial Git | Evolución y contenido de los cambios | Commits y pull requests |
| Issues o tareas | Problema y alcance previsto | GitHub Issues / registro de tareas |
| Decisiones técnicas | Alternativas y motivos de elección | [DECISIONS.md](../DECISIONS.md) |
| Pruebas automatizadas | Comportamiento comprobado por código | [TESTING.md](../TESTING.md), CI y directorios de tests |
| Pruebas manuales | Comprobaciones realizadas por una persona | Registro de validación de cada tarea |
| Documentación | Funcionamiento y límites conocidos | Carpeta [docs](..) |

Un commit demuestra que un cambio entró en el repositorio, pero por sí solo no demuestra quién escribió cada línea ni qué comprensión tiene el alumno. Esa comprensión debe acreditarse también mediante explicaciones y ejercicios prácticos.

## 5. Registro de iteraciones

Añadir una entrada por cada bloque de trabajo relevante. No completar campos con estimaciones presentadas como datos exactos.

| Fecha | Necesidad o tarea | Decisión tomada por el alumno | Ayuda de IA utilizada | Revisión y pruebas | Evidencia |
|---|---|---|---|---|---|
| [Completar] | [Qué había que resolver] | [Decisión y motivo] | [Herramienta y tipo de ayuda, o ninguna] | [Qué se revisó y qué se ejecutó] | [Commit, PR, issue o test] |

## 6. Cómo se acredita el aprendizaje

Para cada parte importante se preparará una evidencia de comprensión:

- **Explicar:** describir el flujo de datos y las responsabilidades de los componentes.
- **Modificar:** realizar un cambio pequeño y comprobarlo.
- **Justificar:** explicar la decisión técnica y una alternativa razonable.
- **Depurar:** interpretar un fallo y describir cómo se localizó.
- **Validar:** identificar qué prueba demuestra el comportamiento y qué no cubre.

La lista de prácticas y preguntas se mantiene en [PLAN-DE-APRENDIZAJE-Y-DEFENSA.md](PLAN-DE-APRENDIZAJE-Y-DEFENSA.md).

## 7. Límites y honestidad académica

- Se respetarán las normas del centro sobre IA, autoría, citas y evaluación.
- Se declarará el uso de IA de forma coherente con la contribución real.
- No se afirmará que una prueba se ha ejecutado si no existe un resultado verificable.
- No se presentarán propuestas generadas por IA como decisiones personales sin revisión.
- Se distinguirá entre funcionalidades terminadas, parcialmente terminadas y pendientes.
- Los datos pendientes de comprobar se marcarán como tales en la memoria.

## 8. Revisión antes de entregar

- [ ] Las fechas y horas corresponden a registros reales.
- [ ] La memoria coincide con el estado actual del repositorio.
- [ ] Las contribuciones de IA están descritas sin ocultarlas ni exagerarlas.
- [ ] Los cambios importantes tienen evidencias localizables.
- [ ] El alumno puede explicar y modificar los flujos principales.
- [ ] Las pruebas citadas se han ejecutado y sus resultados están disponibles.
- [ ] Se han consultado las instrucciones del tutor y del centro.
