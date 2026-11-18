/* Piezas de interfaz de Excel profesional: la cuadrícula de datos y los ejercicios de fórmulas.

   Las usa la ruta #/academia/excel (excel/course.js) desde la fase P2.
   Con `q: ""` no se pinta el enunciado: lo pinta quien monta el ejercicio (excel/course.js, con Markdown).
   Accesibilidad (ARCHITECTURE.md §11): la cuadrícula es una <table> con encabezados de fila y de
   columna; el editor tiene etiqueta y ayuda; el resultado se anuncia en role="status" y no depende
   solo del color. Todo texto se escapa o se pinta con textContent. */

import { escapeHtml } from "../markdown.js";
import { checkFormula, checkResult, describe } from "./checks.js";
import { address, columnLetters, parseAddress } from "./formula/index.js";
import { SPANISH_NAME } from "./formula/locale-es.js";

const DEFAULT_SHEET = "Hoja1";
const numberFormat = new Intl.NumberFormat("es-ES", { maximumFractionDigits: 10 });

const rawValue = (raw) => (raw !== null && typeof raw === "object" ? raw.v : raw);

/** Cómo se ve un valor en la celda, con su formato si lo tiene (moneda, porcentaje o decimales fijos). */
export function formatCell(raw) {
  const value = rawValue(raw);
  if (raw !== null && typeof raw === "object" && typeof raw.f === "string" && value === undefined) return raw.f;
  if (value === null || value === undefined) return "";
  if (typeof value === "boolean") return value ? "VERDADERO" : "FALSO";
  if (typeof value !== "number") return String(value);
  const format = raw !== null && typeof raw === "object" ? raw.format : null;
  if (format === "percent") return `${new Intl.NumberFormat("es-ES", { maximumFractionDigits: 2 }).format(value * 100)} %`;
  if (format === "currency") return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(value);
  if (typeof format === "number") return new Intl.NumberFormat("es-ES", { minimumFractionDigits: format, maximumFractionDigits: format }).format(value);
  return numberFormat.format(value);
}

/** Celdas de la cuadrícula agrupadas por hoja, en el orden en que aparecen. */
function sheetsOf(grid, defaultSheet, extraCells) {
  const sheets = new Map();
  const add = (key, raw) => {
    const { sheet, col, row } = parseAddress(key, defaultSheet);
    if (!sheets.has(sheet)) sheets.set(sheet, new Map());
    if (raw !== undefined) sheets.get(sheet).set(address(col, row), raw);
    return { sheet, col, row };
  };
  if (!sheets.has(defaultSheet)) sheets.set(defaultSheet, new Map());
  for (const [key, raw] of Object.entries(grid)) add(key, raw);
  for (const key of extraCells) add(key);
  return sheets;
}

/**
 * HTML de la cuadrícula: una tabla por hoja. `highlight` es la celda del ejercicio (se marca con
 * texto, no solo con color).
 */
export function gridHtml(grid, { sheet = DEFAULT_SHEET, highlight = null, caption = "Datos del ejercicio", extraCells = [] } = {}) {
  const sheets = sheetsOf(grid, sheet, [...extraCells, ...(highlight ? [highlight] : [])]);
  const target = highlight ? parseAddress(highlight, sheet) : null;
  const tables = [];
  for (const [name, cells] of sheets) {
    const refs = [...cells.keys()].map((key) => parseAddress(key, name));
    if (target && target.sheet === name) refs.push(target);
    if (refs.length === 0) continue;
    const maxCol = Math.max(...refs.map((r) => r.col));
    const maxRow = Math.max(...refs.map((r) => r.row));
    const head = Array.from({ length: maxCol }, (_, i) => `<th scope="col">${columnLetters(i + 1)}</th>`).join("");
    const body = [];
    for (let row = 1; row <= maxRow; row += 1) {
      const tds = [];
      for (let col = 1; col <= maxCol; col += 1) {
        const key = address(col, row);
        const isTarget = target && target.sheet === name && target.col === col && target.row === row;
        const raw = cells.get(key);
        const numeric = typeof rawValue(raw) === "number";
        const classes = [numeric ? "is-number" : "", isTarget ? "is-target" : ""].filter(Boolean).join(" ");
        const content = isTarget ? `<span class="xl-grid__target">?<span class="visually-hidden"> (celda ${key} del ejercicio)</span></span>` : escapeHtml(formatCell(raw ?? null));
        tds.push(`<td${classes ? ` class="${classes}"` : ""}>${content}</td>`);
      }
      body.push(`<tr><th scope="row">${row}</th>${tds.join("")}</tr>`);
    }
    const label = sheets.size > 1 ? `${caption} · hoja ${name}` : caption;
    tables.push(`<div class="xl-grid__scroll" tabindex="0" role="region" aria-label="${escapeHtml(label)}">
  <table class="xl-grid">
    <caption>${escapeHtml(label)}</caption>
    <thead><tr><td class="xl-grid__corner"></td>${head}</tr></thead>
    <tbody>${body.join("")}</tbody>
  </table>
</div>`);
  }
  return tables.join("\n");
}

let uid = 0;
const nextId = (prefix) => `${prefix}-${(uid += 1)}`;

function setStatus(status, ok, message) {
  status.dataset.state = ok ? "ok" : "fail";
  status.textContent = "";
  const mark = document.createElement("strong");
  mark.textContent = ok ? "Correcto. " : "Todavía no. ";
  status.append(mark, document.createTextNode(ok && message === "¡Correcto!" ? "" : message));
}

function hintsBlock(container, hints) {
  if (!hints?.length) return;
  const button = container.querySelector("[data-xl-hint]");
  const list = container.querySelector("[data-xl-hints]");
  let shown = 0;
  button.addEventListener("click", () => {
    const item = document.createElement("li");
    item.textContent = hints[shown];
    list.append(item);
    shown += 1;
    if (shown >= hints.length) button.disabled = true;
  });
}

/**
 * Monta un ejercicio «Escribe la fórmula» en `container`.
 * @param {(ok: boolean, detail: object) => void} [onResult] se llama en cada comprobación (no en las fórmulas sin «=»)
 * @returns {{ check: (formula: string) => object }}
 */
export function mountFormulaExercise(container, question, { onResult } = {}) {
  const inputId = nextId("xl-formula");
  const helpId = `${inputId}-help`;
  const sheet = question.sheet ?? DEFAULT_SHEET;
  container.innerHTML = `<div class="xl-exercise" data-kind="formula">
  ${question.q ? `<p class="xl-exercise__question">${escapeHtml(question.q)}</p>` : ""}
  ${gridHtml(question.grid, { sheet, highlight: question.cell })}
  <form class="xl-exercise__form" novalidate>
    <label for="${inputId}">Fórmula para ${escapeHtml(question.cell)}</label>
    <input id="${inputId}" class="xl-exercise__input" type="text" autocomplete="off" autocapitalize="off" spellcheck="false"
      aria-describedby="${helpId}" placeholder="=" />
    <p id="${helpId}" class="xl-exercise__help">Escríbela como en Excel en español: empieza por = y separa los argumentos con ;.</p>
    <div class="xl-exercise__actions">
      <button type="submit" class="btn btn--primary">Comprobar</button>
      ${question.hints?.length ? '<button type="button" class="btn btn--ghost" data-xl-hint>Pedir una pista</button>' : ""}
    </div>
  </form>
  <p class="xl-exercise__status" role="status" aria-live="polite" data-xl-status></p>
  <ol class="xl-exercise__hints" data-xl-hints></ol>
</div>`;
  const input = container.querySelector("input");
  const status = container.querySelector("[data-xl-status]");
  const check = (formula) => {
    const result = checkFormula(question, formula, { spanishName: (name) => SPANISH_NAME[name] ?? name });
    setStatus(status, result.ok, result.message);
    if (!result.needsEquals) onResult?.(result.ok, result);
    return result;
  };
  container.querySelector("form").addEventListener("submit", (event) => {
    event.preventDefault();
    check(input.value);
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") input.value = "";
  });
  hintsBlock(container, question.hints);
  return { check };
}

/**
 * Monta un ejercicio «¿Qué devuelve esta fórmula?» en `container`.
 * @returns {{ answer: (value: string|number) => object }}
 */
/** Una opción de «elige el resultado» como resultado del motor: número, booleano, { error } o texto. */
function optionResult(option) {
  if (typeof option === "number") return { type: "number", value: option };
  if (typeof option === "boolean") return { type: "boolean", value: option };
  if (option !== null && typeof option === "object" && "error" in option) return { type: "error", value: option.error };
  return { type: "text", value: String(option) };
}

export function mountResultExercise(container, question, { onResult } = {}) {
  const inputId = nextId("xl-result");
  const sheet = question.sheet ?? DEFAULT_SHEET;
  const choice = question.input === "choice";
  const field = choice
    ? `<fieldset class="xl-exercise__options"><legend>Elige el resultado</legend>${question.options
        .map(
          (option, i) => `<label><input type="radio" name="${inputId}" value="${i}" /> ${escapeHtml(describe(optionResult(option)).replace(/^«|»$/g, ""))}</label>`,
        )
        .join("")}</fieldset>`
    : `<label for="${inputId}">Resultado</label>
    <input id="${inputId}" class="xl-exercise__input" type="text" inputmode="${question.input === "number" ? "decimal" : "text"}" autocomplete="off" />`;
  container.innerHTML = `<div class="xl-exercise" data-kind="formula-result">
  ${question.q === "" ? "" : `<p class="xl-exercise__question">${escapeHtml(question.q ?? "¿Qué devuelve la fórmula con estos datos?")}</p>`}
  ${gridHtml(question.grid, { sheet, highlight: question.cell ?? null })}
  <p class="xl-exercise__formula"><span class="visually-hidden">Fórmula: </span><code>${escapeHtml(question.formula)}</code></p>
  <form class="xl-exercise__form" novalidate>
    ${field}
    <div class="xl-exercise__actions"><button type="submit" class="btn btn--primary">Comprobar</button></div>
  </form>
  <p class="xl-exercise__status" role="status" aria-live="polite" data-xl-status></p>
</div>`;
  const status = container.querySelector("[data-xl-status]");
  const answer = (value) => {
    const result = checkResult(question, value);
    setStatus(status, result.ok, result.message);
    if (!result.empty) onResult?.(result.ok, result);
    return result;
  };
  container.querySelector("form").addEventListener("submit", (event) => {
    event.preventDefault();
    const value = choice ? container.querySelector("input[type=radio]:checked")?.value : container.querySelector("input").value;
    answer(value ?? "");
  });
  return { answer };
}
