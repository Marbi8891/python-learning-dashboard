# ruff: noqa: E501
# (fichas de contenido: los textos largos van en una sola línea para poder leerlos y editarlos)
"""Itinerarios del Career Roadmap (docs/CAREER_ROADMAP_ARCHITECTURE.md §4.2).

Aquí solo hay datos. `build_career.py` los valida y genera frontend/data/career/*.json.
Añadir un itinerario es añadir una entrada a ROADMAPS: la lógica no cambia.

Enlaces de una unidad (`links`), siempre a contenido que ya existe en la plataforma:
    ("concept", "<id de learning.json>")          concepto del motor adaptativo
    ("pcap", "<slug de lessons.json>")            lección del curso PCAP
    ("lesson", "<curso>/<slug>")                  lección de un curso de DAW
    ("block", "<curso>:<bloque>")                 bloque de preguntas de un curso de DAW
    ("resource", "<id de resources.json>")        recurso externo con licencia revisada
Una unidad sin enlaces queda marcada como «contenido pendiente» (Sprint 3): no se inventa contenido.

Fuentes de una competencia (`sources`), de donde sale su dominio (career-data.js):
    concepts       ids de learning.json (dominio y confianza del motor 2.0)
    blocks         "<curso>:<bloque>" (acierto y cobertura del bloque)
    projects       ids de proyectos de este itinerario (lista de comprobación entregada)
"""

CATEGORIES = (
    "programming",
    "backend",
    "databases",
    "frontend",
    "testing",
    "devops",
    "ai-ml",
    "professional",
)


def T(es: str, en: str) -> dict[str, str]:
    return {"es": es, "en": en}


PYTHON_BACKEND_JUNIOR = {
    "id": "python-backend-junior",
    "status": "complete",
    "title": T("Python Backend Developer Junior", "Junior Python Backend Developer"),
    "description": T(
        "Itinerario para llegar al primer puesto de desarrollo backend con Python: lenguaje, bases de datos, APIs con FastAPI, pruebas, despliegue y preparación de entrevistas.",
        "A path to a first backend developer job with Python: the language, databases, FastAPI APIs, testing, deployment and interview preparation.",
    ),
    "level": "junior",
    "months": 8,
    "objectives": [
        T(
            "Programar en Python con soltura y buenas prácticas",
            "Write fluent Python following good practices",
        ),
        T(
            "Diseñar y consultar bases de datos relacionales",
            "Design and query relational databases",
        ),
        T("Construir una API REST segura con FastAPI", "Build a secure REST API with FastAPI"),
        T(
            "Probar, desplegar y documentar una aplicación completa",
            "Test, deploy and document a complete application",
        ),
        T(
            "Presentar un portfolio y preparar entrevistas técnicas",
            "Present a portfolio and prepare technical interviews",
        ),
    ],
    "skills": [
        # Programming
        {
            "id": "py-basics",
            "category": "programming",
            "target": 3,
            "requires": [],
            "title": T(
                "Python básico: tipos, operadores y control de flujo",
                "Python basics: types, operators and control flow",
            ),
            "sources": {
                "concepts": [
                    "variables",
                    "tipos",
                    "operadores",
                    "entrada-salida",
                    "condicionales",
                    "bucles",
                ],
                "blocks": ["programacion:prog-ut2", "programacion:prog-ut3"],
            },
        },
        {
            "id": "py-functions",
            "category": "programming",
            "target": 3,
            "requires": ["py-basics"],
            "title": T("Funciones y recorridos", "Functions and iteration patterns"),
            "sources": {"concepts": ["funciones", "acumuladores", "recorridos"]},
        },
        {
            "id": "py-collections",
            "category": "programming",
            "target": 3,
            "requires": ["py-basics"],
            "title": T(
                "Strings, listas, tuplas, sets y diccionarios",
                "Strings, lists, tuples, sets and dictionaries",
            ),
            "sources": {
                "concepts": ["strings", "listas", "tuplas-conjuntos", "diccionarios"],
                "blocks": ["programacion:prog-ut6"],
            },
        },
        {
            "id": "py-oop",
            "category": "programming",
            "target": 2,
            "requires": ["py-functions", "py-collections"],
            "title": T("Programación orientada a objetos", "Object-oriented programming"),
            "sources": {
                "concepts": ["poo"],
                "blocks": ["programacion:prog-ut4", "programacion:prog-ut5"],
                "projects": ["mini-proyecto"],
            },
        },
        {
            "id": "py-errors-modules",
            "category": "programming",
            "target": 2,
            "requires": ["py-functions"],
            "title": T("Excepciones, módulos y ficheros", "Exceptions, modules and files"),
            "sources": {"concepts": ["excepciones", "modulos", "archivos"]},
        },
        {
            "id": "py-professional",
            "category": "programming",
            "target": 2,
            "requires": ["py-oop", "py-errors-modules"],
            "title": T(
                "Python profesional: typing, decoradores, generadores y dataclasses",
                "Professional Python: typing, decorators, generators and dataclasses",
            ),
            "sources": {"projects": ["gestor-tareas"]},
        },
        {
            "id": "clean-code",
            "category": "professional",
            "target": 2,
            "requires": ["py-oop"],
            "title": T(
                "Código limpio, SOLID y patrones básicos", "Clean code, SOLID and basic patterns"
            ),
            "sources": {"projects": ["gestor-tareas"]},
        },
        # Databases
        {
            "id": "sql-model",
            "category": "databases",
            "target": 2,
            "requires": [],
            "title": T("Modelo relacional y diseño de tablas", "Relational model and table design"),
            "sources": {"blocks": ["sql:bd-ud1", "sql:bd-ud2"]},
        },
        {
            "id": "sql-queries",
            "category": "databases",
            "target": 3,
            "requires": ["sql-model"],
            "title": T(
                "Consultas SQL: SELECT, JOIN, GROUP BY y subconsultas",
                "SQL queries: SELECT, JOIN, GROUP BY and subqueries",
            ),
            "sources": {"blocks": ["sql:bd-ud3"]},
        },
        {
            "id": "sql-transactions",
            "category": "databases",
            "target": 2,
            "requires": ["sql-queries"],
            "title": T("Modificar datos y transacciones", "Data changes and transactions"),
            "sources": {"blocks": ["sql:bd-ampliacion"]},
        },
        {
            "id": "orm",
            "category": "databases",
            "target": 2,
            "requires": ["sql-queries", "py-oop"],
            "title": T("SQLAlchemy, ORM y migraciones", "SQLAlchemy, ORM and migrations"),
            "sources": {"projects": ["gestion-clientes"]},
        },
        # Backend
        {
            "id": "http-rest",
            "category": "backend",
            "target": 2,
            "requires": ["py-functions"],
            "title": T("HTTP, REST y JSON", "HTTP, REST and JSON"),
            "sources": {"blocks": ["marcas:mar-json"], "projects": ["api-rest"]},
        },
        {
            "id": "fastapi",
            "category": "backend",
            "target": 3,
            "requires": ["http-rest", "py-professional"],
            "title": T(
                "FastAPI: rutas, Pydantic e inyección de dependencias",
                "FastAPI: routing, Pydantic and dependency injection",
            ),
            "sources": {"projects": ["api-rest"]},
        },
        {
            "id": "api-security",
            "category": "backend",
            "target": 2,
            "requires": ["fastapi"],
            "title": T(
                "Autenticación, autorización y seguridad de APIs",
                "Authentication, authorization and API security",
            ),
            "sources": {"projects": ["api-rest"]},
        },
        # Testing
        {
            "id": "debugging",
            "category": "testing",
            "target": 2,
            "requires": ["py-functions"],
            "title": T("Depuración y trazado de programas", "Debugging and tracing programs"),
            "sources": {"concepts": ["depuracion", "trazado"]},
        },
        {
            "id": "automated-testing",
            "category": "testing",
            "target": 2,
            "requires": ["debugging", "fastapi"],
            "title": T(
                "Pytest: pruebas unitarias y de integración", "Pytest: unit and integration testing"
            ),
            "sources": {"projects": ["bateria-pruebas"]},
        },
        # Frontend
        {
            "id": "html-css",
            "category": "frontend",
            "target": 2,
            "requires": [],
            "title": T("HTML y CSS", "HTML and CSS"),
            "sources": {"blocks": ["marcas:mar-html"]},
        },
        {
            "id": "js-core",
            "category": "frontend",
            "target": 2,
            "requires": [],
            "title": T(
                "JavaScript: tipos, funciones, arrays y objetos",
                "JavaScript: types, functions, arrays and objects",
            ),
            "sources": {"blocks": ["js:js-fundamentos", "js:js-funciones", "js:js-datos"]},
        },
        {
            "id": "dom-async",
            "category": "frontend",
            "target": 2,
            "requires": ["js-core", "html-css"],
            "title": T("DOM, eventos, async/await y fetch", "DOM, events, async/await and fetch"),
            "sources": {"blocks": ["js:js-dom", "js:js-asincronia"], "projects": ["interfaz-web"]},
        },
        # DevOps
        {
            "id": "dev-lifecycle",
            "category": "devops",
            "target": 2,
            "requires": [],
            "title": T(
                "Ciclo de vida del software y metodologías", "Software lifecycle and methodologies"
            ),
            "sources": {"blocks": ["entornos:ent-ciclo-de-vida", "entornos:ent-traduccion"]},
        },
        {
            "id": "git-github",
            "category": "devops",
            "target": 2,
            "requires": [],
            "title": T("Git, GitHub y pull requests", "Git, GitHub and pull requests"),
            "sources": {"projects": ["despliegue"]},
        },
        {
            "id": "docker-ci",
            "category": "devops",
            "target": 2,
            "requires": ["git-github", "fastapi"],
            "title": T("Docker, CI/CD y despliegue", "Docker, CI/CD and deployment"),
            "sources": {"projects": ["despliegue"]},
        },
        # Professional
        {
            "id": "portfolio",
            "category": "professional",
            "target": 2,
            "requires": ["git-github"],
            "title": T(
                "Portfolio, README y documentación técnica",
                "Portfolio, README and technical documentation",
            ),
            "sources": {"projects": ["proyecto-final"]},
        },
        {
            "id": "interviews",
            "category": "professional",
            "target": 2,
            "requires": ["py-collections", "sql-queries"],
            "title": T(
                "Entrevistas técnicas: algoritmos, SQL, Python y diseño de APIs",
                "Technical interviews: algorithms, SQL, Python and API design",
            ),
            "sources": {"projects": ["proyecto-final"]},
        },
    ],
    "phases": [
        {
            "id": "fundamentals",
            "requires": [],
            "title": T("Python Fundamentals", "Python Fundamentals"),
            "description": T(
                "Las bases del lenguaje, de las variables a la programación orientada a objetos.",
                "Language foundations, from variables to object-oriented programming.",
            ),
            "objectives": [
                T(
                    "Resolver problemas con condicionales, bucles y funciones",
                    "Solve problems with conditionals, loops and functions",
                ),
                T(
                    "Elegir la colección adecuada para cada dato",
                    "Choose the right collection for each piece of data",
                ),
                T(
                    "Modelar un problema con clases, herencia y polimorfismo",
                    "Model a problem with classes, inheritance and polymorphism",
                ),
            ],
            "skills": ["py-basics", "py-functions", "py-collections", "py-oop"],
            "units": [
                {
                    "id": "fund-variables-tipos",
                    "title": T("Variables, tipos y operadores", "Variables, types and operators"),
                    "links": [
                        ("concept", "variables"),
                        ("concept", "tipos"),
                        ("concept", "operadores"),
                        ("pcap", "variables"),
                        ("pcap", "tipos"),
                        ("pcap", "operadores"),
                    ],
                },
                {
                    "id": "fund-control",
                    "title": T("Condicionales y bucles", "Conditionals and loops"),
                    "links": [
                        ("concept", "condicionales"),
                        ("concept", "bucles"),
                        ("pcap", "condicionales"),
                        ("pcap", "bucles"),
                        ("lesson", "programacion/prog-ut3-control"),
                    ],
                },
                {
                    "id": "fund-funciones",
                    "title": T("Funciones", "Functions"),
                    "links": [
                        ("concept", "funciones"),
                        ("pcap", "funciones"),
                        ("lesson", "programacion/prog-ut3-funciones"),
                    ],
                },
                {
                    "id": "fund-colecciones",
                    "title": T(
                        "Listas, tuplas, diccionarios y sets",
                        "Lists, tuples, dictionaries and sets",
                    ),
                    "links": [
                        ("concept", "listas"),
                        ("concept", "tuplas-conjuntos"),
                        ("concept", "diccionarios"),
                        ("pcap", "colecciones"),
                        ("lesson", "programacion/prog-ut6-colecciones"),
                    ],
                },
                {
                    "id": "fund-strings",
                    "title": T("Strings", "Strings"),
                    "links": [
                        ("concept", "strings"),
                        ("pcap", "cadenas"),
                        ("pcap", "metodos-string"),
                    ],
                },
                {
                    "id": "fund-comprensiones",
                    "title": T("Comprensiones y lambdas", "Comprehensions and lambdas"),
                    "links": [("pcap", "comprensiones-lambda")],
                },
                {
                    "id": "fund-poo",
                    "title": T(
                        "Clases, herencia y polimorfismo", "Classes, inheritance and polymorphism"
                    ),
                    "links": [
                        ("concept", "poo"),
                        ("pcap", "poo"),
                        ("pcap", "herencia"),
                        ("lesson", "programacion/prog-ut4-poo"),
                        ("lesson", "programacion/prog-ut5-clases"),
                        ("lesson", "programacion/prog-ut6-herencia-excepciones"),
                    ],
                },
            ],
            "assessment": None,
            "project": "mini-proyecto",
        },
        {
            "id": "professional-python",
            "requires": ["fundamentals"],
            "title": T("Professional Python", "Professional Python"),
            "description": T(
                "Lo que separa un script de un programa mantenible: errores, módulos, entornos, tipado y diseño.",
                "What separates a script from maintainable software: errors, modules, environments, typing and design.",
            ),
            "objectives": [
                T(
                    "Gestionar errores y organizar el código en módulos y paquetes",
                    "Handle errors and organise code into modules and packages",
                ),
                T(
                    "Usar typing, decoradores, generadores y context managers",
                    "Use typing, decorators, generators and context managers",
                ),
                T(
                    "Aplicar SOLID y Clean Code en un proyecto propio",
                    "Apply SOLID and Clean Code in your own project",
                ),
            ],
            "skills": ["py-errors-modules", "py-professional", "clean-code"],
            "units": [
                {
                    "id": "pro-excepciones",
                    "title": T("Gestión de excepciones", "Exception handling"),
                    "links": [
                        ("concept", "excepciones"),
                        ("pcap", "excepciones"),
                        ("pcap", "jerarquia-excepciones"),
                    ],
                },
                {
                    "id": "pro-modulos-paquetes",
                    "title": T("Módulos y paquetes", "Modules and packages"),
                    "links": [
                        ("concept", "modulos"),
                        ("pcap", "modulos"),
                        ("pcap", "paquetes"),
                        ("lesson", "programacion/prog-ut5-modulos-cadenas"),
                    ],
                },
                {
                    "id": "pro-entornos-pip",
                    "title": T("Entornos virtuales y pip", "Virtual environments and pip"),
                    "links": [("resource", "res-python-tutorial")],
                },
                {
                    "id": "pro-typing-dataclasses",
                    "title": T("Typing y dataclasses", "Typing and dataclasses"),
                    "links": [],
                },
                {
                    "id": "pro-decoradores-closures",
                    "title": T("Closures y decoradores", "Closures and decorators"),
                    "links": [("pcap", "closures")],
                },
                {
                    "id": "pro-iteradores-generadores",
                    "title": T(
                        "Iteradores, generadores y context managers",
                        "Iterators, generators and context managers",
                    ),
                    "links": [],
                },
                {
                    "id": "pro-ficheros-logging",
                    "title": T("Ficheros y logging", "Files and logging"),
                    "links": [("concept", "archivos"), ("pcap", "archivos")],
                },
                {
                    "id": "pro-solid-clean-code",
                    "title": T(
                        "SOLID, Clean Code y patrones básicos",
                        "SOLID, Clean Code and basic patterns",
                    ),
                    "links": [],
                },
            ],
            "assessment": None,
            "project": "gestor-tareas",
        },
        {
            "id": "databases",
            "requires": ["fundamentals"],
            "title": T("Databases & SQL", "Databases & SQL"),
            "description": T(
                "Diseñar, consultar y modificar bases de datos relacionales, y usarlas desde Python.",
                "Design, query and modify relational databases, and use them from Python.",
            ),
            "objectives": [
                T(
                    "Diseñar un modelo relacional normalizado",
                    "Design a normalised relational model",
                ),
                T(
                    "Escribir consultas con JOIN, GROUP BY y subconsultas",
                    "Write queries with JOIN, GROUP BY and subqueries",
                ),
                T(
                    "Acceder a PostgreSQL con SQLAlchemy y migraciones",
                    "Access PostgreSQL with SQLAlchemy and migrations",
                ),
            ],
            "skills": ["sql-model", "sql-queries", "sql-transactions", "orm"],
            "units": [
                {
                    "id": "db-fundamentos",
                    "title": T(
                        "Fundamentos y modelo relacional", "Foundations and the relational model"
                    ),
                    "links": [
                        ("lesson", "sql/bd-tipos-y-modelos"),
                        ("lesson", "sql/sql-modelo-relacional"),
                        ("block", "sql:bd-ud1"),
                    ],
                },
                {
                    "id": "db-tablas-indices",
                    "title": T(
                        "Tablas, restricciones e índices", "Tables, constraints and indexes"
                    ),
                    "links": [
                        ("lesson", "sql/sql-crear-tablas"),
                        ("lesson", "sql/bd-null-indices-dcl"),
                        ("block", "sql:bd-ud2"),
                    ],
                },
                {
                    "id": "db-select",
                    "title": T(
                        "SELECT, WHERE y funciones de agregado",
                        "SELECT, WHERE and aggregate functions",
                    ),
                    "links": [
                        ("lesson", "sql/sql-select"),
                        ("lesson", "sql/sql-where"),
                        ("lesson", "sql/sql-agregados"),
                        ("lesson", "sql/sql-group-by"),
                    ],
                },
                {
                    "id": "db-join-subconsultas",
                    "title": T("JOIN y subconsultas", "JOIN and subqueries"),
                    "links": [
                        ("lesson", "sql/sql-inner-join"),
                        ("lesson", "sql/sql-left-join-subconsultas"),
                        ("block", "sql:bd-ud3"),
                    ],
                },
                {
                    "id": "db-modificar-transacciones",
                    "title": T(
                        "INSERT, UPDATE, DELETE y transacciones",
                        "INSERT, UPDATE, DELETE and transactions",
                    ),
                    "links": [
                        ("lesson", "sql/sql-modificar-datos"),
                        ("lesson", "sql/sql-transacciones-vistas"),
                        ("block", "sql:bd-ampliacion"),
                    ],
                },
                {
                    "id": "db-python",
                    "title": T("Bases de datos desde Python", "Databases from Python"),
                    "links": [("lesson", "programacion/prog-ut8-ficheros-bd")],
                },
                {
                    "id": "db-postgresql-orm",
                    "title": T(
                        "PostgreSQL, SQLAlchemy y migraciones",
                        "PostgreSQL, SQLAlchemy and migrations",
                    ),
                    "links": [],
                },
            ],
            "assessment": None,
            "project": "gestion-clientes",
        },
        {
            "id": "backend",
            "requires": ["professional-python", "databases"],
            "title": T("Backend Development", "Backend Development"),
            "description": T(
                "Construir APIs REST con FastAPI: rutas, validación, autenticación y seguridad.",
                "Build REST APIs with FastAPI: routing, validation, authentication and security.",
            ),
            "objectives": [
                T("Explicar cómo funcionan HTTP y REST", "Explain how HTTP and REST work"),
                T(
                    "Crear una API con FastAPI, Pydantic e inyección de dependencias",
                    "Create an API with FastAPI, Pydantic and dependency injection",
                ),
                T(
                    "Proteger una API con autenticación, autorización y validación",
                    "Protect an API with authentication, authorization and validation",
                ),
            ],
            "skills": ["http-rest", "fastapi", "api-security"],
            "units": [
                {
                    "id": "be-http-json",
                    "title": T("HTTP, REST y JSON", "HTTP, REST and JSON"),
                    "links": [
                        ("lesson", "marcas/mar-json-intercambio"),
                        ("lesson", "js/js-fetch-json"),
                    ],
                },
                {
                    "id": "be-primera-api",
                    "title": T("Primera API web en Python", "A first web API in Python"),
                    "links": [("pcap", "flask")],
                },
                {
                    "id": "be-fastapi-pydantic",
                    "title": T("FastAPI, routing y Pydantic", "FastAPI, routing and Pydantic"),
                    "links": [],
                },
                {
                    "id": "be-dependencias-middleware",
                    "title": T(
                        "Inyección de dependencias y middleware",
                        "Dependency injection and middleware",
                    ),
                    "links": [],
                },
                {
                    "id": "be-auth-jwt",
                    "title": T("Autenticación, JWT y OAuth2", "Authentication, JWT and OAuth2"),
                    "links": [],
                },
                {
                    "id": "be-errores-paginacion",
                    "title": T("Errores, paginación y OpenAPI", "Errors, pagination and OpenAPI"),
                    "links": [],
                },
                {
                    "id": "be-seguridad-apis",
                    "title": T("Seguridad de APIs (OWASP)", "API security (OWASP)"),
                    "links": [],
                },
            ],
            "assessment": None,
            "project": "api-rest",
        },
        {
            "id": "testing",
            "requires": ["backend"],
            "title": T("Software Testing", "Software Testing"),
            "description": T(
                "Comprobar que el código hace lo que debe, y seguir haciéndolo cuando cambia.",
                "Check that code does what it should, and keeps doing so when it changes.",
            ),
            "objectives": [
                T("Depurar un programa con método", "Debug a program methodically"),
                T(
                    "Escribir pruebas unitarias y de integración con pytest",
                    "Write unit and integration tests with pytest",
                ),
                T(
                    "Medir la cobertura y usar análisis estático",
                    "Measure coverage and use static analysis",
                ),
            ],
            "skills": ["debugging", "automated-testing"],
            "units": [
                {
                    "id": "test-depuracion",
                    "title": T("Depuración y trazado", "Debugging and tracing"),
                    "links": [("concept", "depuracion"), ("concept", "trazado")],
                },
                {
                    "id": "test-pytest",
                    "title": T("Pytest y fixtures", "Pytest and fixtures"),
                    "links": [("pcap", "pytest")],
                },
                {
                    "id": "test-mocking-integracion",
                    "title": T("Mocking y pruebas de integración", "Mocking and integration tests"),
                    "links": [],
                },
                {
                    "id": "test-cobertura-estatico",
                    "title": T(
                        "Cobertura, análisis estático y type checking",
                        "Coverage, static analysis and type checking",
                    ),
                    "links": [],
                },
                {
                    "id": "test-refactoring",
                    "title": T(
                        "Refactorizar con red de pruebas", "Refactoring with a safety net of tests"
                    ),
                    "links": [],
                },
            ],
            "assessment": None,
            "project": "bateria-pruebas",
        },
        {
            "id": "frontend",
            "requires": ["fundamentals"],
            "title": T("Frontend Development", "Frontend Development"),
            "description": T(
                "Lo necesario para construir una interfaz web que consuma tu API. React se estudia como contenido, no como cambio de esta plataforma.",
                "Enough to build a web interface that consumes your API. React is studied as content, not as a change to this platform.",
            ),
            "objectives": [
                T(
                    "Maquetar con HTML y CSS accesibles y adaptables",
                    "Build accessible, responsive HTML and CSS",
                ),
                T(
                    "Manipular el DOM y llamar a una API con fetch",
                    "Manipulate the DOM and call an API with fetch",
                ),
                T(
                    "Conocer TypeScript y los componentes de React",
                    "Get to know TypeScript and React components",
                ),
            ],
            "skills": ["html-css", "js-core", "dom-async"],
            "units": [
                {
                    "id": "fe-html-css",
                    "title": T("HTML5 y CSS3", "HTML5 and CSS3"),
                    "links": [
                        ("lesson", "marcas/mar-html-css"),
                        ("resource", "res-mdn-html"),
                        ("resource", "res-mdn-css"),
                    ],
                },
                {
                    "id": "fe-javascript",
                    "title": T(
                        "JavaScript: fundamentos, funciones y datos",
                        "JavaScript: basics, functions and data",
                    ),
                    "links": [
                        ("lesson", "js/js-variables"),
                        ("lesson", "js/js-funciones"),
                        ("lesson", "js/js-arrays"),
                        ("lesson", "js/js-objetos"),
                        ("resource", "res-mdn-js"),
                    ],
                },
                {
                    "id": "fe-dom-eventos",
                    "title": T("DOM y eventos", "DOM and events"),
                    "links": [("lesson", "js/js-dom"), ("lesson", "js/js-eventos")],
                },
                {
                    "id": "fe-async-fetch",
                    "title": T("Async/await y Fetch API", "Async/await and the Fetch API"),
                    "links": [("lesson", "js/js-asincronia"), ("lesson", "js/js-fetch-json")],
                },
                {
                    "id": "fe-modulos-typescript",
                    "title": T("ES Modules y TypeScript", "ES Modules and TypeScript"),
                    "links": [],
                },
                {
                    "id": "fe-react",
                    "title": T("React: componentes y estado", "React: components and state"),
                    "links": [],
                },
                {
                    "id": "fe-responsive-a11y",
                    "title": T(
                        "Diseño adaptable y accesibilidad", "Responsive design and accessibility"
                    ),
                    "links": [],
                },
            ],
            "assessment": None,
            "project": "interfaz-web",
        },
        {
            "id": "devops",
            "requires": ["backend"],
            "title": T("DevOps & Deployment", "DevOps & Deployment"),
            "description": T(
                "Control de versiones, contenedores, integración continua y despliegue.",
                "Version control, containers, continuous integration and deployment.",
            ),
            "objectives": [
                T("Trabajar con ramas y pull requests", "Work with branches and pull requests"),
                T(
                    "Empaquetar una aplicación con Docker y Docker Compose",
                    "Package an application with Docker and Docker Compose",
                ),
                T(
                    "Desplegar con CI/CD gestionando secretos y logs",
                    "Deploy with CI/CD while handling secrets and logs",
                ),
            ],
            "skills": ["dev-lifecycle", "git-github", "docker-ci"],
            "units": [
                {
                    "id": "ops-ciclo-de-vida",
                    "title": T(
                        "Ciclo de vida y metodologías ágiles", "Lifecycle and agile methodologies"
                    ),
                    "links": [
                        ("lesson", "entornos/ent-fases-y-agiles"),
                        ("lesson", "entornos/ent-compilar-e-interpretar"),
                    ],
                },
                {
                    "id": "ops-git-github",
                    "title": T(
                        "Git, GitHub, ramas y pull requests",
                        "Git, GitHub, branches and pull requests",
                    ),
                    "links": [("resource", "res-pro-git")],
                },
                {
                    "id": "ops-docker",
                    "title": T("Docker y Docker Compose", "Docker and Docker Compose"),
                    "links": [("resource", "res-docker-docs")],
                },
                {
                    "id": "ops-ci-cd",
                    "title": T("GitHub Actions y CI/CD", "GitHub Actions and CI/CD"),
                    "links": [],
                },
                {
                    "id": "ops-config-secretos",
                    "title": T(
                        "Variables de entorno y gestión de secretos",
                        "Environment variables and secret management",
                    ),
                    "links": [],
                },
                {
                    "id": "ops-logs-monitorizacion",
                    "title": T("Logs y monitorización", "Logs and monitoring"),
                    "links": [],
                },
            ],
            "assessment": None,
            "project": "despliegue",
        },
        {
            "id": "career",
            "requires": ["testing", "frontend", "devops"],
            "title": T("Career Preparation", "Career Preparation"),
            "description": T(
                "Presentar tu trabajo y prepararte para las entrevistas técnicas.",
                "Present your work and prepare for technical interviews.",
            ),
            "objectives": [
                T(
                    "Tener un perfil de GitHub y un portfolio cuidados",
                    "Have a polished GitHub profile and portfolio",
                ),
                T(
                    "Escribir un CV técnico y documentación clara",
                    "Write a technical CV and clear documentation",
                ),
                T(
                    "Practicar entrevistas de algoritmos, SQL, Python y diseño",
                    "Practise algorithm, SQL, Python and design interviews",
                ),
            ],
            "skills": ["portfolio", "interviews"],
            "units": [
                {
                    "id": "car-github-portfolio",
                    "title": T(
                        "GitHub profesional y portfolio", "Professional GitHub and portfolio"
                    ),
                    "links": [],
                },
                {
                    "id": "car-readme-docs",
                    "title": T(
                        "README y documentación técnica", "README and technical documentation"
                    ),
                    "links": [],
                },
                {
                    "id": "car-cv-linkedin",
                    "title": T("CV técnico y LinkedIn", "Technical CV and LinkedIn"),
                    "links": [],
                },
                {
                    "id": "car-algoritmos",
                    "title": T(
                        "Algoritmos y estructuras de datos", "Algorithms and data structures"
                    ),
                    "links": [
                        ("concept", "algoritmos"),
                        ("concept", "recorridos"),
                        ("lesson", "programacion/prog-ut1-algoritmos"),
                    ],
                },
                {
                    "id": "car-preguntas-sql-python",
                    "title": T(
                        "Preguntas de entrevista de SQL y Python",
                        "SQL and Python interview questions",
                    ),
                    "links": [("block", "sql:bd-ud3")],
                },
                {
                    "id": "car-api-system-design",
                    "title": T(
                        "Diseño de APIs y system design básico",
                        "API design and basic system design",
                    ),
                    "links": [],
                },
                {
                    "id": "car-simulacros",
                    "title": T("Simulaciones de entrevistas", "Mock interviews"),
                    "links": [],
                },
            ],
            "assessment": None,
            "project": "proyecto-final",
        },
    ],
    "projects": [
        {
            "id": "mini-proyecto",
            "phase": "fundamentals",
            "skills": ["py-oop"],
            "title": T("Mini proyecto de consola", "Console mini project"),
            "description": T(
                "Un programa de consola con clases propias (por ejemplo, una agenda o un inventario).",
                "A console program with your own classes (for example, an address book or an inventory).",
            ),
            "criteria": [
                {
                    "id": "clases",
                    "text": T(
                        "Usa al menos dos clases propias, con herencia o composición",
                        "Uses at least two classes of your own, with inheritance or composition",
                    ),
                },
                {
                    "id": "colecciones",
                    "text": T(
                        "Guarda los datos en listas o diccionarios",
                        "Stores data in lists or dictionaries",
                    ),
                },
                {
                    "id": "entrada-validada",
                    "text": T("Valida la entrada del usuario", "Validates user input"),
                },
                {
                    "id": "repositorio",
                    "text": T(
                        "Está en un repositorio público con README",
                        "Is in a public repository with a README",
                    ),
                },
            ],
        },
        {
            "id": "gestor-tareas",
            "phase": "professional-python",
            "skills": ["py-professional", "clean-code"],
            "title": T("Gestor de tareas con persistencia", "Task manager with persistence"),
            "description": T(
                "Aplicación de gestión de tareas que guarda los datos en disco.",
                "A task management application that stores data on disk.",
            ),
            "criteria": [
                {
                    "id": "paquete",
                    "text": T(
                        "Organizado en un paquete con módulos",
                        "Organised as a package with modules",
                    ),
                },
                {
                    "id": "persistencia",
                    "text": T(
                        "Guarda y carga las tareas (JSON o SQLite)",
                        "Saves and loads tasks (JSON or SQLite)",
                    ),
                },
                {
                    "id": "excepciones",
                    "text": T(
                        "Gestiona los errores con excepciones propias",
                        "Handles errors with custom exceptions",
                    ),
                },
                {
                    "id": "typing",
                    "text": T(
                        "Usa anotaciones de tipo y dataclasses", "Uses type hints and dataclasses"
                    ),
                },
                {
                    "id": "venv",
                    "text": T(
                        "Se instala en un entorno virtual con requirements.txt",
                        "Installs in a virtual environment with requirements.txt",
                    ),
                },
            ],
        },
        {
            "id": "gestion-clientes",
            "phase": "databases",
            "skills": ["orm"],
            "title": T(
                "Sistema de gestión de clientes y operaciones",
                "Customer and operations management system",
            ),
            "description": T(
                "Base de datos relacional de clientes y operaciones accesible desde Python.",
                "A relational database of customers and operations accessed from Python.",
            ),
            "criteria": [
                {
                    "id": "modelo",
                    "text": T(
                        "Modelo normalizado con claves foráneas",
                        "Normalised model with foreign keys",
                    ),
                },
                {
                    "id": "consultas",
                    "text": T(
                        "Incluye consultas con JOIN y GROUP BY",
                        "Includes queries with JOIN and GROUP BY",
                    ),
                },
                {
                    "id": "transacciones",
                    "text": T(
                        "Usa transacciones en las operaciones compuestas",
                        "Uses transactions for compound operations",
                    ),
                },
                {
                    "id": "orm-migraciones",
                    "text": T(
                        "Accede con SQLAlchemy y tiene migraciones",
                        "Uses SQLAlchemy and has migrations",
                    ),
                },
            ],
        },
        {
            "id": "api-rest",
            "phase": "backend",
            "skills": ["http-rest", "fastapi", "api-security"],
            "title": T(
                "API REST con usuarios, roles y CRUD", "REST API with users, roles and CRUD"
            ),
            "description": T(
                "API completa con FastAPI y base de datos.",
                "A complete API with FastAPI and a database.",
            ),
            "criteria": [
                {
                    "id": "crud",
                    "text": T(
                        "Operaciones CRUD con validación Pydantic",
                        "CRUD operations with Pydantic validation",
                    ),
                },
                {
                    "id": "auth",
                    "text": T(
                        "Registro e inicio de sesión con contraseñas cifradas y JWT",
                        "Sign-up and login with hashed passwords and JWT",
                    ),
                },
                {
                    "id": "roles",
                    "text": T(
                        "Roles y control de acceso: nadie ve los datos de otro",
                        "Roles and access control: nobody sees another user's data",
                    ),
                },
                {
                    "id": "errores",
                    "text": T(
                        "Errores coherentes y paginación", "Consistent errors and pagination"
                    ),
                },
                {
                    "id": "openapi",
                    "text": T("Documentación OpenAPI revisada", "Reviewed OpenAPI documentation"),
                },
            ],
        },
        {
            "id": "bateria-pruebas",
            "phase": "testing",
            "skills": ["automated-testing"],
            "title": T("Batería de pruebas de la API", "Test suite for the API"),
            "description": T(
                "Pruebas automáticas para la API de la fase anterior.",
                "Automated tests for the API from the previous phase.",
            ),
            "criteria": [
                {
                    "id": "unitarias",
                    "text": T("Pruebas unitarias con fixtures", "Unit tests with fixtures"),
                },
                {
                    "id": "integracion",
                    "text": T(
                        "Pruebas de los endpoints, incluida la autorización",
                        "Endpoint tests, including authorization",
                    ),
                },
                {
                    "id": "mocks",
                    "text": T(
                        "Dependencias externas sustituidas con mocks",
                        "External dependencies replaced with mocks",
                    ),
                },
                {
                    "id": "cobertura",
                    "text": T("Informe de cobertura en la CI", "Coverage report in CI"),
                },
            ],
        },
        {
            "id": "interfaz-web",
            "phase": "frontend",
            "skills": ["dom-async"],
            "title": T("Interfaz web para la API", "Web interface for the API"),
            "description": T(
                "Una interfaz web que consume la API del backend.",
                "A web interface that consumes the backend API.",
            ),
            "criteria": [
                {
                    "id": "fetch",
                    "text": T(
                        "Lee y escribe datos de la API con fetch",
                        "Reads and writes API data with fetch",
                    ),
                },
                {
                    "id": "estados",
                    "text": T(
                        "Muestra estados de carga, error y vacío",
                        "Shows loading, error and empty states",
                    ),
                },
                {"id": "responsive", "text": T("Se usa bien en el móvil", "Works well on mobile")},
                {
                    "id": "accesible",
                    "text": T(
                        "Se maneja con teclado y tiene etiquetas accesibles",
                        "Keyboard-usable with accessible labels",
                    ),
                },
            ],
        },
        {
            "id": "despliegue",
            "phase": "devops",
            "skills": ["git-github", "docker-ci"],
            "title": T("Despliegue completo", "Full deployment"),
            "description": T(
                "Backend, frontend y PostgreSQL desplegados.",
                "Backend, frontend and PostgreSQL deployed.",
            ),
            "criteria": [
                {
                    "id": "ramas-pr",
                    "text": T(
                        "Trabajo en ramas con pull requests", "Work on branches with pull requests"
                    ),
                },
                {
                    "id": "docker",
                    "text": T(
                        "Dockerfile y Docker Compose funcionando",
                        "Working Dockerfile and Docker Compose",
                    ),
                },
                {
                    "id": "ci",
                    "text": T(
                        "CI que ejecuta las pruebas en cada cambio",
                        "CI that runs the tests on every change",
                    ),
                },
                {
                    "id": "secretos",
                    "text": T(
                        "Secretos fuera del repositorio", "Secrets kept out of the repository"
                    ),
                },
                {
                    "id": "publicado",
                    "text": T(
                        "Aplicación publicada y accesible", "Application published and reachable"
                    ),
                },
            ],
        },
        {
            "id": "proyecto-final",
            "phase": "career",
            "skills": ["portfolio", "interviews"],
            "title": T("Proyecto final", "Final project"),
            "description": T(
                "Aplicación completa, publicada, documentada y con pruebas automatizadas.",
                "A complete application, published, documented and with automated tests.",
            ),
            "criteria": [
                {
                    "id": "publicada",
                    "text": T(
                        "Publicada con backend, frontend y base de datos",
                        "Published with backend, frontend and database",
                    ),
                },
                {
                    "id": "pruebas",
                    "text": T("Pruebas automatizadas en la CI", "Automated tests in CI"),
                },
                {
                    "id": "documentacion",
                    "text": T(
                        "README con instalación, arquitectura y capturas",
                        "README with installation, architecture and screenshots",
                    ),
                },
                {
                    "id": "portfolio",
                    "text": T(
                        "Enlazada desde tu portfolio y tu CV", "Linked from your portfolio and CV"
                    ),
                },
                {
                    "id": "explicable",
                    "text": T(
                        "Sabes explicar sus decisiones en una entrevista",
                        "You can explain its design decisions in an interview",
                    ),
                },
            ],
        },
    ],
}

ROADMAPS = [PYTHON_BACKEND_JUNIOR]
