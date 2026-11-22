import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { HUB_COURSES, courseCard, lessonHref, lessonsOf } from "../../frontend/js/hub/hub-data.js";

const read = (path) => JSON.parse(readFileSync(new URL(`../../frontend/data/${path}`, import.meta.url), "utf-8"));
const byId = (id) => HUB_COURSES.find((c) => c.id === id);

test("el centro presenta los siete cursos pedidos, en orden", () => {
  assert.deepEqual(
    HUB_COURSES.map((c) => c.title),
    ["Python", "PCAP", "Programación (DAW)", "JavaScript", "Java", "Bases de datos", "Ciberseguridad"],
  );
});

test("cada curso tiene lecciones reales en sus datos", () => {
  const data = {
    python: read("learning.json"),
    pcap: read("lessons.json"),
    ciberseguridad: read("cybersecurity/course.json"),
  };
  for (const course of HUB_COURSES) {
    const source = data[course.id] ?? read(`courses/${course.id}/lessons.json`);
    assert.ok(lessonsOf(course, source).length > 0, course.id);
  }
});

test("los enlaces de cada lección siguen las rutas de la web", () => {
  assert.equal(lessonHref(byId("python"), "variables"), "#/teoria/variables");
  assert.equal(lessonHref(byId("pcap"), "tipos"), "#/leccion/tipos");
  assert.equal(lessonHref(byId("js"), "js-variables"), "#/daw/js/leccion/js-variables");
  assert.equal(lessonHref(byId("ciberseguridad"), "semana-01"), "#/ciberseguridad/semana-01");
});

test("courseCard cuenta lo hecho, el porcentaje y la siguiente lección", () => {
  const lessons = [{ slug: "a", title: "A" }, { slug: "b", title: "B" }, { slug: "c", title: "C" }];
  const card = courseCard(byId("js"), lessons, (slug) => slug === "a");
  assert.equal(card.available, true);
  assert.equal(card.done, 1);
  assert.equal(card.total, 3);
  assert.equal(card.percent, 33);
  assert.equal(card.next.slug, "b");
  assert.equal(courseCard(byId("js"), lessons, () => true).next, null);
});

test("un curso sin lecciones sale como no disponible (En desarrollo), sin inventar datos", () => {
  const card = courseCard(byId("java"), lessonsOf(byId("java"), null), () => false);
  assert.equal(card.available, false);
  assert.equal(card.percent, 0);
});
