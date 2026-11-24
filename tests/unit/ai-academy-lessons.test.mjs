import test from "node:test";
import assert from "node:assert/strict";
import { AI_LESSONS } from "../../frontend/js/ai-academy-lessons.js";
import { AI_ACADEMY_COURSES, aiCourseLessons } from "../../frontend/js/ai-academy-data.js";

test("AI Foundations course has eight authored lessons",()=>{
 const lessons=Object.values(AI_LESSONS).filter(x=>x.courseId==="ai-01");
 assert.equal(lessons.length,8);
 assert.equal(aiCourseLessons(AI_ACADEMY_COURSES[0]).length,8);
});
test("authored lesson content has objectives, sections and quiz validation",()=>{
 for(const [id,lesson] of Object.entries(AI_LESSONS)){
  assert.ok(lesson.title,id);
  assert.ok(lesson.objectives.length>=2,id);
  assert.ok(lesson.sections.length>=2,id);
  assert.ok(lesson.quiz.options.length>=3,id);
  assert.ok(lesson.quiz.answer>=0&&lesson.quiz.answer<lesson.quiz.options.length,id);
  assert.ok(lesson.example.input.length>10,id);
 }
});
