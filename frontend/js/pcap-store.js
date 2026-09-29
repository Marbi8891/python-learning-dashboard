/* Estado de la preparación del PCAP, guardado en este navegador (clave pld:pcap).
   Sin dependencias: lo leen la zona de examen (pcap.js) y la gamificación (game.js). */

import { cleanProgress } from "./progress-guard.js";

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

const INTERVAL_DAYS = [0, 1, 3, 7, 14, 30]; // días hasta el siguiente repaso según la caja
const MAX_BOX = INTERVAL_DAYS.length - 1;

export const isoDay = (date = new Date()) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

function addDays(days, from = new Date()) {
  const date = new Date(from);
  date.setDate(date.getDate() + days);
  return isoDay(date);
}

/** Acierto: sube de caja y el repaso se aleja. Fallo: vuelve a la caja 1 (repaso mañana). */
export function review(id, ok) {
  const box = ok ? Math.min((pcap.srs[id]?.box ?? 0) + 1, MAX_BOX) : 1;
  pcap.srs[id] = { box, due: addDays(INTERVAL_DAYS[box]), last: new Date().toISOString() };
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

/** Combina el estado de la cuenta con el local sin perder nada de ninguno de los dos. */
export function mergePcap(remote = {}) {
  const base = { ...empty(), ...cleanProgress(remote) };
  for (const [id, history] of Object.entries(base.answers)) {
    if (!pcap.answers[id] || history.length > pcap.answers[id].length) pcap.answers[id] = history;
  }
  const exams = new Map([...base.exams, ...pcap.exams].map((exam) => [exam.date, exam]));
  pcap.exams = [...exams.values()].sort((a, b) => a.date.localeCompare(b.date)).slice(-30);
  pcap.known = [...new Set([...pcap.known, ...base.known])];
  pcap.bestCombo = Math.max(pcap.bestCombo, base.bestCombo);
  for (const flag of Object.keys(pcap.flags)) pcap.flags[flag] ||= Boolean(base.flags?.[flag]);
  for (const [id, item] of Object.entries(base.srs)) pcap.srs[id] = later(pcap.srs[id], item);
  pcap.plan.examDate ??= base.plan?.examDate ?? null;
  // Progreso de la app Android (XP, racha, ruta, vidas y récords; ADR-0018). La web no lo modifica:
  // conserva la copia de la cuenta para no borrarlo al guardar. La app fusiona el suyo al sincronizar.
  if (base.app) pcap.app = base.app;
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
