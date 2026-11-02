// «Continúa donde lo dejaste» de la portada: solo con actividad real, nunca con datos de ejemplo.
import assert from "node:assert/strict";
import { test } from "node:test";
import { activitySummary, hasLearnActivity } from "../../frontend/js/learn/activity.js";
import { markRead, recordAttempt, reviewConcept } from "../../frontend/js/learn/mastery.js";
import { daysAgo, exercisesOf, fresh, index, NOW } from "./helpers.mjs";

const LESSONS = ["intro", "variables", "bucles"];

test("sin actividad no hay resumen (la portada no muestra el bloque)", () => {
  assert.equal(hasLearnActivity(fresh()), false);
  assert.equal(activitySummary(index, fresh(), { now: NOW }), null);
  assert.equal(activitySummary(index, fresh(), { completed: new Set(), lessons: LESSONS, now: NOW }), null);
});

test("con un concepto leído aparece el resumen y el siguiente paso del plan", () => {
  const state = fresh();
  markRead(state, "algoritmos", NOW);
  const { learn, pcap } = activitySummary(index, state, { now: NOW });
  assert.equal(pcap, null);
  assert.equal(learn.mastered, 0);
  assert.equal(learn.total, index.path.length);
  assert.equal(learn.due, 0);
  assert.equal(learn.next.concept, "algoritmos");
  assert.equal(learn.next.action, "Aprender");
  assert.equal(learn.next.title, index.concepts.get("algoritmos").title);
});

test("cuenta lo dominado, los repasos de hoy, los errores activos y la última actividad", () => {
  const state = fresh();
  for (const e of exercisesOf("algoritmos")) recordAttempt(state, e, { ok: true, error: null }, { now: daysAgo(3) });
  reviewConcept(state, "algoritmos", 1, daysAgo(3)); // vuelve dentro de 1 día: hoy está pendiente
  const wrong = exercisesOf("variables").find((e) => Object.keys(e.traps ?? {}).length);
  const errorId = Object.values(wrong.traps)[0];
  assert.ok(index.errors.has(errorId));
  recordAttempt(state, wrong, { ok: false, error: errorId }, { now: NOW });
  const { learn } = activitySummary(index, state, { now: NOW });
  assert.equal(learn.mastered, 1);
  assert.equal(learn.due, 1);
  assert.equal(learn.errors, 1);
  assert.equal(learn.last.concept, "variables");
  assert.equal(learn.next.type, "review"); // los repasos que tocan van primero
});

test("curso PCAP: solo cuentan las lecciones que existen y propone la primera sin hacer", () => {
  const completed = new Set(["intro", "borrada"]);
  const { learn, pcap } = activitySummary(null, fresh(), { completed, lessons: LESSONS, now: NOW });
  assert.equal(learn, null);
  assert.deepEqual(pcap, { done: 1, total: 3, next: "variables" });
  const all = activitySummary(null, fresh(), { completed: new Set(LESSONS), lessons: LESSONS, now: NOW });
  assert.equal(all.pcap.next, null);
});

test("si learning.json no se ha cargado no se inventa el resumen del núcleo", () => {
  const state = fresh();
  markRead(state, "algoritmos", NOW);
  assert.equal(activitySummary(null, state, { now: NOW }), null);
});
