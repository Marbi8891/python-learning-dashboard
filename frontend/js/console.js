/* Consola interactiva y comprobación de ejercicios. */

import { MOD_KEY, RUN_KEYS_HTML } from "./keys.js";
import { escapeHtml, renderInline } from "./markdown.js";
import { PythonRunner, StoppedError, TimeoutError, isPythonCached } from "./python-runner.js";

const $ = (selector) => document.querySelector(selector);
const DRAFT_PREFIX = "pld:draft:";
const config = window.PLD_CONFIG ?? {};

const STATUS_TEXT = {
  idle: "Python se carga al ejecutar por primera vez",
  loading: "Cargando Python…",
  ready: "Python 3 listo",
  running: "Ejecutando…",
  error: "No se pudo cargar Python. Revisa tu conexión y vuelve a intentarlo.",
};

// La primera vez Python se descarga (unos 10 MB): se dice antes de gastar los datos del alumno
const DOWNLOAD_TEXT = {
  idle: "Python se descarga al ejecutar por primera vez (unos 10 MB)",
  loading: "Descargando Python (unos 10 MB, solo la primera vez)…",
  "slow-loading": "Sigue descargando Python: con una conexión lenta puede tardar unos minutos…",
};

/** Ahorro de datos activado o red 2G (solo lo informan algunos navegadores). */
export function isSlowConnection(connection = navigator.connection) {
  return Boolean(connection?.saveData) || ["slow-2g", "2g"].includes(connection?.effectiveType);
}

let pythonCached = false;
let currentStatus = "idle";

export function statusText(status, { cached = pythonCached, slow = isSlowConnection() } = {}) {
  if (status === "slow-loading") return cached ? "Python está tardando en arrancar…" : DOWNLOAD_TEXT[status];
  if (cached) return STATUS_TEXT[status];
  if (status === "idle" && !slow) return STATUS_TEXT.idle;
  return DOWNLOAD_TEXT[status] ?? STATUS_TEXT[status];
}

/** Indicador de estado de la cabecera de la consola (punto de color y texto, anunciado con aria-live). */
function setStatus(status) {
  currentStatus = status;
  const box = $("#console-status");
  if (!box) return;
  box.textContent = statusText(status);
  box.dataset.status = status === "slow-loading" ? "loading" : status;
}

const runner = new PythonRunner({
  indexURL: config.pyodideUrl,
  timeoutMs: config.runTimeoutMs ?? 10_000,
  onStatus: setStatus,
});

isPythonCached(config.pyodideUrl || undefined).then((cached) => {
  pythonCached = cached;
  if (currentStatus === "idle") setStatus("idle");
});

/** El mismo Python (un solo Worker) para la consola y para los ejercicios del núcleo educativo. */
export const pythonRunner = runner;

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
  // La salida del Worker no es de fiar: el código del alumno puede falsearla
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
  if (error) parts.push(`<span class="console__error"><span class="console__error-label">Error</span>${escapeHtml(String(error))}</span>${renderHint(hint)}`);
  box.innerHTML = parts.join("") || '<span class="console__muted">(El programa no ha mostrado nada)</span>';
  box.dataset.state = error ? "error" : output ? "ok" : "empty";
}

/** Mientras se ejecuta, «Detener» aparece junto a Ejecutar. Si el foco estaba en el botón que se
    desactiva, pasa a «Detener» (y vuelve al terminar) para no perderlo con el teclado. */
function toggleStop(running, button, moveFocus) {
  const stop = $("#console-stop");
  if (!stop) return;
  const focusOnStop = document.activeElement === stop;
  stop.hidden = !running;
  if (running && moveFocus) stop.focus();
  if (!running && focusOnStop) button.focus();
}

async function withRunner(button, label, action) {
  if (busy) return;
  busy = true;
  const original = button.innerHTML;
  // Un botón desactivado pierde el foco: si lo tenía, pasa a «Detener»
  const hadFocus = document.activeElement === button;
  button.disabled = true;
  button.textContent = label;
  toggleStop(true, button, hadFocus);
  try {
    await action();
  } catch (error) {
    if (error instanceof StoppedError) {
      const box = $("#console-output");
      box.innerHTML = `<span class="console__muted">${escapeHtml(error.message)} Puedes cambiar el código y volver a ejecutarlo.</span>`;
      box.dataset.state = "empty";
    } else {
      const message = error instanceof TimeoutError ? `${error.message} ¿Hay un bucle infinito?` : error.message;
      showOutput({ error: message });
    }
  } finally {
    busy = false;
    button.disabled = false;
    button.innerHTML = original;
    toggleStop(false, button, false);
  }
}

export function runConsole() {
  return withRunner($("#console-run"), "Ejecutando…", async () => {
    // «Ejecutando…» solo si Python ya está cargado; si no, el runner muestra «Cargando Python…»
    if ($("#console-status")?.dataset.status === "ready") setStatus("running");
    try {
      const result = await runner.run($("#console-editor").value, $("#console-stdin").value);
      showOutput(result);
      onRun(!result.error);
    } finally {
      if ($("#console-status")?.dataset.status === "running") setStatus("ready");
    }
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
  $("#console-file").textContent = `${next.slug.replace(/-/g, "_")}.py`;
  $("#console-editor").value = readDraft(next.slug) ?? next.example_code;
  syncLineNumbers();
  $("#console-stdin").value = next.example_stdin;
  $("#console-stdin-box").open = Boolean(next.example_stdin);
  delete $("#console-output").dataset.state;
  $("#console-output").innerHTML = next.example_in_browser
    ? `<span class="console__muted">Pulsa «Ejecutar» o ${MOD_KEY}+Enter para ver el resultado.</span>`
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
  const help = $("#console-help");
  if (help) help.innerHTML = `<kbd>Tab</kbd> inserta 4 espacios · <kbd>Esc</kbd> y después <kbd>Tab</kbd> para salir del editor · ${RUN_KEYS_HTML} ejecuta`;
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
  $("#console-stop").addEventListener("click", () => runner.stop());
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
    delete $("#console-output").dataset.state;
    $("#console-output").innerHTML = '<span class="console__muted">(Sin salida)</span>';
  });
  syncLineNumbers();
}
