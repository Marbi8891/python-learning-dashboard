/* Estado de la preparación del PCAP, guardado en este navegador (clave pld:pcap).
   Sin dependencias: lo leen la zona de examen (pcap.js) y la gamificación (game.js). */

import { cleanProgress } from "./progress-guard.js";
import { isoDay, scheduleAnswer } from "./srs.js";

export { isoDay };

const KEY = "pld:pcap";

function empty() {
  return {
    lang: "es", // idioma de las preguntas: "es" | "en"
    answers: {}, // id de pregunta -> [true, false, ...] (los últimos intentos)
    exams: [], // simulacros terminados: { date, correct, total, score, seconds, blocks: {slug: [ok, total]} }
    known: [], // fichas marcadas como sabidas
    bestCombo: 0, // mejor racha de aciertos seguidos en la práctica
    flags: { mastered: false, ready: false, allCards: false },
    srs: {}, // repaso espaciado: id de pregunta o ficha -> { box: 1-5, due: "AAAA-MM-DD", last: ISO }
    plan: { examDate: null }, // fecha prevista del examen ("AAAA-MM-DD")
  };
}

function load() {
  try {
    const saved = cleanProgress(JSON.parse(localStorage.getItem(KEY)));
    return {
      ...empty(),
      ...saved,
      flags: { ...empty().flags, ...saved?.flags },
      plan: { ...empty().plan, ...saved?.plan },
    };
  } catch {
    return empty();
  }
}

export const pcap = load();

const saveListeners = new Set();

/** Avisa de cada guardado (la sincronización con la cuenta lo usa). */
export const onPcapSave = (listener) => saveListeners.add(listener);

export function savePcap() {
  try {
    localStorage.setItem(KEY, JSON.stringify(pcap));
  } catch {
    // sin almacenamiento: dura hasta recargar
  }
  for (const listener of saveListeners) listener();
}

/* ---------- Repaso espaciado (cajas de Leitner) ---------- */

/** Acierto: sube de caja y el repaso se aleja (solo si tocaba repasarlo). Fallo: caja 1 (mañana). Ver srs.js. */
export function review(id, ok, now = new Date()) {
  pcap.srs[id] = scheduleAnswer(pcap.srs[id], ok, now);
}

/** Ids que toca repasar hoy (o que se quedaron atrasados). */
export const dueIds = (ids, today = isoDay()) => ids.filter((id) => pcap.srs[id] && pcap.srs[id].due <= today);

export function recordAnswer(id, ok) {
  const history = (pcap.answers[id] ??= []);
  history.push(ok);
  if (history.length > 5) history.shift();
  review(id, ok);
}

/* ---------- Fusión con la copia guardada en la cuenta ---------- */

const later = (a, b) => ((a?.last ?? "") >= (b?.last ?? "") ? a : b);

/**
 * Historial de una pregunta tras fusionar dos copias (SYNC-02). Cada historial guarda solo los
 * últimos intentos, así que «el más largo» no dice cuál es más reciente: se usa la fecha del último
 * intento, que está en el repaso espaciado (`srs[id].last`). Sin fecha en alguna de las dos copias
 * (datos antiguos) se conserva la regla anterior: gana el más largo y, si empatan, el local.
 */
export function newerHistory(local, remote, localLast, remoteLast) {
  if (!local) return remote;
  if (localLast && remoteLast) return remoteLast > localLast ? remote : local;
  return remote.length > local.length ? remote : local;
}

/** Combina el estado de la cuenta con el local sin perder nada de ninguno de los dos. */
export function mergePcap(remote = {}) {
  const base = { ...empty(), ...cleanProgress(remote) };
  for (const [id, history] of Object.entries(base.answers)) {
    pcap.answers[id] = newerHistory(pcap.answers[id], history, pcap.srs[id]?.last, base.srs[id]?.last);
  }
  const exams = new Map([...base.exams, ...pcap.exams].map((exam) => [exam.date, exam]));
  pcap.exams = [...exams.values()].sort((a, b) => a.date.localeCompare(b.date)).slice(-30);
  pcap.known = [...new Set([...pcap.known, ...base.known])];
  pcap.bestCombo = Math.max(pcap.bestCombo, base.bestCombo);
  for (const flag of Object.keys(pcap.flags)) pcap.flags[flag] ||= Boolean(base.flags?.[flag]);
  for (const [id, item] of Object.entries(base.srs)) pcap.srs[id] = later(pcap.srs[id], item);
  pcap.plan.examDate ??= base.plan?.examDate ?? null;
  pcap.plan.dailyGoal ??= base.plan?.dailyGoal;
  // Progreso guardado por otro cliente (XP, racha, ruta, vidas y récords). La web no lo modifica:
  // conserva la copia de la cuenta para no borrarlo al guardar.
  if (base.app) pcap.app = base.app;
}

/** Preguntas distintas acertadas alguna vez (base de los XP del PCAP). */
export const questionsMastered = () => Object.values(pcap.answers).filter((h) => h.includes(true)).length;

export const examsPassed = (min = 70) => pcap.exams.filter((exam) => exam.score >= min).length;

/** Un bloque cuenta entero cuando se ha respondido al menos esta parte de sus preguntas. */
export const FULL_COVERAGE = 0.5;
/** Por debajo de esta parte del banco respondida no se muestra un porcentaje (AUD-006). */
export const MIN_EVIDENCE = 0.2;

/**
 * Acierto por bloque: último intento de cada pregunta respondida del bloque.
 * @returns {{[slug]: {answered: number, total: number, rate: number | null}}}
 */
export function blockStats(questions, blocks, answers = pcap.answers) {
  const stats = {};
  for (const block of blocks) {
    const inBlock = questions.filter((q) => q.block === block.slug);
    const last = inBlock.filter((q) => answers[q.id]?.length).map((q) => answers[q.id].at(-1));
    stats[block.slug] = {
      answered: last.length,
      total: inBlock.length,
      rate: last.length ? last.filter(Boolean).length / last.length : null,
    };
  }
  return stats;
}

const blockCoverage = (s) => (s.total ? Math.min(1, s.answered / s.total / FULL_COVERAGE) : 0);

/**
 * Preparación estimada (0-100): acierto de cada bloque ponderado por su peso en el examen y por lo que
 * se ha cubierto del bloque. Un bloque con pocas respuestas cuenta menos: acertar una pregunta de cada
 * bloque ya no da el 100 % (AUD-006).
 */
export function readiness(stats, blocks) {
  return Math.round(blocks.reduce((sum, block) => sum + (stats[block.slug].rate ?? 0) * blockCoverage(stats[block.slug]) * block.weight, 0));
}

/** Parte del banco respondida (0-1). */
export function evidenceCoverage(stats) {
  const all = Object.values(stats);
  const total = all.reduce((sum, s) => sum + (s.total ?? 0), 0);
  return total ? all.reduce((sum, s) => sum + s.answered, 0) / total : 0;
}

/** ¿Hay respuestas suficientes para mostrar un porcentaje de preparación? */
export const enoughEvidence = (stats) => evidenceCoverage(stats) >= MIN_EVIDENCE;
