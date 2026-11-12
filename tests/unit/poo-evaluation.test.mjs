// Módulo de POO, PR D: cuestionario de unidad con nota, evaluación final y repaso de las falladas.
import assert from "node:assert/strict";
import { test } from "node:test";
import { cleanLearning, mergeLearning, QUIZ_PASS, quizResult, recordQuiz } from "../../frontend/js/learn/mastery.js";
import { advance, createSession, finish, submit } from "../../frontend/js/learn/session.js";
import { buildPooFinal, shuffle } from "../../frontend/js/learn/exam.js";
import { availableUnits, failedBank, FINAL_ID, needed, renderModule, unitBody } from "../../frontend/js/learn/poo-view.js";
import { allStats } from "../../frontend/js/learn/mastery.js";
import { fresh, index, NOW, seeded } from "./helpers.mjs";

const unit = index.concepts.get("poo-herencia");
const later = (days) => new Date(NOW.getTime() + days * 86_400_000);

/** Responde una sesión entera: acierta las `ok` primeras preguntas y falla las demás. */
function play(session, state, ok) {
  let n = 0;
  while (session.phase !== "done") {
    if (session.phase === "feedback") {
      advance(session);
      continue;
    }
    const right = n < ok;
    submit(session, index, state, { ok: right, error: null }, NOW);
    n += 1;
  }
  return finish(session, index, state, NOW);
}

test("se aprueba con el 70 %: 11 de 15 en la unidad y 21 de 30 en la evaluación final", () => {
  assert.equal(QUIZ_PASS, 0.7);
  assert.equal(needed(15), 11);
  assert.equal(needed(30), 21);
  assert.equal(needed(10), 7);
});

test("el cuestionario de la unidad corrige cada pregunta pero no añade nuevos intentos y guarda la nota", () => {
  const state = fresh();
  const session = createSession({ kind: "quiz", title: "Cuestionario", exercises: unit.bank, meta: { quiz: unit.id } });
  assert.equal(session.feedback, true);
  const summary = play(session, state, 10);
  assert.equal(session.queue.length, 15, "un fallo no añade ejercicios a la cola");
  assert.deepEqual(summary.quiz, { id: unit.id, correct: 10, total: 15, passed: false });
  assert.equal(quizResult(state, unit.id).passedAt, null);
  // Segundo intento aprobado; un tercero peor no quita ni la mejor nota ni el aprobado
  play(createSession({ kind: "quiz", title: "C", exercises: unit.bank, meta: { quiz: unit.id } }), state, 12);
  const passedAt = quizResult(state, unit.id).passedAt;
  assert.ok(passedAt);
  play(createSession({ kind: "quiz", title: "C", exercises: unit.bank, meta: { quiz: unit.id } }), state, 3);
  assert.deepEqual({ ...quizResult(state, unit.id), at: null }, { best: 12, total: 15, last: 3, at: null, passedAt });
});

test("una práctica normal sí añade nuevos intentos y no guarda nota", () => {
  const state = fresh();
  const session = createSession({ kind: "practice", title: "P", exercises: unit.bank.slice(0, 3) });
  submit(session, index, state, { ok: false, error: null }, NOW);
  assert.equal(session.queue.length, 4);
  assert.equal(state.quizzes, undefined);
});

test("la evaluación final tiene 3 preguntas del banco por unidad, una de cada nivel, en orden", () => {
  const ids = buildPooFinal(index, { random: seeded(7) });
  const units = availableUnits(index);
  assert.equal(ids.length, units.length * 3);
  assert.equal(new Set(ids).size, ids.length);
  units.forEach((u, i) => {
    const chunk = ids.slice(i * 3, i * 3 + 3).map((id) => index.exercises.get(id));
    assert.deepEqual(chunk.map((e) => e.level), [1, 2, 3]);
    for (const e of chunk) {
      assert.equal(e.concept, u.id);
      assert.ok(index.concepts.get(u.id).bank.includes(e.id));
    }
  });
  // Al azar: otra semilla da otra selección
  assert.notDeepEqual(buildPooFinal(index, { random: seeded(99) }), ids);
});

test("la evaluación final no corrige hasta el final y las preguntas sin responder cuentan como falladas", () => {
  const state = fresh();
  const ids = buildPooFinal(index, { random: seeded(3) });
  const session = createSession({ kind: "final", title: "Final", exercises: ids, meta: { quiz: FINAL_ID } });
  assert.equal(session.feedback, false);
  for (let i = 0; i < 25; i += 1) submit(session, index, state, { ok: i < 22, error: null }, NOW);
  session.phase = "done"; // el alumno pulsa «Terminar la evaluación»
  const summary = finish(session, index, state, NOW);
  assert.deepEqual(summary.quiz, { id: FINAL_ID, correct: 22, total: 30, passed: true });
  assert.equal(quizResult(state, FINAL_ID).best, 22);
  // Cada unidad trabajada recibe su fecha de repaso
  assert.ok(Object.keys(summary.byConcept).every((id) => state.concepts[id].due));
});

test("los resultados de los cuestionarios sobreviven a la limpieza y se descartan si están manipulados", () => {
  const state = fresh();
  recordQuiz(state, "poo", 12, 15, NOW);
  recordQuiz(state, "<script>", 1, 15, NOW);
  recordQuiz(state, "poo-x", 16, 15, NOW);
  const clean = cleanLearning(JSON.parse(JSON.stringify(state)));
  assert.deepEqual(Object.keys(clean.quizzes), ["poo"]);
  const bad = cleanLearning({ v: 1, quizzes: { poo: { best: 20, total: 15, last: 1, at: NOW.toISOString() }, "poo-herencia": { best: 1, total: 15, last: 1, at: "ayer" } } });
  assert.equal("quizzes" in bad, false);
});

test("al fusionar dos dispositivos se queda la mejor nota, el último intento y el primer aprobado", () => {
  const a = fresh();
  const b = fresh();
  recordQuiz(a, "poo", 13, 15, NOW);
  recordQuiz(b, "poo", 9, 15, later(1));
  recordQuiz(b, FINAL_ID, 20, 30, later(1));
  const merged = mergeLearning(JSON.parse(JSON.stringify(a)), b);
  assert.equal(merged.quizzes.poo.best, 13);
  assert.equal(merged.quizzes.poo.last, 9);
  assert.equal(merged.quizzes.poo.passedAt, NOW.toISOString());
  assert.equal(merged.quizzes[FINAL_ID].best, 20);
  // Una copia sin cuestionarios no borra nada
  assert.deepEqual(mergeLearning(JSON.parse(JSON.stringify(a)), fresh()).quizzes, a.quizzes);
});

test("la unidad muestra la nota, el repaso de las falladas y el cuestionario en los criterios de superación", () => {
  const state = fresh();
  const stats = () => allStats(index, state, NOW).get(unit.id);
  let html = unitBody(index, state, unit, stats());
  assert.match(html, /se supera con 11 aciertos o más/);
  assert.match(html, /Aún no lo has hecho/);
  assert.match(html, /Cuestionario de la unidad: sin hacer \(se piden 11 aciertos\)/);
  assert.doesNotMatch(html, /data-learn="bank-review"/);
  play(createSession({ kind: "quiz", title: "C", exercises: unit.bank, meta: { quiz: unit.id } }), state, 11);
  assert.deepEqual(failedBank(state, unit), unit.bank.slice(11));
  html = unitBody(index, state, unit, stats());
  assert.match(html, /Superado<\/span>\s*Mejor nota: <strong>11 de 15<\/strong>/);
  assert.match(html, /Repasar las 4 preguntas falladas/);
  assert.match(html, /<li data-done="true">✓ Cuestionario de la unidad: mejor nota 11 de 15/);
});

test("el índice del módulo ofrece la evaluación final de 30 preguntas y cuenta los cuestionarios superados", () => {
  const state = fresh();
  recordQuiz(state, "poo", 15, 15, NOW);
  const html = renderModule(index, state, NOW);
  assert.match(html, /Evaluación final del módulo/);
  assert.match(html, /data-learn="poo-final">Empezar la evaluación final \(30 preguntas\)/);
  assert.match(html, /Se supera con 21 aciertos o más/);
  assert.match(html, /llevas 1 de 10/);
  assert.match(html, /<dt>Cuestionarios superados<\/dt><dd>1 de 10<\/dd>/);
});

test("el cuestionario de la unidad baraja sus 15 preguntas sin perder ni repetir ninguna", () => {
  const order = shuffle(unit.bank, seeded(5));
  assert.notDeepEqual(order, unit.bank);
  assert.deepEqual([...order].sort(), [...unit.bank].sort());
  assert.deepEqual(unit.bank, index.concepts.get("poo-herencia").bank, "no cambia el banco original");
});
