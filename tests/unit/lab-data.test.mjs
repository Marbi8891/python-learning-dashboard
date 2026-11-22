import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { LAB_EXAMPLES, LAB_TOPICS, exerciseFromRoute, labExamples, labExercises, shortTitle } from "../../frontend/js/lab/lab-data.js";

const read = (path) => JSON.parse(readFileSync(new URL(`../../frontend/data/${path}`, import.meta.url), "utf-8"));
const lessons = read("lessons.json");
const learning = read("learning.json");

test("el laboratorio cubre los ocho temas pedidos, cada uno con algún ejercicio", () => {
  assert.deepEqual(
    LAB_TOPICS.map((t) => t.id),
    ["variables", "tipos", "condicionales", "bucles", "funciones", "listas", "diccionarios", "poo"],
  );
  const list = labExercises(lessons, learning);
  for (const topic of LAB_TOPICS) assert.ok(list.some((e) => e.topic === topic.id), topic.id);
});

test("cada ejercicio del laboratorio existe en el temario y tiene pruebas reales", () => {
  const lessonSlugs = new Set(lessons.modules.flatMap((m) => m.lessons.map((l) => l.slug)));
  const codeExercises = new Map(learning.exercises.filter((e) => e.kind === "code").map((e) => [e.id, e]));
  for (const topic of LAB_TOPICS) {
    for (const slug of topic.lessons) assert.ok(lessonSlugs.has(slug), `lección ${slug}`);
    for (const id of topic.exercises) assert.ok(codeExercises.has(id), `ejercicio de código ${id}`);
  }
  const list = labExercises(lessons, learning);
  assert.equal(list.length, LAB_TOPICS.reduce((n, t) => n + t.lessons.length + t.exercises.length, 0));
  assert.equal(new Set(list.map((e) => e.id)).size, list.length);
  for (const e of list) {
    assert.ok(e.checks.length > 0, e.id);
    assert.ok(e.checks.every((c) => typeof c.test === "string"), e.id);
    assert.ok(e.statement && e.title, e.id);
  }
});

test("los ejemplos son el código de ejemplo de lecciones que se ejecutan en el navegador", () => {
  const examples = labExamples(lessons);
  assert.ok(examples.length >= 5);
  assert.ok(examples.every((e) => LAB_EXAMPLES.includes(e.slug) && e.code.length > 0));
});

test("la ruta elige el ejercicio, y una desconocida no elige ninguno", () => {
  const list = labExercises(lessons, learning);
  assert.equal(exerciseFromRoute("#/laboratorio/ejercicio-dic-04", list).ref, "dic-04");
  assert.equal(exerciseFromRoute("#/laboratorio/no-existe", list), null);
  assert.equal(exerciseFromRoute("#/laboratorio", list), null);
});

test("shortTitle quita las marcas de Markdown, conserva los nombres con _ y recorta", () => {
  assert.equal(shortTitle("**Ejercicio:** usa `media_positivos(x)`"), "Ejercicio: usa media_positivos(x)");
  assert.equal(shortTitle("\n\n# Título"), "Título");
  assert.equal(shortTitle("a".repeat(100), 10), `${"a".repeat(9)}…`);
  assert.equal(shortTitle(undefined), "");
});
