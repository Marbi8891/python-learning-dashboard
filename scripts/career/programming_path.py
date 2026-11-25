# ruff: noqa: E501
"""Programming Path: currículo secuenciado que reutiliza PLD y enlaza fuentes fiables."""
ID = "programming-path"
VERSION = 1
TITLE = {"es": "Programming Path · De 0 a Experto", "en": "Programming Path · Zero to Expert"}
SPECIALIZATION = {"es": "Ruta progresiva de fundamentos, desarrollo, ingeniería de software y especialización. Las lecciones existentes se reutilizan; las brechas se identifican sin duplicar contenido.", "en": "Progressive path from fundamentals to software engineering and specialization. Existing lessons are reused; gaps are identified without duplicating content."}
LEVELS = [
 {"id":"fundamentos","title":{"es":"Fundamentos","en":"Fundamentals"}},
 {"id":"intermedio","title":{"es":"Intermedio","en":"Intermediate"}},
 {"id":"avanzado","title":{"es":"Avanzado","en":"Advanced"}},
 {"id":"profesional","title":{"es":"Profesional","en":"Professional"}},
]
CATEGORIES = {
 "programming":{"es":"Programación","en":"Programming"},
 "web":{"es":"Desarrollo web","en":"Web development"},
 "databases":{"es":"Bases de datos","en":"Databases"},
 "backend":{"es":"Backend","en":"Backend"},
 "engineering":{"es":"Ingeniería de software","en":"Software engineering"},
 "devops":{"es":"DevOps e infraestructura","en":"DevOps and infrastructure"},
 "ai-ml":{"es":"IA y Machine Learning","en":"AI and Machine Learning"},
 "security":{"es":"Seguridad","en":"Security"},
 "professional":{"es":"Especialización","en":"Specialization"},
}
SALARY_SOURCE={"es":"No se incluyen estimaciones salariales en este itinerario.","en":"No salary estimates are included in this roadmap."}
SALARY_BANDS=[]
DEFAULT_TARGET=None
STAGES=[
 {"id":"s1","months":3,"modules":["m1","m2"],"title":{"es":"Bases de informática y programación","en":"Computer science and programming fundamentals"}},
 {"id":"s2","months":4,"modules":["m3","m4"],"title":{"es":"Python y herramientas de desarrollo","en":"Python and developer tools"}},
 {"id":"s3","months":4,"modules":["m5","m6"],"title":{"es":"Algoritmos, estructuras de datos y web","en":"Algorithms, data structures and web"}},
 {"id":"s4","months":4,"modules":["m7","m8"],"title":{"es":"Frontend y bases de datos","en":"Frontend and databases"}},
 {"id":"s5","months":4,"modules":["m9","m10"],"title":{"es":"Backend y calidad de software","en":"Backend and software quality"}},
 {"id":"s6","months":4,"modules":["m11","m12"],"title":{"es":"Java, arquitectura y sistemas","en":"Java, architecture and systems"}},
 {"id":"s7","months":4,"modules":["m13","m14"],"title":{"es":"DevOps, cloud y seguridad","en":"DevOps, cloud and security"}},
 {"id":"s8","months":4,"modules":["m15","m16"],"title":{"es":"IA aplicada y especialización","en":"Applied AI and specialization"}},
 {"id":"s9","months":3,"modules":["m17"],"title":{"es":"Nivel experto y proyecto final","en":"Expert level and capstone"}},
]
def skill(id_,cat,es,en,links,assessment):
 sources={"concepts":[],"blocks":[],"assessments":[assessment],"criteria":[],"checklists":[]}
 for kind,ref in links:
  if kind=="concept": sources["concepts"].append(ref)
  elif kind=="block": sources["blocks"].append(ref)
 return {"id":id_,"category":cat,"title":{"es":es,"en":en},"sources":sources}
def unit(id_,level,es,en,objectives,skill_id,links=()):
 return {"id":id_,"level":level,"title":{"es":es,"en":en},"objectives":objectives,"skills":[skill_id],"links":[{"kind":k,"id":v} for k,v in links],"pending":not bool(links)}
def module(mid,requires,es,en,summary,units):
 return {"id":mid,"requires":requires,"title":{"es":es,"en":en},"summary":{"es":summary,"en":summary},"units":units,"assessment":{"id":mid,"pass":0.7,"bank":None},"project":{"criteria":[],"checklists":[]}}
# Data is deliberately a navigation layer: unit references point to existing PLD lessons/blocks or vetted sources.
MODULES=[]
SKILLS=[]
def add_module(mid,requires,cat,title_es,title_en,summary_es,unit_specs):
 us=[]
 for uid,level,ues,uen,obj,links in unit_specs:
  sid=f"pp-{mid}-{uid.split('.')[-1]}"
  us.append(unit(uid,level,ues,uen,obj,sid,links))
  SKILLS.append(skill(sid,cat,ues,uen,links,mid))
 MODULES.append(module(mid,requires,title_es,title_en,summary_es,us))
add_module("m1",[], "programming","Fundamentos de informática","Computer science fundamentals","Pensamiento computacional, algoritmos y funcionamiento básico de los sistemas.",[
 ("m1.cs","fundamentos","Cómo funciona un ordenador y cómo se programa","How computers and programs work",["Explicar hardware, software, sistemas operativos y proceso de ejecución","Descomponer problemas y describir soluciones paso a paso"],[("resource","res-harvard-cs50x"),("block","entornos:ent-lenguajes")]),
 ("m1.alg","fundamentos","Algoritmos, pseudocódigo y trazado","Algorithms, pseudocode and tracing",["Representar algoritmos con pseudocódigo y diagramas","Trazar variables y detectar errores de lógica"],[("concept","algoritmos"),("concept","pseudocodigo"),("concept","trazado"),("block","programacion:prog-ut1")]),
 ("m1.logic","fundamentos","Lógica, condiciones y ciclos","Logic, conditions and loops",["Construir condiciones y bucles correctos","Usar tablas de verdad y casos de prueba simples"],[("concept","condicionales"),("concept","bucles"),("block","programacion:prog-ut3")]),
])
add_module("m2",["m1"],"programming","Pensamiento computacional y resolución de problemas","Computational thinking and problem solving","Practicar resolución de problemas antes de elegir un lenguaje.",[
 ("m2.decompose","fundamentos","Descomposición y abstracción","Decomposition and abstraction",["Dividir un problema en tareas pequeñas","Identificar datos, entradas, salidas y restricciones"],[("resource","res-harvard-cs50x")]),
 ("m2.trace","fundamentos","Pruebas manuales y depuración lógica","Manual testing and logical debugging",["Probar casos normales, extremos e inválidos","Explicar por qué falla una solución"],[("concept","depuracion"),("concept","validacion")]),
 ("m2.complexity","intermedio","Coste temporal y espacial","Time and space complexity",["Comparar soluciones por coste","Reconocer crecimiento lineal, cuadrático y logarítmico"],[("resource","res-mit-algorithms"),("resource","res-princeton-algorithms")]),
])
add_module("m3",["m2"],"programming","Python desde cero","Python from zero","Reutiliza el curso Python de PLD y añade referencias universitarias.",[
 ("m3.syntax","fundamentos","Variables, tipos y operadores","Variables, types and operators",["Declarar variables y elegir tipos","Operar y convertir valores"],[("concept","variables"),("concept","tipos"),("concept","operadores"),("block","programacion:prog-ut2"),("resource","res-python-tutorial")]),
 ("m3.io","fundamentos","Entrada, salida y validación","Input, output and validation",["Leer entradas y mostrar resultados","Validar datos y manejar valores inválidos"],[("concept","entrada-salida"),("concept","validacion"),("block","programacion:prog-ut2")]),
 ("m3.control","fundamentos","Condiciones y bucles","Conditionals and loops",["Elegir estructuras de control","Evitar bucles infinitos y errores de límite"],[("concept","condicionales"),("concept","bucles"),("block","programacion:prog-ut3")]),
 ("m3.functions","fundamentos","Funciones y modularidad","Functions and modularity",["Definir funciones con parámetros y retorno","Separar responsabilidades y reutilizar código"],[("concept","funciones"),("block","programacion:prog-ut3")]),
 ("m3.collections","intermedio","Strings y colecciones","Strings and collections",["Manipular cadenas, listas, tuplas, sets y diccionarios","Recorrer colecciones y elegir estructuras"],[("concept","strings"),("concept","listas"),("concept","tuplas-conjuntos"),("concept","diccionarios"),("block","programacion:prog-ut6")]),
 ("m3.errors","intermedio","Excepciones, módulos y archivos","Exceptions, modules and files",["Gestionar excepciones y crear módulos","Leer y escribir archivos con seguridad"],[("concept","excepciones"),("concept","modulos"),("concept","archivos"),("block","programacion:prog-ut5"),("block","programacion:prog-ut8")]),
])
add_module("m4",["m3"],"programming","Python intermedio y profesional","Intermediate and professional Python","Reutiliza OOP, colecciones y proyecto Python existentes; profundiza con fuentes oficiales.",[
 ("m4.oop","intermedio","Clases, encapsulación y composición","Classes, encapsulation and composition",["Modelar objetos y responsabilidades","Preferir composición cuando sea adecuada"],[("concept","poo"),("block","programacion:prog-ut4"),("block","programacion:prog-ut5")]),
 ("m4.inherit","intermedio","Herencia y polimorfismo","Inheritance and polymorphism",["Aplicar herencia y polimorfismo con criterio","Evitar jerarquías innecesarias"],[("concept","poo-herencia"),("concept","poo-polimorfismo"),("block","programacion:prog-ut6")]),
 ("m4.typing","avanzado","Tipado, generadores y decoradores","Typing, generators and decorators",["Añadir anotaciones de tipos","Crear generadores y comprender decoradores"],[("resource","res-python-tutorial"),("resource","res-harvard-cs50p"),("resource","res-python-typing"),("resource","res-python-asyncio"),("resource","res-python-packaging")]),
 ("m4.testing","intermedio","Testing y debugging","Testing and debugging",["Diseñar pruebas unitarias y casos límite","Usar debugging para localizar fallos"],[("resource","res-pytest-docs"),("resource","res-harvard-cs50p"),("resource","res-python-testing"),("resource","res-hypothesis")]),
 ("m4.project","intermedio","Proyecto Python existente: códigos secretos","Existing Python project: secret codes",["Completar y revisar el proyecto ya incluido en PLD","Documentar decisiones y pruebas"],[("block","programacion:prog-ut7")]),
])
add_module("m5",["m4"],"engineering","Herramientas de desarrollo","Developer tooling","Terminal, Git, entornos, debugging y workflow profesional.",[
 ("m5.shell","fundamentos","Terminal y shell","Terminal and shell",["Navegar archivos, pipes, redirecciones y permisos","Automatizar tareas básicas desde terminal"],[("resource","res-mit-missing-semester"),("resource","res-linux-manpages")]),
 ("m5.git","fundamentos","Git y GitHub","Git and GitHub",["Trabajar con commits, ramas, merge y pull requests","Resolver conflictos y revisar diffs"],[("resource","res-pro-git"),("resource","res-mit-missing-semester")]),
 ("m5.env","intermedio","Entornos, dependencias y paquetes","Environments, dependencies and packages",["Usar entornos virtuales y gestores de dependencias","Documentar instalaciones reproducibles"],[("block","entornos:ent-traduccion"),("block","entornos:ent-ciclo-de-vida")]),
 ("m5.debug","intermedio","Debugging, logs y profiling","Debugging, logs and profiling",["Inspeccionar errores y stack traces","Medir antes de optimizar"],[("resource","res-mit-missing-semester")]),
])
add_module("m6",["m5"],"programming","Algoritmos y estructuras de datos","Algorithms and data structures","Profundización: algunas brechas se desarrollarán en PLD; referencias MIT y CS50.",[
 ("m6.array","intermedio","Arrays, listas, stacks, queues y linked lists","Arrays, lists, stacks, queues and linked lists",["Explicar operaciones y coste de estructuras","Implementar estructuras básicas"],[("resource","res-mit-algorithms"),("resource","res-harvard-cs50x")]),
 ("m6.tree","avanzado","Árboles, heaps, hash tables y grafos","Trees, heaps, hash tables and graphs",["Recorrer árboles y grafos","Elegir estructura según problema"],[("resource","res-mit-algorithms")]),
 ("m6.sort","intermedio","Búsqueda, ordenación y recursividad","Search, sorting and recursion",["Implementar búsqueda binaria y ordenación","Analizar recursividad y complejidad"],[("resource","res-mit-algorithms")]),
 ("m6.pattern","avanzado","Patrones de resolución y práctica de problemas","Problem-solving patterns and practice",["Resolver problemas con dos punteros, ventanas y BFS/DFS","Explicar la complejidad de la solución"],[("resource","res-harvard-cs50x"),("resource","res-mit-algorithms")]),
])
add_module("m7",["m6"],"web","Fundamentos web: HTML, CSS y JavaScript","Web foundations: HTML, CSS and JavaScript","Reutiliza el curso de Lenguajes de Marcas y JavaScript de PLD.",[
 ("m7.html","fundamentos","HTML semántico y accesibilidad","Semantic HTML and accessibility",["Construir documentos semánticos","Aplicar etiquetas, formularios y accesibilidad básica"],[("block","marcas:mar-html"),("resource","res-mdn-html")]),
 ("m7.css","fundamentos","CSS, layout y responsive","CSS, layout and responsive design",["Usar cascada, especificidad, Flexbox y Grid","Diseñar para móvil y escritorio"],[("block","marcas:mar-html"),("resource","res-mdn-css")]),
 ("m7.js","fundamentos","JavaScript, DOM y eventos","JavaScript, DOM and events",["Manipular DOM y escuchar eventos","Usar funciones, arrays y objetos"],[("block","js:js-fundamentos"),("block","js:js-funciones"),("block","js:js-dom")]),
 ("m7.async","intermedio","Asincronía, fetch y JSON","Asynchrony, fetch and JSON",["Usar promesas y async/await","Consumir APIs y manejar errores"],[("block","js:js-asincronia"),("block","marcas:mar-json"),("resource","res-mdn-js")]),
])
add_module("m8",["m7"],"web","Frontend moderno","Modern frontend","La base JavaScript existente se amplía con TypeScript y React, sin crear duplicados.",[
 ("m8.ts","intermedio","TypeScript y tipado estático","TypeScript and static typing",["Añadir tipos, interfaces y generics","Reducir errores en aplicaciones JS"],[("resource","res-typescript-handbook")]),
 ("m8.react","intermedio","React: componentes, props y estado","React: components, props and state",["Crear componentes reutilizables","Gestionar estado, formularios y efectos"],[("resource","res-react-learn"),("resource","res-fullstackopen")]),
 ("m8.frontarch","avanzado","Arquitectura frontend y gestión de estado","Frontend architecture and state management",["Separar UI, lógica y servicios","Gestionar navegación, estado y errores"],[("resource","res-fullstackopen"),("resource","res-webdev-performance"),("resource","res-w3c-wai-tutorials")]),
 ("m8.quality","avanzado","Accesibilidad, rendimiento y testing frontend","Accessibility, performance and frontend testing",["Auditar accesibilidad y rendimiento","Probar componentes e interacciones"],[("resource","res-mdn-html"),("resource","res-fullstackopen")]),
])
add_module("m9",["m8"],"databases","Bases de datos y SQL","Databases and SQL","Reutiliza las unidades de SQL de PLD; complementa con PostgreSQL y cursos universitarios.",[
 ("m9.model","fundamentos","Modelado relacional y normalización","Relational modelling and normalization",["Diseñar entidades, claves y relaciones","Normalizar un esquema"],[("block","sql:bd-ud2"),("resource","res-harvard-cs50sql")]),
 ("m9.query","fundamentos","SQL: consultas, JOIN y agregados","SQL: queries, joins and aggregates",["Consultar, agrupar y combinar datos","Escribir subconsultas"],[("block","sql:bd-ud3"),("resource","res-harvard-cs50sql")]),
 ("m9.tx","intermedio","Transacciones, índices y rendimiento","Transactions, indexes and performance",["Comprender ACID y transacciones","Usar índices y analizar consultas"],[("block","sql:bd-ampliacion"),("resource","res-postgresql-docs"),("resource","res-cmu-db")]),
 ("m9.nosql","avanzado","NoSQL y almacenamiento especializado","NoSQL and specialized storage",["Comparar relacional, documento y clave-valor","Elegir almacenamiento según requisitos"],[("resource","res-cmu-db"),("resource","res-mongodb-docs")]),
])
add_module("m10",["m9"],"backend","Backend y APIs","Backend and APIs","Brechas de backend con fuentes oficiales; conecta con el curso Python y el roadmap AI Engineer ya existente.",[
 ("m10.http","fundamentos","HTTP, REST y diseño de API","HTTP, REST and API design",["Diseñar recursos, métodos y códigos de estado","Documentar contratos de API"],[("resource","res-mdn-http"),("resource","res-harvard-cs50web")]),
 ("m10.fastapi","intermedio","FastAPI y Pydantic","FastAPI and Pydantic",["Crear endpoints y validar datos","Organizar dependencias y esquemas"],[("resource","res-fastapi-tutorial")]),
 ("m10.auth","avanzado","Autenticación, autorización y seguridad API","Authentication, authorization and API security",["Implementar autenticación y autorización","Evitar exposición de secretos y datos"],[("resource","res-owasp-cheatsheets"),("resource","res-fastapi-tutorial")]),
 ("m10.data","intermedio","ORM, migraciones y persistencia","ORM, migrations and persistence",["Separar acceso a datos y lógica","Gestionar migraciones"],[("resource","res-postgresql-docs"),("resource","res-fastapi-tutorial")]),
 ("m10.api-tests","avanzado","Testing de APIs y contratos","API and contract testing",["Probar respuestas, errores y permisos","Automatizar pruebas de integración"],[("resource","res-pytest-docs"),("resource","res-fastapi-tutorial")]),
])
add_module("m11",["m10"],"engineering","Ingeniería de software","Software engineering","Principios, arquitectura, revisión, testing y diseño mantenible.",[
 ("m11.clean","intermedio","Clean code, SOLID y refactorización","Clean code, SOLID and refactoring",["Aplicar principios sin sobreingeniería","Refactorizar manteniendo pruebas"],[("resource","res-harvard-cs50web")]),
 ("m11.patterns","avanzado","Patrones de diseño y arquitectura","Design patterns and architecture",["Reconocer patrones y sus trade-offs","Separar responsabilidades y dependencias"],[("resource","res-harvard-cs50web")]),
 ("m11.testing","avanzado","Testing unitario, integración y E2E","Unit, integration and E2E testing",["Definir estrategia de pruebas","Automatizar tests en CI"],[("resource","res-pytest-docs"),("resource","res-fullstackopen")]),
 ("m11.docs","intermedio","Documentación técnica y code review","Technical documentation and code review",["Escribir READMEs y decisiones técnicas","Revisar código con criterios verificables"],[("resource","res-pro-git")]),
])
add_module("m12",["m11"],"programming","Java y programación empresarial","Java and enterprise programming","Reutiliza el curso Java de PLD; complementa con Dev.java y Spring.",[
 ("m12.java","fundamentos","Java: sintaxis, tipos y control","Java: syntax, types and control",["Comprender tipos estáticos y control de flujo","Escribir programas Java"],[("block","java:java-basico"),("block","java:java-control"),("resource","res-dev-java")]),
 ("m12.oop","intermedio","Java OOP, interfaces y colecciones","Java OOP, interfaces and collections",["Aplicar interfaces, herencia y polimorfismo","Usar colecciones y genéricos"],[("block","java:java-poo"),("block","java:java-herencia"),("block","java:java-colecciones")]),
 ("m12.spring","avanzado","Spring Boot y servicios empresariales","Spring Boot and enterprise services",["Crear una API con Spring","Integrar persistencia y validación"],[("resource","res-spring-guides")]),
])
add_module("m13",["m12"],"devops","Linux, redes y sistemas","Linux, networking and systems","Conocimientos de sistemas que permiten diagnosticar y desplegar aplicaciones.",[
 ("m13.linux","fundamentos","Linux, permisos y procesos","Linux, permissions and processes",["Administrar procesos, permisos y servicios","Usar comandos de diagnóstico"],[("resource","res-linux-manpages"),("resource","res-mit-missing-semester")]),
 ("m13.network","intermedio","Redes, DNS, TCP y TLS","Networking, DNS, TCP and TLS",["Explicar DNS, TCP, TLS y HTTP","Diagnosticar conectividad"],[("resource","res-mdn-http"),("resource","res-harvard-cs50x")]),
 ("m13.concurrent","avanzado","Concurrencia, paralelismo y sistemas","Concurrency, parallelism and systems",["Distinguir procesos, threads y async","Reconocer condiciones de carrera"],[("resource","res-mit-algorithms")]),
])
add_module("m14",["m13"],"devops","DevOps, CI/CD y cloud","DevOps, CI/CD and cloud","Contenedores, automatización, despliegue y operación.",[
 ("m14.docker","intermedio","Docker e imágenes","Docker and images",["Crear imágenes y contenedores reproducibles","Configurar redes y volúmenes"],[("resource","res-docker-docs")]),
 ("m14.compose","intermedio","Docker Compose y entornos","Docker Compose and environments",["Orquestar servicios locales","Gestionar variables y persistencia"],[("resource","res-docker-docs")]),
 ("m14.cicd","avanzado","CI/CD y automatización de despliegues","CI/CD and deployment automation",["Crear pipelines de test y build","Automatizar despliegues con control"],[("resource","res-fullstackopen"),("resource","res-github-actions"),("resource","res-12factor")]),
 ("m14.cloud","avanzado","Cloud y arquitectura distribuida","Cloud and distributed architecture",["Comprender compute, storage, redes y observabilidad","Diseñar una arquitectura escalable"],[("resource","res-kubernetes-docs"),("resource","res-azure-fundamentals"),("resource","res-cncft-cloud-native")]),
 ("m14.k8s","profesional","Kubernetes","Kubernetes",["Comprender deployments, services y configuración","Desplegar una aplicación en un clúster de prácticas"],[("resource","res-kubernetes-docs")]),
])
add_module("m15",["m14"],"security","Seguridad en el desarrollo","Secure software development","Seguridad desde el diseño, revisión y protección de aplicaciones.",[
 ("m15.owasp","intermedio","OWASP Top 10 y amenazas web","OWASP Top 10 and web threats",["Reconocer riesgos web comunes","Relacionar amenazas con controles"],[("resource","res-owasp-top10")]),
 ("m15.secure","avanzado","Secure coding y gestión de secretos","Secure coding and secrets management",["Validar entradas y controlar permisos","Proteger secretos, sesiones y datos"],[("resource","res-owasp-cheatsheets"),("resource","res-owasp-api-top10")]),
 ("m15.devsecops","profesional","DevSecOps y análisis de dependencias","DevSecOps and dependency analysis",["Integrar controles en CI","Revisar dependencias y artefactos"],[("resource","res-owasp-cheatsheets")]),
])
add_module("m16",["m15"],"ai-ml","IA y Machine Learning aplicado","Applied AI and machine learning","Enlaza las fuentes y el roadmap Applied AI Engineer de PLD, evitando duplicar su currículo.",[
 ("m16.ml","avanzado","Fundamentos de Machine Learning","Machine learning fundamentals",["Comprender train, validation, test y métricas","Aplicar un modelo supervisado básico"],[("resource","res-pytorch-tutorials"),("resource","res-huggingface-learn"),("resource","res-google-mlcc")]),
 ("m16.deep","avanzado","Deep learning y Transformers","Deep learning and Transformers",["Comprender redes neuronales y Transformers","Usar modelos preentrenados"],[("resource","res-pytorch-tutorials"),("resource","res-huggingface-learn")]),
 ("m16.llm","profesional","LLM Engineering, RAG y evaluación","LLM engineering, RAG and evaluation",["Construir un prototipo RAG","Evaluar calidad, seguridad y coste"],[("resource","res-huggingface-learn")]),
 ("m16.agents","profesional","Agentes, herramientas y supervisión humana","Agents, tools and human oversight",["Diseñar herramientas con permisos mínimos","Añadir evaluación y supervisión"],[("resource","res-huggingface-learn")]),
])
add_module("m17",["m16"],"professional","Especialización y nivel experto","Specialization and expert level","Rutas opcionales de profundización y proyecto integrador con evidencias.",[
 ("m17.system","profesional","System design, escalabilidad y fiabilidad","System design, scalability and reliability",["Diseñar sistemas con trade-offs","Analizar escalabilidad, resiliencia y observabilidad"],[("resource","res-cmu-db"),("resource","res-kubernetes-docs"),("resource","res-google-sre")]),
 ("m17.special","profesional","Elegir especialización","Choose a specialization",["Definir un área y objetivos medibles","Crear un plan de estudio basado en fuentes primarias"],[("resource","res-webdev-roadmap")]),
 ("m17.capstone","profesional","Proyecto final y portfolio","Capstone and portfolio",["Construir una aplicación completa con tests y despliegue","Documentar arquitectura, decisiones, límites y demo"],[("resource","res-fullstackopen"),("resource","res-harvard-cs50web")]),
])
PROJECTS=[]
CHECKLISTS={}
ROLES=[]
