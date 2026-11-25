# Programming Path — 0 to Expert

## Objetivo

Añadir a PLD un itinerario profesional de programación desde fundamentos hasta ingeniería de software avanzada. Se integra en la sección Career/Roadmap existente y comparte el progreso, las competencias, evaluaciones, proyectos, evidencias y sincronización del documento `career`.

No sustituye los cursos DAW, Python, JavaScript, Java, SQL ni el itinerario AI Engineer. Los enlaza y los organiza en un camino progresivo.

## Nombre y ruta

- ID: `programming-path`
- Nombre ES: `Programming Path — De 0 a Experto`
- Nombre EN: `Programming Path — Zero to Expert`
- Ruta UI prevista: `#/carrera/programming-path` o selección del roadmap en `#/carrera` (decidir tras inspeccionar la UI actual).

## Currículo

| Etapa | Módulos | Objetivo |
|---|---|---|
| 0 | Fundamentos de informática y pensamiento computacional | Comprender hardware/software, terminal, lógica, algoritmos y pseudocódigo |
| 1 | Python desde cero | Sintaxis, control, estructuras, funciones, errores, archivos y OOP |
| 2 | Herramientas de desarrollo | Git, GitHub, terminal, entornos, depuración y documentación |
| 3 | Algoritmos y estructuras de datos | Complejidad, listas, stacks, queues, árboles, grafos, búsqueda y ordenación |
| 4 | HTML y CSS | HTML semántico, accesibilidad, CSS, responsive, Flexbox y Grid |
| 5 | JavaScript | DOM, eventos, módulos, async, Fetch y APIs del navegador |
| 6 | TypeScript | Tipos, interfaces, generics, narrowing y tooling |
| 7 | Bases de datos | SQL, modelado, normalización, PostgreSQL, índices, transacciones y NoSQL |
| 8 | Backend Python | HTTP, FastAPI, REST, Pydantic, autenticación, autorización y testing |
| 9 | Frontend moderno | React, componentes, estado, routing, formularios y gestión de datos |
| 10 | Full Stack | Integrar frontend, backend, base de datos, auth y despliegue; proyecto completo |
| 11 | Java y backend empresarial | Java, collections, OOP, streams, concurrencia, Spring Boot, JPA y testing |
| 12 | Ingeniería de software | SOLID, patrones, refactoring, Clean/Hexagonal Architecture y code review |
| 13 | DevOps y Cloud | Linux, Docker, CI/CD, cloud, observabilidad, infraestructura como código y Kubernetes |
| 14 | Sistemas y redes | OS, procesos, memoria, concurrencia, TCP/IP, sockets y sistemas distribuidos |
| 15 | AI Engineering | Data, ML, DL, LLM, embeddings, RAG, evaluación, agentes y aplicaciones IA |
| 16 | Secure Software Development | OWASP, secure coding, threat modeling, SAST/DAST/SCA y DevSecOps |
| 17 | Especialización | Tracks opcionales: Full Stack, AI, Cloud/DevOps, AppSec, Systems, Mobile o Game Dev |
| 18 | Nivel experto | System design, escala, rendimiento, fiabilidad, liderazgo técnico y decisiones de arquitectura |

## Progresión de niveles

- Novice: módulos 0–1.
- Beginner: módulos 2–3.
- Junior Developer: módulos 4–8.
- Intermediate: módulos 9–10.
- Advanced: módulos 11–14.
- Specialist: módulos 15–17.
- Expert: módulo 18 y evidencias de proyectos avanzados.

Los niveles no deben desbloquearse por marcar unidades como completadas. Requieren evidencias de práctica, evaluaciones aprobadas y, cuando corresponda, criterios de proyecto. Se reutilizan las reglas existentes de competencias y dominio; no se inventa una segunda puntuación opaca.

## Proyectos progresivos

1. CLI Utility Pack: calculadora, conversores y herramientas con validación.
2. Task Manager CLI: funciones, archivos, errores, tests y Git.
3. Algorithm Visualizer: algoritmos y estructuras de datos.
4. Responsive Portfolio: HTML, CSS, JS y accesibilidad.
5. Database Management App: SQL, modelo relacional y CRUD.
6. REST API: FastAPI, PostgreSQL, JWT, roles y tests.
7. Frontend Dashboard: React + TypeScript conectado a API.
8. Full Stack SaaS: autenticación, CRUD, tests, Docker y CI/CD.
9. Enterprise API: Java + Spring Boot + JPA.
10. Cloud Deployment: observabilidad, backups, seguridad y despliegue.
11. AI Application: RAG con evaluación y seguridad.
12. Capstone: sistema de producción diseñado, desplegado y documentado.

Cada proyecto tendrá objetivos, requisitos, criterios de aceptación, evidencias (repo/PR/tests/demo/deploy/docs) y rúbrica.

## Formato de cada unidad

Cada unidad debe incluir:
- objetivos medibles;
- explicación y ejemplos;
- contenido enlazado de PLD cuando exista;
- ejercicios guiados;
- ejercicios independientes;
- quiz con explicación;
- reto práctico;
- proyecto o evidencia cuando aplique;
- errores frecuentes;
- fuentes gratuitas y verificadas;
- criterios de evaluación;
- estimación de tiempo y prerequisitos.

Las unidades que todavía no tengan contenido propio se marcarán explícitamente como pendientes y enlazarán a cursos o recursos existentes. No se presentarán como lecciones completas.

## Integración técnica (respetar arquitectura PLD)

- Catálogo estático y bilingüe ES/EN, sin servicios de pago ni dependencia de APIs públicas.
- Fuente de catálogo en `scripts/career/`; generación mediante `scripts/career/build_career.py`. No editar a mano JSON generado.
- IDs registrados en `scripts/career/ids.lock.json`, que solo crece.
- Añadir el roadmap al catálogo/index y hacer que el generador lo valide.
- Reutilizar el documento `career`, `career-store.js`, `career-data.js`, sync gate, doc sync y uploader. Sin tabla ni migración nueva.
- Reutilizar motor de mastery, SRS, ejercicios, evaluaciones, cursos y evidencias. Completar enlaces a fuentes existentes conforme el contenido se vaya creando.
- Frontend: HTML/CSS/ES Modules; no framework nuevo, no bundler.
- PWA/offline: incluir los nuevos JSON y módulos en el precache generado.
- Mantener tutor estático disponible offline; integración IA/Ollama opcional y local.
- El currículo debe funcionar sin iniciar sesión; la sincronización de progreso solo añade la cuenta cuando existe sesión.
- No romper el roadmap AI Engineer, DAW ni los cursos actuales.

## Fases de implementación

### P0 — Diseño y currículo base
- Aprobar este alcance.
- Definir IDs, niveles, prerrequisitos, skills, fuentes, etapas y proyectos.
- Auditoría de reutilización de cursos/conceptos existentes.

### P1 — Catálogo y selector de itinerarios
- Crear fuente de datos del roadmap.
- Regenerar JSON.
- Añadir el roadmap al catálogo.
- Selector de itinerario y navegación sin cambiar el comportamiento por defecto actual.
- Pruebas del generador y del catálogo.

### P2 — Unidades y contenido
- Completar módulos 0–3 (fundamentos, Python, Git, algoritmos) con contenido y bancos de ejercicios.
- Enlazar los cursos DAW existentes donde corresponda.
- Exámenes por módulo y evaluación de dominio.

### P3 — Web y bases de datos
- Módulos 4–7 con lecciones, prácticas y proyectos.
- Usar los cursos existentes de JavaScript, Lenguajes de marcas y SQL en lugar de duplicar contenido.

### P4 — Backend, frontend y Full Stack
- Módulos 8–10.
- Integración API, auth, testing y proyecto full-stack.

### P5 — Ingeniería profesional
- Módulos 11–14.
- Java/Spring, arquitectura, DevOps, Cloud, sistemas y redes.

### P6 — IA, seguridad y especializaciones
- Módulos 15–18.
- AI Engineering, secure coding, tracks y capstone.

### P7 — Calidad y publicación
- Tests unitarios, generador `--check`, pruebas de navegación, sincronización, offline/PWA y accesibilidad.
- Revisar `precache.js` generado.
- Verificar CI; no publicar ni fusionar a `main` automáticamente.

## Criterios de aceptación global

- El usuario puede seleccionar Programming Path sin perder su progreso en otros roadmaps.
- Progreso, unidades, evaluaciones, evidencias y study log persisten y se fusionan sin pérdida.
- Los prerrequisitos bloquean de forma orientativa y explicable.
- La finalización no equivale a dominio.
- El currículo y los cursos actuales funcionan offline.
- El roadmap se muestra en español e inglés.
- Los JSON son generados por scripts y CI comprueba que están actualizados.
- No hay dependencias nuevas innecesarias, migraciones ni endpoints adicionales.
- El roadmap no se declara “experto” sin evidencias de proyectos, tests, despliegues y criterios evaluados.
