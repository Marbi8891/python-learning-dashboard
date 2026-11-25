# Programming Path — 0 to Expert

## Objetivo

Añadir a PLD un itinerario profesional de programación desde fundamentos hasta ingeniería de software avanzada. Se integra en la sección Career/Roadmap existente y comparte el progreso, las competencias, evaluaciones, proyectos, evidencias y sincronización del documento `career`.

No sustituye los cursos DAW, Python, JavaScript, Java, SQL ni el itinerario AI Engineer. Los enlaza y los organiza en un camino progresivo.

## Implementation progress (2026-11-25)

- Added `docs/PROGRAMMING_PATH_MAPPING.md`: curriculum map with explicit reuse of existing DAW lessons, Career roadmap units, and gap-only content.
- Added a draft data source `scripts/career/programming_path.py` with a 17-module sequence, linked objectives and resource/block/concept references. It is intentionally **not registered in the Career generator or runtime index yet** because this environment cannot execute the repository generator locally. Activation requires generating the static catalog, validating IDs and references, and running CI. This prevents an ungenerated catalog from breaking the existing Career pipeline.
- Expanded the resource catalog source and output with 24 programming resources. Resource references are mapped to existing PLD lesson IDs where applicable.
- The resource catalog source and generated JSON were compared structurally: 48 resources, 48 matching IDs, no duplicate IDs, and zero source/output field differences. 129 curriculum references in the draft were checked against existing concepts, blocks and resources; none are invalid.
- The resource generator now recognizes the `curso` resource type.

## Política y catálogo de fuentes fiables

Programming Path debe utilizar una jerarquía de fuentes y registrar enlaces por tema. No se debe generar lecciones basadas únicamente en blogs, respuestas de foros, vídeos sin documentación o contenido SEO.

### Jerarquía de confianza

1. **Nivel A — Fuente primaria:** documentación oficial del lenguaje, estándar, framework, herramienta, organismo de estándares o universidad que imparte el curso.
2. **Nivel B — Curso universitario abierto / libro abierto revisado:** universidades, OpenCourseWare y libros educativos de autores reconocidos con edición y ejercicios.
3. **Nivel C — Plataformas educativas estructuradas:** currículos con ejercicios y proyectos; sirven para práctica y explicación, contrastando afirmaciones técnicas con Nivel A.
4. **Nivel D — Comunidad / artículos:** Stack Overflow, blogs, Reddit, YouTube y tutoriales independientes. Útiles para troubleshooting, ejemplos o perspectivas, pero no como fuente única de teoría ni para recomendaciones críticas.

Para cada recurso se debe registrar: título, URL directa, organización/autor, tipo, idioma, módulos relacionados, nivel, fecha de última revisión, estado (verified/needs-review), licencia si se reutiliza contenido, y notas. Verificar enlaces y actualidad antes de incorporarlos. No copiar contenido protegido; PLD debe enlazar, resumir con sus propias palabras y respetar licencias.

### Catálogo inicial recomendado

| Área | Fuente principal (Nivel A/B) | Complemento de práctica |
|---|---|---|
| Computer Science general | Harvard CS50x — https://cs50.harvard.edu/x/ | Problem sets y proyecto final CS50 |
| Python fundamentos | Python docs/tutorial — https://docs.python.org/3/tutorial/ ; Harvard CS50P — https://cs50.harvard.edu/python/ | Exercism Python — https://exercism.org/tracks/python |
| Python práctico | Think Python (libro abierto) — https://allendowney.github.io/thinkpython/ | Automate the Boring Stuff — https://automatetheboringstuff.com/ |
| Terminal/Git tooling | MIT Missing Semester — https://missing.csail.mit.edu/ ; Git docs — https://git-scm.com/doc | Learn Git Branching — https://learngitbranching.js.org/ |
| Algorithms/CS | MIT OCW — https://ocw.mit.edu/ ; CS50 — https://cs50.harvard.edu/x/ | VisuAlgo — https://visualgo.net/ ; LeetCode solo para práctica |
| Web fundamentals | MDN Learn — https://developer.mozilla.org/en-US/docs/Learn_web_development | freeCodeCamp — https://www.freecodecamp.org/ ; The Odin Project — https://www.theodinproject.com/ |
| HTML/CSS | WHATWG HTML — https://html.spec.whatwg.org/ ; MDN HTML/CSS | web.dev — https://web.dev/learn/ |
| JavaScript | MDN JS Guide — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide ; ECMAScript spec — https://tc39.es/ecma262/ | javascript.info — https://javascript.info/ ; Exercism |
| TypeScript | TypeScript Handbook — https://www.typescriptlang.org/docs/ | Total TypeScript / Type Challenges (practice; verify current availability) |
| React | React docs — https://react.dev/learn | Full Stack Open — https://fullstackopen.com/en/ |
| Next.js | Next.js official Learn — https://nextjs.org/learn | Official docs — https://nextjs.org/docs |
| SQL | PostgreSQL docs — https://www.postgresql.org/docs/ ; SQL standard material where accessible | SQLBolt — https://sqlbolt.com/ ; PGExercises — https://pgexercises.com/ |
| Database concepts | CMU Database Systems — https://15445.courses.cs.cmu.edu/ | PostgreSQL exercises |
| Backend/API | FastAPI docs — https://fastapi.tiangolo.com/tutorial/ ; HTTP/REST primary references | Microsoft Learn web app material / project exercises |
| Java | Dev.java — https://dev.java/learn/ ; Java API docs — https://docs.oracle.com/en/java/ | University of Helsinki Java MOOC — https://java-programming.mooc.fi/ |
| Spring | Spring official guides — https://spring.io/guides | Spring tutorials and project labs |
| Software engineering | MIT OCW, university courses; Google Engineering Practices — https://google.github.io/eng-practices/ | Refactoring exercises and code reviews |
| Testing | pytest docs — https://docs.pytest.org/ ; Playwright — https://playwright.dev/docs/ ; Vitest — https://vitest.dev/ | PLD projects and labs |
| Linux | Linux man-pages — https://man7.org/linux/man-pages/ ; Ubuntu docs — https://ubuntu.com/tutorials | The Linux Command Line (free book) — https://linuxcommand.org/tlcl.php |
| Docker | Docker docs — https://docs.docker.com/ | Official getting-started labs |
| Cloud | Official provider training/documentation (AWS, Azure, Google Cloud) selected per track | Cloud Skills platforms; only official labs as primary |
| Kubernetes | Kubernetes docs — https://kubernetes.io/docs/tutorials/ | Kubernetes interactive tutorials |
| Systems/networking | RFC Editor — https://www.rfc-editor.org/ ; Linux man-pages | CS50, MIT OCW and labs |
| AI/ML | scikit-learn docs — https://scikit-learn.org/stable/ ; PyTorch tutorials — https://pytorch.org/tutorials/ ; Hugging Face course — https://huggingface.co/learn | University courses and reproducible notebooks |
| LLM/GenAI | Official provider API docs; Hugging Face docs; research papers from arXiv (label as preprints) | RAG/agent labs with evaluation and safety criteria |
| Secure coding | OWASP Top 10 — https://owasp.org/www-project-top-ten/ ; Cheat Sheet Series — https://cheatsheetseries.owasp.org/ | PortSwigger Web Security Academy — https://portswigger.net/web-security ; secure coding labs |
| Architecture/System Design | University course material, vendor architecture docs, original papers where relevant | System Design Primer — https://github.com/donnemartin/system-design-primer (community, Level C/D) |
| Programming tracks | roadmap.sh — https://roadmap.sh/ (roadmap inspiration only; not a technical authority) | Project-based path plus official docs |

### Fuentes incorporadas al catálogo PLD

Se añadieron al catálogo existente de `frontend/data/resources.json` estos recursos, usando IDs estables y enlazando a los cursos originales:

| ID | Fuente | Uso en Programming Path |
|---|---|---|
| `res-harvard-cs50x` | Harvard CS50x | Fundamentos, pensamiento computacional, algoritmos y conceptos de informática. |
| `res-harvard-cs50p` | Harvard CS50P | Complemento de práctica Python, testing, debugging, funciones, OOP y archivos. |
| `res-harvard-cs50sql` | Harvard CS50 SQL | Práctica complementaria de bases de datos; no reemplaza ni duplica el curso SQL de PLD. |
| `res-harvard-cs50web` | Harvard CS50 Web | Práctica de desarrollo web/full-stack; enlaza temas existentes y no duplica sus lecciones. |
| `res-mit-missing-semester` | MIT Missing Semester | Shell, herramientas, debugging, Git, empaquetado y flujo de trabajo de desarrollo. |

Los enlaces a estos recursos se revisaron el 25-11-2026. Harvard CS50 publica cursos abiertos con ejercicios y proyectos; MIT Missing Semester ofrece clases y ejercicios sobre herramientas de desarrollo. Se mantiene la regla de enlazar al original y no copiar sus materiales.

### Reglas de selección de recursos por unidad

- Preferir un recurso oficial o universitario primario y, como máximo, uno o dos complementos de práctica que aporten valor real.
- No añadir enlaces por volumen. La unidad debe tener una fuente que enseñe y una actividad que permita demostrar la competencia.
- Comprobar que el enlace existe, que el contenido está actualizado y que el nivel corresponde al estudiante.
- Cuando existan versiones, fijar la versión relevante (p. ej., Python, Java, framework) y revisar cambios.
- Para contenido de seguridad, IA, cloud o APIs que cambia rápidamente, registrar fecha de verificación y hacer revisión periódica.
- Distinguir documentación de referencia, tutorial, curso, práctica, estándar y fuente de investigación.
- No considerar roadmap.sh, blogs ni rankings como autoridades técnicas; pueden orientar la secuencia, pero los conceptos se contrastan con documentación oficial.
- No usar Stack Overflow/Reddit como fundamento único de una lección. Las respuestas se contrastan con documentación, especificaciones o reproducibilidad.
- Las fuentes no sustituyen el contenido existente de PLD: se enlazan desde la ficha curricular y se evita duplicar lecciones.

### Auditoría de recursos existentes antes de añadir

La implementación debe cruzar el catálogo anterior con `frontend/data/resources.json`, cursos y unidades, y Career roadmaps. Si el mismo recurso ya está catalogado, reutilizar su ID y metadata. Si un recurso no se encuentra, proponerlo en una lista de gaps para revisión, no crear duplicados automáticamente.


## Regla de no duplicación (obligatoria)

**Programming Path es una capa de navegación, secuenciación y requisitos de dominio; no es un segundo repositorio de lecciones.** Antes de crear cualquier unidad, ejercicio, evaluación, recurso o proyecto, buscar su equivalente en PLD y reutilizarlo.

- Si ya existe: enlazar por ID estable y consumir su progreso/evidencia. No copiar el título, teoría, ejercicios, quiz, soluciones ni proyecto a otro archivo.
- Si existe parcialmente: enlazar lo disponible y registrar únicamente el gap concreto como pendiente.
- Si no existe: proponer contenido nuevo solo después de documentar la búsqueda y confirmar que no es equivalente a otra unidad.
- No crear copias de conceptos de `learning.json`, lecciones de cursos, bancos de ejercicios, proyectos de Career ni currículum DAW.
- No mantener progreso duplicado: el estado del recurso original es la fuente de verdad. Career guarda solo la referencia y los requisitos propios del roadmap.
- Si se comparte un proyecto entre itinerarios, usar un único proyecto y una única colección de evidencias; los roadmaps pueden exigir distintos criterios de ese proyecto.

## Auditoría de contenido existente (inventario inicial)

Confirmado en el repositorio:

| Fuente existente | Contenido a reutilizar |
|---|---|
| `frontend/data/learning.json` | conceptos de fundamentos, lógica, variables, tipos, operadores, entrada/salida, condicionales, bucles, trazado, validación, funciones, depuración, strings, colecciones, excepciones, módulos, archivos y POO |
| `frontend/data/courses/programacion/lessons.json` + `bank.json` | Programación DAW UT1–UT9: introducción/algoritmos, sintaxis, control, funciones, colecciones, POO y contenidos existentes del curso |
| `frontend/data/courses/js/lessons.json` + `bank.json` | JavaScript existente |
| `frontend/data/courses/marcas/lessons.json` + `bank.json` | HTML, XML, CSS y Lenguajes de marcas existente |
| `frontend/data/courses/sql/lessons.json` + `bank.json` | SQL y bases de datos existente |
| `frontend/data/courses/java/lessons.json` + `bank.json` | Java existente |
| `frontend/data/courses/entornos/lessons.json` + `bank.json` | Entornos, tooling y contenidos relacionados existentes |
| `frontend/data/curriculum/daw-cyl.json` | módulos DAW, resultados de aprendizaje y criterios de evaluación |
| `frontend/data/resources.json` | recursos externos ya catalogados |
| Career roadmap `applied-ai-engineer` | unidades, competencias, proyectos y evidencias del itinerario AI Engineer; compartir referencias cuando coincidan |
| `frontend/data/pcap.json`, `lessons.json` y bancos asociados | contenido de PCAP si alguna etapa requiere fundamentos de redes o Python y la unidad existente aplica |

Este inventario es un primer mapa, no una afirmación de que todo el contenido esté completo. La implementación debe inspeccionar los IDs y contenidos exactos, no deducir cobertura solo por nombre.

## Nombre y ruta

- ID: `programming-path`
- Nombre ES: `Programming Path — De 0 a Experto`
- Nombre EN: `Programming Path — Zero to Expert`
- Ruta UI prevista: `#/carrera/programming-path` o selección del roadmap en `#/carrera` (decidir tras inspeccionar la UI actual).

## Currículo / mapa de competencias

El roadmap organiza y enlaza los contenidos existentes según esta secuencia. Las unidades deben tener `links` con IDs de fuente existente (concept, block, resource u otro tipo de referencia que se valide); no se replicará el contenido fuente.

| Etapa | Área | Qué debe cubrir el path | Fuente preferente / reutilización |
|---|---|---|---|
| 0 | Fundamentos y pensamiento computacional | hardware/software, terminal, lógica, algoritmos, pseudocódigo, resolución de problemas | conceptos `learning.json`, Programación UT1 y Entornos |
| 1 | Python desde cero | sintaxis, control, estructuras, funciones, errores, archivos y OOP | conceptos y curso Programación; añadir contenido solo para gaps verificados |
| 2 | Herramientas | Git/GitHub, terminal, entornos, depuración, documentación | Entornos y recursos existentes; gaps pendientes |
| 3 | Algoritmos y estructuras de datos | complejidad, stacks, queues, árboles, grafos, búsqueda, ordenación | conceptos, Programación UT1 y ejercicios existentes; estructuras avanzadas pendientes si no existen |
| 4 | HTML y CSS | HTML semántico, accesibilidad, CSS, responsive, Flexbox y Grid | Lenguajes de marcas; solo gaps de CSS/layout se crean nuevos |
| 5 | JavaScript | DOM, eventos, módulos, async, Fetch y APIs navegador | curso JavaScript existente |
| 6 | TypeScript | tipos, interfaces, generics, narrowing y tooling | gap nuevo solo si no hay curso/contenido |
| 7 | Bases de datos | SQL, modelado, normalización, PostgreSQL, índices, transacciones y NoSQL | curso SQL y curriculum DAW; PostgreSQL/NoSQL avanzados solo gaps |
| 8 | Backend Python | HTTP, FastAPI, REST, Pydantic, auth, authorization y testing | Career AI Engineer, proyectos PLD y recursos; reutilizar unidades coincidentes |
| 9 | Frontend moderno | React, componentes, estado, routing, formularios y gestión de datos | gap nuevo; no duplicar fundamentos JS |
| 10 | Full Stack | integrar frontend, backend, BD, auth y despliegue | proyectos existentes o un único proyecto compartido con criterios por roadmap |
| 11 | Java y backend empresarial | Java, collections, streams, concurrencia, Spring Boot, JPA y testing | curso Java; Spring solo gaps no cubiertos |
| 12 | Ingeniería de software | SOLID, patrones, refactoring, Clean/Hexagonal Architecture y code review | Career AI Engineer, curso Entornos y recursos; gaps concretos |
| 13 | DevOps y Cloud | Linux, Docker, CI/CD, cloud, observabilidad, IaC y Kubernetes | Entornos, recursos y proyectos; no duplicar NEXARO/AI roadmap evidencias |
| 14 | Sistemas y redes | OS, procesos, memoria, concurrencia, TCP/IP, sockets y distributed systems | PCAP, Entornos y recursos; gaps avanzados |
| 15 | AI Engineering | Data, ML, DL, LLM, embeddings, RAG, evaluación, agentes y apps IA | enlazar roadmap `applied-ai-engineer`; no replicarlo |
| 16 | Secure Software Development | OWASP, secure coding, threat modeling, SAST/DAST/SCA y DevSecOps | cursos/recursos de ciberseguridad y evidencias de proyectos existentes |
| 17 | Especialización | Full Stack, AI, Cloud/DevOps, AppSec, Systems, Mobile o Game Dev | tracks opcionales; enlazar los roadmaps existentes y crear solo los faltantes |
| 18 | Nivel experto | System design, escala, rendimiento, fiabilidad, liderazgo técnico y arquitectura | recursos, proyectos y evidencias de producción; no se completa solo con lecciones |

## Progresión de niveles

- Novice: módulos 0–1.
- Beginner: módulos 2–3.
- Junior Developer: módulos 4–8.
- Intermediate: módulos 9–10.
- Advanced: módulos 11–14.
- Specialist: módulos 15–17.
- Expert: módulo 18 y evidencias de proyectos avanzados.

Los niveles no deben desbloquearse por marcar unidades como completadas. Requieren evidencias de práctica, evaluaciones aprobadas y, cuando corresponda, criterios de proyecto. Se reutilizan las reglas existentes de competencias y dominio; no se inventa una segunda puntuación opaca.

## Proyectos: reutilización y gaps

No crear automáticamente los 12 proyectos de la propuesta inicial. Primero hacer un inventario de proyectos de PLD, Career, DAW y repositorios vinculados.

- Reutilizar proyectos existentes cuando cumplan objetivos.
- Añadir criterios específicos del Programming Path al proyecto compartido, sin duplicarlo.
- Crear proyecto nuevo únicamente si el gap no puede cubrirse ampliando de forma razonable un proyecto existente.
- Las evidencias de repo/PR/tests/demo/deploy/docs se guardan una sola vez y se referencian desde los roadmaps.

## Formato de unidad

Cada unidad es una ficha de roadmap que contiene:
- objetivos medibles;
- IDs de contenido que reutiliza;
- prerequisitos;
- competencias;
- criterios de dominio/evaluación;
- gaps pendientes, si los hay;
- proyecto/evidencia referenciada cuando aplique;
- estimación de tiempo.

No incluir teoría duplicada, soluciones copiadas, quizzes repetidos ni nuevos bancos dentro del roadmap. Las unidades fuente conservan sus contenidos y sus mecanismos de progreso.

## Integración técnica (respetar arquitectura PLD)

- Catálogo estático y bilingüe ES/EN, sin servicios de pago ni dependencia de APIs públicas.
- Fuente de catálogo en `scripts/career/`; generación mediante `scripts/career/build_career.py`. No editar a mano JSON generado.
- IDs registrados en `scripts/career/ids.lock.json`, que solo crece.
- Añadir el roadmap al catálogo/index y hacer que el generador lo valide.
- Reutilizar el documento `career`, `career-store.js`, `career-data.js`, sync gate, doc sync y uploader. Sin tabla ni migración nueva.
- Reutilizar motor de mastery, SRS, ejercicios, evaluaciones, cursos y evidencias. Los recursos originales son fuente de verdad para su progreso.
- Añadir validación de referencias y **detección de duplicados**: enlaces a IDs existentes son preferentes; una unidad nueva debe declarar qué gap cubre.
- Frontend: HTML/CSS/ES Modules; no framework nuevo, no bundler.
- PWA/offline: incluir los nuevos JSON y módulos en el precache generado.
- Mantener tutor estático disponible offline; integración IA/Ollama opcional y local.
- El currículo debe funcionar sin iniciar sesión; la sincronización de progreso solo añade la cuenta cuando existe sesión.
- No romper el roadmap AI Engineer, DAW ni los cursos actuales.

## Fases de implementación

### P0 — Auditoría de reutilización
- Auditar contenidos y proyectos existentes con IDs y cobertura por etapa.
- Crear mapa de referencias (source ID → etapa/unidad).
- Identificar gaps reales, no crear contenidos en esta fase.
- Confirmar que el path es una capa de navegación y evaluación, sin duplicación.

### P1 — Catálogo y selector de itinerarios
- Crear fuente de datos del roadmap con enlaces a contenidos existentes.
- Regenerar JSON.
- Añadir el roadmap al catálogo.
- Selector de itinerario y navegación sin cambiar el comportamiento por defecto actual.
- Pruebas del generador, referencias y catálogo.

### P2 — Enlaces y progreso
- Conectar conceptos, bloques, lecciones, evaluaciones y proyectos existentes.
- Mostrar progreso derivado de las fuentes; evitar un estado duplicado.
- Crear evaluaciones propias solo para gaps y requisitos de nivel que no estén cubiertos.

### P3 — Completar gaps verificados
- Añadir contenido nuevo únicamente para brechas confirmadas (por ejemplo, TypeScript o React si no existe contenido equivalente).
- Usar los cursos existentes de JavaScript, Lenguajes de marcas y SQL en lugar de duplicarlos.
- Cada adición debe tener revisión de duplicación y tests.

### P4 — Backend, frontend y Full Stack
- Mapear y reutilizar contenido/plataformas/proyectos actuales.
- Añadir gaps de framework, API, auth o integración solo cuando estén confirmados.

### P5 — Ingeniería profesional
- Java/Spring, arquitectura, DevOps, Cloud, sistemas y redes: reutilizar Java, Entornos, PCAP, recursos y Career donde coincidan.

### P6 — IA, seguridad y especializaciones
- AI Engineering enlaza al roadmap `applied-ai-engineer`.
- Seguridad enlaza a cursos y recursos actuales.
- Crear tracks nuevos solo para áreas que aún no tengan roadmap.

### P7 — Calidad y publicación
- Tests unitarios, generador `--check`, pruebas de navegación, sincronización, offline/PWA y accesibilidad.
- Revisar `precache.js` generado.
- Verificar CI; no publicar ni fusionar a `main` automáticamente.

## Criterios de aceptación global

- El usuario puede seleccionar Programming Path sin perder su progreso en otros roadmaps.
- El path no duplica lecciones, ejercicios, evaluaciones, proyectos ni progreso.
- Toda unidad enlaza a fuentes existentes o declara un gap concreto pendiente.
- Progreso, evidencias y study log se reutilizan y se fusionan sin pérdida.
- Los prerrequisitos bloquean de forma orientativa y explicable.
- La finalización no equivale a dominio.
- El currículo y los cursos actuales funcionan offline.
- El roadmap se muestra en español e inglés.
- Los JSON son generados por scripts y CI comprueba que están actualizados.
- No hay dependencias nuevas innecesarias, migraciones ni endpoints adicionales.
- El roadmap no se declara “experto” sin evidencias de proyectos, tests, despliegues y criterios evaluados.
