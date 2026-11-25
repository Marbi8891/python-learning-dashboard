import assert from "node:assert/strict";
import { test } from "node:test";
import { cleanPracticeEntry, cleanPracticeMap, mergePractice, practiceStats, setPractice } from "../../frontend/js/career/career-practice.js";\nimport { cleanCareer, emptyCareer, enroll, mergeCareer } from "../../frontend/js/career/career-data.js";

const NOW = new Date("2026-11-25T12:00:00.000Z");

test("practice completion and evidence are validated and saved", () => {
  const progress = {};
  assert.equal(setPractice(progress, "m4-practice-01", { done: true, url: "https://github.com/user/repo", note: "Tests passed" }, NOW), true);
  assert.deepEqual(progress.practice["m4-practice-01"], {
    done: true, url: "https://github.com/user/repo", note: "Tests passed", at: NOW.toISOString(),
  });
  assert.equal(setPractice(progress, "invalid id", { done: true }, NOW), false);
});

test("practice sanitizer rejects unsafe links and bounds notes", () => {
  const clean = cleanPracticeEntry({ done: false, url: "javascript:alert(1)", note: "x".repeat(1200), at: NOW.toISOString() });
  assert.equal(clean.url, null);
  assert.equal(clean.note.length, 1000);
  assert.equal(clean.done, false);
  assert.equal(cleanPracticeEntry({ done: "yes", at: NOW.toISOString() }), null);
});

test("clean practice map ignores malformed keys and entries", () => {
  const map = cleanPracticeMap({
    "practice-1": { done: true, url: "https://example.com", note: "", at: NOW.toISOString() },
    "bad key": { done: true, at: NOW.toISOString() },
    "practice-2": { done: true, at: "not-a-date" },
  });
  assert.deepEqual(Object.keys(map), ["practice-1"]);
});

test("merge uses the latest timestamp and preserves other activities", () => {
  const local = { "practice-1": { done: false, url: null, note: "", at: "2026-11-20T00:00:00.000Z" } };
  const remote = {
    "practice-1": { done: true, url: "https://example.com", note: "done", at: "2026-11-21T00:00:00.000Z" },
    "practice-2": { done: true, url: null, note: "", at: "2026-11-22T00:00:00.000Z" },
  };
  mergePractice(local, remote);
  assert.equal(local["practice-1"].done, true);
  assert.equal(local["practice-2"].done, true);
});

test("practice progress stats handle empty and completed lists", () => {
  assert.deepEqual(practiceStats([], {}), { total: 0, done: 0, remaining: 0, ratio: 0 });
  assert.deepEqual(practiceStats([{ id: "a" }, { id: "b" }], { a: { done: true } }), { total: 2, done: 1, remaining: 1, ratio: 0.5 });
});

test("career document retains and validates practice progress", () => {
  const doc = emptyCareer();
  const progress = enroll(doc, "applied-ai-engineer", NOW);
  setPractice(progress, "practice-1", { done: true, note: "Evidence stored" }, NOW);
  const cleaned = cleanCareer(doc);
  assert.equal(cleaned.roadmaps["applied-ai-engineer"].practice["practice-1"].done, true);
  assert.equal(cleaned.roadmaps["applied-ai-engineer"].practice["practice-1"].note, "Evidence stored");
});

test("career sync merge combines practice records by last update", () => {
  const local = emptyCareer();
  const lp = enroll(local, "applied-ai-engineer", NOW);
  setPractice(lp, "practice-1", { done: false }, new Date("2026-11-20T00:00:00Z"));
  const remote = emptyCareer();
  const rp = enroll(remote, "applied-ai-engineer", NOW);
  setPractice(rp, "practice-1", { done: true, note: "remote" }, new Date("2026-11-21T00:00:00Z"));
  setPractice(rp, "practice-2", { done: true }, new Date("2026-11-22T00:00:00Z"));
  mergeCareer(local, remote);
  assert.equal(local.roadmaps["applied-ai-engineer"].practice["practice-1"].done, true);
  assert.equal(local.roadmaps["applied-ai-engineer"].practice["practice-2"].done, true);
});
