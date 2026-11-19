# ruff: noqa: E501
# (catálogo de datos: los textos van en una sola línea para leerlos y editarlos)
"""Itinerario «AI Engineer & AI Product Developer» (Applied AI Engineering + AI Product Development).

Solo datos: build_career.py los valida y genera frontend/data/career/applied-ai-engineer.json.
Diseño y decisiones: docs/AI_CAREER_PATH_AUDIT.md y docs/DECISIONS.md (DEC-012).

Reglas de este archivo:
- Los ids no se cambian ni se borran (scripts/career/ids.lock.json). Para retirar algo se marca, no se quita.
- Una unidad sin contenido propio todavía lleva `pending: True`; enlaza a lo que ya existe en PLD
  (conceptos de learning.json, bloques de los cursos de DAW o recursos de resources.json) cuando lo hay.
- El itinerario «Python Backend Junior» del Career Roadmap (Sprint 0) queda dentro de M1 y M2 (D2).
- NEXARO Risk Engine no se asocia a ningún repositorio hasta que el autor confirme cuál es (D7).
- Las bandas salariales son objetivos del autor, no datos de mercado.
"""

ID = "applied-ai-engineer"
VERSION = 1

TITLE = {"es": "AI Engineer & AI Product Developer", "en": "AI Engineer & AI Product Developer"}
SPECIALIZATION = {
    "es": "Applied AI Engineering + AI Product Development: construir aplicaciones y sistemas de IA, no investigación ni entrenamiento de modelos desde cero.",
    "en": "Applied AI Engineering + AI Product Development: building AI applications and systems, not research or training models from scratch.",
}

LEVELS = [
    {"id": "fundamentos", "title": {"es": "Fundamentos", "en": "Fundamentals"}},
    {"id": "intermedio", "title": {"es": "Intermedio", "en": "Intermediate"}},
    {"id": "avanzado", "title": {"es": "Avanzado", "en": "Advanced"}},
    {"id": "profesional", "title": {"es": "Profesional", "en": "Professional"}},
]

CATEGORIES = {
    "programming": {"es": "Programación", "en": "Programming"},
    "backend": {"es": "Backend", "en": "Backend"},
    "databases": {"es": "Bases de datos", "en": "Databases"},
    "frontend": {"es": "Frontend", "en": "Frontend"},
    "ai-ml": {"es": "IA y ML", "en": "AI & ML"},
    "llm": {"es": "LLM", "en": "LLM"},
    "agents": {"es": "Agentes", "en": "Agents"},
    "devops": {"es": "Infraestructura", "en": "Infrastructure"},
    "product": {"es": "Producto", "en": "Product"},
    "professional": {"es": "Carrera y negocio", "en": "Career & business"},
}

# Bandas del prompt del autor (18/11/2026): son sus objetivos orientativos, no datos de mercado.
SALARY_SOURCE = {
    "es": "Objetivos orientativos del autor (bruto anual). No son datos de mercado: contrástalos con ofertas reales.",
    "en": "The author's own indicative targets (gross per year). Not market data: check them against real job offers.",
}
SALARY_BANDS = [
    {
        "id": "junior",
        "title": {"es": "Junior / entrada", "en": "Junior / entry"},
        "min": 25000,
        "max": 32000,
    },
    {
        "id": "developer",
        "title": {"es": "Developer", "en": "Developer"},
        "min": 32000,
        "max": 42000,
    },
    {
        "id": "applied",
        "title": {"es": "Applied AI Engineer", "en": "Applied AI Engineer"},
        "min": 42000,
        "max": 55000,
    },
    {
        "id": "senior",
        "title": {"es": "Senior AI Engineer", "en": "Senior AI Engineer"},
        "min": 55000,
        "max": 70000,
    },
    {
        "id": "lead",
        "title": {"es": "Especialista / liderazgo", "en": "Specialist / lead"},
        "min": 70000,
        "max": None,
    },
]
DEFAULT_TARGET = 70000

# Plan orientativo de 36 meses: cada etapa se puede mover y alargar (documento `career`).
STAGES = [
    {
        "id": "s1",
        "months": 6,
        "modules": ["m1", "m2", "m8"],
        "title": {
            "es": "Consolidación de DAW, Python y backend",
            "en": "DAW, Python and backend consolidation",
        },
    },
    {
        "id": "s2",
        "months": 6,
        "modules": ["m3", "m4"],
        "title": {
            "es": "Fundamentos de IA, LLM Engineering y RAG",
            "en": "AI fundamentals, LLM engineering and RAG",
        },
    },
    {
        "id": "s3",
        "months": 6,
        "modules": ["m5", "m6"],
        "title": {
            "es": "Agentes, MCP, infraestructura y despliegues",
            "en": "Agents, MCP, infrastructure and deployments",
        },
    },
    {
        "id": "s4",
        "months": 6,
        "modules": ["m7", "m8"],
        "title": {
            "es": "Experiencia en producción y primeros clientes",
            "en": "Production experience and first clients",
        },
    },
    {
        "id": "s5",
        "months": 6,
        "modules": ["m4", "m5", "m7"],
        "title": {
            "es": "Especialización y crecimiento profesional",
            "en": "Specialization and professional growth",
        },
    },
    {
        "id": "s6",
        "months": 6,
        "modules": ["m8"],
        "title": {
            "es": "Puestos mejor remunerados y expansión de la actividad propia",
            "en": "Better-paid roles and growing your own business",
        },
    },
]

# ---------- Competencias ----------
# sources: concepts (learning.json), blocks ("curso:bloque" de los bancos de DAW), assessments (evaluación de
# módulo), criteria (criterios de proyecto), checklists. Toda competencia necesita una fuente evaluable
# (concepts, blocks o assessments): leer una lección nunca sube una competencia.


def skill(
    id_, category, es, en, *, concepts=(), blocks=(), assessments=(), criteria=(), checklists=()
):
    return {
        "id": id_,
        "category": category,
        "title": {"es": es, "en": en},
        "sources": {
            "concepts": list(concepts),
            "blocks": list(blocks),
            "assessments": list(assessments),
            "criteria": list(criteria),
            "checklists": list(checklists),
        },
    }


SKILLS = [
    skill(
        "py-oop",
        "programming",
        "Programación orientada a objetos en Python",
        "Object-oriented programming in Python",
        concepts=["poo"],
        blocks=["programacion:prog-ut4", "programacion:prog-ut5", "programacion:prog-ut6"],
        assessments=["m1"],
        criteria=["npa-servicio-tests"],
    ),
    skill(
        "py-types-data",
        "programming",
        "Tipado y estructuras de datos",
        "Typing and data structures",
        concepts=["tipos", "listas", "tuplas-conjuntos", "diccionarios"],
        assessments=["m1"],
    ),
    skill(
        "py-errors",
        "programming",
        "Gestión de errores",
        "Error handling",
        concepts=["excepciones", "validacion"],
        assessments=["m1"],
    ),
    skill(
        "py-async",
        "programming",
        "Programación asíncrona con asyncio",
        "Asynchronous programming with asyncio",
        assessments=["m1"],
    ),
    skill(
        "py-architecture",
        "programming",
        "Arquitectura de software y clean code",
        "Software architecture and clean code",
        concepts=["modulos", "funciones"],
        assessments=["m1"],
        criteria=["npa-servicio-tests"],
    ),
    skill(
        "py-testing",
        "programming",
        "Testing con pytest",
        "Testing with pytest",
        concepts=["depuracion"],
        assessments=["m1"],
        criteria=["npa-servicio-tests", "pld-fullstack"],
    ),
    skill(
        "py-data-processing",
        "programming",
        "Procesamiento de datos con Python",
        "Data processing with Python",
        concepts=["archivos", "recorridos"],
        assessments=["m1"],
        criteria=["re-normalizacion"],
    ),
    skill(
        "git-workflow",
        "programming",
        "Git y GitHub profesional",
        "Professional Git and GitHub",
        assessments=["m1"],
        criteria=["pld-fullstack"],
    ),
    skill(
        "api-design",
        "backend",
        "Diseño de APIs REST con FastAPI y Pydantic",
        "REST API design with FastAPI and Pydantic",
        assessments=["m2"],
        criteria=["npa-backend-produccion", "jr-conectores"],
    ),
    skill(
        "api-auth-security",
        "backend",
        "Autenticación, autorización y seguridad de APIs",
        "Authentication, authorization and API security",
        assessments=["m2"],
        criteria=["npa-backend-produccion"],
    ),
    skill(
        "sql",
        "databases",
        "SQL avanzado",
        "Advanced SQL",
        blocks=["sql:bd-ud2", "sql:bd-ud3", "sql:bd-ampliacion"],
        assessments=["m2"],
    ),
    skill(
        "db-postgres-redis",
        "databases",
        "PostgreSQL, Redis y migraciones",
        "PostgreSQL, Redis and migrations",
        blocks=["sql:bd-ampliacion"],
        assessments=["m2"],
        criteria=["npa-backend-produccion"],
    ),
    skill(
        "web-client",
        "frontend",
        "Cliente web que consume APIs",
        "Web client consuming APIs",
        blocks=["js:js-dom", "js:js-asincronia", "marcas:mar-json"],
        criteria=["pld-fullstack"],
    ),
    skill(
        "ml-foundations",
        "ai-ml",
        "Fundamentos de machine learning y deep learning",
        "Machine learning and deep learning foundations",
        assessments=["m3"],
    ),
    skill(
        "transformers-embeddings",
        "ai-ml",
        "Transformers, tokenización y embeddings",
        "Transformers, tokenization and embeddings",
        assessments=["m3"],
    ),
    skill(
        "local-models",
        "ai-ml",
        "Modelos open source en local (Ollama, Hugging Face)",
        "Local open-source models (Ollama, Hugging Face)",
        assessments=["m3"],
        criteria=["npa-comparativa-modelos"],
    ),
    skill(
        "llm-prompting-structured",
        "llm",
        "Prompting, structured outputs y function calling",
        "Prompting, structured outputs and function calling",
        assessments=["m4"],
        criteria=["jr-extraccion"],
    ),
    skill(
        "llm-rag-search",
        "llm",
        "RAG y búsqueda híbrida",
        "RAG and hybrid search",
        assessments=["m4"],
        criteria=["npa-rag-eval"],
    ),
    skill(
        "llm-evaluation",
        "llm",
        "Evaluación de respuestas y control de alucinaciones",
        "Answer evaluation and hallucination control",
        assessments=["m4"],
        criteria=["npa-rag-eval", "npa-comparativa-modelos"],
    ),
    skill(
        "applied-ai-security",
        "llm",
        "IA aplicada a la ciberseguridad",
        "AI applied to cybersecurity",
        assessments=["m4", "m7"],
        criteria=["re-riesgo"],
    ),
    skill(
        "agents-tools",
        "agents",
        "Agentes con herramientas, planificación y memoria",
        "Agents with tools, planning and memory",
        assessments=["m5"],
        criteria=["npa-agente-permisos"],
    ),
    skill(
        "agents-safety-hitl",
        "agents",
        "Permisos, MCP y human-in-the-loop",
        "Permissions, MCP and human-in-the-loop",
        assessments=["m5"],
        criteria=["npa-agente-permisos", "jr-documentos"],
    ),
    skill(
        "agents-observability-eval",
        "agents",
        "Observabilidad y evaluación de agentes",
        "Agent observability and evaluation",
        assessments=["m5"],
    ),
    skill(
        "containers-linux",
        "devops",
        "Docker, Compose y Linux",
        "Docker, Compose and Linux",
        assessments=["m6"],
        criteria=["npa-despliegue"],
    ),
    skill(
        "ci-cd",
        "devops",
        "CI/CD con GitHub Actions",
        "CI/CD with GitHub Actions",
        assessments=["m6"],
        criteria=["pld-fullstack"],
    ),
    skill(
        "cloud-deploy-ops",
        "devops",
        "Despliegue, monitorización y costes",
        "Deployment, monitoring and costs",
        assessments=["m6"],
        criteria=["npa-despliegue"],
    ),
    skill(
        "saas-architecture",
        "product",
        "Arquitectura SaaS y producto de IA",
        "SaaS architecture and AI product",
        assessments=["m7"],
        criteria=["npa-producto"],
    ),
    skill(
        "llm-app-security-privacy",
        "product",
        "Seguridad de aplicaciones LLM y protección de datos",
        "LLM application security and data protection",
        assessments=["m7"],
        criteria=["npa-producto"],
    ),
    skill(
        "product-ux-metrics",
        "product",
        "UX para IA, métricas y validación con usuarios",
        "AI UX, metrics and user validation",
        assessments=["m7"],
        criteria=["pld-a11y", "npa-producto"],
    ),
    skill(
        "portfolio-presence",
        "professional",
        "Portfolio, GitHub, CV y LinkedIn",
        "Portfolio, GitHub, CV and LinkedIn",
        assessments=["m8"],
        checklists=["portfolio"],
    ),
    skill(
        "interviews-english",
        "professional",
        "Entrevistas técnicas e inglés técnico",
        "Technical interviews and technical English",
        assessments=["m8"],
        checklists=["interview"],
    ),
    skill(
        "business-consulting",
        "professional",
        "Freelance, consultoría y modelo de negocio",
        "Freelance, consulting and business model",
        assessments=["m8"],
        checklists=["business"],
    ),
]

# ---------- Proyectos (los repositorios del autor como laboratorios, sin proyectos nuevos) ----------


def criterion(id_, module, es, skills):
    return {"id": id_, "module": module, "title": {"es": es, "en": es}, "skills": list(skills)}


PROJECTS = [
    {
        "id": "nexaro-personal-ai",
        "title": {"es": "NEXARO Personal AI", "en": "NEXARO Personal AI"},
        "repo": None,
        "description": {
            "es": "Asistente de IA local: FastAPI, Ollama, SQLite, RAG, memoria y agentes.",
            "en": "Local AI assistant: FastAPI, Ollama, SQLite, RAG, memory and agents.",
        },
        "criteria": [
            criterion(
                "npa-servicio-tests",
                "m1",
                "Un servicio existente mejorado (tipado, errores, estructura) con tests pytest",
                ["py-oop", "py-architecture", "py-testing"],
            ),
            criterion(
                "npa-backend-produccion",
                "m2",
                "Backend de producción: autenticación, migraciones, límites y tests",
                ["api-design", "api-auth-security", "db-postgres-redis"],
            ),
            criterion(
                "npa-comparativa-modelos",
                "m3",
                "Comparativa medida de varios modelos locales (calidad, latencia, memoria)",
                ["local-models", "llm-evaluation"],
            ),
            criterion(
                "npa-rag-eval",
                "m4",
                "Motor RAG híbrido con conjunto de evaluación y métricas antes/después",
                ["llm-rag-search", "llm-evaluation"],
            ),
            criterion(
                "npa-agente-permisos",
                "m5",
                "Agente con herramientas y permisos controlados, con tests de denegación",
                ["agents-tools", "agents-safety-hitl"],
            ),
            criterion(
                "npa-despliegue",
                "m6",
                "Despliegue reproducible para usuarios reales: compose, logs, copias y monitorización",
                ["containers-linux", "cloud-deploy-ops"],
            ),
            criterion(
                "npa-producto",
                "m7",
                "Diseño de una versión comercial: propuesta de valor, precios, métricas y amenazas LLM",
                ["saas-architecture", "llm-app-security-privacy", "product-ux-metrics"],
            ),
        ],
    },
    {
        "id": "nexaro-risk-engine",
        "title": {"es": "NEXARO Risk Engine", "en": "NEXARO Risk Engine"},
        "repo": None,
        "pendingIdentity": True,
        "description": {
            "es": "Análisis y normalización de resultados de herramientas de ciberseguridad. Repositorio pendiente de confirmar.",
            "en": "Analysis and normalization of cybersecurity tool results. Repository pending confirmation.",
        },
        "criteria": [
            criterion(
                "re-normalizacion",
                "m1",
                "Resultados de varias herramientas normalizados a un esquema común, con tests",
                ["py-data-processing"],
            ),
            criterion(
                "re-riesgo",
                "m4",
                "Priorización de riesgos explicable, con la IA como apoyo y no como única fuente",
                ["applied-ai-security"],
            ),
        ],
    },
    {
        "id": "python-learning-dashboard",
        "title": {"es": "Python Learning Dashboard", "en": "Python Learning Dashboard"},
        "repo": "https://github.com/Marbi8891/python-learning-dashboard",
        "description": {
            "es": "Plataforma educativa full-stack con Python, JavaScript y FastAPI.",
            "en": "Full-stack learning platform with Python, JavaScript and FastAPI.",
        },
        "criteria": [
            criterion(
                "pld-fullstack",
                "m2",
                "Funcionalidad full-stack con tests unitarios, e2e y CI en verde",
                ["web-client", "py-testing", "git-workflow", "ci-cd"],
            ),
            criterion(
                "pld-a11y",
                "m7",
                "Accesibilidad WCAG 2.2 AA verificada en una funcionalidad nueva",
                ["product-ux-metrics"],
            ),
        ],
    },
    {
        "id": "jobradar",
        "title": {"es": "JobRadar", "en": "JobRadar"},
        "repo": None,
        "description": {
            "es": "Búsqueda y análisis de ofertas con generación de CV y cartas mediante IA (local).",
            "en": "Job search and analysis with AI-generated CVs and cover letters (local).",
        },
        "criteria": [
            criterion(
                "jr-conectores",
                "m2",
                "Conectores modulares por fuente, solo con APIs o RSS oficiales",
                ["api-design"],
            ),
            criterion(
                "jr-extraccion",
                "m4",
                "Extracción estructurada de ofertas con salida validada contra un esquema",
                ["llm-prompting-structured"],
            ),
            criterion(
                "jr-documentos",
                "m5",
                "Generación de CV y cartas con revisión humana obligatoria antes de enviar",
                ["agents-safety-hitl"],
            ),
        ],
    },
]

CHECKLISTS = {
    "portfolio": [
        ("pf-github", "Perfil de GitHub con README y repositorios fijados"),
        (
            "pf-readmes",
            "README profesional en cada proyecto: problema, arquitectura, cómo ejecutarlo y tests",
        ),
        ("pf-demo", "Al menos una demo desplegada o un vídeo corto"),
        ("pf-cv", "CV técnico de una página orientado a Applied AI"),
        ("pf-linkedin", "LinkedIn actualizado con los proyectos"),
    ],
    "interview": [
        ("iv-proyecto", "Explicar un proyecto propio en cinco minutos"),
        ("iv-diseno-rag", "Diseñar un sistema RAG en una pizarra con sus trade-offs"),
        ("iv-codigo", "Resolver un ejercicio de Python en vivo explicando el razonamiento"),
        ("iv-ingles", "Responder preguntas de comportamiento en inglés"),
        ("iv-salario", "Preparar la banda salarial y la negociación"),
    ],
    "business": [
        ("bz-propuesta", "Propuesta comercial de servicios de IA"),
        ("bz-tarifa", "Tarifa calculada con costes, horas y margen"),
        ("bz-contrato", "Condiciones de servicio y protección de datos revisadas"),
        ("bz-piloto", "Primer cliente piloto o caso real documentado"),
    ],
}

# ---------- Puestos objetivo ----------
ROLES = [
    {
        "id": "python-backend-developer",
        "band": "junior",
        "title": {"es": "Python Backend Developer", "en": "Python Backend Developer"},
        "skills": {
            "py-oop": 0.6,
            "py-testing": 0.6,
            "api-design": 0.6,
            "sql": 0.6,
            "git-workflow": 0.6,
            "containers-linux": 0.5,
        },
    },
    {
        "id": "ai-application-developer",
        "band": "developer",
        "title": {"es": "AI Application Developer", "en": "AI Application Developer"},
        "skills": {
            "api-design": 0.7,
            "py-testing": 0.6,
            "llm-prompting-structured": 0.6,
            "llm-rag-search": 0.6,
            "web-client": 0.5,
        },
    },
    {
        "id": "ai-automation-engineer",
        "band": "developer",
        "title": {"es": "AI Automation Engineer", "en": "AI Automation Engineer"},
        "skills": {
            "api-design": 0.7,
            "llm-prompting-structured": 0.7,
            "agents-tools": 0.7,
            "agents-safety-hitl": 0.7,
            "ci-cd": 0.6,
        },
    },
    {
        "id": "applied-ai-engineer",
        "band": "applied",
        "title": {"es": "Applied AI Engineer", "en": "Applied AI Engineer"},
        "skills": {
            "api-design": 0.75,
            "py-testing": 0.7,
            "local-models": 0.6,
            "llm-rag-search": 0.75,
            "llm-evaluation": 0.7,
            "agents-tools": 0.6,
            "containers-linux": 0.6,
        },
    },
    {
        "id": "generative-ai-engineer",
        "band": "applied",
        "title": {"es": "Generative AI Engineer", "en": "Generative AI Engineer"},
        "skills": {
            "transformers-embeddings": 0.7,
            "local-models": 0.7,
            "llm-prompting-structured": 0.75,
            "llm-rag-search": 0.75,
            "llm-evaluation": 0.7,
        },
    },
    {
        "id": "ai-solutions-engineer",
        "band": "applied",
        "title": {"es": "AI Solutions Engineer", "en": "AI Solutions Engineer"},
        "skills": {
            "llm-rag-search": 0.7,
            "agents-tools": 0.7,
            "cloud-deploy-ops": 0.6,
            "business-consulting": 0.6,
            "interviews-english": 0.7,
        },
    },
    {
        "id": "llm-engineer",
        "band": "senior",
        "title": {"es": "LLM Engineer", "en": "LLM Engineer"},
        "skills": {
            "transformers-embeddings": 0.75,
            "local-models": 0.75,
            "llm-prompting-structured": 0.8,
            "llm-rag-search": 0.8,
            "llm-evaluation": 0.8,
            "agents-tools": 0.6,
        },
    },
    {
        "id": "ai-product-engineer",
        "band": "senior",
        "title": {"es": "AI Product Engineer", "en": "AI Product Engineer"},
        "skills": {
            "api-design": 0.7,
            "web-client": 0.6,
            "llm-rag-search": 0.7,
            "saas-architecture": 0.7,
            "llm-app-security-privacy": 0.7,
            "product-ux-metrics": 0.7,
        },
    },
    {
        "id": "senior-applied-ai-engineer",
        "band": "senior",
        "title": {"es": "Senior Applied AI Engineer", "en": "Senior Applied AI Engineer"},
        "skills": {
            "py-architecture": 0.85,
            "llm-rag-search": 0.85,
            "llm-evaluation": 0.85,
            "agents-tools": 0.8,
            "agents-safety-hitl": 0.8,
            "agents-observability-eval": 0.8,
            "cloud-deploy-ops": 0.75,
            "saas-architecture": 0.7,
        },
    },
]

# ---------- Módulos y unidades ----------


def unit(id_, level, es, en, objectives, skills, links=(), pending=True):
    return {
        "id": id_,
        "level": level,
        "title": {"es": es, "en": en},
        "objectives": list(objectives),
        "skills": list(skills),
        "links": [{"kind": k, "id": i} for k, i in links],
        "pending": pending,
    }


MODULES = [
    {
        "id": "m1",
        "requires": [],
        "title": {"es": "Python Engineering", "en": "Python Engineering"},
        "summary": {
            "es": "Python de nivel profesional: diseño, tipos, errores, asincronía, tests y Git.",
            "en": "Professional-level Python: design, types, errors, async, tests and Git.",
        },
        "units": [
            unit(
                "m1.poo",
                "fundamentos",
                "Programación orientada a objetos",
                "Object-oriented programming",
                [
                    "Diseñar clases con responsabilidades claras",
                    "Elegir entre herencia y composición con criterio",
                ],
                ["py-oop"],
                [
                    ("concept", "poo"),
                    ("block", "programacion:prog-ut4"),
                    ("block", "programacion:prog-ut5"),
                ],
            ),
            unit(
                "m1.errores",
                "fundamentos",
                "Gestión de errores",
                "Error handling",
                ["Lanzar y capturar excepciones propias", "Validar entradas sin ocultar fallos"],
                ["py-errors"],
                [("concept", "excepciones"), ("concept", "validacion")],
            ),
            unit(
                "m1.git",
                "fundamentos",
                "Git y GitHub",
                "Git and GitHub",
                [
                    "Trabajar con ramas, commits pequeños y pull requests",
                    "Revisar un diff antes de cada commit",
                ],
                ["git-workflow"],
                [("resource", "res-pro-git")],
            ),
            unit(
                "m1.tipado",
                "intermedio",
                "Tipado y estructuras de datos",
                "Typing and data structures",
                [
                    "Anotar tipos y comprobarlos",
                    "Elegir la estructura de datos según el coste de las operaciones",
                ],
                ["py-types-data"],
                [
                    ("concept", "tipos"),
                    ("concept", "diccionarios"),
                    ("concept", "tuplas-conjuntos"),
                    ("resource", "res-python-tutorial"),
                ],
            ),
            unit(
                "m1.iteradores",
                "intermedio",
                "Iteradores, generadores y decoradores",
                "Iterators, generators and decorators",
                [
                    "Escribir generadores que procesan datos sin cargarlos enteros",
                    "Entender y escribir un decorador",
                ],
                ["py-types-data", "py-architecture"],
                [("concept", "recorridos")],
            ),
            unit(
                "m1.testing",
                "intermedio",
                "Testing con pytest",
                "Testing with pytest",
                [
                    "Escribir tests unitarios con fixtures y parametrización",
                    "Medir la cobertura y saber qué no cubre",
                ],
                ["py-testing"],
                [("concept", "depuracion")],
            ),
            unit(
                "m1.asyncio",
                "avanzado",
                "Asyncio y programación asíncrona",
                "Asyncio and asynchronous programming",
                [
                    "Distinguir concurrencia de paralelismo",
                    "Coordinar tareas con async/await sin bloquear el bucle",
                ],
                ["py-async"],
            ),
            unit(
                "m1.arquitectura",
                "avanzado",
                "Arquitectura de software",
                "Software architecture",
                [
                    "Separar dominio, aplicación e infraestructura sin capas inútiles",
                    "Gestionar dependencias entre módulos",
                ],
                ["py-architecture"],
                [("concept", "modulos")],
            ),
            unit(
                "m1.datos",
                "avanzado",
                "Procesamiento de datos",
                "Data processing",
                [
                    "Leer, transformar y validar ficheros de datos",
                    "Normalizar datos de fuentes distintas a un esquema común",
                ],
                ["py-data-processing"],
                [("concept", "archivos"), ("concept", "recorridos")],
            ),
            unit(
                "m1.clean-code",
                "profesional",
                "Clean code y revisión de código",
                "Clean code and code review",
                [
                    "Refactorizar con tests como red de seguridad",
                    "Hacer y recibir revisiones de código con evidencias",
                ],
                ["py-architecture", "git-workflow"],
            ),
        ],
        "assessment": {"id": "m1", "pass": 0.7, "bank": None},
        "project": {"criteria": ["npa-servicio-tests", "re-normalizacion"], "checklists": []},
    },
    {
        "id": "m2",
        "requires": ["m1"],
        "title": {"es": "Backend Engineering", "en": "Backend Engineering"},
        "summary": {
            "es": "APIs de producción con FastAPI, PostgreSQL y Redis, seguras y modulares.",
            "en": "Production APIs with FastAPI, PostgreSQL and Redis, secure and modular.",
        },
        "units": [
            unit(
                "m2.rest",
                "fundamentos",
                "Diseño de APIs REST",
                "REST API design",
                [
                    "Modelar recursos, métodos y códigos de estado",
                    "Versionar una API sin romper clientes",
                ],
                ["api-design"],
            ),
            unit(
                "m2.sql",
                "fundamentos",
                "SQL avanzado",
                "Advanced SQL",
                [
                    "Escribir consultas con JOIN, agregados y subconsultas",
                    "Leer un plan de ejecución",
                ],
                ["sql"],
                [("block", "sql:bd-ud2"), ("block", "sql:bd-ud3")],
            ),
            unit(
                "m2.cliente",
                "fundamentos",
                "Consumir la API desde el navegador",
                "Consuming the API from the browser",
                [
                    "Llamar a una API con fetch y gestionar errores",
                    "Entender CORS y las cookies de sesión",
                ],
                ["web-client"],
                [
                    ("block", "js:js-asincronia"),
                    ("block", "js:js-dom"),
                    ("block", "marcas:mar-json"),
                    ("resource", "res-mdn-js"),
                ],
            ),
            unit(
                "m2.pydantic",
                "intermedio",
                "Pydantic",
                "Pydantic",
                [
                    "Validar entradas y salidas con esquemas",
                    "Separar el modelo de la API del de la base de datos",
                ],
                ["api-design"],
            ),
            unit(
                "m2.fastapi",
                "intermedio",
                "FastAPI avanzado",
                "Advanced FastAPI",
                [
                    "Usar dependencias, routers y ciclo de vida",
                    "Probar endpoints con el cliente de tests",
                ],
                ["api-design"],
            ),
            unit(
                "m2.migraciones",
                "intermedio",
                "Migraciones de base de datos",
                "Database migrations",
                [
                    "Crear migraciones versionadas y reversibles",
                    "Migrar datos existentes sin perderlos",
                ],
                ["db-postgres-redis"],
                [("block", "sql:bd-ampliacion")],
            ),
            unit(
                "m2.auth",
                "avanzado",
                "Autenticación y autorización",
                "Authentication and authorization",
                ["Implementar sesiones o tokens y su revocación", "Aplicar autorización sin IDOR"],
                ["api-auth-security"],
            ),
            unit(
                "m2.postgres",
                "avanzado",
                "PostgreSQL",
                "PostgreSQL",
                ["Usar índices, transacciones y bloqueos", "Diagnosticar consultas lentas"],
                ["db-postgres-redis", "sql"],
                [("block", "sql:bd-ampliacion")],
            ),
            unit(
                "m2.redis",
                "avanzado",
                "Redis",
                "Redis",
                [
                    "Usar Redis como caché y para límites de peticiones",
                    "Decidir cuándo no hace falta Redis",
                ],
                ["db-postgres-redis"],
            ),
            unit(
                "m2.modular",
                "profesional",
                "Arquitectura modular",
                "Modular architecture",
                ["Organizar un monolito modular", "Decidir con datos cuándo separar un servicio"],
                ["api-design", "py-architecture"],
            ),
            unit(
                "m2.seguridad",
                "profesional",
                "Seguridad de APIs",
                "API security",
                [
                    "Revisar una API con el OWASP API Security Top 10",
                    "Configurar límites, cabeceras y registros de seguridad",
                ],
                ["api-auth-security"],
            ),
        ],
        "assessment": {"id": "m2", "pass": 0.7, "bank": None},
        "project": {
            "criteria": ["npa-backend-produccion", "jr-conectores", "pld-fullstack"],
            "checklists": [],
        },
    },
    {
        "id": "m3",
        "requires": ["m1"],
        "title": {"es": "AI Fundamentals", "en": "AI Fundamentals"},
        "summary": {
            "es": "Lo necesario de ML, deep learning y transformers para usar y elegir modelos con criterio.",
            "en": "The ML, deep learning and transformer basics needed to use and choose models wisely.",
        },
        "units": [
            unit(
                "m3.ml",
                "fundamentos",
                "Fundamentos de machine learning",
                "Machine learning fundamentals",
                [
                    "Distinguir entrenamiento, validación y prueba",
                    "Interpretar métricas básicas de un modelo",
                ],
                ["ml-foundations"],
            ),
            unit(
                "m3.open-source",
                "fundamentos",
                "Modelos open source y Hugging Face",
                "Open-source models and Hugging Face",
                [
                    "Leer la ficha de un modelo: licencia, tamaño y datos",
                    "Elegir un modelo para una tarea concreta",
                ],
                ["local-models"],
            ),
            unit(
                "m3.ollama",
                "fundamentos",
                "Ollama en local",
                "Ollama locally",
                ["Servir y consultar un modelo local por API", "Medir latencia y memoria"],
                ["local-models"],
            ),
            unit(
                "m3.redes",
                "intermedio",
                "Redes neuronales y deep learning",
                "Neural networks and deep learning",
                [
                    "Explicar capas, pesos y retropropagación con un ejemplo pequeño",
                    "Entender por qué hacen falta tantos datos",
                ],
                ["ml-foundations"],
            ),
            unit(
                "m3.tokenizacion",
                "intermedio",
                "Tokenización",
                "Tokenization",
                [
                    "Contar tokens y estimar costes y contexto",
                    "Ver cómo cambia la tokenización entre idiomas",
                ],
                ["transformers-embeddings"],
            ),
            unit(
                "m3.embeddings",
                "intermedio",
                "Embeddings",
                "Embeddings",
                [
                    "Calcular similitud coseno entre vectores",
                    "Elegir un modelo de embeddings para español",
                ],
                ["transformers-embeddings"],
            ),
            unit(
                "m3.inferencia",
                "intermedio",
                "Inferencia",
                "Inference",
                [
                    "Ajustar temperatura, top-p y longitud",
                    "Entender qué hace el modelo al generar token a token",
                ],
                ["transformers-embeddings", "local-models"],
            ),
            unit(
                "m3.transformers",
                "avanzado",
                "Transformers y atención",
                "Transformers and attention",
                [
                    "Explicar la atención con un ejemplo numérico",
                    "Relacionar la ventana de contexto con la arquitectura",
                ],
                ["transformers-embeddings"],
            ),
            unit(
                "m3.cuantizacion",
                "avanzado",
                "Cuantización y rendimiento",
                "Quantization and performance",
                [
                    "Comparar formatos cuantizados por calidad y memoria",
                    "Elegir el modelo que cabe en el hardware disponible",
                ],
                ["local-models"],
            ),
            unit(
                "m3.comparar",
                "profesional",
                "Comparar modelos locales",
                "Comparing local models",
                ["Diseñar una comparativa reproducible", "Decidir con datos, no con impresiones"],
                ["local-models", "llm-evaluation"],
            ),
        ],
        "assessment": {"id": "m3", "pass": 0.7, "bank": None},
        "project": {"criteria": ["npa-comparativa-modelos"], "checklists": []},
    },
    {
        "id": "m4",
        "requires": ["m1", "m3"],
        "title": {"es": "LLM Engineering", "en": "LLM Engineering"},
        "summary": {
            "es": "Construir sistemas con LLM fiables: prompts, salidas estructuradas, RAG híbrido y evaluación.",
            "en": "Building reliable LLM systems: prompts, structured outputs, hybrid RAG and evaluation.",
        },
        "units": [
            unit(
                "m4.prompting",
                "fundamentos",
                "Prompt engineering",
                "Prompt engineering",
                [
                    "Escribir instrucciones con contexto, ejemplos y formato",
                    "Probar un prompt con casos que deben fallar",
                ],
                ["llm-prompting-structured"],
            ),
            unit(
                "m4.structured",
                "intermedio",
                "Structured outputs",
                "Structured outputs",
                [
                    "Pedir JSON y validarlo contra un esquema",
                    "Reintentar o rechazar una salida inválida",
                ],
                ["llm-prompting-structured"],
            ),
            unit(
                "m4.function-calling",
                "intermedio",
                "Function calling",
                "Function calling",
                [
                    "Declarar herramientas con esquemas",
                    "Ejecutar solo llamadas permitidas y validadas",
                ],
                ["llm-prompting-structured", "agents-tools"],
            ),
            unit(
                "m4.streaming",
                "intermedio",
                "Streaming",
                "Streaming",
                [
                    "Enviar la respuesta por fragmentos al cliente",
                    "Gestionar cancelaciones y errores a mitad",
                ],
                ["llm-prompting-structured", "api-design"],
            ),
            unit(
                "m4.contexto",
                "intermedio",
                "Gestión del contexto",
                "Context management",
                [
                    "Presupuestar tokens entre instrucciones, historial y documentos",
                    "Resumir o recortar sin perder lo importante",
                ],
                ["llm-rag-search"],
            ),
            unit(
                "m4.rag",
                "intermedio",
                "RAG",
                "RAG",
                [
                    "Explicar las fases: ingesta, troceado, recuperación y generación",
                    "Citar las fuentes en cada respuesta",
                ],
                ["llm-rag-search"],
            ),
            unit(
                "m4.semantica",
                "intermedio",
                "Búsqueda semántica",
                "Semantic search",
                ["Indexar fragmentos con embeddings", "Recuperar por similitud y fijar un umbral"],
                ["llm-rag-search", "transformers-embeddings"],
            ),
            unit(
                "m4.hibrida",
                "avanzado",
                "Búsqueda híbrida BM25 + embeddings",
                "Hybrid search: BM25 + embeddings",
                [
                    "Implementar BM25 y combinarlo con embeddings (RRF)",
                    "Medir si la combinación mejora a cada método solo",
                ],
                ["llm-rag-search"],
            ),
            unit(
                "m4.reranking",
                "avanzado",
                "Reranking",
                "Reranking",
                [
                    "Reordenar candidatos con un modelo o reglas",
                    "Valorar el coste en latencia del reranking",
                ],
                ["llm-rag-search"],
            ),
            unit(
                "m4.vectores",
                "avanzado",
                "Bases de datos vectoriales: Qdrant o pgvector",
                "Vector databases: Qdrant or pgvector",
                [
                    "Elegir entre Qdrant y pgvector con criterios",
                    "Filtrar por metadatos y permisos en la búsqueda",
                ],
                ["llm-rag-search", "db-postgres-redis"],
            ),
            unit(
                "m4.evaluacion",
                "profesional",
                "Evaluación de respuestas",
                "Answer evaluation",
                [
                    "Construir un conjunto de preguntas con respuestas esperadas",
                    "Medir recuperación y fidelidad antes y después de un cambio",
                ],
                ["llm-evaluation"],
            ),
            unit(
                "m4.alucinaciones",
                "profesional",
                "Gestión de alucinaciones",
                "Handling hallucinations",
                [
                    "Detectar respuestas sin respaldo en las fuentes",
                    "Responder «no lo sé» cuando falta información",
                ],
                ["llm-evaluation"],
            ),
            unit(
                "m4.seguridad-aplicada",
                "profesional",
                "IA aplicada a resultados de seguridad",
                "AI applied to security findings",
                [
                    "Usar un LLM para resumir y priorizar hallazgos sin delegarle la decisión",
                    "Explicar cada prioridad con datos verificables",
                ],
                ["applied-ai-security"],
            ),
        ],
        "assessment": {"id": "m4", "pass": 0.7, "bank": None},
        "project": {"criteria": ["npa-rag-eval", "jr-extraccion", "re-riesgo"], "checklists": []},
    },
    {
        "id": "m5",
        "requires": ["m4"],
        "title": {"es": "AI Agents", "en": "AI Agents"},
        "summary": {
            "es": "Agentes que usan herramientas con permisos, supervisión humana y evaluación.",
            "en": "Agents that use tools with permissions, human oversight and evaluation.",
        },
        "units": [
            unit(
                "m5.arquitectura",
                "fundamentos",
                "Arquitectura de agentes",
                "Agent architecture",
                [
                    "Distinguir un flujo fijo de un agente",
                    "Decidir cuándo un agente no aporta valor",
                ],
                ["agents-tools"],
            ),
            unit(
                "m5.tools",
                "fundamentos",
                "Tool calling",
                "Tool calling",
                [
                    "Registrar herramientas con esquema y descripción",
                    "Tratar los resultados de herramientas como datos no confiables",
                ],
                ["agents-tools"],
            ),
            unit(
                "m5.planificacion",
                "intermedio",
                "Planificación y ejecución",
                "Planning and execution",
                [
                    "Implementar un bucle planificar-actuar-observar con límite de pasos",
                    "Recuperarse de una herramienta que falla",
                ],
                ["agents-tools"],
            ),
            unit(
                "m5.memoria",
                "intermedio",
                "Memoria",
                "Memory",
                [
                    "Separar memoria de la conversación y memoria persistente",
                    "Decidir qué se guarda y quién puede verlo",
                ],
                ["agents-tools", "llm-app-security-privacy"],
            ),
            unit(
                "m5.permisos",
                "intermedio",
                "Gestión de permisos",
                "Permission management",
                [
                    "Aplicar mínimo privilegio a cada herramienta",
                    "Probar que una acción no permitida se rechaza",
                ],
                ["agents-safety-hitl"],
            ),
            unit(
                "m5.hitl",
                "intermedio",
                "Human-in-the-loop",
                "Human-in-the-loop",
                [
                    "Pedir confirmación antes de acciones irreversibles",
                    "Diseñar la pantalla de aprobación",
                ],
                ["agents-safety-hitl"],
            ),
            unit(
                "m5.mcp",
                "avanzado",
                "MCP",
                "MCP",
                ["Exponer herramientas por MCP", "Conectar un cliente MCP con permisos acotados"],
                ["agents-safety-hitl", "agents-tools"],
            ),
            unit(
                "m5.langgraph",
                "avanzado",
                "LangGraph",
                "LangGraph",
                [
                    "Modelar un agente como grafo de estados",
                    "Comparar LangGraph con un bucle propio",
                ],
                ["agents-tools"],
            ),
            unit(
                "m5.multiagente",
                "avanzado",
                "Sistemas multiagente",
                "Multi-agent systems",
                [
                    "Repartir una tarea entre agentes con roles",
                    "Medir si varios agentes mejoran a uno",
                ],
                ["agents-tools"],
            ),
            unit(
                "m5.observabilidad",
                "profesional",
                "Observabilidad de agentes",
                "Agent observability",
                [
                    "Registrar cada paso, herramienta y coste",
                    "Reconstruir por qué un agente tomó una decisión",
                ],
                ["agents-observability-eval"],
            ),
            unit(
                "m5.evaluacion",
                "profesional",
                "Evaluación de agentes",
                "Agent evaluation",
                [
                    "Definir tareas de prueba con criterio de éxito",
                    "Comparar versiones de un agente con los mismos casos",
                ],
                ["agents-observability-eval"],
            ),
        ],
        "assessment": {"id": "m5", "pass": 0.7, "bank": None},
        "project": {"criteria": ["npa-agente-permisos", "jr-documentos"], "checklists": []},
    },
    {
        "id": "m6",
        "requires": ["m2"],
        "title": {"es": "AI Infrastructure & MLOps", "en": "AI Infrastructure & MLOps"},
        "summary": {
            "es": "Desplegar, observar y mantener aplicaciones de IA con costes controlados.",
            "en": "Deploying, observing and running AI applications with controlled costs.",
        },
        "units": [
            unit(
                "m6.linux",
                "fundamentos",
                "Linux para despliegues",
                "Linux for deployments",
                [
                    "Gestionar servicios, usuarios y permisos",
                    "Diagnosticar con registros y procesos",
                ],
                ["containers-linux"],
            ),
            unit(
                "m6.compose",
                "fundamentos",
                "Docker Compose",
                "Docker Compose",
                [
                    "Definir servicios, redes y volúmenes",
                    "Arrancar el entorno completo con un comando",
                ],
                ["containers-linux"],
                [("resource", "res-docker-docs")],
            ),
            unit(
                "m6.docker",
                "intermedio",
                "Docker avanzado",
                "Advanced Docker",
                ["Construir imágenes pequeñas multi-etapa", "Ejecutar contenedores sin root"],
                ["containers-linux"],
                [("resource", "res-docker-docs")],
            ),
            unit(
                "m6.ci-cd",
                "intermedio",
                "CI/CD con GitHub Actions",
                "CI/CD with GitHub Actions",
                ["Automatizar lint, tests y build", "Proteger secretos y permisos del flujo"],
                ["ci-cd"],
            ),
            unit(
                "m6.logging",
                "intermedio",
                "Logging y monitorización",
                "Logging and monitoring",
                ["Escribir registros estructurados", "Definir alertas útiles"],
                ["cloud-deploy-ops"],
            ),
            unit(
                "m6.cloud",
                "avanzado",
                "AWS o Azure",
                "AWS or Azure",
                [
                    "Desplegar un servicio gestionado básico",
                    "Entender el modelo de responsabilidad compartida",
                ],
                ["cloud-deploy-ops"],
            ),
            unit(
                "m6.modelos",
                "avanzado",
                "Despliegue de modelos",
                "Model deployment",
                [
                    "Servir un modelo con límites de concurrencia",
                    "Elegir entre modelo local y API externa por coste y privacidad",
                ],
                ["cloud-deploy-ops", "local-models"],
            ),
            unit(
                "m6.observabilidad",
                "avanzado",
                "Observabilidad",
                "Observability",
                [
                    "Relacionar métricas, trazas y registros",
                    "Medir latencia y coste por petición de IA",
                ],
                ["cloud-deploy-ops", "agents-observability-eval"],
            ),
            unit(
                "m6.costes",
                "profesional",
                "Gestión de costes",
                "Cost management",
                ["Estimar el coste mensual de un servicio de IA", "Poner topes de gasto"],
                ["cloud-deploy-ops"],
            ),
            unit(
                "m6.escalabilidad",
                "profesional",
                "Escalabilidad",
                "Scalability",
                ["Encontrar el cuello de botella con medidas", "Escalar solo lo que lo necesita"],
                ["cloud-deploy-ops"],
            ),
            unit(
                "m6.seguridad",
                "profesional",
                "Seguridad de infraestructura",
                "Infrastructure security",
                [
                    "Endurecer un servidor y sus contenedores",
                    "Gestionar secretos y copias de seguridad",
                ],
                ["containers-linux", "cloud-deploy-ops"],
            ),
        ],
        "assessment": {"id": "m6", "pass": 0.7, "bank": None},
        "project": {"criteria": ["npa-despliegue", "pld-fullstack"], "checklists": []},
    },
    {
        "id": "m7",
        "requires": ["m2", "m4"],
        "title": {"es": "AI Product Engineering", "en": "AI Product Engineering"},
        "summary": {
            "es": "Convertir un sistema de IA en un producto útil, seguro, legal y medible.",
            "en": "Turning an AI system into a useful, secure, lawful and measurable product.",
        },
        "units": [
            unit(
                "m7.diseno",
                "fundamentos",
                "Diseño de productos de IA",
                "Designing AI products",
                [
                    "Definir el problema y el usuario antes que el modelo",
                    "Decidir dónde la IA aporta valor real",
                ],
                ["saas-architecture", "product-ux-metrics"],
            ),
            unit(
                "m7.ux",
                "fundamentos",
                "UX para aplicaciones de IA",
                "UX for AI applications",
                [
                    "Mostrar incertidumbre, fuentes y errores",
                    "Diseñar con accesibilidad WCAG desde el principio",
                ],
                ["product-ux-metrics"],
            ),
            unit(
                "m7.privacidad",
                "intermedio",
                "Privacidad y protección de datos",
                "Privacy and data protection",
                ["Aplicar minimización y base legal (RGPD)", "Documentar un tratamiento de datos"],
                ["llm-app-security-privacy"],
            ),
            unit(
                "m7.seguridad-llm",
                "intermedio",
                "Seguridad de aplicaciones LLM",
                "LLM application security",
                [
                    "Revisar una aplicación con el OWASP Top 10 para LLM",
                    "Mitigar inyección de prompts y fuga de datos",
                ],
                ["llm-app-security-privacy", "applied-ai-security"],
            ),
            unit(
                "m7.apis",
                "intermedio",
                "Integración de APIs",
                "API integration",
                [
                    "Integrar servicios externos con reintentos y límites",
                    "Aislar al proveedor para poder cambiarlo",
                ],
                ["api-design", "saas-architecture"],
            ),
            unit(
                "m7.usuarios",
                "intermedio",
                "Gestión de usuarios",
                "User management",
                ["Modelar cuentas, roles y equipos", "Gestionar alta, baja y exportación de datos"],
                ["saas-architecture", "api-auth-security"],
            ),
            unit(
                "m7.saas",
                "avanzado",
                "Arquitectura SaaS",
                "SaaS architecture",
                ["Diseñar un SaaS empezando por un monolito", "Separar configuración por cliente"],
                ["saas-architecture"],
            ),
            unit(
                "m7.multi-tenancy",
                "avanzado",
                "Multi-tenancy",
                "Multi-tenancy",
                [
                    "Comparar modelos de aislamiento entre clientes",
                    "Probar que un cliente no ve datos de otro",
                ],
                ["saas-architecture", "api-auth-security"],
            ),
            unit(
                "m7.pagos",
                "avanzado",
                "Suscripciones y pagos",
                "Subscriptions and payments",
                [
                    "Modelar planes, pruebas y cancelaciones",
                    "Delegar los datos de pago en un proveedor certificado",
                ],
                ["saas-architecture"],
            ),
            unit(
                "m7.metricas",
                "profesional",
                "Métricas de producto",
                "Product metrics",
                [
                    "Definir activación, retención y coste por usuario",
                    "Medir sin recoger más datos de los necesarios",
                ],
                ["product-ux-metrics"],
            ),
            unit(
                "m7.validacion",
                "profesional",
                "Validación con usuarios",
                "User validation",
                [
                    "Preparar entrevistas y pruebas con usuarios reales",
                    "Decidir qué construir con lo aprendido",
                ],
                ["product-ux-metrics"],
            ),
        ],
        "assessment": {"id": "m7", "pass": 0.7, "bank": None},
        "project": {"criteria": ["npa-producto", "pld-a11y"], "checklists": []},
    },
    {
        "id": "m8",
        "requires": [],
        "title": {"es": "Career & Business Development", "en": "Career & Business Development"},
        "summary": {
            "es": "Hacer visible el trabajo, conseguir el puesto y construir una actividad propia rentable.",
            "en": "Making the work visible, landing the role and building a profitable own business.",
        },
        "units": [
            unit(
                "m8.github",
                "fundamentos",
                "GitHub profesional",
                "Professional GitHub",
                [
                    "Presentar repositorios que se entienden en dos minutos",
                    "Mostrar tests, CI y decisiones",
                ],
                ["portfolio-presence"],
            ),
            unit(
                "m8.portfolio",
                "fundamentos",
                "Portfolio profesional",
                "Professional portfolio",
                [
                    "Elegir tres proyectos que demuestran el perfil",
                    "Contar problema, solución y resultado",
                ],
                ["portfolio-presence"],
            ),
            unit(
                "m8.cv",
                "fundamentos",
                "CV técnico",
                "Technical CV",
                ["Escribir logros medibles en lugar de tareas", "Adaptar el CV a cada puesto"],
                ["portfolio-presence"],
            ),
            unit(
                "m8.linkedin",
                "fundamentos",
                "LinkedIn",
                "LinkedIn",
                [
                    "Alinear el perfil con el puesto objetivo",
                    "Publicar avances de proyectos con regularidad",
                ],
                ["portfolio-presence"],
            ),
            unit(
                "m8.ingles",
                "intermedio",
                "Inglés técnico",
                "Technical English",
                ["Explicar una arquitectura en inglés", "Leer y escribir documentación técnica"],
                ["interviews-english"],
            ),
            unit(
                "m8.entrevistas",
                "intermedio",
                "Entrevistas técnicas",
                "Technical interviews",
                [
                    "Preparar ejercicios de código y de diseño de sistemas",
                    "Responder con ejemplos propios",
                ],
                ["interviews-english"],
            ),
            unit(
                "m8.negociacion",
                "intermedio",
                "Negociación salarial",
                "Salary negotiation",
                [
                    "Investigar la banda real del puesto",
                    "Negociar el paquete completo, no solo el sueldo",
                ],
                ["interviews-english"],
            ),
            unit(
                "m8.freelance",
                "intermedio",
                "Freelance",
                "Freelancing",
                [
                    "Conocer las obligaciones de un autónomo en España",
                    "Separar facturación, gastos y beneficio",
                ],
                ["business-consulting"],
            ),
            unit(
                "m8.consultoria",
                "avanzado",
                "Consultoría de IA",
                "AI consulting",
                [
                    "Diagnosticar dónde la IA ahorra tiempo o dinero a un cliente",
                    "Definir alcance y entregables",
                ],
                ["business-consulting"],
            ),
            unit(
                "m8.captacion",
                "avanzado",
                "Captación de clientes",
                "Finding clients",
                ["Definir el cliente ideal", "Preparar una propuesta y hacer seguimiento"],
                ["business-consulting"],
            ),
            unit(
                "m8.saas",
                "avanzado",
                "Modelos SaaS",
                "SaaS business models",
                [
                    "Comparar suscripción, uso y licencias",
                    "Estimar ingresos recurrentes y abandono",
                ],
                ["business-consulting", "saas-architecture"],
            ),
            unit(
                "m8.pricing",
                "profesional",
                "Pricing y rentabilidad",
                "Pricing and profitability",
                [
                    "Calcular precio con costes, horas y margen",
                    "Distinguir facturación, beneficio y salario",
                ],
                ["business-consulting"],
            ),
            unit(
                "m8.empresa",
                "profesional",
                "Crear una empresa tecnológica",
                "Starting a tech company",
                ["Comparar autónomo y sociedad con números", "Planificar los primeros doce meses"],
                ["business-consulting"],
            ),
        ],
        "assessment": {"id": "m8", "pass": 0.7, "bank": None},
        "project": {"criteria": [], "checklists": ["portfolio", "business"]},
    },
]
