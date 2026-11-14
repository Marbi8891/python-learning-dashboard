import test from "node:test";
import assert from "node:assert/strict";
import { DEVOPS_COURSE } from "../../frontend/js/devops-content.js";

test("el itinerario DevOps contiene cuatro semanas y ocho lecciones", () => {
  assert.equal(DEVOPS_COURSE.weeks.length, 4);
  assert.equal(DEVOPS_COURSE.weeks.reduce((total, week) => total + week.lessons.length, 0), 8);
});

test("cada lección tiene objetivos prácticos, quiz y fuentes", () => {
  const slugs = new Set();
  for (const week of DEVOPS_COURSE.weeks) {
    for (const lesson of week.lessons) {
      assert.match(lesson.slug, /^[a-z0-9-]+$/);
      assert.equal(slugs.has(lesson.slug), false, `slug duplicado: ${lesson.slug}`);
      slugs.add(lesson.slug);
      assert.ok(lesson.title && lesson.theory && lesson.example && lesson.task && lesson.deliverable);
      assert.ok(lesson.quiz.length >= 3);
      assert.ok(lesson.sources.length >= 1);
      for (const question of lesson.quiz) {
        assert.ok(question.options.length >= 2);
        assert.ok(question.answer >= 0 && question.answer < question.options.length);
        assert.ok(question.explain);
      }
      for (const source of lesson.sources) assert.match(source.url, /^https:\/\//);
    }
  }
});
