# Android: aprendizaje primero

La app Android ya no se plantea como una copia de la navegación web.

## Objetivo

El flujo principal es:

1. recomendar qué practicar;
2. presentar una pregunta;
3. corregir inmediatamente;
4. explicar el error;
5. repetir las preguntas falladas;
6. volver a recomendar según el historial.

## Primera entrega

La pestaña **Aprender** es la pantalla inicial.

La recomendación prioriza:

- preguntas cuyo repaso está pendiente;
- preguntas falladas recientemente;
- preguntas nuevas;
- finalmente, repaso general.

Cada sesión contiene hasta cinco preguntas y utiliza `LessonRun` para volver a poner al final de la sesión una pregunta fallada.

El estado de aprendizaje sigue usando el modelo local existente (`PcapState`) y por tanto funciona sin conexión y puede sincronizarse con la cuenta.

## Lo que queda fuera

Esta entrega no intenta resolver todavía:

- ejecución nativa de Python;
- generación de ejercicios por IA;
- recomendación basada en un modelo estadístico complejo;
- gamificación adicional;
- una migración completa de las pantallas existentes.

Primero se valida el ciclo básico de aprendizaje.

## Siguiente paso

Convertir la recomendación en un motor de dominio independiente de Compose y añadir métricas por concepto: precisión reciente, número de errores, tiempo desde el último intento y dominio estimado.
