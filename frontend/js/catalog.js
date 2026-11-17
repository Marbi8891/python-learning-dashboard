/* Catálogo de cursos que guardan su progreso como documento de curso
   (pld:course:<id> en el navegador y /api/course-state/<id> en la cuenta).

   Cada curso pertenece a una familia:
   - "daw": cursos de los módulos oficiales del ciclo DAW. Tienen `module` (código oficial), salen en
     #/daw/cursos, en el panel por módulo y en los certificados de DAW.
   - "academia": itinerarios profesionales que no son módulos de DAW (Excel profesional). No tienen
     `module` ni currículo oficial y tendrán su propia ruta (#/academia/<id>).

   El PCAP no está aquí: tiene su propio almacén (pcap-store.js, /api/pcap-state).
   Todo id de SYNCED_COURSES tiene que estar en COURSES de backend/app/schemas.py; lo comprueba
   backend/tests/test_course_catalog.py. */

/** Cursos de DAW, en el orden del catálogo. `lang` es el lenguaje para resaltar el código y
    `module`, el código del módulo oficial que trabaja (sus recursos salen de data/resources.json).
    `structure` dice de dónde sale el orden de las unidades (Fase D, 6.1): los textos, ejemplos y
    preguntas son siempre propios de la plataforma (ver daw.js, «De dónde sale este contenido»). */
export const DAW_COURSES = [
  {
    id: "programacion", module: "0485", title: "Programación", subtitle: "Módulo 0485 en Python · UT1-UT9", lang: "python",
    structure: "Sigue el orden y los contenidos de las UT1-UT9 del curso «DAW-Programacion» de César San Juan Pastor (IES Arcipreste de Hita, licencia CC BY-NC), sin copiar su texto.",
  },
  {
    id: "sql", module: "0484", title: "Bases de datos", subtitle: "Módulo 0484 · SQL · UD1-UD3 del centro", lang: "sql",
    structure: "Sigue el orden de las UD1-UD3 del temario del centro, con un bloque de ampliación propio.",
  },
  {
    id: "entornos", module: "0487", title: "Entornos de desarrollo", subtitle: "Módulo 0487 · UD1 del centro", lang: "python",
    structure: "Sigue el orden de la UD1 «Desarrollo de software» del temario del centro.",
  },
  {
    id: "marcas", module: "0373", title: "Lenguajes de marcas", subtitle: "Módulo 0373 · XML, HTML, JSON y XPath", lang: "python",
    structure: "Las unidades se organizan por los resultados de aprendizaje del Real Decreto 405/2023. Los objetivos de cada lección los resumen con palabras propias y citan el RA y sus criterios.",
  },
  {
    id: "js", module: "0612", title: "JavaScript", subtitle: "Entorno cliente", lang: "javascript",
    structure: "Selección propia de la plataforma para el módulo 0612; no sigue ningún temario.",
  },
  {
    id: "java", module: "0485", title: "Java", subtitle: "Para más adelante: Java desde cero", lang: "java",
    structure: "Curso propio de la plataforma para practicar Java; no sigue ningún temario.",
  },
];

/** Itinerarios de la familia «academia». `status: "active"`: con contenido, ruta y entrada en el menú
    (Excel profesional desde la fase P2: M01 y M02; el resto del itinerario sale como «Próximamente»). */
export const ACADEMY_COURSES = [
  {
    id: "excel", family: "academia", title: "Excel profesional", subtitle: "Excel de Microsoft 365 en español",
    lang: "excel", route: "#/academia/excel", hours: 120, status: "active",
    structure: "Itinerario propio de la plataforma. No sigue ningún temario oficial ni de Microsoft.",
  },
];

/** Nombre visible de cada familia. Las fichas de DAW no llevan `family` para no cambiar su forma:
    su familia es «daw» por estar en DAW_COURSES. */
export const COURSE_FAMILIES = Object.freeze({ daw: "Cursos de DAW", academia: "Academia" });

/** Todos los cursos con documento de curso, en orden: primero los de DAW y después las academias. */
export const SYNCED_COURSES = [...DAW_COURSES, ...ACADEMY_COURSES];

/** Familia de un curso del catálogo, o null si no está. */
export const familyOf = (id) =>
  DAW_COURSES.some((course) => course.id === id) ? "daw" : ACADEMY_COURSES.find((course) => course.id === id)?.family ?? null;
