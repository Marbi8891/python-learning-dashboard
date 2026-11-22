/* Laboratorio de Python (#/laboratorio): editor con color, ejecución real y ejercicios corregidos.

   Usa el mismo Python que la consola de las lecciones (pythonRunner de console.js: Pyodide en un Web
   Worker, con tiempo límite y «Detener»). No se simula nada: cada ejecución y cada comprobación corre
   en ese Worker. El color del editor lo pone highlight.js (vendor/) en una capa detrás del textarea,
   así que el teclado, el lector de pantalla y deshacer funcionan como en cualquier campo de texto. */

import hljs from "../../vendor/highlight/core.min.js";
import python from "../../vendor/highlight/python.min.js";
import { RUN_KEYS_HTML } from "../keys.js";
import { checkFailureHtml, isRiskyPaste, pythonRunner as runner, renderHint } from "../console.js";
import { StoppedError, TimeoutError } from "../python-runner.js";
import { escapeHtml, renderMarkdown } from "../markdown.js";
import { game, recordExercise, recordRun } from "../game.js";
import { recordAttempt as recordLessonAttempt } from "../store.js";
import { learning, loadLearningContent, saveLearning } from "../learn/learn-store.js";
import { recordAttempt as recordConceptAttempt } from "../learn/mastery.js";
import { storage } from "../demo/demo-mode.js";
import { LAB_ROUTE, LAB_TOPICS, exerciseFromRoute, labExamples, labExercises } from "./lab-data.js";

if (!hljs.getLanguage("python")) hljs.registerLanguage("python", python);

const $ = (selector) => document.querySelector(selector);
const DRAFT_PREFIX = "pld:lab-draft:";

let data = null; // { exercises, examples, learningIndex }
let current = null;
let busy = false;
let loading = null;

function readDraft(id) {
  try {
    return storage.getItem(DRAFT_PREFIX + id);
  } catch {
    return null;
  }
}

function saveDraft() {
  if (!current) return;
  try {
    storage.setItem(DRAFT_PREFIX + current.id, $("#lab-editor").value);
  } catch {
    // sin almacenamiento: el borrador dura hasta recargar
  }
}

async function loadData() {
  loading ??= Promise.all([
    fetch("data/lessons.json").then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    }),
    loadLearningContent(),
  ]).then(([lessons, index]) => ({
    exercises: labExercises(lessons, index.data),
    examples: labExamples(lessons),
    index,
  }));
  loading.catch(() => {
    loading = null; // sin conexión: se reintenta al volver a entrar
  });
  return loading;
}

/** ¿Lo ha superado ya el alumno? Ejercicio de lección: en la XP; del núcleo: su último intento. */
function isPassed(exercise) {
  if (exercise.source === "lesson") return game.passed.includes(exercise.ref);
  return learning.ex[exercise.ref]?.h.at(-1) === true;
}

/* ---------- Pintado ---------- */

function listHtml() {
  return LAB_TOPICS.map((topic) => {
    const items = data.exercises.filter((e) => e.topic === topic.id);
    if (!items.length) return "";
    return `
      <h3 class="lab__topic" id="lab-topic-${topic.id}">${escapeHtml(topic.title)}</h3>
      <ul class="lab__items" aria-labelledby="lab-topic-${topic.id}">
        ${items
          .map(
            (e) => `<li><a href="${LAB_ROUTE}/${encodeURIComponent(e.id)}"${e === current ? ' aria-current="page"' : ""}>
              <span class="lab__check" aria-hidden="true">${isPassed(e) ? "✓" : ""}</span>
              <span>${escapeHtml(e.title)}</span>${isPassed(e) ? '<span class="visually-hidden"> (superado)</span>' : ""}</a></li>`,
          )
          .join("")}
      </ul>`;
  }).join("");
}

function taskHtml() {
  const topic = LAB_TOPICS.find((t) => t.id === current.topic);
  return `
    <p class="eyebrow">${escapeHtml(topic.title)} · ${current.source === "lesson" ? "Ejercicio de lección" : "Ejercicio del núcleo por conceptos"}</p>
    <h2 class="lab__task-title" id="lab-task-title" tabindex="-1">${escapeHtml(current.title)}</h2>
    <div class="markdown lab__statement">${renderMarkdown(current.statement)}</div>
    ${current.hint ? `<details class="lab__hint"><summary>Ver una pista</summary><p>${escapeHtml(current.hint)}</p></details>` : ""}
    ${isPassed(current) ? '<p class="lab__done">✓ Ya lo has superado. Puedes repetirlo cuando quieras.</p>' : ""}`;
}

function pageHtml() {
  const examples = data.examples.map((e) => `<option value="${escapeHtml(e.slug)}">${escapeHtml(e.title)}</option>`).join("");
  return `
    <header class="lab__head">
      <p class="eyebrow">Laboratorio</p>
      <h1 class="profile-hero__title" id="lab-title" tabindex="-1">Laboratorio de Python</h1>
      <p class="lab__lead">Escribe Python y ejecútalo de verdad en tu navegador, sin instalar nada. Los ejercicios se corrigen con pruebas automáticas, igual que en las lecciones.</p>
    </header>
    <div class="lab">
      <nav class="lab__list" aria-label="Ejercicios del laboratorio">
        <details${matchMedia("(min-width: 901px)").matches ? " open" : ""}>
          <summary class="lab__list-title">Ejercicios (${data.exercises.length})</summary>
          <div id="lab-list">${listHtml()}</div>
        </details>
      </nav>
      <div class="lab__work">
        <article class="lab__task" id="lab-task" aria-labelledby="lab-task-title">${taskHtml()}</article>
        <section class="console lab__console" aria-labelledby="lab-editor-title">
          <div class="console__head">
            <h2 class="console__title" id="lab-editor-title">Editor</h2>
            <span class="console__status" id="lab-status" data-status="idle" aria-live="polite">Python se carga al ejecutar por primera vez</span>
          </div>
          <label class="console__label" for="lab-editor">Código Python</label>
          <div class="lab-editor">
            <pre class="lab-editor__highlight" aria-hidden="true"><code class="hljs language-python" id="lab-highlight"></code></pre>
            <textarea class="lab-editor__input" id="lab-editor" rows="14" spellcheck="false" autocapitalize="off" autocomplete="off" aria-describedby="lab-help"></textarea>
          </div>
          <p class="console__warning" id="lab-paste-warning" role="status" hidden>Ojo: lo que has pegado usa funciones del navegador o de la red, no solo Python. No ejecutes código que no entiendas.</p>
          <p class="console__help" id="lab-help"><kbd>Tab</kbd> inserta 4 espacios · <kbd>Esc</kbd> y después <kbd>Tab</kbd> para salir del editor · ${RUN_KEYS_HTML} ejecuta</p>
          <details class="console__stdin" id="lab-stdin-box">
            <summary>Entrada para <code>input()</code></summary>
            <label class="visually-hidden" for="lab-stdin">Entrada: una línea por cada input()</label>
            <textarea id="lab-stdin" rows="3" spellcheck="false" placeholder="Una línea por cada input()"></textarea>
          </details>
          <div class="console__actions">
            <button class="btn btn--primary" id="lab-run" type="button"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M7 4v16l13-8z" fill="currentColor"/></svg> Ejecutar</button>
            <button class="btn btn--primary" id="lab-check" type="button">Comprobar ejercicio</button>
            <button class="btn btn--ghost" id="lab-stop" type="button" hidden>Detener</button>
            <button class="btn btn--ghost" id="lab-reset" type="button">Restablecer</button>
          </div>
          <div class="lab__examples">
            <label for="lab-example">Cargar un ejemplo</label>
            <select id="lab-example"><option value="">Elige un ejemplo…</option>${examples}</select>
          </div>
          <p class="console__label" id="lab-output-label">Salida</p>
          <pre class="console__output" id="lab-output" aria-labelledby="lab-output-label" aria-live="polite" tabindex="0"><span class="console__muted">Pulsa «Ejecutar» para ver el resultado.</span></pre>
          <div class="check lab__result" id="lab-result" tabindex="-1" role="status" hidden></div>
        </section>
      </div>
    </div>`;
}

function highlight() {
  const code = $("#lab-editor").value;
  // Un salto de línea final no ocupa altura en un <pre>: se añade un espacio para que las capas coincidan
  $("#lab-highlight").innerHTML = `${hljs.highlight(code, { language: "python", ignoreIllegals: true }).value}${code.endsWith("\n") ? " " : ""}`;
}

function syncScroll() {
  const editor = $("#lab-editor");
  const layer = $(".lab-editor__highlight");
  layer.scrollTop = editor.scrollTop;
  layer.scrollLeft = editor.scrollLeft;
}

function setCode(code, stdin = "") {
  $("#lab-editor").value = code;
  $("#lab-stdin").value = stdin;
  $("#lab-stdin-box").open = Boolean(stdin);
  highlight();
  syncScroll();
}

function openExercise(exercise, { moveFocus }) {
  current = exercise;
  $("#lab-task").innerHTML = taskHtml();
  $("#lab-list").innerHTML = listHtml();
  setCode(readDraft(exercise.id) ?? exercise.starter, exercise.stdin);
  $("#lab-result").hidden = true;
  $("#lab-output").innerHTML = '<span class="console__muted">Pulsa «Ejecutar» para ver el resultado.</span>';
  delete $("#lab-output").dataset.state;
  if (moveFocus) $("#lab-task-title").focus();
}

/* ---------- Ejecutar y comprobar ---------- */

function showOutput({ output = "", error = null, hint = null }) {
  const box = $("#lab-output");
  const parts = [];
  if (output) parts.push(`<span>${escapeHtml(String(output))}</span>`);
  if (error) parts.push(`<span class="console__error"><span class="console__error-label">Error</span>${escapeHtml(String(error))}</span>${renderHint(hint)}`);
  box.innerHTML = parts.join("") || '<span class="console__muted">(El programa no ha mostrado nada)</span>';
  box.dataset.state = error ? "error" : output ? "ok" : "empty";
}

async function withRunner(button, label, action) {
  if (busy) return;
  busy = true;
  const original = button.innerHTML;
  const stop = $("#lab-stop");
  const hadFocus = document.activeElement === button;
  button.disabled = true;
  button.textContent = label;
  stop.hidden = false;
  if (hadFocus) stop.focus();
  try {
    await action();
  } catch (error) {
    if (error instanceof StoppedError) {
      $("#lab-output").innerHTML = `<span class="console__muted">${escapeHtml(error.message)} Puedes cambiar el código y volver a ejecutarlo.</span>`;
      $("#lab-output").dataset.state = "empty";
    } else {
      showOutput({ error: error instanceof TimeoutError ? `${error.message} ¿Hay un bucle infinito?` : error.message });
    }
  } finally {
    busy = false;
    button.disabled = false;
    button.innerHTML = original;
    const focusOnStop = document.activeElement === stop;
    stop.hidden = true;
    if (focusOnStop) button.focus();
  }
}

function run() {
  return withRunner($("#lab-run"), "Ejecutando…", async () => {
    const result = await runner.run($("#lab-editor").value, $("#lab-stdin").value);
    showOutput(result);
    recordRun(!result.error);
  });
}

function check() {
  const exercise = current;
  return withRunner($("#lab-check"), "Comprobando…", async () => {
    const code = $("#lab-editor").value;
    const result = await runner.check(code, exercise.checks);
    const box = $("#lab-result");
    const [done, total] = [Number(result.case), Number(result.total)];
    const where = total > 1 && !result.passed ? ` (prueba ${done} de ${total})` : "";
    box.hidden = false;
    box.dataset.passed = String(result.passed);
    box.innerHTML = result.passed ? `<p class="check__title">✓ ¡Correcto!</p><p>${escapeHtml(result.message ?? "Todas las pruebas han pasado.")}</p>` : checkFailureHtml(result, where);
    box.focus();
    if (exercise.source === "lesson") {
      recordExercise(exercise.ref, result.passed);
      await recordLessonAttempt(exercise.ref, code, result.passed);
    } else {
      const source = data.index.exercises.get(exercise.ref);
      if (source) {
        recordConceptAttempt(learning, source, { ok: result.passed, error: null });
        saveLearning();
      }
    }
    if (result.passed) {
      $("#lab-list").innerHTML = listHtml();
      $("#lab-task").innerHTML = taskHtml();
    }
  });
}

/* ---------- Entrada ---------- */

let initialized = false;

function init(view) {
  if (initialized) return;
  initialized = true;
  let tabInsertsSpaces = true;
  view.addEventListener("keydown", (event) => {
    if (event.target.id !== "lab-editor") return;
    const editor = event.target;
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      run();
    } else if (event.key === "Escape") {
      tabInsertsSpaces = false; // sin trampa de teclado: Esc y Tab sale del editor
    } else if (event.key === "Tab" && !event.shiftKey && tabInsertsSpaces) {
      event.preventDefault();
      const { selectionStart: start, selectionEnd: end, value } = editor;
      editor.value = `${value.slice(0, start)}    ${value.slice(end)}`;
      editor.selectionStart = editor.selectionEnd = start + 4;
      highlight();
      saveDraft();
    }
  });
  view.addEventListener("focusin", (event) => {
    if (event.target.id === "lab-editor") tabInsertsSpaces = true;
  });
  view.addEventListener("input", (event) => {
    if (event.target.id !== "lab-editor") return;
    highlight();
    syncScroll();
    saveDraft();
  });
  view.addEventListener("scroll", (event) => {
    if (event.target.id === "lab-editor") syncScroll();
  }, true);
  view.addEventListener("paste", (event) => {
    if (event.target.id !== "lab-editor") return;
    $("#lab-paste-warning").hidden = !isRiskyPaste(event.clipboardData?.getData("text") ?? "");
  });
  view.addEventListener("change", (event) => {
    if (event.target.id !== "lab-example" || !event.target.value) return;
    const example = data.examples.find((e) => e.slug === event.target.value);
    if (example) {
      setCode(example.code, example.stdin);
      saveDraft();
      $("#lab-editor").focus();
    }
    event.target.value = "";
  });
  view.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    if (button.id === "lab-run") run();
    if (button.id === "lab-check") check();
    if (button.id === "lab-stop") runner.stop();
    if (button.id === "lab-reset") {
      setCode(current.starter, current.stdin);
      saveDraft();
      $("#lab-result").hidden = true;
      $("#lab-editor").focus();
    }
  });
}

/**
 * Abre el laboratorio en #lab-view.
 * @param {string} hash  @param {{ moveFocus?: boolean }} options
 */
export async function openLab(hash, { moveFocus = true } = {}) {
  const view = $("#lab-view");
  if (!data) {
    view.innerHTML = `<p class="dash-status" role="status">Cargando el laboratorio…</p>`;
    try {
      data = await loadData();
    } catch (error) {
      view.innerHTML = `<h1 class="profile-hero__title" id="lab-title" tabindex="-1">No se pudo cargar el laboratorio</h1>
        <p>Comprueba la conexión y vuelve a intentarlo. (${escapeHtml(error.message)})</p>
        <p><a class="btn btn--primary" href="${LAB_ROUTE}">Reintentar</a></p>`;
      if (moveFocus) $("#lab-title").focus();
      return;
    }
    if (!location.hash.startsWith(LAB_ROUTE)) return; // el alumno se fue mientras cargaba
  }
  const target = exerciseFromRoute(hash, data.exercises) ?? data.exercises[0];
  if (!view.querySelector(".lab")) {
    current = target;
    view.innerHTML = pageHtml();
    init(view);
    openExercise(target, { moveFocus: false });
    if (moveFocus) $("#lab-title").focus();
    return;
  }
  openExercise(target, { moveFocus });
}
