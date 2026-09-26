/* Ficha del curso: estimación de duración y resúmenes que comparten la portada y el perfil. */

const WORDS_PER_MINUTE = 120; // lectura atenta de un texto técnico
const MINUTES = { example: 5, exercise: 8, quiz: 2, perStar: 10 };

/** Minutos estimados de una lección (teoría + ejemplo + ejercicio + quiz), redondeados a 5. */
export function lessonMinutes(lesson) {
  const words = lesson.theory.split(/\s+/).length;
  const minutes = words / WORDS_PER_MINUTE + MINUTES.example + MINUTES.exercise + MINUTES.quiz;
  return Math.max(5, Math.round(minutes / 5) * 5);
}

/** Minutos estimados de un reto opcional según su dificultad. */
const challengeMinutes = (lesson) => lesson.challenge.stars * MINUTES.perStar;

/** "3 h 45 min", "50 min"... */
export function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  if (!hours) return `${rest} min`;
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}

/** Totales del curso para la ficha: lecciones, horas, preguntas y retos. */
export function courseTotals(content) {
  const lessons = [...content.lessons.values()];
  return {
    lessons: lessons.length,
    minutes: lessons.reduce((sum, l) => sum + lessonMinutes(l), 0),
    challengeMinutes: lessons.reduce((sum, l) => sum + challengeMinutes(l), 0),
    questions: lessons.reduce((sum, l) => sum + l.quiz.length, 0),
    challenges: lessons.length,
  };
}

/** Estrellas en texto accesible: "★★☆" + "2 de 3 estrellas". */
export function stars(count, max = 3) {
  return {
    visual: "★".repeat(count) + "☆".repeat(max - count),
    label: `dificultad ${count} de ${max}`,
  };
}
