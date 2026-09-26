/* Gamificación: XP, niveles, racha y logros.

   Los XP no son un contador que se incrementa: se CALCULAN a partir de hechos
   (lecciones completadas, mejor nota de cada quiz, retos superados...), así que
   repetir una acción nunca da puntos dobles y el total siempre es coherente.
   Se guarda en este navegador (ver ADR-0005). */

import { state as store, subscribe as onStore } from "./store.js";

const KEY = "pld:game";
const XP = { lesson: 50, quizPerQuestion: 10, quizPerfectBonus: 10, firstTry: 20, perStar: 30 };

export const LEVELS = [
  { xp: 0, name: "Novato/a" },
  { xp: 100, name: "Aprendiz" },
  { xp: 300, name: "Programador/a en prácticas" },
  { xp: 600, name: "Pythonista" },
  { xp: 1000, name: "Pythonista avanzado/a" },
  { xp: 1500, name: "Maestro/a Python" },
  { xp: 2200, name: "Leyenda de Python" },
];

let lessons = []; // [{ slug, module, challenge }]
const listeners = new Set();

function empty() {
  return {
    quiz: {}, // slug -> mejor número de aciertos
    read: [], // lecciones cuya teoría el alumno ha marcado como leída
    passed: [], // ejercicios superados
    tried: [], // ejercicios comprobados al menos una vez
    firstTry: [], // ejercicios superados en el primer intento
    challenges: [], // retos superados
    days: [], // días con actividad (AAAA-MM-DD, hora local)
    flags: { firstRun: false, bugHunter: false, lastRunFailed: false },
    badges: [],
  };
}

function load() {
  try {
    return { ...empty(), ...JSON.parse(localStorage.getItem(KEY)) };
  } catch {
    return empty();
  }
}

export const game = load();

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(game));
  } catch {
    // sin almacenamiento: el juego dura hasta recargar
  }
}

const add = (list, value) => {
  if (!list.includes(value)) list.push(value);
};

export const today = (date = new Date()) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

/* ---------- Cálculos ---------- */

export function xpTotal() {
  const quiz = Object.values(game.quiz).reduce(
    (sum, best) => sum + best * XP.quizPerQuestion + (best === 3 ? XP.quizPerfectBonus : 0),
    0,
  );
  const stars = lessons
    .filter((l) => game.challenges.includes(l.slug))
    .reduce((sum, l) => sum + l.challenge.stars * XP.perStar, 0);
  return store.completed.size * XP.lesson + quiz + game.firstTry.length * XP.firstTry + stars;
}

export function levelInfo(xp = xpTotal()) {
  let index = 0;
  LEVELS.forEach((level, i) => {
    if (xp >= level.xp) index = i;
  });
  const next = LEVELS[index + 1];
  const current = LEVELS[index];
  const progress = next ? (xp - current.xp) / (next.xp - current.xp) : 1;
  return { number: index + 1, name: current.name, xp, next, progress: Math.round(progress * 100) };
}

/** Días seguidos con actividad, terminando hoy (o ayer, si hoy aún no has estudiado). */
export function streak(now = new Date()) {
  const days = new Set(game.days);
  const cursor = new Date(now);
  if (!days.has(today(cursor))) cursor.setDate(cursor.getDate() - 1);
  let count = 0;
  while (days.has(today(cursor))) {
    count += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return count;
}

const perfectQuizzes = () => Object.values(game.quiz).filter((best) => best === 3).length;
const moduleDone = (slug) => {
  const own = lessons.filter((l) => l.module === slug);
  return own.length > 0 && own.every((l) => store.completed.has(l.slug));
};

export const BADGES = [
  { id: "hola-mundo", icon: "▶", name: "¡Hola, mundo!", goal: "Ejecuta tu primer programa sin errores", test: () => game.flags.firstRun },
  { id: "primer-ejercicio", icon: "✓", name: "Primer ejercicio", goal: "Supera un ejercicio", test: () => game.passed.length >= 1 },
  { id: "a-la-primera", icon: "1", name: "A la primera", goal: "Supera un ejercicio en el primer intento", test: () => game.firstTry.length >= 1 },
  { id: "cazabugs", icon: "✎", name: "Cazador/a de bugs", goal: "Arregla un error: ejecuta sin fallos justo después de un error", test: () => game.flags.bugHunter },
  { id: "quiz-perfecto", icon: "?", name: "Quiz perfecto", goal: "Acierta las 3 preguntas de un quiz", test: () => perfectQuizzes() >= 1 },
  { id: "cerebrito", icon: "✦", name: "Cerebrito", goal: "Consigue 5 quizzes perfectos", test: () => perfectQuizzes() >= 5 },
  { id: "retador", icon: "★", name: "Retador/a", goal: "Supera tu primer reto extra", test: () => game.challenges.length >= 1 },
  {
    id: "tres-estrellas",
    icon: "★★★",
    name: "Tres estrellas",
    goal: "Supera un reto de dificultad ★★★",
    test: () => lessons.some((l) => l.challenge.stars === 3 && game.challenges.includes(l.slug)),
  },
  { id: "base-solida", icon: "F", name: "Base sólida", goal: "Completa el módulo Fundamentos", test: () => moduleDone("fundamentos") },
  { id: "medio-camino", icon: "½", name: "Medio camino", goal: "Completa 8 lecciones", test: () => store.completed.size >= 8 },
  { id: "graduado", icon: "⚑", name: "Graduado/a", goal: "Completa las 15 lecciones", test: () => lessons.length > 0 && store.completed.size >= lessons.length },
  { id: "constancia", icon: "3", name: "Constancia", goal: "Estudia 3 días seguidos", test: () => streak() >= 3 },
  { id: "imparable", icon: "7", name: "Imparable", goal: "Estudia 7 días seguidos", test: () => streak() >= 7 },
];

/* ---------- Eventos ---------- */

export function subscribe(listener) {
  listeners.add(listener);
}

let lastLevel = null;

/** Recalcula logros y nivel, guarda y avisa de lo nuevo. */
function commit(events = []) {
  const unlocked = BADGES.filter((badge) => !game.badges.includes(badge.id) && badge.test());
  for (const badge of unlocked) game.badges.push(badge.id);
  const level = levelInfo();
  const levelUp = lastLevel !== null && level.number > lastLevel;
  lastLevel = level.number;
  save();
  for (const listener of listeners) listener({ events, unlocked, levelUp, level });
}

function activity() {
  add(game.days, today());
}

/** El alumno ha leído la teoría (paso 1 de la guía). No da XP: es solo orientación. */
export function recordRead(slug) {
  if (game.read.includes(slug)) return;
  add(game.read, slug);
  activity();
  commit();
}

export function recordRun(ok) {
  activity();
  if (ok) {
    game.flags.firstRun = true;
    if (game.flags.lastRunFailed) game.flags.bugHunter = true;
  }
  game.flags.lastRunFailed = !ok;
  commit();
}

export function recordExercise(slug, passed) {
  activity();
  const events = [];
  if (passed && !game.passed.includes(slug)) {
    if (!game.tried.includes(slug)) {
      add(game.firstTry, slug);
      events.push(`+${XP.firstTry} XP extra por acertar a la primera`);
    }
    add(game.passed, slug);
  }
  add(game.tried, slug);
  commit(events);
}

export function recordQuiz(slug, correct) {
  activity();
  const previous = game.quiz[slug] ?? 0;
  const events = [];
  // Se guarda aunque sea 0/3: el quiz cuenta como hecho (guía y perfil)
  if (game.quiz[slug] === undefined || correct > previous) {
    game.quiz[slug] = correct;
    const gained = (correct - previous) * XP.quizPerQuestion + (correct === 3 ? XP.quizPerfectBonus : 0);
    if (gained > 0) events.push(`+${gained} XP en el quiz`);
  }
  commit(events);
}

export function recordChallenge(slug, stars) {
  activity();
  const events = [];
  if (!game.challenges.includes(slug)) {
    add(game.challenges, slug);
    events.push(`+${stars * XP.perStar} XP por el reto`);
  }
  commit(events);
}

export function initGame(allLessons) {
  lessons = allLessons.map((l) => ({ slug: l.slug, module: l.module.slug, challenge: l.challenge }));
  lastLevel = levelInfo().number;
  onStore((change) => {
    if (change.type !== "progress") return;
    activity();
    commit();
  });
  commit();
}
