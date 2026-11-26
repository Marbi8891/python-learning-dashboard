# Catálogo de contenido — PLD Beta 0.1.0

Este inventario separa contenido que ya está en `main` de propuestas todavía en PR. Es una foto del 26/11/2026; los builders y JSON del repositorio siguen siendo la fuente autoritativa.

## Contenido que ya está en main

| Área | Fuente principal | Estado / alcance confirmado |
|---|---|---|
| Python | `frontend/data/learning.json`, `lessons.json` | 31 conceptos, 387 ejercicios, 7 módulos de lecciones (27 lecciones), ruta base de 31 unidades. |
| PCAP | `frontend/data/pcap.json` | 126 preguntas, 48 tarjetas; simulacro configurado de 40 preguntas/65 min, aprobado al 70 %, con 5 bloques temáticos. Simulacros verificados desde backend. |
| DAW oficial | `frontend/data/curriculum/daw-cyl.json`, `scripts/curriculum/` | Currículo oficial del título y Castilla y León, trazabilidad de módulos/RA/CE, scripts de extracción y generación. |
| Programación DAW | `frontend/data/courses/programacion/`, `scripts/courses/programacion_course.py` | Lecciones y banco generado; vinculado a currículo DAW. |
| POO | `scripts/learning/poo_module.py`, `poo_u1.py`…`poo_u10.py` | 10 unidades, ejercicios, evaluaciones, progreso y bibliografía integrados. |
| JavaScript | `frontend/data/courses/js/`, `scripts/courses/js_course.py` | Lecciones y banco de preguntas. |
| Java | `frontend/data/courses/java/`, `scripts/courses/java_course.py` | Lecciones y banco de preguntas. |
| SQL / bases de datos | `frontend/data/courses/sql/`, `scripts/courses/sql_course.py` | Lecciones y banco de preguntas. |
| Entornos | `frontend/data/courses/entornos/`, `scripts/courses/entornos_course.py` | Lecciones y banco de preguntas. |
| Lenguajes de marcas | `frontend/data/courses/marcas/`, `scripts/courses/marcas_course.py` | Lecciones y banco de preguntas. |
| Excel profesional | `frontend/data/academia/excel/`, `scripts/courses/excel_course.py` | Motor de fórmulas y academia con módulos M01–M05; banco y lecciones generados. |
| Ciberseguridad | `frontend/data/cybersecurity/course.json`, `frontend/js/cybersecurity*` | Curso de 16 semanas, 3 tracks y evaluación por cuestionarios, laboratorios, scripts, reporting y proyecto final. |
| Career / AI Engineer | `frontend/data/career/applied-ai-engineer.json` | 6 etapas, 8 módulos, 32 competencias, 4 proyectos y 9 roles. |
| Recursos | `frontend/data/resources.json`, `scripts/resources/build_resources.py` | 24 recursos catalogados, con metadatos de calidad, idioma, acceso, URL, licencias y correspondencia con contenidos. |
| Adaptativo | `frontend/js/learn/`, `scripts/learning/` | Dominio, confianza, retención, repaso espaciado, recomendación y planificador. |
| Gamificación | `frontend/js/game.js` y documento de progreso | XP, niveles, logros, racha y actividad. |
| Cuenta/progreso | backend state documents y stores frontend | Local y sincronizado, versionado/conflictos, cuenta y progreso compartido por curso. |
| Tutor/NEXARO | PR #190 fusionada; backend `ai`/NEXARO | Integración opcional en servidor. La conexión a una instancia real requiere validación de configuración y disponibilidad. |

## Contenido y funcionalidades propuestas en PR (no contar como integradas)

| PR | Contenido | Qué falta antes de Beta |
|---|---|---|
| #207 Programming Path | Ruta curricular 0→experto, mapa de reutilización y 28 prácticas con evidencias. | CI verde, confirmar builder/IDs y conectar prácticas al progreso común sin duplicar cursos. |
| #201 Roadmaps | Rutas iniciales Python, PCAP, DAW y Web. | Integración del progreso local con el estado compartido; verificar enlaces a lecciones. |
| #199 AI Academy | Catálogo de 20 cursos/5 itinerarios según especificación; 8 lecciones iniciales authored en AI Fundamentals; otros cursos están en outline. | Corregir routing, E2E/WebKit y completar el contenido antes de anunciar catálogo completo. |
| #146 DevOps Academy | MVP de academia DevOps. | CI, revisión curricular, progresión compartida y validación de enlaces. |
| #175 Demo Edition | Modo demo con alumno sintético, hub de cursos y laboratorio Python con 14 ejercicios. | CI actualizado, revisión de aislamiento demo, reconciliar catálogo/hub con rutas actuales. |
| #195 DAW Exam Coach | Exámenes, mastery, flashcards, fuentes, prompt tutor, errores y sesiones. | Consolidar con preparación DAW y progreso existente; validar UX, imports/exports y tests. |
| #196 DAW Coach Mobile | Coach móvil y Second Brain/knowledge library. | Evitar app paralela; compartir currículo, mastery, SRS y progreso con DAW Coach principal. |
| #209 PLD ACADEMY | Workspace institucional de demo con grupos, actividades, analítica y roles simulados. | CI verde y backend multi-tenant, permisos, autenticación, persistencia, privacidad y auditoría antes de piloto real. |

## Recursos/repositorios externos

PLD debe mantener enlaces curados y metadata; no copiar repositorios ni materiales completos sin comprobar licencia y términos. La catalogación debe usar el builder de recursos y IDs estables.

Fuentes ya presentes en el catálogo: MDN (HTML/CSS/JavaScript), Python oficial, XML/XPath/XSLT specs, W3C validator, Pro Git, Docker docs, Odoo docs, currículo BOE/orden autonómica, apuntes FP y repositorios/proyectos de DAW.

Fuentes a añadir o verificar para la Beta (no están todas confirmadas en el catálogo actual): CS50/CS50P, MIT Missing Semester, Exercism, freeCodeCamp, The Odin Project, PortSwigger Web Security Academy, OWASP, Nmap, Wireshark, Metasploit, Kali, FastAPI/Django, PostgreSQL, TypeScript/React/Node, scikit-learn/PyTorch/TensorFlow/Hugging Face, Jupyter/Kaggle y documentación oficial cloud. Antes de registrar cada una, verificar URL, disponibilidad, idioma, licencia/reutilización y vincular a módulos concretos.

## Reglas para consolidar

1. Una lección o banco se mantiene en su fuente actual; Academy, Path y Roadmap apuntan a ella.
2. El progreso se guarda en el Learning Engine/store existente por cuenta y local, no en cada academia.
3. Los proyectos y prácticas tienen IDs estables, entregables y rúbricas; su evidencia puede enlazarse desde Career/portfolio.
4. Los cursos outline no se presentan como cursos completos.
5. Los recursos externos son enlaces, no copias, salvo contenido original o licencia verificada.
6. La beta solo anuncia funciones que pasan CI y validación manual de rutas, responsive, accesibilidad y PWA.
