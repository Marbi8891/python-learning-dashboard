/* Consola interactiva y comprobación de ejercicios. */

import { escapeHtml } from "./markdown.js";
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

function explain(error) {
  if (!error) return "";
  if (error.includes("EOFError")) {
    return "\nPista: tu programa pide datos con input(). Escríbelos en «Entrada», uno por línea.";
  }
  if (error.includes("ModuleNotFoundError")) {
    return "\nPista: ese paquete no está disponible en el navegador. Ejecuta este código en PyCharm.";
  }
  return "";
}

function showOutput({ output = "", error = null }) {
  const box = $("#console-output");
  const parts = [];
  if (output) parts.push(`<span>${escapeHtml(output)}</span>`);
  if (error) parts.push(`<span class="console__error">${escapeHtml(error + explain(error))}</span>`);
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
    const where = result.total > 1 && !result.passed ? ` (prueba ${result.case} de ${result.total})` : "";
    box.innerHTML = `
      <p class="check__title">${result.passed ? "✓ ¡Correcto!" : "✗ Todavía no"}${where}</p>
      <p>${escapeHtml(result.message)}</p>
      ${result.error ? `<pre class="console__error">${escapeHtml(result.error)}</pre>` : ""}`;
    box.focus();
    await onResult(result, code);
  });
}

/** Cambia la lección: carga el borrador guardado o el ejemplo. */
export function setLesson(next) {
  lesson = next;
  $("#console-editor").value = readDraft(next.slug) ?? next.example_code;
  $("#console-stdin").value = next.example_stdin;
  $("#console-stdin-box").open = Boolean(next.example_stdin);
  $("#console-output").innerHTML = next.example_in_browser
    ? '<span class="console__muted">Pulsa «Ejecutar» o Ctrl+Enter para ver el resultado.</span>'
    : '<span class="console__muted">El ejemplo de esta lección usa un paquete externo: ejecútalo en PyCharm. Aquí puedes practicar el ejercicio.</span>';
}

export function loadExample() {
  $("#console-editor").value = lesson.example_code;
  $("#console-stdin").value = lesson.example_stdin;
  $("#console-stdin-box").open = Boolean(lesson.example_stdin);
  saveDraft();
}

/** Carga la plantilla del ejercicio o, con "challenge", la del reto extra. */
export function loadStarter(kind = "exercise") {
  const source = kind === "challenge" ? lesson.challenge : lesson;
  const stdin = kind === "challenge" ? source.stdin : lesson.exercise_stdin;
  $("#console-editor").value = source.starter;
  $("#console-stdin").value = stdin ?? "";
  $("#console-stdin-box").open = Boolean(stdin);
  saveDraft();
  $("#console-editor").focus();
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
  editor.addEventListener("input", saveDraft);

  $("#console-run").addEventListener("click", runConsole);
  $("#console-example").addEventListener("click", loadExample);
  $("#console-clear").addEventListener("click", () => {
    $("#console-output").innerHTML = "";
  });
}
