import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";

const course = JSON.parse(await readFile(new URL("../../frontend/data/cybersecurity/course.json", import.meta.url), "utf8"));

test("el curso tiene 16 semanas y 320 horas", () => {
  assert.equal(course.durationHours, 320);
  assert.equal(course.hoursPerWeek, 20);
  assert.equal(course.weeks.length, 16);
});

test("cada semana tiene objetivos, prácticas, entregables, evaluación y bibliografía", () => {
  for (const [index, week] of course.weeks.entries()) {
    assert.equal(week.number, index + 1);
    assert.match(week.id, /^semana-\d{2}$/);
    assert.ok(week.title.length > 5);
    assert.ok(week.goal.length > 15);
    assert.ok(week.topics.length >= 4);
    assert.ok(week.labs.length >= 3);
    assert.ok(week.deliverables.length >= 2);
    assert.ok(week.resources.length >= 2);
    assert.equal(week.quiz.length, 3);
  }
});

test("todas las preguntas tienen una respuesta válida", () => {
  for (const week of course.weeks) {
    for (const question of week.quiz) {
      assert.ok(question.question.length > 10);
      assert.ok(question.options.length >= 3);
      assert.ok(Number.isInteger(question.answer));
      assert.ok(question.answer >= 0 && question.answer < question.options.length);
    }
  }
});

test("la evaluación global suma 100 por ciento", () => {
  assert.equal(course.assessment.reduce((sum, item) => sum + item.weight, 0), 100);
});
