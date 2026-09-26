/* Estado de la preparación del PCAP, guardado en este navegador (clave pld:pcap).
   Sin dependencias: lo leen la zona de examen (pcap.js) y la gamificación (game.js). */

const KEY = "pld:pcap";

function empty() {
  return {
    lang: "es", // idioma de las preguntas: "es" | "en"
    answers: {}, // id de pregunta -> [true, false, ...] (los últimos intentos)
    exams: [], // simulacros terminados: { date, correct, total, score, seconds, blocks: {slug: [ok, total]} }
    known: [], // fichas marcadas como sabidas
    bestCombo: 0, // mejor racha de aciertos seguidos en la práctica
    flags: { mastered: false, ready: false, allCards: false },
  };
}

function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY));
    return { ...empty(), ...saved, flags: { ...empty().flags, ...saved?.flags } };
  } catch {
    return empty();
  }
}

export const pcap = load();

export function savePcap() {
  try {
    localStorage.setItem(KEY, JSON.stringify(pcap));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
}

export function recordAnswer(id, ok) {
  const history = (pcap.answers[id] ??= []);
  history.push(ok);
  if (history.length > 5) history.shift();
}

/** Preguntas distintas acertadas alguna vez (base de los XP del PCAP). */
export const questionsMastered = () => Object.values(pcap.answers).filter((h) => h.includes(true)).length;

export const examsPassed = (min = 70) => pcap.exams.filter((exam) => exam.score >= min).length;

/**
 * Acierto por bloque: último intento de cada pregunta respondida del bloque.
 * @returns {{[slug]: {answered: number, rate: number | null}}}
 */
export function blockStats(questions, blocks) {
  const stats = {};
  for (const block of blocks) {
    const last = questions
      .filter((q) => q.block === block.slug && pcap.answers[q.id])
      .map((q) => pcap.answers[q.id].at(-1));
    stats[block.slug] = {
      answered: last.length,
      rate: last.length ? last.filter(Boolean).length / last.length : null,
    };
  }
  return stats;
}

/** Preparación estimada: acierto de cada bloque ponderado por su peso en el examen (0-100). */
export function readiness(stats, blocks) {
  return Math.round(blocks.reduce((sum, block) => sum + (stats[block.slug].rate ?? 0) * block.weight, 0));
}
