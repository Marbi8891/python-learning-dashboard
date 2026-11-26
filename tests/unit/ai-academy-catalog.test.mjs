import test from "node:test";
import assert from "node:assert/strict";
import { AI_ACADEMY_TRACKS, AI_ACADEMY_COURSES, aiCourseById, aiCourseLessons } from "../../frontend/js/ai-academy-data.js";

test("AI Academy contains the full 20-course catalogue", () => {
  assert.equal(AI_ACADEMY_COURSES.length, 20);
  assert.equal(new Set(AI_ACADEMY_COURSES.map((course) => course.id)).size, 20);
});
test("each course has hours, description, modules and unique lesson IDs", () => {
  for (const course of AI_ACADEMY_COURSES) {
    assert.ok(course.hours > 0, course.id);
    assert.ok(course.description.length > 20, course.id);
    assert.ok(course.modules.length > 0, course.id);
    assert.ok(aiCourseLessons(course).length > 0, course.id);
    assert.equal(new Set(aiCourseLessons(course).map((lesson) => lesson.id)).size, aiCourseLessons(course).length, course.id);
  }
});
test("track references resolve to existing courses", () => {
  for (const track of AI_ACADEMY_TRACKS) {
    assert.ok(track.courseIds.length);
    for (const id of track.courseIds) assert.ok(aiCourseById(id), `Missing ${id} in ${track.id}`);
  }
});
test("the capstone is the final course and project pathway", () => {
  assert.equal(AI_ACADEMY_COURSES.at(-1).id, "ai-20");
  assert.equal(AI_ACADEMY_TRACKS.find((track) => track.id === "capstone").courseIds[0], "ai-20");
});
