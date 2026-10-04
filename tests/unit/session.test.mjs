import assert from "node:assert/strict";
import { test } from "node:test";
import { conceptStats } from "../../frontend/js/learn/mastery.js";
import { advance, createSession, currentItem, finish, isExpired, MAX_RETRIES, secondsLeft, stop, submit, summarize } from "../../frontend/js/learn/session.js";
import { fresh, index, NOW } from "./helpers.mjs";

test("ciclo completo: fallo → explicación → nuevo intento con un ejercicio parecido → resumen", () => {
  const state = fresh();
  const session = createSession({ kind: "practice", title: "Bucles", exercises: ["buc-01", "buc-06"], now: NOW });
  submit(session, index, state, { ok: false, error: "bucles.range-fin" }, NOW);
  assert.equal(session.phase, "feedback", "tras corregir se muestra la explicación");
  assert.equal(session.queue.length, 3, "se añade un nuevo intento al final");
  const retry = session.queue[2];
  assert.equal(retry.retryOf, "buc-01");
  advance(session);
  submit(session, index, state, { ok: true, error: null }, NOW);
  advance(session);
  assert.equal(currentItem(session).id, retry.id);
  submit(session, index, state, { ok: true, error: null }, NOW);
  advance(session);
  assert.equal(session.phase, "done");
  const summary = finish(session, index, state, NOW);
  assert.deepEqual([summary.correct, summary.total], [1, 2], "la nota cuenta solo los primeros intentos");
  assert.deepEqual([summary.retried, summary.fixed], [1, 1]);
  assert.equal(summary.errors[0].id, "bucles.range-fin");
  assert.ok(summary.errors[0].why, "el resumen trae la explicación del error");
  assert.equal(state.concepts.bucles.box, 1, "50 %: el repaso del concepto se programa para mañana");
});

test("si no hay ejercicio parecido, el nuevo intento repite el mismo y no cuenta para el dominio", () => {
  const state = fresh();
  const all = index.byConcept.get("modulos").map((e) => e.id);
  const session = createSession({ kind: "practice", title: "Módulos", exercises: all, now: NOW });
  submit(session, index, state, { ok: false, error: "modulos.prefijo" }, NOW);
  const retry = session.queue.at(-1);
  assert.deepEqual([retry.id, retry.retry], ["mod-01", true]);
  while (session.phase !== "done") {
    advance(session);
    if (session.phase === "done") break;
    submit(session, index, state, { ok: true, error: null }, NOW);
  }
  assert.deepEqual(state.ex["mod-01"].h, [false], "el acierto en el nuevo intento no se suma al historial");
});

test("como mucho MAX_RETRIES nuevos intentos por sesión", () => {
  const state = fresh();
  const ids = index.byConcept.get("bucles").map((e) => e.id);
  const session = createSession({ kind: "practice", title: "x", exercises: ids, now: NOW });
  for (let i = 0; i < ids.length; i += 1) {
    submit(session, index, state, { ok: false, error: null }, NOW);
    advance(session);
  }
  assert.equal(session.queue.length, ids.length + MAX_RETRIES);
});

test("simulacro: sin explicación entre preguntas, sin nuevos intentos, cronometrado y guardado", () => {
  const state = fresh();
  const session = createSession({ kind: "exam", title: "Simulacro", exercises: ["buc-01", "con-01", "var-01"], timeLimit: 600, now: NOW, meta: { examKind: "daw" } });
  submit(session, index, state, { ok: false, error: "bucles.range-fin" }, NOW);
  assert.equal(session.phase, "answer");
  assert.equal(session.index, 1, "pasa directamente a la siguiente");
  assert.equal(session.queue.length, 3);
  submit(session, index, state, { ok: true, error: null }, NOW);
  const later = new Date(NOW.getTime() + 300_000);
  assert.equal(secondsLeft(session, later), 300);
  assert.equal(isExpired(session, new Date(NOW.getTime() + 601_000)), true);
  stop(session);
  const summary = finish(session, index, state, later);
  assert.equal(summary.unanswered, 1);
  assert.deepEqual(state.exams[0], {
    date: later.toISOString(),
    kind: "daw",
    correct: 1,
    total: 3,
    seconds: 300,
    concepts: { bucles: [0, 1], condicionales: [1, 1] },
  });
  assert.equal(state.errors["bucles.range-fin"].n, 1, "los errores del simulacro también se registran");
});

test("una sesión vacía empieza terminada", () => {
  const session = createSession({ kind: "review", title: "Nada", exercises: [], now: NOW });
  assert.equal(session.phase, "done");
  assert.deepEqual(summarize(session, index).total, 0);
});

test("una sesión de aprendizaje con todo acertado hace avanzar el dominio", () => {
  const state = fresh();
  const ids = index.byConcept.get("variables").map((e) => e.id);
  const session = createSession({ kind: "learn", title: "Variables", exercises: ids, now: NOW });
  for (const _ of ids) {
    submit(session, index, state, { ok: true, error: null }, NOW);
    advance(session);
  }
  finish(session, index, state, NOW);
  assert.equal(conceptStats(index, state, "variables", NOW).status, "dominado");
  assert.equal(state.concepts.variables.box, 1);
});
