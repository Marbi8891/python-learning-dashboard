import assert from "node:assert/strict";
import { test } from "node:test";
import {
  activeErrors,
  cleanLearning,
  conceptStats,
  FIXED_STREAK,
  markRead,
  mergeLearning,
  recordAttempt,
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
  assert.equal(stats.status, "aprendiendo");
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
  reviewConcept(state, "bucles", 0.9, NOW);
  assert.deepEqual([state.concepts.bucles.box, state.concepts.bucles.due], [2, "2026-10-07"]);
  reviewConcept(state, "bucles", 0.6, NOW);
  assert.equal(state.concepts.bucles.box, 2, "acierto medio: se mantiene");
  reviewConcept(state, "bucles", 0.2, NOW);
  assert.deepEqual([state.concepts.bucles.box, state.concepts.bucles.due], [1, "2026-10-05"]);
  assert.equal(conceptStats(index, state, "bucles", new Date("2026-10-05T09:00:00")).due, true);
  assert.equal(conceptStats(index, state, "bucles", NOW).due, false);
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
  assert.deepEqual(clean.concepts.bucles, { box: 0, due: null, last: null, read: NOW.toISOString() });
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
  assert.equal(local.ex["buc-01"].n, 2, "gana el historial con más intentos");
  assert.ok(local.ex["var-01"]);
  assert.ok(local.errors["variables.orden-asignacion"]);
  assert.equal(local.concepts.bucles.read, daysAgo(3).toISOString());
  assert.equal(local.log.length, 4);
  assert.deepEqual(local.log.map((l) => l.at), [...local.log.map((l) => l.at)].sort());
  // Idempotente: fusionar otra vez no duplica
  mergeLearning(local, JSON.parse(JSON.stringify(remote)));
  assert.equal(local.log.length, 4);
});
