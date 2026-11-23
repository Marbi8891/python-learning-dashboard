# PLD AI Tutor — Especificación funcional y técnica

Estado: propuesta de implementación (no implica que el agente esté desplegado).

## Objetivo
Añadir un tutor conversacional al Python Learning Dashboard que ayude al alumno a comprender, practicar y revisar contenidos de Python, PCAP y DAW. Debe usar el progreso real de PLD para adaptar la explicación, sin sustituir ni recalcular el motor adaptativo.

## Principios
- Enseñanza guiada: primero diagnóstico y pistas; solución completa solo cuando el alumno la solicite o tras intentos suficientes.
- El motor adaptativo sigue siendo determinista y la fuente de verdad del dominio, la confianza, la retención y las recomendaciones.
- El agente no inventa contenido del temario, resultados de evaluación ni datos del alumno. Distingue entre contexto recuperado e inferencias.
- El LLM no ejecuta código arbitrario en el servidor.
- La IA es opcional. Si no está disponible, el resto de PLD funciona igual.
- Se conserva HTML/CSS/JavaScript ES Modules, FastAPI, Pyodide, los almacenes y la sincronización existentes.

## Modos del tutor
1. Explicar: explicación adaptada al nivel, analogías breves, ejemplo y comprobación de comprensión.
2. Pista: identifica el siguiente paso sin revelar toda la solución.
3. Depurar: analiza código y error; separa causa, corrección y aprendizaje.
4. Practicar: propone un ejercicio alineado con conceptos y dificultad del catálogo.
5. Preparar examen: preguntas originales de práctica y explicación de respuestas; no presenta contenido generado como pregunta oficial.
6. Revisar progreso: interpreta datos autorizados que proporciona PLD y recomienda una acción compatible con el motor adaptativo.
7. Planificar: ayuda a distribuir el tiempo respetando el planificador existente; nunca modifica fechas o tareas sin acción expresa del alumno.

## Contexto que puede recibir
- Identificador de usuario obtenido de la sesión autenticada, nunca del cuerpo enviado por el navegador.
- Curso, módulo, unidad, lección, concepto y ejercicio actuales, validados contra el catálogo servido por PLD.
- Enunciado y código que el alumno decide compartir.
- Resultado de ejecución y error producido en Pyodide.
- Resumen mínimo del dominio, evidencias, errores activos y repaso pendiente.
- Tiempo disponible y próximos exámenes/entregas del planificador.
No adjuntar todos los historiales ni el documento completo del alumno en cada petición. Construir un contexto acotado y versionado.

## Arquitectura
Frontend ES Modules -> cliente API existente -> router IA FastAPI -> orquestador de tutor -> cliente NEXARO ya inicializado en app.state / Knowledge retrieval / herramientas de aprendizaje permitidas.
Reutilizar el cliente NEXARO existente y el router ai actual. No crear un segundo cliente LLM ni otro proveedor obligatorio. La implementación debe inspeccionar primero los contratos reales de ambos módulos.

### Contrato lógico de conversación
POST /api/v1/ai/tutor
Request:
{
  "message": "string (1..4000)",
  "mode": "explain|hint|debug|practice|exam|progress|plan",
  "context": {
    "course_id": "optional stable catalog id",
    "module_id": "optional",
    "lesson_id": "optional stable id",
    "concept_ids": ["optional stable ids"],
    "exercise_id": "optional stable id",
    "code": "optional, max 12000 chars",
    "execution": {"stdout": "optional bounded text", "stderr": "optional bounded text"}
  },
  "conversation_id": "optional opaque UUID"
}
Response:
{
  "conversation_id": "uuid",
  "message": {
    "role": "assistant",
    "content": "markdown text",
    "hints": ["optional"],
    "suggested_actions": [{"type": "practice|review|open_lesson", "target_id": "stable id"}],
    "sources": [{"type": "catalog|lesson|docs", "id": "stable id", "title": "label"}]
  },
  "usage": {"input_tokens": 0, "output_tokens": 0}
}
El contrato anterior es una propuesta de diseño: ajustar nombres, validación y versionado al router existente antes de implementarlo. No aceptar del cliente user_id, mastery, role, ni permisos.

GET /api/v1/ai/tutor/conversations?limit=20
GET /api/v1/ai/tutor/conversations/{id}
DELETE /api/v1/ai/tutor/conversations/{id}
Los endpoints de historial solo se implementarán si la política de privacidad y el almacenamiento están definidos. Cada consulta debe filtrar por el usuario autenticado.

## Herramientas internas permitidas
- get_current_lesson: recupera una lección publicada por id.
- get_concept_context: devuelve concepto, prerrequisitos y errores típicos del catálogo.
- get_student_learning_snapshot: consulta únicamente al usuario autenticado y devuelve resumen agregado.
- get_due_reviews: consulta repasos pendientes desde la lógica/almacén existente.
- get_today_plan: lee el planificador actual.
- propose_practice: selecciona o solicita un ejercicio del catálogo; la autoría del intento corresponde al flujo normal de PLD.
- explain_execution: interpreta salida/error compartidos; no vuelve a ejecutar el código en servidor.
Herramientas de solo lectura por defecto. Ninguna herramienta puede conceder XP, alterar dominio, marcar ejercicios como superados ni cambiar el planificador.

## Recuperación de conocimiento
Primera versión: recuperación por metadatos e ids estables desde el contenido publicado de PLD; evitar una base vectorial nueva mientras el volumen sea manejable. Recuperar únicamente fragmentos necesarios (lección, concepto, explicación del error, criterio de evaluación). Cada respuesta académica debe poder identificar los materiales consultados. Si no encuentra fuente, el tutor lo reconoce y pide contexto o deriva al contenido existente.
Fase posterior: embeddings/vector store solo si una evaluación muestra que la búsqueda por ids y metadatos es insuficiente.

## Memoria
- Memoria efímera: últimos turnos de la conversación, con límite de tokens y resumen incremental.
- Memoria persistente opcional: preferencias de explicación explícitamente guardadas por el alumno, objetivos de estudio y resúmenes de sesiones.
- No persistir código, datos personales ni conversaciones completas por defecto.
- Aislamiento estricto por user_id obtenido de la sesión.
- Permitir consultar, exportar y borrar la memoria persistente. Aplicar retención limitada y documentada.
- Modo invitado: sin historial persistente y sin contexto privado sincronizado.

## Experiencia de usuario
- Entrada contextual desde la lección, el ejercicio y la consola Python.
- Panel lateral/chat accesible desde teclado y móvil; no bloquear el editor.
- Acciones rápidas: «Explícame», «Dame una pista», «Analiza mi error», «Ponme otro ejercicio».
- Respuesta con secciones breves: qué ocurre, por qué ocurre, siguiente paso, mini comprobación.
- Mostrar fuentes del temario cuando se usen.
- Estados: IA no configurada, cargando, respuesta, límite alcanzado, desconexión y reintento.
- El alumno puede copiar respuesta, detener generación y borrar conversación.
- En pantallas pequeñas, chat como vista completa; respetar reduced-motion, contraste y WCAG 2.2 AA.

## Seguridad y privacidad
- Reutilizar autenticación, CSRF, CORS, límites de cuerpo, cabeceras y rate limit existentes.
- Limitar longitud de mensajes, código, salida de consola, tokens y duración de la petición.
- Rate limit por usuario y por IP para invitados, con límites de concurrencia y coste.
- No registrar prompts, código o tokens en logs. Métricas agregadas sin contenido.
- Secretos únicamente en entorno del backend. Nunca enviar claves LLM al frontend.
- Tratar el contenido del temario, código y salida como datos no confiables; resistir prompt injection. El contenido del usuario nunca puede cambiar instrucciones de sistema ni activar herramientas no autorizadas.
- No exponer datos de otros alumnos ni permitir que el modelo elija el user_id.
- Proveedor local NEXARO/Ollama como opción; cualquier proveedor remoto debe quedar sujeto a configuración, aviso de privacidad y consentimiento/contrato aplicable.
- La consola Pyodide continúa siendo el entorno de ejecución del alumno; el tutor no ejecuta el código en el servidor.

## Evaluación y pruebas
Unitarias: validación de esquemas, construcción del contexto, recorte de tokens, filtrado por usuario, sanitización de fuentes y permisos de herramientas.
Integración: IA desactivada, proveedor caído, timeout, rate limit, sesión caducada, conversación ajena, contenido inexistente, salida de Pyodide extensa, historial borrado.
Frontend: entrada desde lección y ejercicio, teclado, móvil, cancelación, reintentos y fallback sin IA.
Calidad pedagógica: conjunto de casos dorados por tema y nivel; evaluar exactitud, utilidad de pistas, cita de fuentes, no revelar solución prematuramente y ausencia de afirmaciones sobre progreso no sustentadas.
CI: no depender de llamadas reales a un LLM; usar proveedor falso determinista. Pruebas manuales separadas para modelos locales.

## Fases
P0 — Auditoría de integración actual: inspeccionar backend/app/routers/ai.py, backend/app/nexaro_client.py, configuración, modelos y pruebas. Confirmar contrato de NEXARO y capacidades del cliente.
P1 — Tutor mínimo: endpoint sobre router existente, contexto de lección/concepto, modos explicar/pista/depurar, límites y pruebas. Sin memoria persistente.
P2 — Integración adaptativa: snapshot de progreso, repasos pendientes, recomendaciones basadas en la salida de funciones existentes. Solo lectura.
P3 — UI contextual: panel y acciones en lecciones y ejercicios, accesibilidad y fallback.
P4 — Memoria privada, práctica guiada y analítica agregada, solo después de definir retención y controles de usuario.
P5 — Evaluación y despliegue gradual con bandera de configuración.

## Criterios de aceptación del MVP
- No cambia el comportamiento de PLD cuando IA está desactivada.
- Responde en contexto de una lección/concepto real y cita la fuente usada.
- Puede dar una pista sin devolver la solución completa.
- Analiza errores/código aportados por el alumno sin ejecutarlos en servidor.
- El contexto de progreso corresponde al usuario autenticado.
- No modifica XP, dominio, intentos ni planificador.
- Tiene límites de tamaño, tiempo y frecuencia.
- Cobertura de pruebas para proveedor falso y fallos de red.
- Mantiene compatibilidad con la arquitectura y pipeline CI existente.

## Decisiones pendientes
1. Confirmar si NEXARO ofrece streaming; si no, MVP con respuesta completa y contrato preparado para streaming posterior.
2. Confirmar modelo local por defecto y límites de hardware.
3. Definir política de retención y consentimiento antes de guardar conversaciones.
4. Acordar si invitados pueden usar el tutor con límites menores.
