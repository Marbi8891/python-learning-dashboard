// Progreso del curso de ciberseguridad (cybersecurity-data.js): formato, migración y fusión.
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  LEGACY_AT,
  cleanCyber,
  completedWeeks,
  isWeekDone,
  mergeCyber,
  quizScore,
  setQuizScore,
  toggleWeek,
} from "../../frontend/js/cybersecurity-data.js";

const T1 = new Date("2026-11-20T10:00:00.000Z");
const T2 = new Date("2026-11-20T11:00:00.000Z");

test("lee el formato anterior (sin fechas) sin perder nada", () => {
  const doc = cleanCyber({ completed: ["semana-01", "semana-02"], quizScores: { "semana-01": 3, "semana-02": 2 } });
  assert.deepEqual(doc.weeks, {
    "semana-01": { done: true, at: LEGACY_AT },
    "semana-02": { done: true, at: LEGACY_AT },
  });
  assert.equal(quizScore(doc, "semana-01"), 3);
  assert.equal(completedWeeks(doc), 2);
  assert.ok(!("completed" in doc) && !("quizScores" in doc));
});

test("descarta lo que no es válido y conserva los campos que no conoce (DEC-007)", () => {
  const doc = cleanCyber({
    v: 2,
    weeks: { "semana-01": { done: "sí", at: T1.toISOString() }, "otra": { done: true, at: T1.toISOString() }, "semana-02": { done: true, at: "ayer" } },
    quiz: { "semana-01": { score: 4, at: T1.toISOString() }, "semana-03": { score: 1, at: "2026-11-20T10:00:00Z" } },
    notas: { futuro: true },
  });
  assert.deepEqual(doc.weeks, {});
  // La fecha se normaliza para que se pueda comparar como texto
  assert.deepEqual(doc.quiz, { "semana-03": { score: 1, at: T1.toISOString() } });
  assert.deepEqual(doc.notas, { futuro: true });
  for (const raw of [null, "x", [], 7]) assert.deepEqual(cleanCyber(raw), { v: 2, weeks: {}, quiz: {} });
});

test("solo se completa una semana con el cuestionario superado, y se puede desmarcar", () => {
  const doc = cleanCyber(null);
  toggleWeek(doc, "semana-01", T1);
  assert.equal(isWeekDone(doc, "semana-01"), false);
  setQuizScore(doc, "semana-01", 1, T1);
  toggleWeek(doc, "semana-01", T1);
  assert.equal(isWeekDone(doc, "semana-01"), false);
  setQuizScore(doc, "semana-01", 2, T1);
  toggleWeek(doc, "semana-01", T1);
  assert.equal(isWeekDone(doc, "semana-01"), true);
  toggleWeek(doc, "semana-01", T2);
  assert.deepEqual(doc.weeks["semana-01"], { done: false, at: T2.toISOString() });
  setQuizScore(doc, "no-es-semana", 3, T1);
  setQuizScore(doc, "semana-02", 9, T1);
  assert.deepEqual(Object.keys(doc.quiz), ["semana-01"]);
});

test("al fusionar gana el cambio más reciente: desmarcar en otro dispositivo no se deshace", () => {
  const local = cleanCyber({ weeks: { "semana-01": { done: true, at: T1.toISOString() } } });
  const remote = { weeks: { "semana-01": { done: false, at: T2.toISOString() } } };
  assert.equal(mergeCyber(local, remote), true);
  assert.equal(isWeekDone(local, "semana-01"), false);

  // Y al revés: una copia más antigua no pisa la de aquí
  const newer = cleanCyber({ weeks: { "semana-01": { done: true, at: T2.toISOString() } } });
  assert.equal(mergeCyber(newer, { weeks: { "semana-01": { done: false, at: T1.toISOString() } } }), false);
  assert.equal(isWeekDone(newer, "semana-01"), true);
});

test("la fusión junta las dos copias y no depende del orden", () => {
  const a = { weeks: { "semana-01": { done: true, at: T1.toISOString() } }, quiz: { "semana-01": { score: 2, at: T1.toISOString() } } };
  const b = { completed: ["semana-02"], quizScores: { "semana-01": 3, "semana-02": 2 }, extra: 1 };
  const ab = cleanCyber(a);
  mergeCyber(ab, b);
  const ba = cleanCyber(b);
  mergeCyber(ba, a);
  assert.deepEqual(ab.weeks, ba.weeks);
  assert.deepEqual(ab.quiz, ba.quiz);
  assert.equal(completedWeeks(ab), 2);
  // El resultado con fecha es más reciente que el del formato anterior
  assert.equal(quizScore(ab, "semana-01"), 2);
  assert.equal(ab.extra, 1);

  // Con la misma fecha (dos copias del formato anterior) se queda lo que conserva más progreso
  const old = cleanCyber({ quizScores: { "semana-04": 1 } });
  mergeCyber(old, { completed: ["semana-04"], quizScores: { "semana-04": 3 } });
  assert.equal(isWeekDone(old, "semana-04"), true);
  assert.equal(quizScore(old, "semana-04"), 3);
});

test("fusionar con la misma copia no cuenta como cambio (no se repinta)", () => {
  const doc = cleanCyber({ weeks: { "semana-01": { done: true, at: T1.toISOString() } } });
  assert.equal(mergeCyber(doc, structuredClone(doc)), false);
  assert.equal(mergeCyber(doc, null), false);
});
