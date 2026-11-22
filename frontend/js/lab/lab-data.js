/* Laboratorio de Python (#/laboratorio): qué ejercicios y ejemplos ofrece. Funciones puras, sin DOM,
   probadas con node --test.

   No hay contenido propio: cada ejercicio es uno que ya existe en el temario, con sus pruebas reales
   (lessons.json: el ejercicio de una lección; learning.json: un ejercicio de código del núcleo por
   conceptos). Si el temario cambia y un id desaparece, la prueba unitaria lo avisa. */

export const LAB_ROUTE = "#/laboratorio";

/** Temas en el orden del curso. `lessons`: lecciones de lessons.json; `exercises`: ids de learning.json. */
export const LAB_TOPICS = Object.freeze([
  { id: "variables", title: "Variables", lessons: ["variables"], exercises: [] },
  { id: "tipos", title: "Tipos de datos", lessons: ["tipos"], exercises: [] },
  { id: "condicionales", title: "Condicionales", lessons: ["condicionales"], exercises: ["con-05"] },
  { id: "bucles", title: "Bucles", lessons: ["bucles"], exercises: ["acu-04", "rec-03"] },
  { id: "funciones", title: "Funciones", lessons: ["funciones"], exercises: ["fun-05"] },
  { id: "listas", title: "Listas", lessons: ["colecciones"], exercises: ["lis-05"] },
  { id: "diccionarios", title: "Diccionarios", lessons: [], exercises: ["dic-04"] },
  { id: "poo", title: "Programación orientada a objetos", lessons: ["poo"], exercises: ["poo-03"] },
]);

/** Ejemplos para cargar en el editor: el código de ejemplo de estas lecciones. */
export const LAB_EXAMPLES = Object.freeze(["variables", "tipos", "condicionales", "bucles", "funciones", "colecciones", "poo"]);

/** Primera línea de un enunciado en Markdown, sin marcas, para usarla como título corto. */
export function shortTitle(markdown, max = 70) {
  const line = String(markdown ?? "").split("\n").find((l) => l.trim()) ?? "";
  // Sin negritas, código ni títulos de Markdown; los «_» se quedan (son parte de nombres como media_positivos)
  const plain = line.replace(/\*\*|[`#>]/g, "").trim();
  return plain.length > max ? `${plain.slice(0, max - 1).trimEnd()}…` : plain;
}

/**
 * Ejercicios del laboratorio con una forma común:
 * { id, topic, source: "lesson" | "learning", ref, title, statement, starter, stdin, checks, hint }
 * @param {{ modules: object[] }} lessonsData contenido de lessons.json
 * @param {{ exercises: object[] }} learningData contenido de learning.json
 */
export function labExercises(lessonsData, learningData) {
  const lessons = new Map(lessonsData.modules.flatMap((m) => m.lessons).map((l) => [l.slug, l]));
  const exercises = new Map(learningData.exercises.map((e) => [e.id, e]));
  const list = [];
  for (const topic of LAB_TOPICS) {
    for (const slug of topic.lessons) {
      const lesson = lessons.get(slug);
      if (!lesson?.checks?.length) continue;
      list.push({
        id: `leccion-${slug}`,
        topic: topic.id,
        source: "lesson",
        ref: slug,
        title: `Lección «${lesson.title}»`,
        statement: lesson.exercise,
        starter: lesson.starter ?? "",
        stdin: lesson.exercise_stdin ?? "",
        checks: lesson.checks,
        hint: null,
      });
    }
    for (const id of topic.exercises) {
      const exercise = exercises.get(id);
      if (exercise?.kind !== "code" || !exercise.checks?.length) continue;
      list.push({
        id: `ejercicio-${id}`,
        topic: topic.id,
        source: "learning",
        ref: id,
        title: shortTitle(exercise.q),
        statement: exercise.q,
        starter: exercise.starter ?? "",
        stdin: exercise.checks[0]?.stdin ?? "",
        checks: exercise.checks,
        hint: exercise.hint ?? null,
      });
    }
  }
  return list;
}

/** Ejemplos { slug, title, code, stdin } de LAB_EXAMPLES que se pueden ejecutar en el navegador. */
export function labExamples(lessonsData) {
  const lessons = new Map(lessonsData.modules.flatMap((m) => m.lessons).map((l) => [l.slug, l]));
  return LAB_EXAMPLES.map((slug) => lessons.get(slug))
    .filter((l) => l?.example_code && l.example_in_browser !== false)
    .map((l) => ({ slug: l.slug, title: l.title, code: l.example_code, stdin: l.example_stdin ?? "" }));
}

/** Ejercicio de una ruta «#/laboratorio/<id>», o null (entonces se abre el primero). */
export function exerciseFromRoute(hash, list) {
  const id = hash.startsWith(`${LAB_ROUTE}/`) ? decodeURIComponent(hash.slice(LAB_ROUTE.length + 1)) : "";
  return list.find((e) => e.id === id) ?? null;
}
