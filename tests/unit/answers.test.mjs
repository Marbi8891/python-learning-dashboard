import assert from "node:assert/strict";
import { test } from "node:test";
import { codeResult, errorsTested, grade, missingAnswer, normalizeOutput } from "../../frontend/js/learn/answers.js";
import { index } from "./helpers.mjs";

const ex = (id) => index.exercises.get(id);

test("normalizeOutput ignora espacios al final de línea y saltos finales, no los del principio", () => {
  assert.equal(normalizeOutput("a  \r\nb\n\n"), "a\nb");
  assert.equal(normalizeOutput("  a"), "  a");
});

test("choice: acierto y error típico de la opción elegida", () => {
  const e = ex("var-04");
  assert.deepEqual(grade(e, { choice: e.answer }), { ok: true, error: null });
  assert.deepEqual(grade(e, { choice: 1 }), { ok: false, error: "variables.asigna-compara" });
});

test("output: acepta la salida con espacios sobrantes y reconoce las trampas", () => {
  const e = ex("buc-01"); // 2 3 4 5
  assert.equal(grade(e, { text: "2 3 4 5  \n" }).ok, true);
  assert.deepEqual(grade(e, { text: "2 3 4 5 6" }), { ok: false, error: "bucles.range-fin" });
  assert.deepEqual(grade(e, { text: "otra cosa" }), { ok: false, error: null });
});

test("fill: ignora espacios y reconoce la trampa", () => {
  const e = ex("buc-06");
  assert.equal(grade(e, { text: " 6 " }).ok, true);
  assert.equal(grade(e, { text: "5" }).error, "bucles.range-fin");
});

test("order: compara los textos de las líneas", () => {
  const e = ex("pse-05");
  assert.equal(grade(e, { order: [0, 1, 2, 3] }).ok, true);
  assert.deepEqual(grade(e, { order: [0, 1, 3, 2] }), { ok: false, error: "pseudocodigo.orden-pasos" });
});

test("bug: la línea correcta y el error que ilustra", () => {
  const e = ex("acu-02");
  assert.equal(grade(e, { line: 1 }).ok, true);
  assert.deepEqual(grade(e, { line: 3 }), { ok: false, error: "acumuladores.producto-cero" });
});

test("code: el caso que falla indica el error típico", () => {
  const e = ex("acu-04");
  assert.deepEqual(codeResult(e, { passed: false, case: 3 }), { ok: false, error: "acumuladores.media-dentro" });
  assert.deepEqual(codeResult(e, { passed: true, case: 4 }), { ok: true, error: null });
  assert.throws(() => grade(e, {}));
});

test("missingAnswer pide completar antes de corregir", () => {
  assert.equal(missingAnswer(ex("var-04"), {}), "Elige una respuesta.");
  assert.equal(missingAnswer(ex("buc-01"), { text: "  " }), "Escribe lo que crees que muestra el programa.");
  assert.equal(missingAnswer(ex("pse-05"), { order: [0] }), "Coloca todas las líneas.");
  assert.equal(missingAnswer(ex("var-04"), { choice: 0 }), null);
});

test("errorsTested reúne los errores de opciones, trampas, tests y bug sin repetir", () => {
  assert.deepEqual(errorsTested(ex("acu-02")), ["acumuladores.producto-cero"]);
  assert.ok(errorsTested(ex("acu-04")).includes("acumuladores.media-dentro"));
});

test("todo el contenido es coherente: cada ejercicio corregible tiene respuesta alcanzable", () => {
  for (const e of index.data.exercises) {
    if (e.kind === "choice") assert.equal(grade(e, { choice: e.answer }).ok, true, e.id);
    if (e.kind === "output") assert.equal(grade(e, { text: e.expect }).ok, true, e.id);
    if (e.kind === "fill") assert.equal(grade(e, { text: e.accept[0] }).ok, true, e.id);
    if (e.kind === "order") assert.equal(grade(e, { order: e.lines.map((_, i) => i) }).ok, true, e.id);
    if (e.kind === "bug") assert.equal(grade(e, { line: e.line }).ok, true, e.id);
  }
});
