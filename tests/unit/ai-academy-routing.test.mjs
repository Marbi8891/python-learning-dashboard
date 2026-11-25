import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("PLD ACADEMY institutional workspace is wired into lazy routing", () => {
  const app = read("../../frontend/js/app.js");
  const html = read("../../frontend/index.html");
  const academy = read("../../frontend/js/academy-institutional.js");

  assert.match(app, /academy: \(load\) => load\("\.\/academy-institutional\.js"\)/);
  assert.match(app, /academy: \{ element: "#academy-view".*render: \(\) => zones\.academy\.renderAcademy\(\)/);
  assert.ok(app.includes('location.hash === ACADEMY_ROUTE'));
  assert.match(app, /zones\.academy\.initAcademy\(\)/);
  assert.match(html, /id="academy-view"/);
  assert.match(html, /href="#\/academy" data-nav="academy"/);
  assert.match(academy, /export function initAcademy\(\)/);
  assert.match(academy, /academy-group-form/);
  assert.match(academy, /academy-assignment-form/);
});
