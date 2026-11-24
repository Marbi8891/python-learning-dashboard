import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
const read=(path)=>readFileSync(new URL(path,import.meta.url),"utf8");
test("AI Academy is wired into app routing and view registry",()=>{
 const app=read("../../frontend/js/app.js");
 const html=read("../../frontend/index.html");
 assert.match(app,/aiacademy: \(load\) => load\("\.\/ai-academy\.js"\)/);
 assert.match(app,/aiacademy: \{ element: "#ai-academy-view".*render: \(\) => renderAIacademy\(location\.hash\)/);
 assert.match(app,/location\.hash === "#\/ai-academy" \|\| location\.hash\.startsWith\("#\/ai-academy\/"\)/);
 assert.match(html,/id="ai-academy-view"/);
 assert.match(html,/href="#\/ai-academy" data-nav="ai-academy"/);
});
