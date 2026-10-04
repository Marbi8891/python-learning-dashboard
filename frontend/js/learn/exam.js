/* Preparación DAW (ADR-0031, fase 2): competencias, avisos de qué reforzar y composición de
   simulacros. Funciones puras, probadas con node --test. */

import { allStats } from "./mastery.js";
import { READY_SCORE } from "./recommend.js";

/** Minutos de un simulacro: 3 por pregunta corta y 10 por problema de escribir código. */
export const examMinutes = (exercises) => exercises.reduce((sum, e) => sum + (e.kind === "code" ? 10 : 3), 0);

/**
 * Estado de cada competencia: dominio medio ponderado por la importancia para DAW de sus conceptos,
 * conceptos dominados y los más flojos.
 */
export function competencyStats(index, stats = null, state = null) {
  const all = stats ?? allStats(index, state);
  return index.data.daw.map((competency) => {
    const list = competency.concepts.map((id) => all.get(id));
    const weights = competency.concepts.map((id) => index.concepts.get(id).daw);
    const total = weights.reduce((a, b) => a + b, 0);
    const score = list.reduce((sum, s, i) => sum + s.score * weights[i], 0) / total;
    const weakest = list
      .filter((s) => s.status !== "dominado")
      .sort((a, b) => a.score - b.score || index.path.indexOf(a.id) - index.path.indexOf(b.id))
      .slice(0, 2)
      .map((s) => s.id);
    return {
      ...competency,
      score,
      mastered: list.filter((s) => s.status === "dominado").length,
      started: list.some((s) => s.attempted > 0),
      weakest,
    };
  });
}

/**
 * Avisos «Necesitas reforzar X antes de pasar a Y» entre competencias (`requires` en learning.json):
 * Programación y Lógica se apoyan en Fundamentos. Se avisa cuando la competencia base ya se ha
 * empezado, está por debajo de READY_SCORE y la que depende de ella aún no está superada.
 */
export function competencyAdvice(index, competencies) {
  const byId = new Map(competencies.map((c) => [c.id, c]));
  const advice = [];
  for (const current of competencies) {
    if (current.score >= READY_SCORE) continue;
    for (const required of (current.requires ?? []).map((id) => byId.get(id))) {
      if (!required.started || required.score >= READY_SCORE || required.weakest.length === 0) continue;
      const names = required.weakest.map((id) => index.concepts.get(id).title).join(" y ");
      advice.push({ before: current.id, concepts: required.weakest, text: `Necesitas reforzar ${names} antes de pasar a ${current.title}.` });
    }
  }
  return advice;
}

/** Preparación estimada (0-1): dominio de cada competencia ponderado por su peso en el simulacro. Orientativa. */
export const examReadiness = (competencies) => competencies.reduce((sum, c) => sum + c.score * c.weight, 0) / 100;

function shuffle(list, random) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

/**
 * Compone un simulacro con ejercicios de formato de examen (`daw: true`):
 * - reparto por competencias según su peso;
 * - entre 1 y 2 problemas de escribir código (son los que más tiempo llevan);
 * - `scope: "studied"` solo usa conceptos empezados o leídos; `"all"`, todo el temario.
 * Devuelve los ejercicios ordenados de más sencillo a más completo, como un examen.
 */
export function buildExam(index, state, { scope = "studied", size = 12, random = Math.random, maxCode = 2 } = {}) {
  const stats = allStats(index, state);
  const allowed = new Set(
    index.path.filter((id) => scope === "all" || stats.get(id).attempted > 0 || stats.get(id).status === "leido"),
  );
  const chosen = [];
  const used = new Set();
  let code = 0;
  const take = (exercise) => {
    if (used.has(exercise.id) || (exercise.kind === "code" && code >= maxCode)) return false;
    used.add(exercise.id);
    chosen.push(exercise);
    if (exercise.kind === "code") code += 1;
    return true;
  };
  const poolOf = (competency) =>
    shuffle(
      competency.concepts.filter((id) => allowed.has(id)).flatMap((id) => index.byConcept.get(id).filter((e) => e.daw)),
      random,
    );

  // Un problema de código primero (si hay alguno disponible), para que no falte nunca
  const codePool = shuffle(index.data.exercises.filter((e) => e.daw && e.kind === "code" && allowed.has(e.concept)), random);
  if (codePool.length) take(codePool[0]);

  for (const competency of index.data.daw) {
    const quota = Math.round((size * competency.weight) / 100);
    let have = chosen.filter((e) => competency.concepts.includes(e.concept)).length;
    for (const exercise of poolOf(competency)) {
      if (have >= quota) break;
      if (take(exercise)) have += 1;
    }
  }
  // Si alguna competencia no tenía bastantes ejercicios, se completa con las demás
  const rest = shuffle(index.data.exercises.filter((e) => e.daw && allowed.has(e.concept)), random);
  for (const exercise of rest) {
    if (chosen.length >= size) break;
    take(exercise);
  }
  return chosen.slice(0, size).sort((a, b) => a.level - b.level || (a.kind === "code") - (b.kind === "code"));
}

/**
 * Prueba de nivel: un ejercicio corto de cada concepto de la ruta (salvo los de «Más adelante»),
 * de aplicación si lo hay, sin problemas de escribir código para que sea rápida (≈ 15 min).
 */
export function buildDiagnostic(index, { random = Math.random } = {}) {
  return index.path
    .filter((id) => index.concepts.get(id).area !== "avanzado")
    .map((id) => {
      const quick = index.byConcept.get(id).filter((e) => e.kind !== "code" && e.kind !== "order");
      const applied = quick.filter((e) => e.level >= 2);
      const pool = applied.length ? applied : quick;
      return pool[Math.floor(random() * pool.length)];
    })
    .filter(Boolean);
}

/** Acierto por competencia de un simulacro guardado ({ [concepto]: [aciertos, total] }). */
export function examByCompetency(index, exam) {
  return index.data.daw.map((competency) => {
    let ok = 0;
    let total = 0;
    for (const id of competency.concepts) {
      const [a, t] = exam.concepts[id] ?? [0, 0];
      ok += a;
      total += t;
    }
    return { id: competency.id, title: competency.title, ok, total };
  });
}
