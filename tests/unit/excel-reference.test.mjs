// Casos de referencia del motor de fórmulas (tests/fixtures/excel/reference-cases.json): ≥ 150 casos
// con fuente independiente del motor (LibreOffice 24.2, regla documentada de Excel o regla propia
// del motor especificada en docs/excel-academy/FORMULA_ENGINE_SPEC.md). La e2e repite los mismos
// casos en el navegador.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import { evaluate, parseFormula } from "../../frontend/js/excel/formula/index.js";
import { matches } from "./excel-helpers.mjs";

const { cases } = JSON.parse(readFileSync(new URL("../fixtures/excel/reference-cases.json", import.meta.url), "utf8"));

test("hay al menos 150 casos de referencia, con id único y fuente", () => {
  assert.ok(cases.length >= 150, `solo hay ${cases.length}`);
  assert.equal(new Set(cases.map((c) => c.id)).size, cases.length);
  for (const c of cases) assert.ok(["libreoffice", "regla", "motor"].includes(c.source), c.id);
  for (const c of cases.filter((c) => c.source !== "libreoffice")) assert.ok(c.note, `${c.id}: falta la nota con la fuente`);
});

for (const c of cases) {
  test(`${c.id}: ${c.formula}`, () => {
    const result = evaluate(parseFormula(c.formula), { grid: c.grid ?? {}, at: c.at ?? null, sheet: c.sheet });
    assert.ok(matches(result, c.expect), `da ${JSON.stringify(result)} y se esperaba ${JSON.stringify(c.expect)}`);
  });
}
