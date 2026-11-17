// Progreso de Excel profesional (frontend/js/excel/progress.js): «superada» frente a «completada».
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { courseSummary, unitQuestions, unitStatus } from "../../frontend/js/excel/progress.js";
import { verifyQuestion } from "../../frontend/js/excel/checks.js";

const bank = JSON.parse(readFileSync(new URL("../../frontend/data/academia/excel/bank.json", import.meta.url), "utf8"));
const { modules } = JSON.parse(readFileSync(new URL("../../frontend/data/academia/excel/lessons.json", import.meta.url), "utf8"));
const lessons = modules.flatMap((m) => m.lessons);

const QUESTIONS = [
  { id: "t1", kind: "choice" },
  { id: "t2", kind: "choice" },
  { id: "t3", kind: "choice" },
  { id: "t4", kind: "choice" },
  { id: "r1", kind: "formula-result" },
  { id: "f1", kind: "formula" },
  { id: "f2", kind: "formula" },
];
const PASS = { test: 0.8, required: ["f1"] };

test("sin respuestas, la unidad no está superada", () => {
  const status = unitStatus(QUESTIONS, {}, PASS);
  assert.deepEqual(status.test, { total: 5, answered: 0, correct: 0, rate: 0 });
  assert.deepEqual(status.required, { total: 1, done: 0, missing: ["f1"] });
  assert.equal(status.passed, false);
});

test("superada con el 80 % del test (último intento) y los obligatorios resueltos alguna vez", () => {
  const answers = { t1: [true], t2: [false, true], t3: [true], t4: [true], r1: [false], f1: [true, false] };
  const status = unitStatus(QUESTIONS, answers, PASS);
  assert.equal(status.test.correct, 4);
  assert.equal(status.test.rate, 0.8);
  assert.equal(status.required.done, 1, "un obligatorio resuelto una vez sigue contando");
  assert.equal(status.formulas.done, 1);
  assert.equal(status.passed, true);
});

test("no basta con el test: falta un obligatorio", () => {
  const answers = { t1: [true], t2: [true], t3: [true], t4: [true], r1: [true], f2: [true] };
  assert.equal(unitStatus(QUESTIONS, answers, PASS).passed, false);
});

test("el último intento manda en el test, y hay que responderlo todo", () => {
  const answers = { t1: [true, false], t2: [true], t3: [true], t4: [true], r1: [true], f1: [true] };
  assert.equal(unitStatus(QUESTIONS, answers, PASS).passed, true, "4 de 5 es el 80 %");
  const half = { t1: [true], t2: [true], t3: [true], t4: [true], f1: [true] };
  assert.equal(unitStatus(QUESTIONS, half, PASS).passed, false, "r1 sin responder");
});

test("completada (botón) y superada (criterios) se cuentan por separado", () => {
  const xl1 = unitQuestions(bank, "xl1-archivos");
  const answers = Object.fromEntries(xl1.map((q) => [q.id, [true]]));
  const summary = courseSummary(lessons, bank, { answers, done: { "xl1-interfaz": "2026-11-17T10:00:00.000Z" } });
  assert.deepEqual(summary, { units: 9, done: 1, passed: 1, questions: 111, solved: xl1.length });
});

test("cada ejercicio de fórmula publicado pasa la verificación del motor (mismo código que la web)", () => {
  for (const q of bank.questions.filter((item) => item.kind === "formula" || item.kind === "formula-result")) {
    assert.deepEqual(verifyQuestion({ id: q.id, kind: q.kind, q: q.q.es, ...q.excel }), [], q.id);
  }
});
