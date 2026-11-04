import assert from "node:assert/strict";
import { test } from "node:test";
import {
  activeErrors,
  cleanLearning,
  conceptStats,
  explainStats,
  FIXED_STREAK,
  halfLifeDays,
  markRead,
  mergeLearning,
  recordAttempt,
  retention,
  reviewConcept,
} from "../../frontend/js/learn/mastery.js";
import { daysAgo, exercisesOf, fresh, index, NOW } from "./helpers.mjs";

const solve = (state, exercises, ok = true, now = NOW) => {
  for (const e of exercises) recordAttempt(state, e, { ok, error: null }, { now });
};

test("un concepto sin actividad es nuevo; tras leer la teoría, leído", () => {
  const state = fresh();
  assert.equal(conceptStats(index, state, "bucles", NOW).status, "nuevo");
  markRead(state, "bucles", NOW);
  assert.equal(conceptStats(index, state, "bucles", NOW).status, "leido");
});

test("acertar un solo ejercicio no basta para dominar un concepto", () => {
  const state = fresh();
  solve(state, exercisesOf("bucles").slice(0, 1));
  const stats = conceptStats(index, state, "bucles", NOW);
  assert.equal(stats.status, "insuficiente", "con una sola evidencia no se estima el dominio (F1.5)");
  assert.equal(stats.enough, false);
  assert.ok(stats.score > 0 && stats.score < 0.5);
});

test("acertar todos los ejercicios de un concepto lo domina", () => {
  const state = fresh();
  solve(state, exercisesOf("condicionales"));
  const stats = conceptStats(index, state, "condicionales", NOW);
  assert.equal(stats.score, 1);
  assert.equal(stats.status, "dominado");
});

test("el dominio usa el último intento: un fallo posterior lo baja", () => {
  const state = fresh();
  const list = exercisesOf("condicionales");
  solve(state, list);
  recordAttempt(state, list.at(-1), { ok: false, error: null }, { now: NOW });
  assert.ok(conceptStats(index, state, "condicionales", NOW).score < 1);
});

test("dominar exige haber acertado algún ejercicio de aplicación (nivel ≥ 2)", () => {
  const state = fresh();
  const list = exercisesOf("bucles");
  solve(state, list.filter((e) => e.level === 1));
  recordAttempt(state, list.find((e) => e.level >= 2), { ok: false, error: null }, { now: NOW });
  assert.notEqual(conceptStats(index, state, "bucles", NOW).status, "dominado");
});

test("un error activo del concepto impide darlo por dominado hasta corregirlo", () => {
  const state = fresh();
  const list = exercisesOf("condicionales");
  solve(state, list);
  // Falla una vez con un error típico y luego vuelve a acertar ese mismo ejercicio
  const target = list.find((e) => e.id === "con-01");
  recordAttempt(state, target, { ok: false, error: "condicionales.orden-elif" }, { now: NOW });
  recordAttempt(state, target, { ok: true, error: null }, { now: NOW });
  assert.equal(activeErrors(state, NOW).length, 1, "un acierto no basta");
  assert.equal(conceptStats(index, state, "condicionales", NOW).status, "progreso");
  recordAttempt(state, list.find((e) => e.id === "con-05"), { ok: true, error: null }, { now: NOW });
  assert.equal(state.errors["condicionales.orden-elif"].streak, FIXED_STREAK);
  assert.equal(activeErrors(state, NOW).length, 0);
  assert.equal(conceptStats(index, state, "condicionales", NOW).status, "dominado");
});

test("los errores antiguos dejan de estar activos aunque no se hayan corregido", () => {
  const state = fresh();
  recordAttempt(state, index.exercises.get("buc-01"), { ok: false, error: "bucles.range-fin" }, { now: daysAgo(30) });
  assert.equal(activeErrors(state, NOW).length, 0);
  assert.equal(activeErrors(state, daysAgo(25)).length, 1);
});

test("un nuevo intento del mismo ejercicio (retry) no cuenta para el dominio pero sí registra errores", () => {
  const state = fresh();
  const e = index.exercises.get("buc-01");
  recordAttempt(state, e, { ok: false, error: "bucles.range-fin" }, { now: NOW });
  recordAttempt(state, e, { ok: true, error: null }, { now: NOW, retry: true });
  assert.deepEqual(state.ex["buc-01"].h, [false]);
  assert.equal(state.log.length, 2);
  assert.equal(state.errors["bucles.range-fin"].streak, 0);
});

test("el historial guarda los 5 últimos intentos y el registro tiene un tamaño máximo", () => {
  const state = fresh();
  const e = index.exercises.get("buc-01");
  for (let i = 0; i < 7; i += 1) recordAttempt(state, e, { ok: i % 2 === 0, error: null }, { now: NOW });
  assert.equal(state.ex["buc-01"].h.length, 5);
  assert.equal(state.ex["buc-01"].n, 7);
});

test("repaso espaciado: acierto alto aleja el repaso, acierto bajo lo trae a mañana", () => {
  const state = fresh();
  reviewConcept(state, "bucles", 1, NOW);
  assert.deepEqual([state.concepts.bucles.box, state.concepts.bucles.due], [1, "2026-10-05"]);
  const tomorrow = new Date("2026-10-05T10:00:00");
  reviewConcept(state, "bucles", 0.9, tomorrow);
  assert.deepEqual([state.concepts.bucles.box, state.concepts.bucles.due], [2, "2026-10-08"]);
  const later = new Date("2026-10-08T10:00:00");
  reviewConcept(state, "bucles", 0.6, later);
  assert.deepEqual([state.concepts.bucles.box, state.concepts.bucles.due], [2, "2026-10-11"], "acierto medio: se mantiene la caja");
  reviewConcept(state, "bucles", 0.2, later);
  assert.deepEqual([state.concepts.bucles.box, state.concepts.bucles.due], [1, "2026-10-09"]);
  assert.equal(conceptStats(index, state, "bucles", new Date("2026-10-09T09:00:00")).due, true);
  assert.equal(conceptStats(index, state, "bucles", later).due, false);
});

test("repaso espaciado: cinco sesiones perfectas la misma tarde no lo mandan a un mes (AUD-004)", () => {
  const state = fresh();
  for (let i = 0; i < 5; i += 1) reviewConcept(state, "bucles", 1, NOW);
  assert.deepEqual([state.concepts.bucles.box, state.concepts.bucles.due], [1, "2026-10-05"]);
});

test("una sesión abandonada deja el repaso programado para mañana (AUD-003)", () => {
  const state = fresh();
  solve(state, exercisesOf("variables"));
  const stats = conceptStats(index, state, "variables", NOW);
  assert.equal(stats.nextReview, "2026-10-05");
  assert.equal(state.concepts.variables.box, 0, "la caja la sube el cierre de una sesión");
  reviewConcept(state, "variables", 1, NOW);
  assert.equal(state.concepts.variables.box, 1, "la primera sesión cerrada sí sube de caja");
});

test("cleanLearning descarta datos manipulados y conserva los válidos", () => {
  const clean = cleanLearning({
    ex: { "buc-01": { h: [true, "x", false], last: NOW.toISOString(), n: 3 }, "<img>": { h: [], last: NOW.toISOString(), n: 1 } },
    concepts: { bucles: { box: 99, due: "mañana", last: "no", read: NOW.toISOString() } },
    errors: { "bucles.range-fin": { n: 2, last: NOW.toISOString(), streak: -1 }, malo: { n: "2" } },
    log: [{ at: NOW.toISOString(), ex: "buc-01", ok: true, err: "<script>" }, { at: "x" }],
    exams: [{ date: NOW.toISOString(), kind: "daw", correct: 3, total: 5, seconds: 60, concepts: { bucles: [1, 2], mal: ["a", 1] } }],
  });
  assert.deepEqual(clean.ex["buc-01"].h, [true, false]);
  assert.equal(clean.ex["<img>"], undefined);
  assert.deepEqual(clean.concepts.bucles, { box: 0, due: null, last: null, read: NOW.toISOString(), placed: null });
  assert.equal(clean.errors["bucles.range-fin"].streak, 0);
  assert.equal(clean.errors.malo, undefined);
  assert.equal(clean.log.length, 1);
  assert.equal(clean.log[0].err, null);
  assert.deepEqual(clean.exams[0].concepts, { bucles: [1, 2] });
  assert.deepEqual(cleanLearning(null), fresh());
});

test("mergeLearning une el progreso de dos dispositivos sin perder nada", () => {
  const local = fresh();
  const remote = fresh();
  recordAttempt(local, index.exercises.get("buc-01"), { ok: true, error: null }, { now: NOW });
  recordAttempt(remote, index.exercises.get("var-01"), { ok: false, error: "variables.orden-asignacion" }, { now: daysAgo(1) });
  recordAttempt(remote, index.exercises.get("buc-01"), { ok: false, error: null }, { now: daysAgo(2) });
  recordAttempt(remote, index.exercises.get("buc-01"), { ok: true, error: null }, { now: daysAgo(1) });
  markRead(remote, "bucles", daysAgo(3));
  mergeLearning(local, JSON.parse(JSON.stringify(remote)));
  assert.equal(local.ex["buc-01"].n, 2, "el número de intentos no baja");
  assert.deepEqual(local.ex["buc-01"].h, [true], "gana el historial del intento más reciente (SYNC-02)");
  assert.ok(local.ex["var-01"]);
  assert.ok(local.errors["variables.orden-asignacion"]);
  assert.equal(local.concepts.bucles.read, daysAgo(3).toISOString());
  assert.equal(local.log.length, 4);
  assert.deepEqual(local.log.map((l) => l.at), [...local.log.map((l) => l.at)].sort());
  // Idempotente: fusionar otra vez no duplica
  mergeLearning(local, JSON.parse(JSON.stringify(remote)));
  assert.equal(local.log.length, 4);
});

test("compatibilidad hacia delante: cleanLearning conserva los campos de versiones futuras (F1.0)", () => {
  const at = NOW.toISOString();
  const clean = cleanLearning({
    ex: { "buc-01": { h: [true], last: at, n: 1, okAt: at, raro: { a: 1 }, __proto__x: 1 } },
    concepts: { bucles: { box: 1, due: "2026-10-05", last: at, read: null, placed: null, ease: 2.5 } },
    errors: { "bucles.range-fin": { n: 1, last: at, streak: 0, seen: 3 } },
    planner: { tasks: [{ id: "t1" }] },
    "<mal>": 1,
  });
  assert.equal(clean.ex["buc-01"].okAt, at, "un campo simple nuevo se conserva");
  assert.equal(clean.ex["buc-01"].raro, undefined, "dentro de una entrada solo pasan valores simples");
  assert.equal(clean.concepts.bucles.ease, 2.5);
  assert.equal(clean.errors["bucles.range-fin"].seen, 3);
  assert.deepEqual(clean.planner, { tasks: [{ id: "t1" }] }, "un bloque nuevo se conserva tal cual");
  assert.equal(clean["<mal>"], undefined, "claves con formato raro no pasan");
  assert.equal(Object.getPrototypeOf(clean), Object.prototype);
});

test("compatibilidad hacia delante: mergeLearning no pierde los campos de versiones futuras", () => {
  const local = fresh();
  const remote = fresh();
  recordAttempt(remote, index.exercises.get("buc-01"), { ok: true, error: null }, { now: NOW });
  remote.ex["buc-01"].okAt = NOW.toISOString();
  remote.planner = { minutes: 30 };
  mergeLearning(local, JSON.parse(JSON.stringify(remote)));
  assert.equal(local.ex["buc-01"].okAt, NOW.toISOString());
  assert.deepEqual(local.planner, { minutes: 30 });
  local.planner = { minutes: 45 };
  mergeLearning(local, JSON.parse(JSON.stringify(remote)));
  assert.deepEqual(local.planner, { minutes: 45 }, "si aquí existe, no se pisa");
});

/* ---------- Dominio 2.0 (F1.5) ---------- */

test("dominio 2.0: es reproducible (mismo documento y misma fecha, mismo resultado)", () => {
  const state = fresh();
  solve(state, exercisesOf("listas").slice(0, 3));
  const a = conceptStats(index, JSON.parse(JSON.stringify(state)), "listas", NOW);
  const b = conceptStats(index, JSON.parse(JSON.stringify(state)), "listas", NOW);
  assert.deepEqual(a, b);
});

test("dominio 2.0: repetir el mismo ejercicio no infla el dominio ni la confianza", () => {
  const once = fresh();
  const many = fresh();
  const [first] = exercisesOf("listas");
  solve(once, [first]);
  for (let i = 0; i < 20; i += 1) solve(many, [first]);
  const a = conceptStats(index, once, "listas", NOW);
  const b = conceptStats(index, many, "listas", NOW);
  assert.equal(b.score, a.score);
  assert.equal(b.confidence, a.confidence);
  assert.equal(b.evidence.length, 1, "una evidencia por ejercicio distinto");
  assert.equal(b.evidence[0].n, 20);
});

test("dominio 2.0: la confianza depende de la cantidad y la variedad de evidencias, no del acierto", () => {
  const state = fresh();
  const list = exercisesOf("listas");
  solve(state, list.slice(0, 1));
  const low = conceptStats(index, state, "listas", NOW);
  solve(state, list.slice(1), false);
  const high = conceptStats(index, state, "listas", NOW);
  assert.ok(high.confidence > low.confidence);
  assert.ok(high.score <= low.score + 1e-9, "más evidencias falladas no suben el dominio");
  assert.equal(high.enough, true);
  assert.equal(low.enough, false);
});

test("dominio 2.0: cada evidencia se identifica con su ejercicio, tipo, resultado y fecha", () => {
  const state = fresh();
  const [a, b] = exercisesOf("listas");
  solve(state, [a]);
  solve(state, [b], false);
  const s = conceptStats(index, state, "listas", NOW);
  assert.deepEqual(
    s.evidence.map((e) => [e.id, e.ok, e.okAt]),
    [
      [a.id, true, NOW.toISOString()],
      [b.id, false, null],
    ],
  );
  assert.equal(state.ex[a.id].okAt, NOW.toISOString(), "recordAttempt guarda la fecha del último acierto");
});

test("dominio 2.0: si el repaso se pasa, la retención baja y el concepto se marca como olvidado", () => {
  const state = fresh();
  solve(state, exercisesOf("variables"), true, daysAgo(60));
  reviewConcept(state, "variables", 1, daysAgo(60)); // caja 1: repaso al día siguiente
  const s = conceptStats(index, state, "variables", NOW);
  assert.equal(s.base, 1);
  assert.ok(s.retention < 0.2);
  assert.ok(s.score < 0.2);
  assert.equal(s.forgotten, true);
  assert.notEqual(s.status, "dominado");
  const fresh1 = conceptStats(index, state, "variables", daysAgo(59));
  assert.equal(fresh1.retention, 1, "hasta la fecha de repaso se supone intacta");
});

test("dominio 2.0: una caja alta olvida más despacio", () => {
  assert.ok(halfLifeDays(5) > halfLifeDays(1));
  const at = daysAgo(30).toISOString();
  const low = retention({ box: 1, due: "2026-09-05", last: at }, NOW);
  const high = retention({ box: 5, due: "2026-09-05", last: at }, NOW);
  assert.ok(high > low);
});

test("dominio 2.0: los datos antiguos sin okAt deducen el último acierto del historial", () => {
  const state = cleanLearning({ ex: { "lis-01": { h: [false, true], last: NOW.toISOString(), n: 2 } } });
  const s = conceptStats(index, state, "listas", NOW);
  assert.equal(s.evidence[0].okAt, NOW.toISOString());
});

test("explainStats explica el dominio con palabras", () => {
  const state = fresh();
  assert.match(explainStats(conceptStats(index, state, "listas", NOW)), /Aún no/);
  solve(state, exercisesOf("listas").slice(0, 1));
  assert.match(explainStats(conceptStats(index, state, "listas", NOW)), /pocas evidencias/);
});

test("fusión (F1.6): el último acierto de cualquier dispositivo no se pierde", () => {
  const local = fresh();
  const remote = fresh();
  const ex = index.exercises.get("lis-01");
  recordAttempt(remote, ex, { ok: true, error: null }, { now: daysAgo(2) });
  recordAttempt(local, ex, { ok: false, error: null }, { now: daysAgo(1) });
  mergeLearning(local, JSON.parse(JSON.stringify(remote)));
  assert.deepEqual(local.ex["lis-01"].h, [false], "el resultado actual es el del intento más reciente");
  assert.equal(local.ex["lis-01"].okAt, daysAgo(2).toISOString(), "pero la evidencia del acierto sigue");
  assert.equal(local.ex["lis-01"].n, 1);
});
