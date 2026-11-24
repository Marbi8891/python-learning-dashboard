/* Centro de aprendizaje (#/cursos): los cursos principales con su progreso y sus lecciones.
   Funciones puras (sin DOM ni almacenamiento), probadas con node --test. Solo lee el progreso que
   ya guarda cada curso; no guarda nada propio. */

export const HUB_ROUTE = "#/cursos";

/**
 * Cursos del centro, en el orden en que se presentan. `source` dice de dónde salen las lecciones:
 * - "concepts": conceptos del núcleo (learning.json); hecho = dominado.
 * - "pcap": lecciones del curso PCAP (lessons.json); hecho = lección completada.
 * - "daw": lecciones de un curso de DAW (data/courses/<id>/lessons.json); hecho = lección completada.
 * - "cyber": semanas del curso de ciberseguridad; hecho = semana completada.
 */
export const HUB_COURSES = Object.freeze([
  { id: "python", source: "concepts", title: "Python", subtitle: "Núcleo por conceptos: de cero a programación orientada a objetos", href: "#/aprender", unit: ["concepto", "conceptos"], doneLabel: "dominados" },
  { id: "pcap", source: "pcap", title: "PCAP", subtitle: "Curso con consola, ejercicio corregido y quiz, y zona de examen", href: "#/inicio", extra: { href: "#/pcap", label: "Zona de examen PCAP" }, unit: ["lección", "lecciones"], doneLabel: "completadas" },
  { id: "programacion", source: "daw", title: "Programación (DAW)", subtitle: "Módulo 0485 en Python · UT1-UT9", href: "#/daw/programacion", unit: ["lección", "lecciones"], doneLabel: "completadas" },
  { id: "js", source: "daw", title: "JavaScript", subtitle: "Entorno cliente · módulo 0612", href: "#/daw/js", unit: ["lección", "lecciones"], doneLabel: "completadas" },
  { id: "java", source: "daw", title: "Java", subtitle: "Java desde cero", href: "#/daw/java", unit: ["lección", "lecciones"], doneLabel: "completadas" },
  { id: "sql", source: "daw", title: "Bases de datos", subtitle: "Módulo 0484 · SQL", href: "#/daw/sql", unit: ["lección", "lecciones"], doneLabel: "completadas" },
  { id: "ciberseguridad", source: "cyber", title: "Ciberseguridad", subtitle: "Itinerario de 16 semanas con laboratorios", href: "#/ciberseguridad", unit: ["semana", "semanas"], doneLabel: "completadas" },
]);

/** Enlace a una lección concreta de cada tipo de curso. */
export function lessonHref(course, slug) {
  const id = encodeURIComponent(slug);
  if (course.source === "concepts") return `#/teoria/${id}`;
  if (course.source === "pcap") return `#/leccion/${id}`;
  if (course.source === "daw") return `#/daw/${course.id}/leccion/${id}`;
  return `#/ciberseguridad/${id}`;
}

/** Lecciones { slug, title } de los datos de cada curso. */
export function lessonsOf(course, data) {
  if (!data) return [];
  if (course.source === "concepts") return (data.concepts ?? []).map((c) => ({ slug: c.id, title: c.title }));
  if (course.source === "cyber") return (data.weeks ?? []).map((w) => ({ slug: w.id, title: `Semana ${w.number}: ${w.title}` }));
  return (data.modules ?? []).flatMap((m) => m.lessons.map((l) => ({ slug: l.slug, title: l.title })));
}

/**
 * Tarjeta de un curso: lecciones con su estado, totales y la siguiente pendiente.
 * Sin lecciones (datos que no han llegado o curso vacío), `available: false`: se muestra «En desarrollo».
 * @param {object} course  @param {{ slug: string, title: string }[]} lessons  @param {(slug: string) => boolean} isDone
 */
export function courseCard(course, lessons, isDone) {
  const items = lessons.map((l) => ({ ...l, done: Boolean(isDone(l.slug)), href: lessonHref(course, l.slug) }));
  const done = items.filter((l) => l.done).length;
  return {
    ...course,
    available: items.length > 0,
    lessons: items,
    total: items.length,
    done,
    percent: items.length ? Math.round((done * 100) / items.length) : 0,
    next: items.find((l) => !l.done) ?? null,
  };
}
