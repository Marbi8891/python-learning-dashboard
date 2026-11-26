import assert from "node:assert/strict";
import { test } from "node:test";
import { pathProgress } from "../../frontend/js/paths-progress.js";
import { AI_ACADEMY_COURSES, aiCourseLessons } from "../../frontend/js/ai-academy-data.js";

const saved = new Map();
globalThis.localStorage = {
  getItem: (key) => saved.has(key) ? JSON.stringify(saved.get(key)) : null,
  setItem: () => { throw new Error("Learning Paths must not write progress"); },
};
const lessons = (prefix) => ({ modules: [{ lessons: [{ slug: `${prefix}-1` }, { slug: `${prefix}-2` }] }] });
const json = (data) => ({ ok: true, json: async () => data });
globalThis.fetch = async (url) => {
  if (url === "data/learning.json") return json({ concepts: [{ id: "c1" }, { id: "c2" }, { id: "c3" }] });
  if (url === "data/cybersecurity/course.json") return json({ weeks: [{ id: "semana-01" }, { id: "semana-02" }] });
  if (url === "data/academia/excel/lessons.json") return json(lessons("excel"));
  if (url.startsWith("data/courses/")) return json(lessons(url.split("/")[2]));
  throw new Error(`Unexpected fetch: ${url}`);
};

test("Python Path aggregates existing concept read/mastery without creating storage", async () => {
  saved.set("pld:learn", { concepts: { c1: { read: "2026-01-01" }, c2: { box: 2 }, c3: { box: 1 } } });
  const result = await pathProgress("python-developer");
  assert.deepEqual(result, { done: 2, total: 3, label: "conceptos", percent: 67 });
});

test("DAW and Web Paths read the same course lesson completion store", async () => {
  saved.set("pld:course:programacion", { done: { "programacion-1": "2026-01-01" } });
  saved.set("pld:course:js", { done: { "js-2": "2026-01-02" } });
  const daw = await pathProgress("daw-developer");
  const web = await pathProgress("web-developer");
  assert.deepEqual(daw, { done: 2, total: 12, label: "lecciones DAW", percent: 17 });
  assert.deepEqual(web, { done: 1, total: 4, label: "lecciones web", percent: 25 });
});

test("Excel Path reads the existing Excel course state", async () => {
  saved.set("pld:course:excel", { done: { "excel-2": "2026-01-02" } });
  assert.deepEqual(await pathProgress("excel-professional"), { done: 1, total: 2, label: "unidades Excel", percent: 50 });
});

test("Cybersecurity Path aggregates the existing week store", async () => {
  saved.set("pld:cybersecurity:v1", { weeks: { "semana-01": { done: true } } });
  assert.deepEqual(await pathProgress("cybersecurity"), { done: 1, total: 2, label: "semanas", percent: 50 });
});

test("AI Engineer Path counts only valid existing Academy lesson IDs", async () => {
  const course = AI_ACADEMY_COURSES[0];
  const first = aiCourseLessons(course)[0];
  const total = AI_ACADEMY_COURSES.reduce((sum, item) => sum + aiCourseLessons(item).length, 0);
  saved.set("pld:ai-academy:progress", { [course.id]: [first.id, "not-a-real-lesson", first.id] });
  assert.deepEqual(await pathProgress("ai-engineer"), { done: 1, total, label: "temas IA", percent: Math.round(100 / total) });
});
