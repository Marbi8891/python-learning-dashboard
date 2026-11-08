// Validación HTML (html-validate) y CSS (stylelint) con la configuración del repositorio.
// Se comprueba que la web pasa y que la configuración detecta errores reales (no está vacía).
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import { HtmlValidate } from "html-validate";
import stylelint from "stylelint";

const root = new URL("../../", import.meta.url);
const htmlConfig = JSON.parse(readFileSync(new URL(".htmlvalidate.json", root), "utf8"));
const cssConfig = JSON.parse(readFileSync(new URL(".stylelintrc.json", root), "utf8"));
delete cssConfig["//"];

test("html-validate detecta HTML mal formado e ids repetidos", async () => {
  const report = await new HtmlValidate(htmlConfig).validateString(
    '<!doctype html><html lang="es"><head><title>x</title></head><body><div id="a"><span id="a">x</div></body></html>',
  );
  const rules = report.results.flatMap((r) => r.messages.map((m) => m.ruleId));
  assert.ok(rules.includes("no-dup-id"), rules.join());
  assert.ok(rules.some((r) => r.startsWith("close-")), rules.join());
});

test("stylelint detecta propiedades, unidades y colores que no existen", async () => {
  const { results } = await stylelint.lint({
    code: "a { colr: red; width: 10pz; color: #12345z; }\nb { color: red; color: blue; }",
    config: cssConfig,
  });
  const rules = new Set(results[0].warnings.map((w) => w.rule));
  for (const rule of [
    "property-no-unknown",
    "unit-no-unknown",
    "color-no-invalid-hex",
    "declaration-block-no-duplicate-properties",
  ]) {
    assert.ok(rules.has(rule), `${rule} no ha saltado: ${[...rules]}`);
  }
});
