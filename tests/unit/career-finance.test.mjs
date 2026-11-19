import assert from "node:assert/strict";
import { test } from "node:test";
import {
  amount,
  cleanFinance,
  emptyFinance,
  exportFinance,
  FORMAT,
  importFinance,
  MAX_AMOUNT,
  mergeFinance,
  projection,
  setTargets,
  setYear,
} from "../../frontend/js/career/career-finance.js";

const NOW = new Date("2026-11-18T10:00:00Z");
const at = (iso) => new Date(iso);

test("no confunde facturación, beneficio y salario bruto", () => {
  const doc = emptyFinance();
  setTargets(doc, { combined: 70000, salary: 55000 }, NOW);
  setYear(doc, 2027, { salary: 26000, revenue: 12000, expenses: 4000 }, NOW);
  const [row] = projection(doc);
  assert.equal(row.profit, 8000, "beneficio = facturación − gastos");
  assert.equal(row.combined, 34000, "combinado = salario + beneficio, no + facturación");
  assert.equal(row.gap, 36000);
  assert.equal(row.reached, false);
});

test("evolución anual ordenada, con crecimiento y objetivo alcanzado", () => {
  const doc = emptyFinance();
  setTargets(doc, { combined: 70000 }, NOW);
  setYear(doc, 2029, { salary: 52000, revenue: 30000, expenses: 8000 }, NOW);
  setYear(doc, 2027, { salary: 26000 }, NOW);
  setYear(doc, 2028, { salary: 39000, revenue: 0, expenses: 0 }, NOW);
  const rows = projection(doc);
  assert.deepEqual(rows.map((r) => r.year), [2027, 2028, 2029]);
  assert.equal(rows[0].growth, null);
  assert.equal(rows[1].growth, 0.5);
  assert.equal(rows[2].combined, 74000);
  assert.equal(rows[2].reached, true);
  assert.equal(rows[2].gap, -4000);
});

test("pérdidas: el beneficio puede ser negativo y sin objetivo no hay distancia", () => {
  const doc = emptyFinance();
  setYear(doc, 2027, { salary: 0, revenue: 1000, expenses: 3000 }, NOW);
  setYear(doc, 2028, { salary: 20000 }, NOW);
  const rows = projection(doc);
  assert.deepEqual([rows[0].profit, rows[0].combined, rows[0].gap, rows[0].reached], [-2000, -2000, null, false]);
  assert.equal(rows[1].growth, 11, "crecimiento sobre el valor absoluto del año anterior");
});

test("importes: enteros de 0 a 10 millones; lo demás se rechaza", () => {
  assert.equal(amount(70000), 70000);
  for (const bad of [-1, 1.5, "70000", MAX_AMOUNT + 1, null, Number.NaN]) assert.equal(amount(bad), null, String(bad));
  const doc = emptyFinance();
  assert.equal(setYear(doc, 2027, { salary: -5 }, NOW), false);
  assert.equal(setYear(doc, 1999, { salary: 5 }, NOW), false);
  assert.equal(setYear(doc, "20x7", { salary: 5 }, NOW), false);
  assert.deepEqual(doc.years, {});
});

test("exportar e importar: ida y vuelta sin perder datos y fusionando con lo que hay", () => {
  const original = emptyFinance();
  setTargets(original, { combined: 70000 }, at("2026-11-01T10:00:00Z"));
  setYear(original, 2027, { salary: 26000, revenue: 5000, expenses: 1000 }, at("2026-11-01T10:00:00Z"));
  const text = exportFinance(original, NOW);
  assert.equal(JSON.parse(text).format, FORMAT);

  const other = emptyFinance();
  setYear(other, 2027, { salary: 28000 }, at("2026-11-10T10:00:00Z")); // más reciente: gana
  setYear(other, 2028, { salary: 35000 }, at("2026-11-10T10:00:00Z"));
  assert.deepEqual(importFinance(other, text), { ok: true, years: 1 });
  assert.equal(other.years["2027"].salary, 28000);
  assert.equal(other.years["2028"].salary, 35000, "importar no borra lo que había");
  assert.equal(other.targets.combined, 70000);
});

test("importar rechaza archivos que no son una exportación de PLD", () => {
  const doc = emptyFinance();
  assert.equal(importFinance(doc, "{no es json").ok, false);
  assert.match(importFinance(doc, JSON.stringify({ format: "otra-app", v: 1, data: {} })).error, /no es una exportación/);
  assert.equal(importFinance(doc, JSON.stringify({ format: FORMAT, v: 2, data: {} })).ok, false);
  assert.deepEqual(doc, emptyFinance());
});

test("limpieza: años y fechas válidos, importes inválidos a 0 y objetivos a null", () => {
  const doc = cleanFinance({
    targets: { combined: "mucho", salary: 50000, at: "2026-11-18T10:00:00Z" },
    years: { 2027: { salary: 1.5, revenue: 100, at: "2026-11-18T10:00:00Z" }, abc: { at: "2026-11-18T10:00:00Z" }, 2028: { salary: 1 } },
  });
  assert.deepEqual(doc.targets, { combined: null, salary: 50000, at: "2026-11-18T10:00:00Z" });
  assert.deepEqual(doc.years, { 2027: { salary: 0, revenue: 100, expenses: 0, at: "2026-11-18T10:00:00Z" } });
  assert.deepEqual(cleanFinance(null), emptyFinance());
  const merged = mergeFinance(emptyFinance(), doc);
  assert.deepEqual(merged, doc);
});
