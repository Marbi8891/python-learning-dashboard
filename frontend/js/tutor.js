/* Tutor Python: una sección más del dashboard, no la app convertida en chat.
   Habla con el agente Python Tutor del backend por A2A 1.0 (JSON-RPC, ver tutor-protocol.js).
   - Solo aparece si el servidor lo ofrece (su Agent Card responde) y pide la sesión iniciada.
   - Lo que escribes se envía como texto: tu código nunca se ejecuta en el servidor. Los ejemplos de
     las respuestas se pueden ejecutar aquí, en tu navegador, con el mismo Python de la consola.
   - Cada respuesta dice de dónde sale: un modelo de IA, el tutor sin IA o una respuesta preparada.
   - Tutor híbrido: modalidad gratuita (por defecto) o IA avanzada, que solo se puede
     elegir si el servidor la ofrece y al alumno le queda cuota. La decide el servidor en cada
     mensaje: si no la concede, responde en modo gratuito y aquí se ofrece seguir en ese modo.
   - La conversación vive solo en esta página (no se guarda en el navegador) y se borra al cerrar
     sesión o al empezar una nueva. Una respuesta que llega tarde a una conversación ya cerrada
     se descarta. */

import { openAccount } from "./account.js";
import { API_URL, apiEnabled, request } from "./api.js";
import { isRiskyPaste, pythonRunner } from "./console.js";
import { escapeHtml, renderMarkdown } from "./markdown.js";
import { TimeoutError } from "./python-runner.js";
import { state, subscribe } from "./store.js";
import {
  A2A_VERSION,
  advancedStatus,
  MODES_PATH,
  readTaskResult,
  sendMessageRequest,
  sourceLabel,
  TUTOR_PATH,
  withRemaining,
} from "./tutor-protocol.js";

const $ = (selector) => document.querySelector(selector);
const QUESTION_PLACEHOLDER = "Ejemplo: ¿por qué me sale NameError?";
const ANSWER_PLACEHOLDER = "Escribe tu respuesta (por ejemplo, la salida que esperas)";

/** ¿Hay tutor en este servidor? Se pregunta a su Agent Card, la ficha pública del agente. */
export const tutorAvailable = apiEnabled
  ? fetch(`${API_URL}${TUTOR_PATH}/.well-known/agent-card.json`)
      // Se lee la card entera: una respuesta a medio leer deja la conexión abierta
      .then((response) => (response.ok ? response.json() : null))
      .then((card) => Boolean(card?.supportedInterfaces?.length))
      .catch(() => false)
  : Promise.resolve(false);

let contextId = null; // conversación actual (contextId de A2A)
let conversation = 0; // sube con cada conversación nueva: descarta respuestas tardías
let renderedFor; // usuario para el que está pintada la vista (undefined = nada pintado)
let requestId = 0;
let pending = null; // { controller, conversation } de la pregunta en curso
let lastQuery = null; // para «Reintentar» (solo si lo pide el alumno)
let mode = "free"; // modalidad elegida: «free» o «advanced» (el servidor decide si la concede)
let modes = null; // lo que dice GET /api/v1/tutor/modes (null: no se sabe)
let modesFailed = false;

function hero(note) {
  return `
    <header class="profile-hero">
      <p class="eyebrow">Tutor Python</p>
      <h1 class="profile-hero__title" id="tutor-title" tabindex="-1">Pregunta tus dudas de Python</h1>
      <p class="profile-hero__note">${note}</p>
    </header>`;
}

function unavailableHtml() {
  return hero("El tutor no está disponible en este servidor. El resto de la web funciona igual.");
}

function signedOutHtml() {
  return `${hero("El tutor usa tu progreso para adaptar las explicaciones, así que necesita que inicies sesión.")}
    <p><button class="btn btn--primary" type="button" data-open-account>Iniciar sesión o crear cuenta</button></p>`;
}

function chatHtml(lessons, lessonSlug) {
  const options = lessons
    .map((lesson) => {
      const selected = lesson.slug === lessonSlug ? " selected" : "";
      return `<option value="${escapeHtml(lesson.slug)}"${selected}>${escapeHtml(lesson.title)}</option>`;
    })
    .join("");
  return `${hero(
    "Te explica conceptos y errores, revisa tu código y te da pistas sin resolver el ejercicio por ti. " +
      "No ejecuta tu código en el servidor: los ejemplos los puedes ejecutar aquí, en tu navegador.",
  )}
    <section class="course-section tutor" aria-labelledby="tutor-chat-title">
      ${modesHtml()}
      <h2 class="section-title" id="tutor-chat-title">Conversación</h2>
      <ol class="tutor__messages" id="tutor-messages" aria-live="polite" aria-relevant="additions"></ol>
      <p class="tutor__status" id="tutor-status" role="status"></p>
      <form class="tutor__form" id="tutor-form">
        <label>Tu pregunta
          <textarea name="question" rows="3" maxlength="4000" required placeholder="${QUESTION_PLACEHOLDER}"></textarea>
        </label>
        <details class="tutor__extra"${lessonSlug ? " open" : ""}>
          <summary>Añadir lección, código o error (opcional)</summary>
          <label>Lección <select name="lesson"><option value="">Ninguna</option>${options}</select></label>
          <label>Tu código <textarea name="code" rows="6" maxlength="20000" spellcheck="false" class="tutor__code"></textarea></label>
          <label>Mensaje de error <textarea name="error" rows="3" maxlength="4000" spellcheck="false" class="tutor__code"></textarea></label>
        </details>
        <label class="tutor__check"><input type="checkbox" name="gradual"> Explícamelo paso a paso</label>
        <div class="tutor__actions">
          <button class="btn btn--primary" type="submit">Preguntar</button>
          <button class="btn btn--ghost" type="button" data-tutor-hint>Pedir una pista</button>
          <button class="btn btn--ghost" type="button" data-tutor-alt>Explícamelo de otra forma</button>
          <button class="btn btn--ghost" type="button" data-tutor-exercise>Otro ejercicio</button>
          <button class="btn btn--ghost" type="button" data-tutor-free hidden>Seguir en modo gratuito</button>
          <button class="btn btn--ghost" type="button" data-tutor-cancel hidden>Cancelar</button>
          <button class="btn btn--ghost" type="button" data-tutor-retry hidden>Reintentar</button>
          <button class="btn btn--ghost" type="button" data-tutor-reset>Nueva conversación</button>
        </div>
      </form>
      <p class="account-card__meta">Según la configuración del servidor responde un modelo de IA o el tutor
        sin IA, con reglas y el contenido revisado del curso: cada respuesta indica su origen. Solo se envía lo
        que escribes aquí y, si eliges una lección, tu estado en ella y en sus conceptos. No incluyas datos
        personales. No se guarda en tu cuenta: el servidor conserva la conversación en memoria temporal (solo
        cuenta cuántas consultas haces cada día, para los límites). Las respuestas del tutor no marcan lecciones
        como completadas: eso solo lo hacen tus ejercicios superados.
        <a href="privacidad.html">Privacidad</a></p>
    </section>`;
}

function modesHtml() {
  return `
      <fieldset class="tutor-modes" id="tutor-modes">
        <legend class="section-title">Modalidad del tutor</legend>
        <label class="tutor-mode">
          <input type="radio" name="tutor-mode" value="free" checked
            aria-labelledby="tutor-mode-free" aria-describedby="tutor-mode-free-text">
          <span class="tutor-mode__body">
            <span class="tutor-mode__title" id="tutor-mode-free">Gratuito</span>
            <span class="tutor-mode__text" id="tutor-mode-free-text">Explicaciones, pistas y ejercicios con el contenido revisado del curso.
              No usa IA de pago y sigue funcionando aunque la IA avanzada no esté disponible.</span>
          </span>
        </label>
        <label class="tutor-mode">
          <input type="radio" name="tutor-mode" value="advanced" disabled
            aria-labelledby="tutor-mode-advanced" aria-describedby="tutor-mode-advanced-text tutor-advanced-status">
          <span class="tutor-mode__body">
            <span class="tutor-mode__title" id="tutor-mode-advanced">IA avanzada</span>
            <span class="tutor-mode__text" id="tutor-mode-advanced-text">Explicaciones adaptadas a tu nivel, pistas progresivas, análisis de tus
              errores y ejercicios a tu medida. Tiene un número limitado de consultas al día.</span>
            <span class="tutor-mode__status" id="tutor-advanced-status">Comprobando si está disponible…</span>
          </span>
        </label>
        <p class="tutor-mode__privacy" id="tutor-advanced-privacy" hidden></p>
      </fieldset>`;
}

/** Pinta el estado de la IA avanzada según lo que dice el servidor. */
function renderModes() {
  const radio = document.querySelector('#tutor-modes input[value="advanced"]');
  if (!radio) return;
  const status = modesFailed
    ? { selectable: false, text: "No se ha podido comprobar si está disponible. Sigues en el modo gratuito." }
    : advancedStatus(modes);
  radio.disabled = !status.selectable;
  $("#tutor-advanced-status").textContent = status.text;
  const privacy = $("#tutor-advanced-privacy");
  const provider = modes?.advanced?.available ? modes.advanced : null;
  privacy.hidden = !provider;
  if (provider) {
    const limit = provider.max_input_chars ? ` (máximo ${provider.max_input_chars} caracteres entre pregunta, código y error)` : "";
    privacy.textContent = provider.simulated
      ? "Modo de pruebas: la IA avanzada está simulada en este servidor y no envía nada a ningún servicio externo."
      : `Con la IA avanzada, tu pregunta, el código y el error que escribas${limit} y tu nivel en el tema se envían a ` +
        `${provider.provider === "openai" ? "OpenAI" : "un proveedor externo de IA"} para generar la respuesta. ` +
        "No incluyas datos personales. Las preguntas de comprobación las corrige el tutor, no la IA.";
  }
  if (!status.selectable && mode === "advanced") chooseMode("free");
}

async function loadModes() {
  try {
    modes = await request("GET", MODES_PATH);
    modesFailed = false;
  } catch {
    modes = null;
    modesFailed = true; // sin respuesta del servidor no se ofrece la IA avanzada
  }
  renderModes();
}

function chooseMode(value) {
  mode = value === "advanced" ? "advanced" : "free";
  const radio = document.querySelector(`#tutor-modes input[value="${mode}"]`);
  if (radio) radio.checked = true;
  const free = document.querySelector("[data-tutor-free]");
  if (free && mode === "free") free.hidden = true;
}

function addMessage(html, from, note = "") {
  const item = document.createElement("li");
  item.className = `assistant__msg assistant__msg--${from}`;
  const who = from === "user" ? "Tú" : "Tutor";
  item.innerHTML = `<span class="visually-hidden">${who}:</span>${html}${
    note ? `<p class="tutor__source">${escapeHtml(note)}</p>` : ""
  }`;
  if (from === "bot") addRunButtons(item);
  $("#tutor-messages").append(item);
  // Una respuesta larga se muestra desde su principio: no arrastra al alumno hasta el final
  item.scrollIntoView({ block: from === "bot" ? "start" : "nearest" });
}

/** Un botón «Ejecutar en tu navegador» bajo cada ejemplo de Python de la respuesta. */
function addRunButtons(item) {
  for (const block of item.querySelectorAll('pre.md-code[data-lang="python"]')) {
    const code = block.textContent;
    if (isRiskyPaste(code)) continue; // código que toca el navegador o la red: no se ofrece
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn--ghost tutor__run";
    button.textContent = "Ejecutar en tu navegador";
    button.dataset.tutorRun = "";
    block.after(button);
  }
}

async function runExample(button) {
  const block = button.previousElementSibling;
  let output = button.nextElementSibling;
  if (!output?.classList.contains("tutor__output")) {
    output = document.createElement("pre");
    output.className = "tutor__output";
    output.setAttribute("role", "status");
    output.tabIndex = 0;
    button.after(output);
  }
  button.disabled = true;
  output.textContent = "Ejecutando en tu navegador…";
  try {
    const result = await pythonRunner.run(block.textContent, "");
    const text = [result.output, result.error].filter(Boolean).join("\n");
    output.textContent = `Salida real (Python en tu navegador):\n${text || "(El programa no ha mostrado nada)"}`;
  } catch (error) {
    output.textContent = error instanceof TimeoutError ? `${error.message} ¿Hay un bucle infinito?` : error.message;
  } finally {
    button.disabled = false;
  }
}

function setStatus(text, problem = false) {
  const status = $("#tutor-status");
  status.textContent = text;
  status.dataset.problem = String(problem);
}

function setWaiting(form, waiting) {
  for (const button of form.querySelectorAll('[type="submit"], [data-tutor-hint], [data-tutor-alt], [data-tutor-exercise]')) {
    button.disabled = waiting;
  }
  form.querySelector("[data-tutor-cancel]").hidden = !waiting;
  form.closest(".tutor").setAttribute("aria-busy", String(waiting));
}

function readQuery(form, question, extra = {}) {
  const fields = form.elements;
  return {
    question,
    lessonSlug: fields.lesson.value,
    code: fields.code.value,
    error: fields.error.value,
    gradual: fields.gradual.checked,
    mode,
    ...extra,
  };
}

async function ask(form, query, { echo = true } = {}) {
  if (!query.question || pending) return;
  const mine = { controller: new AbortController(), conversation };
  pending = mine;
  lastQuery = query;
  form.querySelector("[data-tutor-retry]").hidden = true;
  if (echo) addMessage(`<p>${escapeHtml(query.question)}</p>`, "user");
  setWaiting(form, true);
  setStatus("Pregunta enviada. El tutor está pensando…");
  try {
    requestId += 1;
    const response = await request("POST", TUTOR_PATH, {
      json: sendMessageRequest(query, { contextId, id: requestId }),
      headers: { "A2A-Version": A2A_VERSION },
      signal: mine.controller.signal,
    });
    if (mine.conversation !== conversation) return; // llega tarde: la conversación ya no existe
    const result = readTaskResult(response);
    if (result.contextId) contextId = result.contextId;
    if (result.text) addMessage(renderMarkdown(result.text), "bot", sourceLabel(result.meta));
    setStatus(result.label, !result.ok);
    form.querySelector("[data-tutor-retry]").hidden = !result.retry;
    const offerFree = Boolean(result.reason?.startsWith("advanced_"));
    form.querySelector("[data-tutor-free]").hidden = !offerFree;
    if (result.meta.mode === "advanced") {
      modes = withRemaining(modes, result.meta);
      renderModes();
    } else if (offerFree) {
      loadModes(); // la cuota o la disponibilidad han cambiado: se vuelve a preguntar
    }
    if (result.ok) {
      form.elements.question.value = "";
      form.elements.question.placeholder = result.meta.expects_answer ? ANSWER_PLACEHOLDER : QUESTION_PLACEHOLDER;
    }
  } catch (error) {
    if (mine.conversation !== conversation) return;
    if (mine.controller.signal.aborted) {
      setStatus("Has cancelado la espera. Si el servidor ya estaba respondiendo, esa respuesta no se mostrará.");
    } else {
      setStatus(error.message, true);
      form.querySelector("[data-tutor-retry]").hidden = error.status === 429;
    }
  } finally {
    if (pending === mine) {
      pending = null;
      if (mine.conversation === conversation && $("#tutor-form")) setWaiting(form, false);
    }
  }
}

/** Olvida la conversación: la pregunta en curso, si la hay, ya no se pintará. */
function forgetConversation() {
  conversation += 1;
  contextId = null;
  lastQuery = null;
  pending?.controller.abort();
  pending = null;
}

/** Abre la sección. `lessons`: [{ slug, title }]; `lessonSlug`: la lección en la que estaba. */
export async function openTutor(lessons, { moveFocus = true, lessonSlug = "" } = {}) {
  const view = $("#tutor-view");
  const available = await tutorAvailable;
  const user = available ? (state.user?.id ?? null) : "sin-tutor";
  if (renderedFor !== user) {
    renderedFor = user;
    forgetConversation();
    view.innerHTML = !available ? unavailableHtml() : user === null ? signedOutHtml() : chatHtml(lessons, lessonSlug);
    mode = "free"; // cada vez se empieza en la gratuita: la de pago se elige expresamente
    modes = null;
    modesFailed = false;
    if (available && user !== null) loadModes();
  } else if (lessonSlug && $("#tutor-form") && !$("#tutor-messages").children.length) {
    $("#tutor-form").elements.lesson.value = lessonSlug; // sin conversación empezada: la lección actual
  }
  if (moveFocus) $("#tutor-title").focus();
}

export function initTutor() {
  const view = $("#tutor-view");
  view.addEventListener("submit", (event) => {
    if (event.target.id !== "tutor-form") return;
    event.preventDefault();
    ask(event.target, readQuery(event.target, event.target.elements.question.value.trim()));
  });
  view.addEventListener("change", (event) => {
    if (event.target.name !== "tutor-mode") return;
    chooseMode(event.target.value);
    setStatus(mode === "advanced" ? `Modalidad: IA avanzada. ${advancedStatus(modes).text}` : "Modalidad: gratuita.");
  });
  view.addEventListener("click", (event) => {
    const form = $("#tutor-form");
    if (event.target.closest("[data-open-account]")) openAccount();
    if (event.target.closest("[data-tutor-run]")) runExample(event.target.closest("[data-tutor-run]"));
    if (event.target.closest("[data-tutor-hint]")) ask(form, readQuery(form, "Dame una pista del ejercicio"));
    if (event.target.closest("[data-tutor-alt]")) ask(form, readQuery(form, "Explícamelo de otra forma", { alternative: true }));
    if (event.target.closest("[data-tutor-exercise]")) ask(form, readQuery(form, "Proponme otro ejercicio"));
    if (event.target.closest("[data-tutor-free]")) {
      chooseMode("free");
      setStatus("Sigues en el modo gratuito.");
      form.elements.question.focus();
    }
    if (event.target.closest("[data-tutor-cancel]")) pending?.controller.abort();
    if (event.target.closest("[data-tutor-retry]") && lastQuery) ask(form, { ...lastQuery, mode }, { echo: false });
    if (event.target.closest("[data-tutor-reset]")) {
      forgetConversation();
      setWaiting(form, false);
      form.querySelector("[data-tutor-retry]").hidden = true;
      form.elements.question.placeholder = QUESTION_PLACEHOLDER;
      $("#tutor-messages").innerHTML = "";
      setStatus("Conversación nueva.");
      form.elements.question.focus();
    }
  });
  // Al cerrar sesión (o cambiar de cuenta) con el tutor en otra pestaña, la conversación se borra
  // ya, no al volver (con el tutor a la vista, app.js lo vuelve a pintar)
  subscribe((change) => {
    if (change.type !== "user" || !view.hidden || renderedFor === undefined || renderedFor === "sin-tutor") return;
    if ((state.user?.id ?? null) === renderedFor) return;
    forgetConversation();
    renderedFor = undefined;
    view.innerHTML = "";
  });
  tutorAvailable.then((available) => {
    $("#tutor-nav").hidden = !available;
  });
}
