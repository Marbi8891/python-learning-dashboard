# PLD AI Academy — Currículo completo

**Versión:** 1.0 · **Estado:** propuesta curricular inicial · **Idioma:** español  
**Ruta principal:** Fundamentos → Aplicación → Desarrollo → Especialización → Proyecto final

## Propósito

PLD AI Academy enseña a comprender, utilizar, desarrollar, evaluar y desplegar soluciones basadas en inteligencia artificial. La formación se integra en el sistema actual de cursos, lecciones, ejercicios, progreso, XP, repaso adaptativo y proyectos de Python Learning Dashboard.

No se presupone que el alumno sepa programar al comenzar. Los itinerarios técnicos introducen Python progresivamente y reutilizan el editor/laboratorio existente cuando sea posible.

## Itinerarios

- **AI Essentials (nivel inicial):** cursos 01–05. 48 horas de cursos + 2 horas de orientación.
- **AI Practitioner (aplicación profesional):** cursos 06, 08 y 13. 42 horas.
- **AI Developer (perfil técnico):** cursos 07–12 y 14–15. 146 horas (incluye solapamientos con otros itinerarios).
- **AI Specialist (especialización):** cursos 16–18 y al menos dos optativas del curso 19. 62 horas.
- **Capstone:** proyecto final integrador. 30 horas.

El catálogo suma **354 horas** si se cursan todas las optativas. El itinerario mínimo que elige dos optativas suma aproximadamente **314 horas**, incluidas 2 horas de orientación. Las rutas se solapan y no deben sumarse entre sí. Las horas son estimaciones de aprendizaje activo, no duración de vídeo.

## Competencias finales

Al finalizar, el estudiante podrá:
1. Explicar conceptos de IA, ML, DL, IA generativa y LLM con vocabulario correcto.
2. Elegir una herramienta o modelo en función de un problema, coste, privacidad y calidad.
3. Formular instrucciones, estructurar contextos y evaluar resultados generados.
4. Aplicar IA a tareas profesionales y verificar los resultados.
5. Programar en Python soluciones que consuman APIs de modelos.
6. Crear aplicaciones web de IA con backend, persistencia, interfaz y pruebas.
7. Implementar búsqueda semántica y RAG sobre documentación propia.
8. Crear agentes con herramientas, límites, trazabilidad y evaluación.
9. Automatizar procesos con herramientas visuales y código.
10. Identificar riesgos de seguridad, privacidad, sesgos, alucinaciones y prompt injection.
11. Desplegar, monitorizar y mantener soluciones con control de costes.
12. Documentar, presentar y defender un proyecto de IA.

## Convenciones de cada lección

Cada lección debe incluir: objetivos de aprendizaje medibles; explicación; ejemplos; vocabulario; actividad guiada; práctica individual; comprobación automática cuando sea viable; preguntas de reflexión; resumen; referencias y fecha de revisión. Las lecciones técnicas deben contener código ejecutable, instrucciones para el laboratorio, solución de referencia y criterios de evaluación.

---

# Currículo

## 00. Orientación y diagnóstico (2 h)
- 00.1 Cómo utilizar PLD AI Academy
- 00.2 Diagnóstico de conocimientos y objetivos
- 00.3 Configuración del entorno y hábitos de aprendizaje
- 00.4 Uso responsable de IA durante la formación

**Entrega:** perfil inicial y plan de aprendizaje personal.

## 01. Fundamentos de Inteligencia Artificial (8 h)
- 01.1 Qué es la IA: definiciones, alcance y límites
- 01.2 Evolución histórica: sistemas expertos, ML y modelos generativos
- 01.3 IA simbólica, aprendizaje automático y redes neuronales
- 01.4 Tipos de aprendizaje: supervisado, no supervisado y por refuerzo
- 01.5 Datos, características, etiquetas y modelos
- 01.6 Entrenamiento, validación, inferencia y generalización
- 01.7 IA estrecha, sistemas generales y conceptos que no deben confundirse
- 01.8 Casos de uso y selección de problemas

**Práctica:** mapa de soluciones de IA para una empresa ficticia.  
**Evaluación:** test conceptual + clasificación de casos.

## 02. Datos y pensamiento computacional para IA (8 h)
- 02.1 Datos estructurados y no estructurados
- 02.2 Calidad, limpieza, representatividad y procedencia
- 02.3 Variables, características y etiquetas
- 02.4 Correlación y causalidad
- 02.5 Métricas básicas y lectura de resultados
- 02.6 Sesgo de datos y leakage
- 02.7 Diseño de un problema medible
- 02.8 Preparación de un conjunto de datos sencillo

**Práctica:** detectar problemas en un dataset.  
**Proyecto corto:** definir problema, datos, métrica y riesgos.

## 03. IA Generativa y modelos de lenguaje (8 h)
- 03.1 Qué es la IA generativa
- 03.2 Cómo funcionan los LLM a nivel conceptual
- 03.3 Tokens, tokenización y ventanas de contexto
- 03.4 Predicción de tokens y generación
- 03.5 Temperatura, top-p y parámetros de generación
- 03.6 Limitaciones, alucinaciones y conocimiento desactualizado
- 03.7 Multimodalidad: texto, imagen, audio y vídeo
- 03.8 Modelos, proveedores, modelos abiertos y cerrados

**Práctica:** comparar respuestas de modelos y documentar diferencias.

## 04. Prompt Engineering profesional (10 h)
- 04.1 Anatomía de una instrucción eficaz
- 04.2 Objetivo, contexto, rol, restricciones y formato
- 04.3 Prompts zero-shot y few-shot
- 04.4 Descomposición de tareas y prompting por etapas
- 04.5 Instrucciones estructuradas y salida JSON
- 04.6 Contexto, ejemplos y delimitación de fuentes
- 04.7 Prompt chaining y plantillas reutilizables
- 04.8 Prompts para investigación y análisis
- 04.9 Prompts para programación y depuración
- 04.10 Evaluación, versionado y mejora de prompts

**Laboratorio:** construir una biblioteca de 20 prompts con casos de prueba.  
**Evaluación:** comparar prompt inicial y versión optimizada con rúbrica.

## 05. Herramientas y productividad con IA (14 h)
- 05.1 ChatGPT: modos, archivos, análisis y proyectos
- 05.2 Claude: trabajo con documentos y código
- 05.3 Gemini y ecosistema multimodal
- 05.4 Copilotos de productividad
- 05.5 Investigación asistida y verificación de fuentes
- 05.6 Documentos, informes y presentaciones
- 05.7 Hojas de cálculo y análisis de datos
- 05.8 Imagen generativa: usos y límites
- 05.9 Audio, transcripción y síntesis
- 05.10 Gestión de contexto y proyectos
- 05.11 Comparación de herramientas: calidad, privacidad y precio
- 05.12 Flujo de trabajo profesional con revisión humana

**Proyecto:** flujo de trabajo personal que documente ahorro de tiempo, calidad y riesgos.

## 06. IA aplicada a empresas y profesiones (12 h)
- 06.1 Identificar procesos candidatos
- 06.2 Matriz impacto, esfuerzo, riesgo y coste
- 06.3 Atención al cliente y clasificación de solicitudes
- 06.4 Marketing, contenidos y revisión editorial
- 06.5 Administración y extracción de información
- 06.6 Recursos humanos: límites y usos apropiados
- 06.7 Ventas, CRM y preparación comercial
- 06.8 Operaciones, documentación y conocimiento interno
- 06.9 Human-in-the-loop
- 06.10 Medición de ROI y KPIs
- 06.11 Diseño de pilotos y gestión del cambio
- 06.12 Elaboración de propuesta de IA

**Proyecto:** propuesta de automatización para una PYME, con mapa del proceso, KPIs, riesgos y estimación.

## 07. Python para Inteligencia Artificial (20 h)
- 07.1 Preparación de Python y entorno virtual
- 07.2 Repaso de tipos, estructuras y funciones
- 07.3 Módulos, paquetes y gestión de dependencias
- 07.4 Ficheros, JSON y CSV
- 07.5 HTTP, requests y APIs
- 07.6 Variables de entorno y secretos
- 07.7 Manejo de errores, logging y reintentos
- 07.8 Programación orientada a objetos aplicada
- 07.9 NumPy: arrays y operaciones
- 07.10 Pandas: carga, limpieza y transformación
- 07.11 Visualización de datos
- 07.12 Notebook y experimentación reproducible
- 07.13 Validación de entradas y tipos
- 07.14 Tests unitarios
- 07.15 Proyecto Python de análisis asistido por IA

**Laboratorio:** entorno Python en el editor PLD; para librerías incompatibles con Pyodide, laboratorio alternativo documentado.

## 08. APIs de IA y desarrollo de aplicaciones (16 h)
- 08.1 Arquitectura cliente, servidor y proveedor de modelo
- 08.2 API keys, autenticación y secretos
- 08.3 Peticiones, respuestas y manejo de errores
- 08.4 APIs de modelos: conceptos comunes
- 08.5 Mensajes, roles y contexto
- 08.6 Streaming de respuestas
- 08.7 Salidas estructuradas y validación
- 08.8 Tool/function calling
- 08.9 Control de tokens, latencia y coste
- 08.10 Rate limits, backoff y resiliencia
- 08.11 Abstracción de proveedor
- 08.12 Caching y persistencia
- 08.13 Logging y observabilidad
- 08.14 Diseño de endpoints de IA
- 08.15 Tests con mocks
- 08.16 Proyecto: aplicación web de asistente

**Proyecto:** chatbot con backend FastAPI, UI, historial, límites, configuración y pruebas.

## 09. Machine Learning aplicado (20 h)
- 09.1 Qué problemas resuelve ML
- 09.2 Flujo de un proyecto ML
- 09.3 Preparación y exploración de datos
- 09.4 División train, validation y test
- 09.5 Regresión lineal
- 09.6 Regresión logística
- 09.7 Clasificación y métricas
- 09.8 Árboles de decisión
- 09.9 Random Forest y ensembles
- 09.10 Clustering
- 09.11 Reducción de dimensionalidad, concepto
- 09.12 Overfitting y underfitting
- 09.13 Cross-validation
- 09.14 Selección de características
- 09.15 Pipelines reproducibles
- 09.16 Interpretación y límites del modelo
- 09.17 Persistencia y uso de un modelo
- 09.18 Introducción a scikit-learn
- 09.19 Proyecto de clasificación
- 09.20 Revisión y presentación

**Proyecto:** modelo ML con dataset documentado, baseline, métricas, análisis de errores y demo.

## 10. Deep Learning y redes neuronales (18 h)
- 10.1 Neuronas artificiales y perceptrones
- 10.2 Tensores y operaciones
- 10.3 Funciones de activación
- 10.4 Forward pass
- 10.5 Loss functions
- 10.6 Gradient descent
- 10.7 Backpropagation, explicación conceptual y práctica
- 10.8 Optimización y learning rate
- 10.9 Regularización
- 10.10 Redes neuronales multicapa
- 10.11 CNN y visión por computador
- 10.12 RNN y secuencias: contexto histórico
- 10.13 Transformers: arquitectura conceptual
- 10.14 Frameworks y ecosistema
- 10.15 Evaluación y overfitting
- 10.16 Hardware, GPU y recursos
- 10.17 Proyecto introductorio
- 10.18 Informe de resultados

**Proyecto:** experimento reproducible con una red pequeña o modelo preentrenado.

## 11. LLM Engineering (18 h)
- 11.1 Selección de modelos según tarea
- 11.2 Context windows y gestión de contexto
- 11.3 System prompts y políticas
- 11.4 Structured output
- 11.5 Function calling
- 11.6 Streaming
- 11.7 Conversaciones e historial
- 11.8 Memoria: tipos y límites
- 11.9 Routing entre modelos
- 11.10 Modelos pequeños y grandes
- 11.11 Evaluación automática y humana
- 11.12 Evals y datasets de prueba
- 11.13 Guardrails y validación
- 11.14 Coste, latencia y calidad
- 11.15 Observabilidad
- 11.16 Fallos y degradación controlada
- 11.17 Diseño de arquitectura
- 11.18 Proyecto: servicio LLM robusto

## 12. RAG y sistemas de conocimiento (18 h)
- 12.1 Por qué RAG
- 12.2 Ingesta documental
- 12.3 Extracción y parsing
- 12.4 Chunking
- 12.5 Embeddings
- 12.6 Bases vectoriales
- 12.7 Búsqueda semántica
- 12.8 Búsqueda híbrida
- 12.9 Reranking
- 12.10 Metadatos y filtros
- 12.11 Context assembly
- 12.12 Citación y trazabilidad
- 12.13 Calidad de recuperación
- 12.14 Evaluación de RAG
- 12.15 Actualización y eliminación de documentos
- 12.16 Seguridad y permisos
- 12.17 Optimización
- 12.18 Proyecto: chat sobre documentación

**Proyecto:** RAG con corpus propio, citas verificables, evaluación y controles de acceso.

## 13. Automatización con IA (14 h)
- 13.1 Qué es un workflow
- 13.2 Triggers y acciones
- 13.3 APIs y webhooks
- 13.4 Automatización no-code/low-code
- 13.5 Introducción a n8n
- 13.6 Conexión de servicios
- 13.7 Clasificación y extracción con LLM
- 13.8 Ramas, filtros y condiciones
- 13.9 Manejo de errores
- 13.10 Aprobación humana
- 13.11 Logs y monitorización
- 13.12 Secretos y permisos
- 13.13 Automatización de tareas de oficina
- 13.14 Proyecto: workflow completo

**Proyecto:** flujo de recepción, clasificación, borrador y aprobación de solicitudes; sin enviar acciones externas automáticamente por defecto.

## 14. Agentes de IA (20 h)
- 14.1 Diferencia entre chatbot, workflow y agente
- 14.2 Componentes de un agente
- 14.3 Objetivos y planificación
- 14.4 Tool calling
- 14.5 Definición de herramientas seguras
- 14.6 Estado y memoria
- 14.7 Ciclo de ejecución
- 14.8 Reglas de parada
- 14.9 Supervisión humana
- 14.10 Agentes especializados
- 14.11 Orquestación de agentes
- 14.12 Sistemas multiagente: cuándo no usarlos
- 14.13 Evaluación de agentes
- 14.14 Simulación y pruebas
- 14.15 Gestión de permisos
- 14.16 Costes y límites de ejecución
- 14.17 Trazas y auditoría
- 14.18 Recuperación ante fallos
- 14.19 Diseño de agente para un caso real
- 14.20 Proyecto: agente con herramientas y límites

**Proyecto:** agente que ejecuta herramientas autorizadas, requiere aprobación para acciones sensibles y mantiene trazabilidad.

## 15. Despliegue, MLOps y operación (16 h)
- 15.1 De prototipo a producción
- 15.2 Configuración por entorno
- 15.3 Docker
- 15.4 Backend y APIs
- 15.5 Persistencia
- 15.6 CI/CD
- 15.7 Versionado de prompts y modelos
- 15.8 Gestión de datasets y evaluaciones
- 15.9 Monitorización de calidad
- 15.10 Monitorización de coste y latencia
- 15.11 Logs y trazas
- 15.12 Feedback y revisión
- 15.13 Cambios de proveedor/modelo
- 15.14 Rollback y fallback
- 15.15 Escalabilidad y límites
- 15.16 Proyecto: despliegue reproducible

## 16. IA local y modelos open source (14 h)
- 16.1 Modelos open weights frente a servicios
- 16.2 Hardware: RAM, VRAM, CPU y almacenamiento
- 16.3 Cuantización
- 16.4 Ollama y runtimes locales
- 16.5 Descargar y ejecutar modelos
- 16.6 APIs locales
- 16.7 Comparación de modelos
- 16.8 Contexto y límites
- 16.9 Embeddings locales
- 16.10 RAG local
- 16.11 Privacidad y aislamiento
- 16.12 Actualización de modelos
- 16.13 Rendimiento
- 16.14 Proyecto: asistente local

## 17. IA multimodal (12 h)
- 17.1 Conceptos multimodales
- 17.2 Análisis de imágenes
- 17.3 OCR y extracción de texto
- 17.4 Audio y speech-to-text
- 17.5 Text-to-speech
- 17.6 Conversación por voz
- 17.7 Vídeo y resumen temporal
- 17.8 Datos multimodales y formatos
- 17.9 Aplicaciones
- 17.10 Evaluación
- 17.11 Privacidad y derechos
- 17.12 Proyecto multimodal

## 18. Seguridad, privacidad, ética y regulación (16 h)
- 18.1 Riesgos y límites de sistemas generativos
- 18.2 Privacidad y minimización de datos
- 18.3 Datos personales y RGPD: principios
- 18.4 Secretos y datos sensibles
- 18.5 Prompt injection
- 18.6 Jailbreaks y abuso
- 18.7 RAG poisoning
- 18.8 Exfiltración de datos
- 18.9 Tool abuse y permisos
- 18.10 Supply chain de modelos y datasets
- 18.11 Seguridad de APIs
- 18.12 Human oversight
- 18.13 Sesgos y evaluación de impactos
- 18.14 Transparencia y documentación
- 18.15 AI Act: visión general y seguimiento de obligaciones
- 18.16 Threat modelling para aplicaciones de IA

**Laboratorio:** threat model y pruebas de seguridad de una aplicación de IA en entorno local/controlado.

## 19. Especializaciones optativas (10 h cada una; escoger al menos dos, 20 h mínimo)
### 19A. IA para análisis de datos (10 h)
- Preparación de datos con asistentes
- Exploración y visualización
- Análisis crítico de resultados
- Automatización de informes
- Proyecto de análisis

### 19B. IA para desarrollo de software (10 h)
- Asistentes de código
- Diseño antes de generar
- Refactorización
- Tests generados y revisión
- Seguridad de código generado
- Proyecto de software asistido

### 19C. IA para ciberseguridad defensiva (10 h)
- Clasificación y resumen de alertas
- Análisis de logs
- Threat intelligence asistida
- Detección de phishing
- Riesgos de uso de IA en SOC
- Proyecto defensivo con dataset de laboratorio

### 19D. Computer Vision (10 h)
- Clasificación de imágenes
- Detección y segmentación
- Modelos preentrenados
- Inferencia
- Métricas y errores
- Proyecto

### 19E. NLP clásico (10 h)
- Limpieza y tokenización
- Clasificación de texto
- Sentimiento y extracción
- Evaluación
- Proyecto

### 19F. IA para emprendimiento y producto (10 h)
- Validación de problema
- Prototipos
- UX con IA
- Costes y monetización
- Riesgos y posicionamiento
- Proyecto de MVP

## 20. Proyecto final / Capstone (30 h)
El alumno escoge una solución, documenta su alcance y construye un prototipo funcional.

**Requisitos mínimos:**
- Problema real y usuario objetivo.
- Arquitectura y decisión de modelo.
- Dataset o fuentes con procedencia.
- Código versionado.
- Interfaz funcional.
- Backend o workflow cuando corresponda.
- Evaluación de calidad.
- Seguridad y privacidad.
- Coste estimado.
- Tests.
- Documentación de instalación.
- Demo y defensa.

**Entregables:** repositorio, README, arquitectura, demo, informe de evaluación, threat model y presentación.

**Rúbrica (100 puntos):**
- Problema y alcance: 10
- Arquitectura y decisiones: 15
- Implementación: 25
- Calidad y evaluación: 15
- Seguridad y privacidad: 15
- Documentación y reproducibilidad: 10
- Demo y defensa: 10

Aprobado: 70/100 y sin fallos críticos de seguridad o privacidad sin resolver.

## Evaluación y acreditación PLD

- Tests de módulo: 20 %
- Laboratorios: 25 %
- Proyectos: 35 %
- Capstone: 20 %

Condiciones recomendadas para el certificado de itinerario:
- 70 % mínimo global.
- Completar todos los módulos obligatorios.
- Aprobar los laboratorios esenciales.
- Presentar y defender el capstone.
- Certificado emitido por PLD; no se presentará como acreditación oficial ni certificación externa.

## Sistema pedagógico

- Lecciones cortas y objetivos concretos.
- Aprendizaje activo, práctica deliberada y repaso espaciado.
- Evaluación diagnóstica y adaptativa.
- Explicaciones de errores, no solo respuesta correcta.
- El tutor IA debe ayudar a razonar y evitar resolver automáticamente los ejercicios salvo que el alumno solicite una solución tras intentarlo.
- En programación, el alumno debe explicar, modificar y justificar el código.
- Registro transparente del uso de IA en proyectos y actividades.

## Revisión del contenido

Cada curso debe registrar: versión, responsable/editor, fecha de revisión, fuentes, herramientas/versiones y avisos de contenido que cambia con rapidez. Los modelos, precios, interfaces y normas deben revisarse periódicamente. Evitar afirmar que una herramienta o certificación está vigente sin verificación.

## Prioridad de implementación en PLD

1. Añadir catálogo AI Academy y rutas.
2. Cargar cursos y lecciones desde datos declarativos.
3. Reutilizar progreso, XP, niveles, logros y repaso adaptativo.
4. Añadir quizzes y ejercicios por lección.
5. Implementar laboratorios Python donde sean compatibles.
6. Crear Projects Hub y rúbricas.
7. Añadir AI Mentor con contexto de curso/lección y políticas pedagógicas.
8. Implementar evaluación final y certificado interno.
9. Añadir analytics de aprendizaje.
10. Diseñar integración de proveedor IA con configuración, límites, privacidad y trazabilidad.

