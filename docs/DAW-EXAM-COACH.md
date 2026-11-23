# DAW Exam Coach — diseño de implementación

## Objetivo personal

Convertir Python Learning Dashboard en el centro de preparación del usuario para aprobar 2.º de DAW. No es una función SaaS ni un repositorio para redistribuir apuntes: los materiales se importan para estudio personal y se mantienen sus atribuciones/licencias.

## Alcance MVP

- **Panel de 2.º DAW**: cuatro módulos prioritarios (DWEC, DWES, DIW y DAW/Despliegue), progreso por tema, tareas pendientes, próxima evaluación y sesión recomendada.
- **Biblioteca personal**: importar archivos PDF, Markdown, TXT, ZIP de apuntes y enlaces/repositorios. Mantener metadatos (origen, autor, licencia declarada, fecha de importación, módulo y tema). No publicar ni copiar contenido de fuentes sin permiso.
- **Tutor**: responder usando materiales seleccionados, mostrar referencias (archivo + página/fragmento cuando esté disponible), admitir preguntas, explicar con ejemplos y generar preguntas de comprobación. Si no hay material relevante, indicarlo y separar conocimiento general de lo que dicen los apuntes.
- **Práctica**: test, preguntas cortas, ejercicios de código, retos guiados y simulacros cronometrados. En modo práctica, no mostrar la solución antes de que el alumno lo intente.
- **Registro de errores**: guardar pregunta/tema, respuesta, explicación del fallo y siguiente repaso. Repetición espaciada con intervalos ajustables.
- **Planificador**: sesiones de lunes a viernes, configurable en minutos disponibles; priorizar exámenes/entregas, temas con menor dominio y repasos vencidos. No programar automáticamente fines de semana.
- **Privacidad**: uso personal. Materiales y progreso local por defecto; sincronización solo mediante los mecanismos de cuenta existentes y con consentimiento. No añadir APIs de pago ni enviar documentos a proveedores externos sin una elección explícita.

## Módulos y estructura de contenidos inicial

### DWEC — Desarrollo Web en Entorno Cliente
JavaScript moderno; tipos, funciones y módulos; DOM; eventos; formularios y validación; almacenamiento; asincronía (Promises/async-await); fetch y APIs; JSON; testing básico; accesibilidad en interacción.

### DWES — Desarrollo Web en Entorno Servidor
Arquitectura cliente-servidor; PHP (o lenguaje del centro); rutas y controladores; sesiones/cookies; formularios; validación; persistencia y SQL; APIs REST; autenticación/autorización; errores; seguridad web; pruebas.

### DIW — Diseño de Interfaces Web
HTML semántico; CSS; layout (Flexbox/Grid); responsive; diseño visual; accesibilidad WCAG; usabilidad; formularios; rendimiento; herramientas de inspección.

### DAW — Despliegue de Aplicaciones Web
Linux y permisos; DNS; HTTP/HTTPS/TLS; servidores web; Apache/Nginx; despliegue; variables de entorno; Docker; CI/CD; logs; monitorización; backups; seguridad y documentación.

Los temas son una plantilla inicial, no sustituyen el currículo, el aula virtual ni las instrucciones del profesor. Ajustar nombres y orden a la programación del centro.

## Fuentes de estudio — catálogo de referencia

Las fuentes se guardan como enlaces y metadatos, no se clonan ni se redistribuyen automáticamente.

- rSainz21/DAW2 — prioridad de referencia por su curso 2026–27 y organización por módulos.
- DanielGodoyDAW/2-DAW-PUBLICO — ejercicios y prácticas de 2.º DAW.
- Mboza28/DAW_2 — material de JavaScript, Node/Express, bases de datos y Docker.
- BertoMP/temario-daw — temario general de ambos cursos.
- jamj2000/DAW2-DAW-Apuntes — Despliegue.
- rosepac/daw-temario y statickidz/TemarioDAW — consulta teórica; verificar condiciones de uso.
- ApuntesDAM.com — ejercicios y simulacros; respetar condiciones del sitio.
- fp-informatica/material-formativo — índice para descubrir fuentes externas.
- Los repositorios sin licencia explícita se consideran solo consulta, sin redistribución. MIT/Apache/CC indicadas por un README se deben verificar a nivel de archivo y contenido antes de reutilizar.

## Integración con PLD

Mantener HTML, CSS y JavaScript ES Modules, la navegación/hash existente, FastAPI y los almacenes actuales. Reutilizar currículo DAW, planificador, progreso, SRS, cuenta y componentes de quiz siempre que encaje. No migrar a React ni duplicar sistemas de progreso.

### Entregas por fases

1. **MVP frontend**: nueva ruta `#/daw/exam-coach`; panel de módulos y temas, biblioteca de fuentes, objetivos, lista de errores y plan de hoy; persistencia local con esquema versionado.
2. **Importador**: carga local de PDF/TXT/MD/ZIP, extracción de texto en cliente o backend local; límites de tamaño y validación de ZIP; metadatos y eliminación de documentos.
3. **Tutor grounded**: interfaz desacoplada de proveedor; modo local con Ollama/NEXARO cuando esté disponible; búsqueda textual primero, RAG después. Citas obligatorias a documentos consultados.
4. **Práctica y simulacros**: banco propio de preguntas, generador asistido por tutor, feedback, temporizador y resultados.
5. **Sincronización opcional**: integrar con cuenta PLD existente solo tras definir esquema y migración, sin alterar datos actuales.
6. **Pruebas**: unitarias para importación, almacenamiento, scoring y SRS; Playwright para navegación, persistencia, accesibilidad y flujo de simulacro.

## Criterios de aceptación

- El acceso a DAW Exam Coach no rompe las rutas actuales de DAW, currículo, aprendizaje ni cursos.
- El alumno puede crear/importar una fuente, etiquetarla, buscarla y borrarla.
- Cada módulo tiene temas y progreso editable; las métricas se derivan de actividad real, no se inventan.
- Un repaso completado se registra y el algoritmo programa la próxima fecha.
- El plan de estudio muestra una razón concreta para cada tarea.
- Tutoría basada en documentos muestra fuente; si no puede citar, lo declara.
- No se envía contenido privado a un servicio remoto por defecto.
- Se conserva la preferencia de lunes a viernes y el objetivo de aprobar 2.º DAW.

## Próximo paso de implementación

Implementar fase 1 en una rama aislada, inspeccionando los patrones actuales de navegación, estilos, store y pruebas. Antes de integrar, ejecutar las pruebas documentadas en `docs/TESTING.md` y revisar el diff. No mergear a `main` ni publicar sin autorización del propietario.
