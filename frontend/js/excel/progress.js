/* Cálculos del progreso de Excel profesional, sin DOM (se prueban en tests/unit/excel-progress.test.mjs).

   Una unidad está «superada» (CURRICULUM_M1_M2.md §5) cuando:
   1. todas sus preguntas de test y de resultado están respondidas y al menos el 80 % lo están bien con
      el último intento, y
   2. cada ejercicio de fórmula obligatorio (`pass.required`) se ha resuelto bien alguna vez.
   «Completada» es otra cosa: la marca el alumno con el botón, como en los cursos de DAW. */

export const TEST_KINDS = new Set(["choice", "formula-result"]);
const kindOf = (q) => q.kind ?? "choice";

/** Preguntas del banco de una unidad, en el orden del banco. */
export const unitQuestions = (bank, slug) => bank.questions.filter((q) => q.lesson === slug);

/**
 * Estado de una unidad a partir de las respuestas guardadas ({ id: [true, false…] }).
 * @returns {{ test: {total: number, answered: number, correct: number, rate: number}, required: {total: number, done: number, missing: string[]}, formulas: {total: number, done: number}, passed: boolean }}
 */
export function unitStatus(questions, answers, { test = 0.8, required = [] } = {}) {
  const tests = questions.filter((q) => TEST_KINDS.has(kindOf(q)));
  const answered = tests.filter((q) => answers[q.id]?.length);
  const correct = answered.filter((q) => answers[q.id].at(-1) === true).length;
  const rate = tests.length ? correct / tests.length : 1;
  const everSolved = (id) => (answers[id] ?? []).includes(true);
  const missing = required.filter((id) => !everSolved(id));
  const formulas = questions.filter((q) => kindOf(q) === "formula");
  return {
    test: { total: tests.length, answered: answered.length, correct, rate },
    required: { total: required.length, done: required.length - missing.length, missing },
    formulas: { total: formulas.length, done: formulas.filter((q) => everSolved(q.id)).length },
    passed: answered.length === tests.length && rate >= test && missing.length === 0,
  };
}

/** Resumen del curso: unidades completadas (botón) y superadas (criterios), y ejercicios resueltos. */
export function courseSummary(lessons, bank, progress) {
  let passed = 0;
  let solved = 0;
  for (const lesson of lessons) {
    const status = unitStatus(unitQuestions(bank, lesson.slug), progress.answers ?? {}, lesson.excel?.pass);
    if (status.passed) passed += 1;
  }
  for (const q of bank.questions) if ((progress.answers?.[q.id] ?? []).at(-1) === true) solved += 1;
  const done = lessons.filter((lesson) => progress.done?.[lesson.slug]).length;
  return { units: lessons.length, done, passed, questions: bank.questions.length, solved };
}
