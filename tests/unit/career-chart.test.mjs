// Gráfica de la evolución económica (career-chart.js): SVG accesible, sin estilos en línea y sin
// sumar nunca salario y facturación.
import assert from "node:assert/strict";
import { test } from "node:test";
import { financeChart, niceMax, SERIES } from "../../frontend/js/career/career-chart.js";
import { emptyFinance, projection, setYear } from "../../frontend/js/career/career-finance.js";

const money = (n) => `${n} €`;
const NOW = new Date("2026-11-19T10:00:00Z");

function rows(years) {
  const doc = emptyFinance();
  for (const [year, data] of Object.entries(years)) setYear(doc, year, data, NOW);
  return projection(doc);
}

test("con menos de dos años no hay gráfica (la tabla ya lo dice)", () => {
  assert.equal(financeChart([], { money }), "");
  assert.equal(financeChart(rows({ 2027: { salary: 26000 } }), { money }), "");
});

test("el SVG tiene título y descripción enlazados y no usa style en línea (CSP)", () => {
  const svg = financeChart(rows({ 2027: { salary: 26000 }, 2028: { salary: 30000, revenue: 10000, expenses: 2000 } }), { target: 70000, money });
  assert.match(svg, /role="img" aria-labelledby="career-chart-title career-chart-desc"/);
  assert.match(svg, /<title id="career-chart-title">/);
  assert.match(svg, /<desc id="career-chart-desc">Del 2027 al 2028, el ingreso combinado pasa de 26000 € a 38000 €; el objetivo es 70000 €/);
  assert.doesNotMatch(svg, /style=/);
  assert.equal((svg.match(/<polyline /g) ?? []).length, SERIES.length, "una línea por serie");
  assert.match(svg, /class="cc-target"/, "con objetivo, su línea");
});

test("el ingreso combinado es salario + beneficio, nunca salario + facturación", () => {
  const data = rows({ 2027: { salary: 20000, revenue: 50000, expenses: 45000 }, 2028: { salary: 20000 } });
  const svg = financeChart(data, { money });
  assert.match(svg, /pasa de 25000 €/); // 20 000 + (50 000 − 45 000), no 70 000
  assert.doesNotMatch(svg, /cc-target/, "sin objetivo no se dibuja su línea");
});

test("un beneficio negativo baja del cero sin salirse del dibujo", () => {
  const svg = financeChart(rows({ 2027: { revenue: 1000, expenses: 9000 }, 2028: { salary: 30000 } }), { money });
  const ys = [...svg.matchAll(/cy="([\d.-]+)"/g)].map((m) => Number(m[1]));
  assert.ok(ys.every((y) => y >= 0 && y <= 260), `todos los puntos dentro: ${ys}`);
  assert.match(svg, />-8000 €</, "el eje empieza en el mínimo negativo");
});

test("los textos del catálogo y los importes se escapan", () => {
  const svg = financeChart(rows({ 2027: { salary: 1 }, 2028: { salary: 2 } }), { money: (n) => `<b>${n}</b>` });
  assert.doesNotMatch(svg, /<b>/);
  assert.match(svg, /&lt;b&gt;/);
});

test("niceMax: el máximo cubre el valor y cada cuarto del eje es un número redondo", () => {
  assert.equal(niceMax(0), 1000);
  assert.equal(niceMax(38000), 40000); // 0, 10 000, 20 000, 30 000, 40 000
  assert.equal(niceMax(70000), 80000); // 0, 20 000, 40 000…
  for (const value of [1, 999, 38000, 70000, 123456, 9_999_999]) {
    const max = niceMax(value);
    assert.ok(max >= value, `${max} cubre ${value}`);
    const quarter = max / 4;
    const mantissa = quarter / 10 ** Math.floor(Math.log10(quarter));
    assert.ok([1, 2, 2.5, 5].includes(Math.round(mantissa * 100) / 100), `${quarter} es redondo`);
  }
});
