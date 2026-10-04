/* Vista de una sesión de estudio (#/sesion): concepto → ejemplo → intento → corrección →
   explicación → nuevo intento → resumen con los errores explicados (ADR-0031). */

import { pythonRunner } from "../console.js";
import { codeResult, grade, missingAnswer } from "./answers.js";
import { learning, saveLearning } from "./learn-store.js";
import { allStats, markRead } from "./mastery.js";
import { exercisesForError, selectExercises, todayPlan } from "./recommend.js";
import { advance, createSession, currentItem, finish, isExpired, secondsLeft, stop, submit } from "./session.js";
import {
  codeBlock,
  enhanceEditor,
  errorExplanation,
  escapeHtml,
  exerciseHtml,
  feedbackHtml,
  percent,
  renderInline,
  renderMarkdown,
  STATUS,
  usesInput,
} from "./ui.js";

const $ = (selector) => document.querySelector(selector);

let index = null; // contenido indexado
let session = null;
let draft = {}; // respuesta en curso del ejercicio actual
let lastResult = null; // { ok, error } del ejercicio recién corregido
let summary = null;
let intro = false; // en las sesiones «learn», primero se enseña el concepto
let timer = null;
let busy = false;

const conceptTitle = (id) => index.concepts.get(id)?.title ?? "";

/* ---------- Arranque de sesiones (lo usan las demás vistas) ---------- */

export function setSessionIndex(value) {
  index = value;
}

/**
 * Empieza una sesión y navega a #/sesion.
 * @param {{kind: string, title: string, exercises: string[], concept?: string, timeLimit?: number, meta?: object}} options
 */
export function startSession({ kind, title, exercises, concept = null, timeLimit = null, meta = {} }) {
  session = createSession({ kind, title, exercises, timeLimit, meta: { ...meta, concept } });
  draft = {};
  lastResult = null;
  summary = null;
  intro = kind === "learn" && Boolean(concept);
  if (location.hash === "#/sesion") renderSession({ focus: true });
  else location.hash = "#/sesion";
}

/** Sesión para una acción del plan de «Hoy» (o para practicar un concepto). */
export function startPlanItem(type, conceptId, { errors = [] } = {}) {
  const title = conceptTitle(conceptId);
  if (type === "learn") {
    const exercises = selectExercises(index, learning, [conceptId], 4).map((e) => e.id);
    return startSession({ kind: "learn", title: `Aprender: ${title}`, exercises, concept: conceptId });
  }
  if (type === "errors") {
    // selectExercises ya da prioridad a los ejercicios que detectan errores activos
    const exercises = selectExercises(index, learning, [conceptId], 4).map((e) => e.id);
    return startSession({ kind: "errors", title: `Corregir errores: ${title}`, exercises, concept: conceptId, meta: { errors } });
  }
  const count = type === "review" ? 3 : 4;
  const exercises = selectExercises(index, learning, [conceptId], count).map((e) => e.id);
  const label = type === "review" ? "Repaso" : type === "reinforce" ? "Reforzar" : "Practicar";
  return startSession({ kind: type === "review" ? "review" : "practice", title: `${label}: ${title}`, exercises, concept: conceptId });
}

/** Practicar un error concreto (desde «Mis errores» o el resumen). */
export function startErrorPractice(errorId) {
  const error = index.errors.get(errorId);
  const pool = exercisesForError(index, errorId);
  const concepts = [...new Set(pool.map((e) => e.concept))];
  // Mismo criterio de selección que el resto, limitado a los ejercicios que detectan ese error
  const exercises = selectExercises(index, learning, concepts, 4, { only: pool.map((e) => e.id) }).map((e) => e.id);
  return startSession({ kind: "errors", title: `Error: ${error.label}`, exercises, concept: error.concept });
}

/* ---------- Pintado ---------- */

function header() {
  const total = session.queue.length;
  const position = Math.min(session.index + 1, total);
  const left = secondsLeft(session);
  return `
    <div class="exam-bar lx-session-bar">
      <span class="exam-bar__title" id="learn-title" tabindex="-1">${escapeHtml(session.title)}</span>
      ${session.phase === "done" ? "" : `<span>Ejercicio ${position} de ${total}</span>`}
      ${left !== null && session.phase !== "done" ? `<span class="exam-bar__timer" id="lx-timer" role="timer" aria-live="off">${formatTime(left)}</span>` : ""}
    </div>`;
}

const formatTime = (seconds) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;

function introHtml() {
  const concept = index.concepts.get(session.meta.concept);
  const lines = concept.example.lines.map(([n, text]) => `<li><span class="lx-line-ref">Línea ${n}</span> ${renderInline(text)}</li>`).join("");
  return `
    <section class="course-section lx-intro" aria-labelledby="lx-intro-title">
      <p class="eyebrow">Concepto</p>
      <h2 class="section-title" id="lx-intro-title">${escapeHtml(concept.title)}</h2>
      <p class="lx-lead">${renderInline(concept.summary)}</p>
      <h3 class="lx-h4">Ejemplo</h3>
      ${codeBlock(concept.example.code, { numbered: true, label: "Código de ejemplo" })}
      <ol class="lx-lines">${lines}</ol>
      ${concept.example.output ? `<p class="lx-note">Salida:</p><pre class="lx-output">${escapeHtml(concept.example.output)}</pre>` : ""}
      <h3 class="lx-h4">Cuándo usarlo</h3>
      <p>${renderInline(concept.when)}</p>
      <div class="lx-actions">
        <button class="btn btn--primary btn--lg" type="button" data-lx="begin">Entendido: a practicar →</button>
        <a class="btn btn--ghost" href="#/teoria/${escapeHtml(concept.id)}">Leer la teoría completa</a>
      </div>
    </section>`;
}

function questionHtml() {
  const item = currentItem(session);
  const ex = index.exercises.get(item.id);
  const reveal = session.phase === "feedback";
  const retryBanner = item.retryOf
    ? `<p class="lx-retry">Nuevo intento${item.retry ? " del mismo ejercicio" : " con un ejercicio parecido"}: aplica lo que acabas de ver.</p>`
    : "";
  const actions = reveal
    ? `<button class="btn btn--primary" type="button" data-lx="next">${session.index + 1 < session.queue.length ? "Siguiente →" : "Ver el resumen"}</button>`
    : `<button class="btn btn--primary" type="submit">${ex.kind === "code" ? "Comprobar con los tests" : "Comprobar"}</button>
       ${session.feedback ? '<button class="btn btn--ghost" type="button" data-lx="skip">No lo sé: ver la explicación</button>' : ""}
       ${session.kind === "exam" ? '<button class="btn btn--ghost" type="button" data-lx="finish">Terminar el simulacro</button>' : ""}`;
  return `
    ${retryBanner}
    <form class="exam-form" id="lx-form" novalidate>
      ${exerciseHtml(ex, draft, { number: session.index + 1, reveal, conceptTitle: conceptTitle(ex.concept) })}
      ${reveal ? feedbackHtml(ex, lastResult, { error: lastResult.error ? index.errors.get(lastResult.error) : null, conceptTitle: conceptTitle(ex.concept), retryNote: willRetry(item) }) : ""}
      <p class="quiz__message" id="lx-message" role="alert"></p>
      <div class="exam-actions">${actions}</div>
    </form>`;
}

/** ¿Se ha programado un nuevo intento para el ejercicio recién fallado? */
const willRetry = (item) => session.queue.some((q, i) => i > session.index && q.retryOf === item.id);

function summaryHtml() {
  const stats = allStats(index, learning);
  const concepts = Object.entries(summary.byConcept)
    .map(([id, [ok, total]]) => {
      const s = stats.get(id);
      return `<li class="lx-row"><a href="#/teoria/${escapeHtml(id)}">${escapeHtml(conceptTitle(id))}</a>
        <span>${ok} de ${total}</span><span class="lx-status" data-status="${s.status}">${STATUS[s.status].short}</span></li>`;
    })
    .join("");
  const errors = summary.errors
    .map(
      (error) => `
      <li class="lx-error-item">
        ${errorExplanation(error, { conceptTitle: conceptTitle(error.concept) })}
        <button class="btn btn--ghost" type="button" data-lx="error" data-id="${escapeHtml(error.id)}">Practicar este error</button>
      </li>`,
    )
    .join("");
  const next = todayPlan(index, learning)[0];
  const exam = session.kind === "exam";
  const total = exam ? session.queue.length : summary.total;
  const message =
    total === 0 ? "" : summary.correct / total >= 0.8 ? "Muy bien: lo tienes claro." : summary.correct / total >= 0.5 ? "Vas bien, pero conviene repasar lo que has fallado." : "Toca repasar la teoría y volver a intentarlo.";
  const review = exam ? examReviewHtml() : "";
  return `
    <section class="course-section lx-summary" aria-labelledby="lx-summary-title">
      <h2 class="section-title" id="lx-summary-title">${summary.correct} de ${total} correctos${exam ? ` · ${percent(total ? summary.correct / total : 0)}` : ""}</h2>
      <p class="lx-lead">${message}</p>
      ${summary.retried ? `<p>Nuevos intentos tras la explicación: ${summary.fixed} de ${summary.retried} bien resueltos.</p>` : ""}
      ${exam && summary.unanswered ? `<p>Sin responder: ${summary.unanswered} (cuentan como fallos).</p>` : ""}
      ${concepts ? `<h3 class="lx-h4">Conceptos trabajados</h3><ul class="lx-list">${concepts}</ul>` : ""}
      ${errors ? `<h3 class="lx-h4">Errores que has cometido</h3><ul class="lx-errors">${errors}</ul>` : '<p>No se ha detectado ningún error típico en esta sesión.</p>'}
      ${review}
      <div class="lx-actions">
        ${next ? `<button class="btn btn--primary" type="button" data-lx="plan" data-type="${next.type}" data-concept="${escapeHtml(next.concept)}">Siguiente recomendación: ${escapeHtml(conceptTitle(next.concept))} →</button>` : ""}
        <a class="btn btn--ghost" href="#/aprender">Volver a Hoy</a>
      </div>
    </section>`;
}

/** En los simulacros, la corrección de cada pregunta se ve al final. */
function examReviewHtml() {
  const items = session.queue
    .map((item, i) => {
      const ex = index.exercises.get(item.id);
      const result = session.results[i];
      const verdict = !result ? "Sin responder" : result.ok ? "✓ Correcto" : "✗ Incorrecto";
      const error = result?.error ? index.errors.get(result.error) : null;
      return `
        <li class="lx-review" data-result="${result?.ok ? "ok" : "ko"}">
          <details>
            <summary><span class="quiz__num">${i + 1}</span> ${escapeHtml(verdict)} · ${escapeHtml(conceptTitle(ex.concept))}</summary>
            <div class="prose">${renderMarkdown(ex.q)}</div>
            ${ex.code ? codeBlock(ex.code, { numbered: ex.kind === "bug" || ex.kind === "output" }) : ""}
            ${ex.kind === "output" ? `<p class="lx-note">Salida correcta:</p><pre class="lx-output">${escapeHtml(ex.expect)}</pre>` : ""}
            <div class="prose">${renderMarkdown(ex.explain)}</div>
            ${error ? errorExplanation(error, { heading: "p" }) : ""}
          </details>
        </li>`;
    })
    .join("");
  return `<h3 class="lx-h4">Corrección pregunta a pregunta</h3><ol class="lx-reviews">${items}</ol>`;
}

export function renderSession({ focus = false } = {}) {
  const root = $("#learn-view");
  if (!session || !index) {
    root.innerHTML = `
      <header class="course-hero"><h1 class="course-hero__title" id="learn-title" tabindex="-1">No hay ninguna sesión en curso</h1>
      <p class="course-hero__lead">Elige qué estudiar en <a href="#/aprender">Hoy</a> o en <a href="#/practicar">Practicar</a>.</p></header>`;
    if (focus) $("#learn-title")?.focus();
    return;
  }
  if (session.phase === "done" && !summary) return; // se está cerrando: endSession() la pinta
  const body = session.phase === "done" ? summaryHtml() : intro ? introHtml() : session.queue.length ? questionHtml() : "";
  root.innerHTML = `<p class="daw-crumb"><a href="#/aprender">Hoy</a></p>${header()}${body}`;
  enhanceEditor($("#lx-code"), { onRun: runCode });
  syncTimer();
  if (focus) (session.phase === "feedback" ? $(".lx-feedback") : $("#learn-title"))?.focus();
}

/* ---------- Simulacro: tiempo ---------- */

function syncTimer() {
  clearInterval(timer);
  timer = null;
  if (!session?.timeLimit || session.phase === "done") return;
  timer = setInterval(() => {
    if (location.hash !== "#/sesion") return;
    if (isExpired(session)) {
      clearInterval(timer);
      endSession();
      return;
    }
    const element = $("#lx-timer");
    if (element) element.textContent = formatTime(secondsLeft(session));
  }, 1000);
}

/* ---------- Acciones ---------- */

function readAnswer() {
  const form = $("#lx-form");
  if (!form) return;
  const choice = form.querySelector('input[name="lx-choice"]:checked');
  if (choice) draft.choice = Number(choice.value);
  const line = form.querySelector('input[name="lx-line"]:checked');
  if (line) draft.line = Number(line.value);
  const text = $("#lx-text");
  if (text) draft.text = text.value;
  const code = $("#lx-code");
  if (code) draft.code = code.value;
  const stdin = $("#lx-stdin");
  if (stdin) draft.stdin = stdin.value;
}

function apply(result) {
  submit(session, index, learning, result);
  lastResult = result;
  if (session.kind !== "exam") markRead(learning, index.exercises.get(currentItem(session).id).concept);
  saveLearning();
  if (!session.feedback) {
    draft = {};
    if (session.phase === "done") return endSession();
  }
  renderSession({ focus: true });
}

function endSession() {
  stop(session);
  summary = finish(session, index, learning);
  saveLearning();
  renderSession({ focus: true });
}

async function check() {
  readAnswer();
  const ex = index.exercises.get(currentItem(session).id);
  if (ex.kind === "code") return checkCode(ex);
  const missing = missingAnswer(ex, draft);
  if (missing) {
    $("#lx-message").textContent = missing;
    return;
  }
  apply(grade(ex, draft));
}

async function withBusy(label, action) {
  if (busy) return;
  busy = true;
  const buttons = [...document.querySelectorAll("#lx-form button")];
  buttons.forEach((b) => {
    b.disabled = true;
  });
  $("#lx-message").textContent = label;
  try {
    await action();
  } catch (error) {
    $("#lx-message").textContent = `${error.message} ¿Hay un bucle infinito?`;
    buttons.forEach((b) => {
      b.disabled = false;
    });
  } finally {
    busy = false;
  }
}

function checkCode(ex) {
  return withBusy("Comprobando con los tests… (la primera vez Python tarda unos segundos en cargar)", async () => {
    const result = await pythonRunner.check(draft.code ?? ex.starter, ex.checks.map(({ stdin, test }) => ({ stdin, test })));
    draft.check = { passed: Boolean(result.passed), case: Number(result.case), total: Number(result.total), message: String(result.message ?? ""), error: result.error ? String(result.error) : null };
    apply(codeResult(ex, result));
  });
}

function runCode() {
  readAnswer();
  const ex = index.exercises.get(currentItem(session).id);
  return withBusy("Ejecutando…", async () => {
    const result = await pythonRunner.run(draft.code ?? ex.starter, usesInput(ex) ? (draft.stdin ?? "") : "");
    draft.runOutput = [result.output, result.error].filter(Boolean).join("\n") || "(El programa no ha mostrado nada)";
    renderSession();
    $("#lx-run-output")?.focus();
  });
}

function onClick(event) {
  const target = event.target.closest("[data-lx]");
  if (!target || !session) return;
  switch (target.dataset.lx) {
    case "begin":
      intro = false;
      markRead(learning, session.meta.concept);
      saveLearning();
      renderSession({ focus: true });
      break;
    case "add":
    case "remove": {
      readAnswer();
      const line = Number(target.dataset.line);
      draft.order = target.dataset.lx === "add" ? [...(draft.order ?? []), line] : (draft.order ?? []).filter((i) => i !== line);
      renderSession();
      $(".daw-line:not([disabled])")?.focus();
      break;
    }
    case "run":
      runCode();
      break;
    case "skip":
      apply({ ok: false, error: null });
      break;
    case "next":
      advance(session);
      draft = {};
      if (session.phase === "done") endSession();
      else renderSession({ focus: true });
      break;
    case "finish":
      endSession();
      break;
    case "error":
      startErrorPractice(target.dataset.id);
      break;
    case "plan":
      startPlanItem(target.dataset.type, target.dataset.concept);
      break;
    default:
      break;
  }
}

function onSubmit(event) {
  if (event.target.id !== "lx-form") return;
  event.preventDefault();
  if (session.phase === "answer") check();
}

let listening = false;

export function initSessionEvents() {
  if (listening) return;
  listening = true;
  $("#learn-view").addEventListener("click", onClick);
  $("#learn-view").addEventListener("submit", onSubmit);
}
