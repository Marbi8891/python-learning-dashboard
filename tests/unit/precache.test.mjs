import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { OUT, precacheList, precacheSource } from "../../scripts/web/build_precache.mjs";

test("precache.js está al día con los archivos de la web (AUD-008)", () => {
  assert.equal(readFileSync(OUT, "utf8"), precacheSource(), "ejecuta node scripts/web/build_precache.mjs");
});

test("precache incluye lo necesario para estudiar sin conexión y nada privado", () => {
  const list = precacheList();
  for (const file of ["./", "index.html", "js/app.js", "js/learn/learn-app.js", "js/srs.js", "data/learning.json", "data/pcap.json", "py/runner.py"]) {
    assert.ok(list.includes(file), file);
  }
  assert.ok(list.some((f) => f.startsWith("data/courses/")));
  assert.ok(!list.some((f) => f.includes("_pyo") || f.endsWith("package.json") || f.includes(".env")));
});
