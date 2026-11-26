# PLD AI Academy — Especificación de integración

## Principios
- Mantener arquitectura actual: HTML/CSS/JavaScript ES Modules, backend FastAPI, SQLAlchemy/Alembic, Pyodide en Worker y PWA.
- No migrar a React/Vue ni introducir una segunda plataforma educativa.
- La formación debe ser data-driven; los cursos no se hardcodean en componentes.
- Reutilizar mecanismos existentes de cursos, lecciones, quiz, progreso, XP, logros, plan de estudio y repaso adaptativo.
- Progresión modular, accesible y responsive.
- Contenido versionado en Git y validado por scripts.
- No exigir una API key para consumir el contenido curricular. El tutor IA será una función separada, opcional y sujeta a configuración.

## Modelo de contenido propuesto

Course:
- id (estable, slug)
- track_id
- title, subtitle, description
- level (beginner/intermediate/advanced/specialist)
- estimated_hours
- order
- prerequisites[]
- outcomes[]
- tags[]
- status (draft/published)
- curriculum_version
- review_date

Module:
- id
- course_id
- title
- description
- order
- estimated_minutes
- objectives[]
- lessons[]
- assessment_id (opcional)

Lesson:
- id
- module_id
- title
- type (concept/video/reading/demo/lab/project/review)
- estimated_minutes
- content_blocks[]
- objectives[]
- vocabulary[]
- exercise_ids[]
- quiz_id
- resources[]
- reviewed_at
- content_version

Exercise:
- id
- lesson_id
- type (multiple_choice, code, short_answer, scenario, project_task)
- prompt
- starter_code (opcional)
- test_cases (solo ejercicios de código)
- hints[]
- solution (no exponer antes de completar intentos o solicitar ayuda)
- rubric
- difficulty
- tags

Assessment:
- id
- lesson/module/course scope
- question_pool
- time_limit (opcional)
- pass_score
- attempts_policy
- feedback_policy

Project:
- id
- course_id
- title
- brief
- requirements[]
- milestones[]
- rubric[]
- submission_types[]
- suggested_tools[]
- safety_notes

## UX

Añadir entrada «AI Academy» al menú y navegación. La página debe mostrar:
- hero compacto con progreso global
- rutas/itinerarios
- catálogo filtrable por nivel, duración, tema y prerequisitos
- tarjeta de curso: progreso, horas, nivel, próximo paso
- página de curso: módulos y lecciones, requisitos y proyecto
- vista de lección: contenido, ejemplos, práctica, quiz, recursos
- laboratorio integrado cuando el ejercicio sea ejecutable
- panel de proyectos
- progreso y logros
- evaluación/certificado interno
- AI Mentor contextual, con opción de ocultarlo

## AI Mentor: contrato pedagógico
El tutor recibe solo el contexto necesario: curso, módulo, lección, objetivo, intento del alumno, código/resultado si el alumno lo comparte, nivel de dominio y preferencia de ayuda.

Modos:
1. Socrático: pistas y preguntas; predeterminado.
2. Explicación: explicación del concepto con ejemplo nuevo.
3. Debugging: analizar error y sugerir pasos, sin reemplazar automáticamente todo el código.
4. Revisión: feedback basado en rúbrica.
5. Solución completa: disponible después de intentos o petición explícita; mostrar explicación y reflexión.

Debe:
- reconocer incertidumbre y no inventar documentación
- citar/identificar fuentes cuando consulte material externo
- no afirmar que ejecutó código si no se ejecutó
- proteger secretos y datos personales
- evitar exponer respuestas de evaluación activa sin política de desbloqueo
- registrar metadatos mínimos: modelo/proveedor, fecha, modo, tokens/coste si disponibles, contexto curricular y feedback del usuario; no guardar conversaciones por defecto si no existe consentimiento/configuración clara
- tener límites de tasa y coste, fallback y manejo de errores
- separar contenido curricular del proveedor de IA

## Backend (propuesta, adaptar a APIs existentes)
- GET /api/academy/tracks
- GET /api/academy/courses
- GET /api/academy/courses/{course_id}
- GET /api/academy/modules/{module_id}
- GET /api/academy/lessons/{lesson_id}
- GET /api/academy/projects
- POST /api/academy/assessments/{assessment_id}/attempts
- GET /api/academy/progress
- POST /api/academy/mentor/chat (feature flag/configuración)
- POST /api/academy/projects/{project_id}/submissions

No crear endpoints duplicados si el backend ya ofrece equivalentes. Revisar la arquitectura real antes de implementar.

## Persistencia
Evaluar reutilización de tablas actuales de course/lesson/progress/quiz. Si es necesario, crear migraciones incrementales para tracks, proyectos, submissions, evaluaciones y AI mentor audit metadata. No almacenar API keys en DB en texto plano. No registrar contenido sensible en logs.

## Frontend
- Mantener módulos ES.
- Añadir feature folder independiente (p.ej. frontend/src/features/academy/) siguiendo la organización real.
- Estado de progreso mediante la capa existente.
- Renderizar contenido con sanitización; evitar HTML arbitrario desde JSON.
- Soportar offline para el contenido curricular publicado y progreso local cuando la arquitectura actual lo permita.
- Accesibilidad WCAG 2.2 AA: teclado, foco, contraste, headings, mensajes de estado, reduced motion.

## Contenido y validación
- Fuente declarativa JSON/Markdown, con esquema y scripts de validación.
- IDs únicos y enlaces internos válidos.
- Requerir objetivos, contenido, actividad y evaluación para lecciones publicables.
- Test de integridad curricular.
- Test de regresión del progreso y repaso adaptativo.
- Tests de API, frontend unitarios y E2E.
- No publicar cursos como completos si solo existe el índice: usar estado draft y marcadores de contenido pendiente.

## Fases de desarrollo
### Fase A — Currículo y catálogo
- Crear AI Academy navigation, catálogo y curso.
- Importar currículo como cursos draft.
- Validación de datos.
- Sin AI Mentor aún.

### Fase B — Lecciones y aprendizaje
- Lección con bloques de contenido.
- Quiz, ejercicios, progreso, XP y repaso.
- PWA/offline.

### Fase C — Laboratorios
- Ejercicios Python con Pyodide/Worker.
- Soporte para ejercicios no ejecutables y simulaciones.
- Test runner y feedback.

### Fase D — Projects Hub
- Milestones, entregas, rúbricas, checklist y portfolio.

### Fase E — AI Mentor
- Backend abstraction/provider config.
- Context-aware tutor, modos, límites, privacidad, tests y auditoría.

### Fase F — Evaluación y certificados
- Exámenes por ruta.
- Capstone rubric.
- Certificado interno verificable, claramente no oficial.

## Definition of Done
- La ruta se ve y navega desde PLD.
- Curso, módulos y lecciones se cargan desde datos.
- Progreso persistente y sincronizado con el sistema existente.
- Un usuario puede completar al menos una lección, quiz y práctica end-to-end.
- Datos curricularmente validados y tests.
- Responsive, accesible y compatible con PWA.
- No hay secretos ni contenido de evaluación expuesto indebidamente.
- Documentación para añadir/editar cursos.
- Feature flag o mecanismo de despliegue gradual si la funcionalidad es incompleta.

## Alcance de este PR
Este PR añade el currículo y la especificación. No declara la Academy implementada en la aplicación ni incluye contenido completo de todas las lecciones. La siguiente fase debe convertir el currículo en datos publicables y UI funcional mediante PRs pequeños y verificables.
