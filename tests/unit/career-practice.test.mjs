import assert from "node:assert/strict";
import { test } from "node:test";
import { cleanPracticeEntry, cleanPracticeMap, mergePractice, practiceStats, setPractice } from "../../frontend/js/career/career-practice.js";

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
