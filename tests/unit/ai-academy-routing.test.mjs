import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");

test("AI Academy and PLD ACADEMY are wired into lazy routing and views", () => {
  const app = read("../../frontend/js/app.js");
  const html = read("../../frontend/index.html");

  assert.match(app, /aiacademy: \(load\) => load\("\.\/ai-academy\.js"\)/);
  assert.match(app, /aiacademy: \{ element: "#ai-academy-view".*render: \(\) => renderAIacademy\(location\.hash\)/);
  assert.match(app, /location\.hash === "#\/ai-academy" \|\| location\.hash\.startsWith\("#\/ai-academy\/"\)/);
  assert.match(app, /academy: \(load\) => load\("\.\/academy-institutional\.js"\)/);
  assert.match(app, /academyInfo: \{ element: "#academy-info-view".*render: \(\) => renderAcademyInfo\(\)/);
  assert.match(app, /location\.hash === ACADEMY_INFO_ROUTE/);
  assert.match(app, /location\.hash === ACADEMY_ROUTE/);
  assert.match(html, /id="ai-academy-view"/);
  assert.match(html, /href="#\/ai-academy" data-nav="ai-academy"/);
  assert.match(html, /id="academy-info-view"/);
  assert.match(html, /id="academy-view"/);
  assert.match(html, /href="#\/academy-info" data-nav="academy"/);
});
