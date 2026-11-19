/* Gráfica de la evolución económica del itinerario (DEC-012), en SVG nativo y sin dependencias.

   Función pura: recibe las filas de projection() (career-finance.js) y devuelve el SVG como texto, así
   que se prueba con node --test. Sin style="…" (la CSP no lo permite): los colores salen de las clases
   .cc-* de career.css, con los tokens de cada tema. Cada serie va con un trazo distinto, no solo con un
   color, y la tabla de al lado da los mismos datos (WCAG 1.1.1 y 1.4.1). Nunca se suman salario y
   facturación: se dibujan el ingreso combinado (salario + beneficio), el salario y el beneficio. */

const W = 640;
const H = 260;
const PAD = { top: 16, right: 16, bottom: 32, left: 64 };

export const SERIES = Object.freeze([
  { key: "combined", label: "Ingreso combinado (salario + beneficio)", css: "cc-line cc-line--combined" },
  { key: "salary", label: "Salario bruto", css: "cc-line cc-line--salary" },
  { key: "profit", label: "Beneficio del negocio", css: "cc-line cc-line--profit" },
]);

/** Máximo del eje: el eje tiene 4 tramos iguales, así que cada tramo es un número redondo (1, 2, 2,5 o 5 × 10ⁿ). */
export function niceMax(value) {
  if (!(value > 0)) return 1000;
  const raw = value / 4;
  const power = 10 ** Math.floor(Math.log10(raw));
  return [1, 2, 2.5, 5, 10].find((s) => s * power >= raw) * power * 4;
}

const escape = (text) => String(text).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

/**
 * @param {Array<{year:number, salary:number, profit:number, combined:number}>} rows de projection()
 * @param {{target?: number|null, money: (n:number) => string, id?: string}} options
 * @returns {string} SVG, o "" con menos de dos años (una línea necesita dos puntos)
 */
export function financeChart(rows, { target = null, money, id = "career-chart" }) {
  if (rows.length < 2) return "";
  const values = rows.flatMap((r) => [r.combined, r.salary, r.profit]);
  const min = Math.min(0, ...values);
  const max = niceMax(Math.max(target ?? 0, ...values));
  const x = (i) => PAD.left + (i * (W - PAD.left - PAD.right)) / (rows.length - 1);
  const y = (v) => PAD.top + ((max - v) * (H - PAD.top - PAD.bottom)) / (max - min || 1);
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => min + f * (max - min));
  const grid = ticks
    .map((v) => `<line class="cc-grid" x1="${PAD.left}" x2="${W - PAD.right}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}"/><text class="cc-axis" x="${PAD.left - 8}" y="${(y(v) + 4).toFixed(1)}" text-anchor="end">${escape(money(Math.round(v)))}</text>`)
    .join("");
  const years = rows.map((r, i) => `<text class="cc-axis" x="${x(i).toFixed(1)}" y="${H - 10}" text-anchor="middle">${r.year}</text>`).join("");
  const lines = SERIES.map(
    (s) =>
      `<polyline class="${s.css}" fill="none" points="${rows.map((r, i) => `${x(i).toFixed(1)},${y(r[s.key]).toFixed(1)}`).join(" ")}"/>` +
      rows.map((r, i) => `<circle class="${s.css} cc-dot" cx="${x(i).toFixed(1)}" cy="${y(r[s.key]).toFixed(1)}" r="3.5"/>`).join(""),
  ).join("");
  const goal = target === null ? "" : `<line class="cc-target" x1="${PAD.left}" x2="${W - PAD.right}" y1="${y(target).toFixed(1)}" y2="${y(target).toFixed(1)}"/>`;
  const first = rows[0];
  const last = rows.at(-1);
  const desc = `Del ${first.year} al ${last.year}, el ingreso combinado pasa de ${money(first.combined)} a ${money(last.combined)}${target === null ? "" : `; el objetivo es ${money(target)}`}. Los datos completos están en la tabla.`;
  return `<svg class="cc" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="${id}-title ${id}-desc" focusable="false">
<title id="${id}-title">Evolución económica por año</title><desc id="${id}-desc">${escape(desc)}</desc>
${grid}${years}${goal}${lines}</svg>`;
}
