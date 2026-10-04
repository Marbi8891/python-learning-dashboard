/* Piezas de interfaz compartidas por las vistas del núcleo educativo (ADR-0031):
   código resaltado, ejercicios, explicación de errores y medidores. Todo el texto se escapa. */

import hljs from "../../vendor/highlight/core.min.js";
import python from "../../vendor/highlight/python.min.js";
import { escapeHtml, renderInline, renderMarkdown } from "../markdown.js";
import { grade } from "./answers.js";

if (!hljs.getLanguage("python")) hljs.registerLanguage("python", python);

export { escapeHtml, renderInline, renderMarkdown };

export const STATUS = {
  nuevo: { label: "Sin empezar", short: "Nuevo" },
  leido: { label: "Teoría leída", short: "Leído" },
  aprendiendo: { label: "Aprendiendo", short: "Aprendiendo" },
  progreso: { label: "En progreso", short: "En progreso" },
  dominado: { label: "Dominado", short: "Dominado" },
};

export const KIND_LABEL = {
  choice: "Pregunta",
  output: "¿Qué muestra?",
  fill: "Completa el código",
  order: "Ordena las líneas",
  bug: "Encuentra el error",
  code: "Escribe el programa",
};

export const percent = (value) => `${Math.round((value ?? 0) * 100)} %`;

export function highlight(source) {
  return hljs.highlight(source, { language: "python" }).value;
}

/** Bloque de código resaltado. Con `numbered`, cada línea lleva su número (para «encuentra el error» y las explicaciones). */
export function codeBlock(source, { label = "Código", numbered = false, plain = false } = {}) {
  if (!source) return "";
  const html = plain ? escapeHtml(source) : highlight(source);
  if (!numbered) return `<pre class="lx-code" tabindex="0" aria-label="${escapeHtml(label)}"><code>${html}</code></pre>`;
  // El resaltado puede abrir un <span> en una línea y cerrarlo en otra: se resalta línea a línea
  const lines = source.split("\n").map((line, i) => `<span class="lx-line"><span class="lx-line__n" aria-hidden="true">${i + 1}</span>${plain ? escapeHtml(line) : highlight(line) || " "}</span>`);
  return `<pre class="lx-code lx-code--numbered" tabindex="0" aria-label="${escapeHtml(label)}"><code>${lines.join("")}</code></pre>`;
}

export function meter(value, label) {
  const pct = Math.round((value ?? 0) * 100);
  return `<span class="meter" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}"><span class="meter__fill" style="--value: ${pct}%"></span></span>`;
}

export function statusBadge(stats) {
  const status = STATUS[stats.status];
  return `<span class="lx-status" data-status="${stats.status}">${status.short}</span>${stats.due ? '<span class="lx-status" data-status="due">Repaso pendiente</span>' : ""}`;
}

/** Explicación de un error típico: qué falla, por qué, cómo pensarlo y cómo evitarlo. */
export function errorExplanation(error, { heading = "h3", conceptTitle = null } = {}) {
  return `
    <div class="lx-error">
      <${heading} class="lx-error__title">${renderInline(error.label)}</${heading}>
      ${conceptTitle ? `<p class="lx-error__concept">Concepto: <a href="#/teoria/${escapeHtml(error.concept)}">${escapeHtml(conceptTitle)}</a></p>` : ""}
      <dl class="lx-error__list">
        <div><dt>Por qué está mal</dt><dd>${renderInline(error.why)}</dd></div>
        <div><dt>Cómo pensarlo</dt><dd>${renderInline(error.think)}</dd></div>
        <div><dt>Cómo evitarlo</dt><dd>${renderInline(error.avoid)}</dd></div>
      </dl>
    </div>`;
}

/* ---------- Ejercicios ---------- */

/** Orden estable para «ordenar líneas» (y nunca ya resuelto), como en los cursos de DAW. */
export function stableShuffle(id, count) {
  let seed = [...id].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
  const indices = [...Array(count).keys()];
  for (let i = count - 1; i > 0; i -= 1) {
    seed = (seed * 1103515245 + 12345) >>> 0;
    const j = seed % (i + 1);
    [indices[i], indices[j]] = [indices[j], indices[i]];
  }
  return indices.every((v, i) => v === i) ? indices.reverse() : indices;
}


function choiceBody(ex, answer, reveal) {
  return `
    ${codeBlock(ex.code, { plain: ex.concept === "depuracion" && ex.code?.startsWith("Traceback") })}
    <div class="quiz__options" role="radiogroup" aria-label="Opciones">
      ${ex.options
        .map((option, i) => {
          const correct = reveal && i === ex.answer ? ' data-correct="true"' : "";
          const chosen = answer.choice === i ? " checked" : "";
          return `<label class="quiz__option"${correct}><input type="radio" name="lx-choice" value="${i}"${chosen}${reveal ? " disabled" : ""}> <span>${ex.codeOptions ? `<code class="opt-code">${escapeHtml(option.text)}</code>` : renderInline(option.text)}</span></label>`;
        })
        .join("")}
    </div>`;
}

function outputBody(ex, answer, reveal) {
  return `
    ${codeBlock(ex.code, { numbered: true })}
    ${ex.stdin ? `<p class="lx-note">El usuario escribe: <code>${escapeHtml(ex.stdin.trim().replace(/\n/g, " ⏎ "))}</code></p>` : ""}
    <label class="lx-field">Lo que muestra el programa (una línea por cada línea de salida)
      <textarea class="lx-answer" id="lx-text" rows="3" spellcheck="false" autocapitalize="off" autocomplete="off"${reveal ? " disabled" : ""}>${escapeHtml(answer.text ?? "")}</textarea>
    </label>
    ${reveal && !grade(ex, answer).ok ? `<p class="lx-solution">Salida correcta:</p><pre class="lx-output">${escapeHtml(ex.expect)}</pre>` : ""}`;
}

function fillBody(ex, answer, reveal) {
  return `
    ${codeBlock(ex.code)}
    <label class="lx-field">Lo que va en <code>___</code>
      <input class="lx-answer" type="text" id="lx-text" value="${escapeHtml(answer.text ?? "")}" autocomplete="off" autocapitalize="off" spellcheck="false"${reveal ? " disabled" : ""}>
    </label>
    ${reveal && !grade(ex, answer).ok ? `<p class="lx-solution">Solución: <code>${escapeHtml(ex.accept[0])}</code></p>` : ""}`;
}

function orderBody(ex, answer, reveal) {
  const plain = ex.pseudo;
  const line = (i, action, label) =>
    `<li><button class="daw-line" type="button" data-lx="${action}" data-line="${i}" aria-label="${escapeHtml(label)}"${reveal ? " disabled" : ""}><code>${plain ? escapeHtml(ex.lines[i]) : highlight(ex.lines[i])}</code></button></li>`;
  const placed = (answer.order ?? []).map((i, n) => line(i, "remove", `Línea ${n + 1}: ${ex.lines[i].trim()}. Pulsa para quitarla.`)).join("");
  const available = stableShuffle(ex.id, ex.lines.length)
    .filter((i) => !(answer.order ?? []).includes(i))
    .map((i) => line(i, "add", `${ex.lines[i].trim()}. Pulsa para añadirla al final.`))
    .join("");
  const wrong = reveal && !grade(ex, answer).ok;
  return `
    <p class="daw-order__label">Tu orden · pulsa una línea para quitarla</p>
    <ol class="daw-order" data-result="${reveal ? (wrong ? "ko" : "ok") : ""}">${placed || '<li class="daw-order__empty">Pulsa las líneas de abajo en orden.</li>'}</ol>
    ${available ? `<p class="daw-order__label">Líneas disponibles · pulsa para añadir</p><ul class="daw-order daw-order--pool">${available}</ul>` : ""}
    ${wrong ? `<p class="lx-solution">Orden correcto:</p>${codeBlock(ex.lines.join("\n"), { plain })}` : ""}`;
}

function bugBody(ex, answer, reveal) {
  const lines = ex.code.split("\n");
  return `
    <fieldset class="lx-bug">
      <legend class="lx-note">Elige la línea que tiene el error</legend>
      ${lines
        .map((text, i) => {
          const n = i + 1;
          const correct = reveal && n === ex.line ? ' data-correct="true"' : "";
          return `<label class="lx-bug__line"${correct}><input type="radio" name="lx-line" value="${n}"${answer.line === n ? " checked" : ""}${reveal ? " disabled" : ""}>
            <span class="lx-line__n">${n}</span><code>${highlight(text) || " "}</code></label>`;
        })
        .join("")}
    </fieldset>
    ${ex.stdin ? `<p class="lx-note">El usuario escribe: <code>${escapeHtml(ex.stdin.trim().replace(/\n/g, " ⏎ "))}</code></p>` : ""}
    ${reveal ? `<p class="lx-solution">Línea ${ex.line} corregida:</p>${ex.fix ? codeBlock(ex.fix) : '<p class="lx-note">(La línea sobra: hay que eliminarla.)</p>'}` : ""}`;
}

export const usesInput = (ex) => (ex.checks ?? []).some((c) => c.stdin);

function codeBody(ex, answer, reveal) {
  return `
    <label class="lx-field">Tu programa
      <textarea class="lx-editor" id="lx-code" rows="${Math.max(8, (answer.code ?? ex.starter).split("\n").length + 2)}" spellcheck="false" autocapitalize="off" autocomplete="off" aria-describedby="lx-code-help"${reveal ? " readonly" : ""}>${escapeHtml(answer.code ?? ex.starter)}</textarea>
    </label>
    <p class="console__help" id="lx-code-help"><kbd>Tab</kbd> inserta 4 espacios · <kbd>Esc</kbd> y después <kbd>Tab</kbd> para salir del editor · <kbd>Ctrl</kbd>+<kbd>Enter</kbd> ejecuta</p>
    ${usesInput(ex) ? `<label class="lx-field">Entrada para probar (una línea por cada <code>input()</code>)<textarea id="lx-stdin" rows="2" spellcheck="false">${escapeHtml(answer.stdin ?? ex.checks.find((c) => c.stdin)?.stdin ?? "")}</textarea></label>` : ""}
    <div class="lx-actions">
      <button class="btn btn--ghost" type="button" data-lx="run"${reveal ? " disabled" : ""}>▶ Ejecutar</button>
      ${ex.hint ? `<details class="daw-faq"><summary>Pista</summary><p>${renderInline(ex.hint)}</p></details>` : ""}
    </div>
    <pre class="lx-output" id="lx-run-output" aria-live="polite" tabindex="0"${answer.runOutput ? "" : " hidden"}>${escapeHtml(answer.runOutput ?? "")}</pre>
    ${answer.check ? `<div class="check" data-passed="${answer.check.passed}"><p class="check__title">${answer.check.passed ? "✓ Todos los tests superados" : `✗ Falla la prueba ${Number(answer.check.case)} de ${Number(answer.check.total)}`}</p><p>${escapeHtml(answer.check.message)}</p>${answer.check.error ? `<pre class="console__error">${escapeHtml(answer.check.error)}</pre>` : ""}</div>` : ""}
    ${reveal ? `<details class="daw-faq"><summary>Ver una solución posible</summary>${codeBlock(ex.solution)}</details>` : ""}`;
}

const BODY = { choice: choiceBody, output: outputBody, fill: fillBody, order: orderBody, bug: bugBody, code: codeBody };

/** Enunciado y respuesta de un ejercicio. `reveal`: corregido (sin poder cambiar la respuesta). */
export function exerciseHtml(ex, answer, { number, reveal = false, conceptTitle = "" } = {}) {
  return `
    <fieldset class="quiz__q lx-exercise" data-kind="${ex.kind}">
      <legend>
        <span class="lx-exercise__meta">${number ? `<span class="quiz__num">${number}</span>` : ""}<span class="lx-kind">${KIND_LABEL[ex.kind]}</span>
          <span class="lx-concept-tag">${escapeHtml(conceptTitle)}</span></span>
        <span class="lx-exercise__q">${ex.kind === "code" ? "" : renderInline(ex.q)}</span>
      </legend>
      ${ex.kind === "code" ? `<div class="prose">${renderMarkdown(ex.q)}</div>` : ""}
      ${BODY[ex.kind](ex, answer, reveal)}
    </fieldset>`;
}

/** Explicación tras corregir: veredicto, por qué y, si se reconoce, el error típico. */
export function feedbackHtml(ex, result, { error = null, conceptTitle = "", retryNote = false } = {}) {
  return `
    <section class="quiz__feedback lx-feedback" data-result="${result.ok ? "ok" : "ko"}" tabindex="-1" aria-labelledby="lx-verdict">
      <p class="quiz__verdict" id="lx-verdict">${result.ok ? "✓ Correcto" : "✗ No es correcto"}</p>
      <div class="lx-feedback__why"><h3 class="lx-h4">${result.ok ? "Por qué funciona" : "Cómo pensarlo"}</h3>${renderMarkdown(ex.explain)}</div>
      ${!result.ok && error ? `<h3 class="lx-h4">Error típico detectado</h3>${errorExplanation(error, { heading: "p" })}` : ""}
      ${!result.ok && retryNote ? '<p class="lx-note">Al final de la sesión volverás a intentarlo con un ejercicio parecido.</p>' : ""}
      <p class="lx-feedback__links"><a href="#/teoria/${escapeHtml(ex.concept)}">Repasar la teoría: ${escapeHtml(conceptTitle)}</a></p>
    </section>`;
}

/** Inserta 4 espacios con Tab y permite salir con Esc + Tab (sin trampa de teclado). Igual que la consola. */
export function enhanceEditor(editor, { onRun } = {}) {
  if (!editor || editor.dataset.enhanced) return;
  editor.dataset.enhanced = "1";
  let tabInsertsSpaces = true;
  editor.addEventListener("focus", () => {
    tabInsertsSpaces = true;
  });
  editor.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      onRun?.();
    } else if (event.key === "Escape") {
      tabInsertsSpaces = false;
    } else if (event.key === "Tab" && !event.shiftKey && tabInsertsSpaces && !editor.readOnly) {
      event.preventDefault();
      const { selectionStart: start, selectionEnd: end, value } = editor;
      editor.value = `${value.slice(0, start)}    ${value.slice(end)}`;
      editor.selectionStart = editor.selectionEnd = start + 4;
      editor.dispatchEvent(new Event("input", { bubbles: true }));
    }
  });
}
