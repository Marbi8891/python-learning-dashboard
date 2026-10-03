/* Consola interactiva y comprobación de ejercicios. */

import { escapeHtml, renderInline } from "./markdown.js";
import { PythonRunner, TimeoutError } from "./python-runner.js";

const $ = (selector) => document.querySelector(selector);
const DRAFT_PREFIX = "pld:draft:";
const config = window.PLD_CONFIG ?? {};

const STATUS_TEXT = {
  idle: "Python se carga al ejecutar por primera vez",
  loading: "Cargando Python… (solo la primera vez, unos segundos)",
  ready: "Python 3 listo",
  error: "No se pudo cargar Python. Revisa tu conexión y vuelve a intentarlo.",
};

const runner = new PythonRunner({
  indexURL: config.pyodideUrl,
  timeoutMs: config.runTimeoutMs ?? 10_000,
  onStatus: (status) => {
    $("#console-status").textContent = STATUS_TEXT[status];
    $("#console-status").dataset.status = status;
  },
});

let lesson = null;
let busy = false;
let onRun = () => {};

/** Permite a otros módulos (el juego) saber si cada ejecución fue bien. */
export function setRunListener(listener) {
  onRun = listener;
}

function readDraft(slug) {
  try {
    return localStorage.getItem(DRAFT_PREFIX + slug);
  } catch {
    return null;
  }
}

function saveDraft() {
  if (!lesson) return;
  try {
    localStorage.setItem(DRAFT_PREFIX + lesson.slug, $("#console-editor").value);
  } catch {
    // sin almacenamiento
  }
}

function syncLineNumbers() {
  const editor = $("#console-editor");
  const gutter = $("#console-line-numbers");
  if (!editor || !gutter) return;
  const count = Math.max(1, editor.value.split("\n").length);
  gutter.textContent = Array.from({ length: count }, (_, i) => i + 1).join("\n");
  gutter.scrollTop = editor.scrollTop;
}

/** Explicación en español del error (la genera runner.py) con botón para ir a la línea. */
export function renderHint(hint) {
  if (!hint) return "";
  // La salida del Worker no es de fiar: el código del alumno puede falsearla (ADR-0022)
  const number = Number.isInteger(hint.line) && hint.line > 0 ? hint.line : null;
  const line = number
    ? `<button type="button" class="error-help__line" data-go-line="${number}">Ir a la línea ${number}</button>`
    : "";
  return `<span class="error-help" role="note"><strong>${renderInline(hint.title)}</strong>${renderInline(hint.text)}<br>${line}</span>`;
}

/** Selecciona una línea del editor (para señalar dónde está el error). */
function goToLine(number) {
  const editor = $("#console-editor");
  const lines = editor.value.split("\n");
  const start = lines.slice(0, number - 1).reduce((sum, text) => sum + text.length + 1, 0);
  editor.focus();
  editor.setSelectionRange(start, start + (lines[number - 1] ?? "").length);
}

function showOutput({ output = "", error = null, hint = null }) {
  const box = $("#console-output");
  const parts = [];
  if (output) parts.push(`<span>${escapeHtml(String(output))}</span>`);
  if (error) parts.push(`<span class="console__error">${escapeHtml(String(error))}</span>${renderHint(hint)}`);
  box.innerHTML = parts.join("") || '<span class="console__muted">(El programa no ha mostrado nada)</span>';
}

async function withRunner(button, label, action) {
  if (busy) return;
  busy = true;
  const original = button.innerHTML;
  button.disabled = true;
  button.textContent = label;
  try {
    await action();
  } catch (error) {
    const message = error instanceof TimeoutError ? `${error.message} ¿Hay un bucle infinito?` : error.message;
    showOutput({ error: message });
  } finally {
    busy = false;
    button.disabled = false;
    button.innerHTML = original;
  }
}

export function runConsole() {
  return withRunner($("#console-run"), "Ejecutando…", async () => {
    const result = await runner.run($("#console-editor").value, $("#console-stdin").value);
    showOutput(result);
    onRun(!result.error);
  });
}

/** Comprueba el código de la consola con unos tests (del ejercicio o del reto). */
export function checkCode({ checks, button, box, onResult }) {
  return withRunner(button, "Comprobando…", async () => {
    const code = $("#console-editor").value;
    const result = await runner.check(code, checks);
    box.hidden = false;
    box.dataset.passed = String(result.passed);
    const [done, total] = [Number(result.case), Number(result.total)]; // números o NaN, nunca HTML
    const where = total > 1 && !result.passed ? ` (prueba ${done} de ${total})` : "";
    box.innerHTML = `
      <p class="check__title">${result.passed ? "✓ ¡Correcto!" : "✗ Todavía no"}${where}</p>
      <p>${escapeHtml(result.message)}</p>
      ${result.error ? `<pre class="console__error">${escapeHtml(result.error)}</pre>${renderHint(result.hint)}` : ""}`;
    box.focus();
    await onResult(result, code);
  });
}

/** Cambia la lección: carga el borrador guardado o el ejemplo. */
export function setLesson(next) {
  lesson = next;
  $("#console-editor").value = readDraft(next.slug) ?? next.example_code;
  syncLineNumbers();
  $("#console-stdin").value = next.example_stdin;
  $("#console-stdin-box").open = Boolean(next.example_stdin);
  $("#console-output").innerHTML = next.example_in_browser
    ? '<span class="console__muted">Pulsa «Ejecutar» o Ctrl+Enter para ver el resultado.</span>'
    : '<span class="console__muted">El ejemplo de esta lección usa un paquete externo: ejecútalo en PyCharm. Aquí puedes practicar el ejercicio.</span>';
}

export function loadExample() {
  $("#console-editor").value = lesson.example_code;
  syncLineNumbers();
  $("#console-stdin").value = lesson.example_stdin;
  $("#console-stdin-box").open = Boolean(lesson.example_stdin);
  saveDraft();
}

/** Carga la plantilla del ejercicio o, con "challenge", la del reto extra. */
export function loadStarter(kind = "exercise") {
  const source = kind === "challenge" ? lesson.challenge : lesson;
  const stdin = kind === "challenge" ? source.stdin : lesson.exercise_stdin;
  $("#console-editor").value = source.starter;
  syncLineNumbers();
  $("#console-stdin").value = stdin ?? "";
  $("#console-stdin-box").open = Boolean(stdin);
  saveDraft();
  $("#console-editor").focus();
}

// Código pegado que sale del ejercicio de Python y toca el navegador o la red: puede ser una
// trampa de «copia y pega esto» (MITRE ATT&CK T1204.004, mitigación M1017 «User Training»).
// Solo avisa; no bloquea, porque aprender también es probar código ajeno.
const RISKY_PASTE = /\b(import\s+js|from\s+js\b|pyodide|fetch|XMLHttpRequest|localStorage|sessionStorage|indexedDB|document\.cookie|postMessage|eval\s*\(|exec\s*\(|base64)/i;

export function isRiskyPaste(text) {
  return RISKY_PASTE.test(text);
}

export function initConsole() {
  const editor = $("#console-editor");
  let tabInsertsSpaces = true;

  editor.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      runConsole();
    } else if (event.key === "Escape") {
      tabInsertsSpaces = false; // permite salir del editor con Tab (sin trampa de teclado)
    } else if (event.key === "Tab" && !event.shiftKey && tabInsertsSpaces) {
      event.preventDefault();
      const { selectionStart: start, selectionEnd: end, value } = editor;
      editor.value = `${value.slice(0, start)}    ${value.slice(end)}`;
      editor.selectionStart = editor.selectionEnd = start + 4;
      saveDraft();
    }
  });
  editor.addEventListener("focus", () => {
    tabInsertsSpaces = true;
  });
  editor.addEventListener("input", () => {
    saveDraft();
    syncLineNumbers();
  });
  editor.addEventListener("scroll", () => {
    $("#console-line-numbers").scrollTop = editor.scrollTop;
  });
  editor.addEventListener("paste", (event) => {
    const pasted = event.clipboardData?.getData("text") ?? "";
    $("#console-paste-warning").hidden = !isRiskyPaste(pasted);
  });

  $("#console-run").addEventListener("click", runConsole);
  // «Ir a la línea N» funciona tanto en la salida como en el resultado de la comprobación
  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-go-line]");
    if (button) goToLine(Number(button.dataset.goLine));
  });
  $("#console-example").addEventListener("click", loadExample);
  $("#console-copy").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(editor.value);
      $("#console-copy").textContent = "Copiado";
      setTimeout(() => { $("#console-copy").textContent = "Copiar código"; }, 1400);
    } catch {
      $("#console-copy").textContent = "No disponible";
      setTimeout(() => { $("#console-copy").textContent = "Copiar código"; }, 1400);
    }
  });
  $("#console-clear").addEventListener("click", () => {
    $("#console-output").innerHTML = '<span class="console__muted">(Sin salida)</span>';
  });
  syncLineNumbers();
}
