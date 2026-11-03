// Progreso por lección de los cursos de DAW: completar, última lección y fusión sin perder datos.
import assert from "node:assert/strict";
import { test } from "node:test";
import { cleanDone, cleanLastLesson, completedCount, completeLesson, mergeLessonProgress, visitLesson } from "../../frontend/js/lesson-progress.js";
import { cleanProgress } from "../../frontend/js/progress-guard.js";

const T1 = "2026-11-01T10:00:00.000Z";
const T2 = "2026-11-02T10:00:00.000Z";

test("completar una lección es idempotente: la segunda vez no cambia la fecha", () => {
  const course = { done: {} };
  assert.equal(completeLesson(course, "mar-html-css", T1), true);
  assert.equal(completeLesson(course, "mar-html-css", T2), false);
  assert.deepEqual(course.done, { "mar-html-css": T1 });
});

test("la fusión es una unión: una copia vacía o parcial no borra lecciones completadas", () => {
  const local = { done: { a: T2, b: T1 }, lastLesson: { slug: "b", at: T2 } };
  mergeLessonProgress(local, {}); // la cuenta aún no tiene el campo (cuenta antigua)
  assert.deepEqual(local.done, { a: T2, b: T1 });
  assert.deepEqual(local.lastLesson, { slug: "b", at: T2 });

  mergeLessonProgress(local, { done: { a: T1, c: T2 } });
  assert.deepEqual(local.done, { a: T1, b: T1, c: T2 }, "se conserva la fecha más antigua de cada lección");
});

test("la última lección estudiada es la más reciente de las dos copias", () => {
  const local = { done: {}, lastLesson: { slug: "a", at: T1 } };
  mergeLessonProgress(local, { lastLesson: { slug: "b", at: T2 } });
  assert.deepEqual(local.lastLesson, { slug: "b", at: T2 });
  mergeLessonProgress(local, { lastLesson: { slug: "c", at: T1 } });
  assert.deepEqual(local.lastLesson, { slug: "b", at: T2 });
  const empty = { done: {} };
  mergeLessonProgress(empty, { lastLesson: { slug: "c", at: T1 } });
  assert.deepEqual(empty.lastLesson, { slug: "c", at: T1 });
});

test("visitar la misma lección no obliga a guardar otra vez", () => {
  const course = { lastLesson: null };
  assert.equal(visitLesson(course, "a", T1), true);
  assert.equal(visitLesson(course, "a", T2), false);
  assert.equal(visitLesson(course, "b", T2), true);
  assert.deepEqual(course.lastLesson, { slug: "b", at: T2 });
});

test("se descartan los datos manipulados: ids raros, fechas inválidas o HTML", () => {
  assert.deepEqual(cleanDone({ ok: T1, "<img src=x>": T1, mal: "ayer", num: 3 }), { ok: T1 });
  assert.deepEqual(cleanDone(["a"]), {});
  assert.equal(cleanLastLesson({ slug: "<b>", at: T1 }), null);
  assert.equal(cleanLastLesson({ slug: "a", at: "hoy" }), null);
  assert.equal(cleanLastLesson("a"), null);
  const clean = cleanProgress({ done: { a: T1, "x y": T1 }, lastLesson: { slug: "a", at: T1, extra: "<script>" } });
  assert.deepEqual(clean.done, { a: T1 });
  assert.deepEqual(clean.lastLesson, { slug: "a", at: T1 });
  assert.equal("done" in cleanProgress({ answers: {} }), false, "sin el campo no se añade nada");
});

test("cuenta solo las lecciones del curso que están completadas", () => {
  assert.equal(completedCount({ done: { a: T1, z: T1 } }, ["a", "b", "c"]), 1);
  assert.equal(completedCount({}, ["a"]), 0);
});
