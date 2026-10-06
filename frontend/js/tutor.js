/* Tutor Python (ADR-0034): una sección más del dashboard, no la app convertida en chat.
   Habla con el agente Python Tutor del backend por A2A 1.0 (JSON-RPC, ver tutor-protocol.js).
   - Solo aparece si el servidor lo ofrece (su Agent Card responde) y pide la sesión iniciada.
   - Lo que escribes se envía como texto: tu código nunca se ejecuta en el servidor.
   - La conversación vive solo en esta página (no se guarda en el navegador). */

import { openAccount } from "./account.js";
import { API_URL, apiEnabled, request } from "./api.js";
import { escapeHtml, renderMarkdown } from "./markdown.js";
import { state } from "./store.js";
import { A2A_VERSION, readTaskResult, sendMessageRequest, TUTOR_PATH } from "./tutor-protocol.js";

const $ = (selector) => document.querySelector(selector);

/** ¿Hay tutor en este servidor? Se pregunta a su Agent Card, la ficha pública del agente. */
export const tutorAvailable = apiEnabled
  ? fetch(`${API_URL}${TUTOR_PATH}/.well-known/agent-card.json`)
      // Se lee la card entera: una respuesta a medio leer deja la conexión abierta
      .then((response) => (response.ok ? response.json() : null))
      .then((card) => Boolean(card?.supportedInterfaces?.length))
      .catch(() => false)
  : Promise.resolve(false);

let contextId = null; // conversación actual (contextId de A2A)
let renderedFor; // usuario para el que está pintada la vista (undefined = nada pintado)
let requestId = 0;

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

function chatHtml(lessons) {
  const options = lessons.map((lesson) => `<option value="${escapeHtml(lesson.slug)}">${escapeHtml(lesson.title)}</option>`).join("");
  return `${hero(
    "Te explica conceptos y errores, revisa tu código y te da pistas sin resolver el ejercicio por ti. " +
      "No ejecuta tu código: para probarlo usa la consola de cada lección.",
  )}
    <section class="course-section tutor" aria-labelledby="tutor-chat-title">
      <h2 class="section-title" id="tutor-chat-title">Conversación</h2>
      <ol class="tutor__messages" id="tutor-messages" aria-live="polite"></ol>
      <p class="tutor__status" id="tutor-status" role="status"></p>
      <form class="tutor__form" id="tutor-form">
        <label>Tu pregunta
          <textarea name="question" rows="3" maxlength="4000" required placeholder="Ejemplo: ¿por qué me sale NameError?"></textarea>
        </label>
        <details class="tutor__extra">
          <summary>Añadir lección, código o error (opcional)</summary>
          <label>Lección <select name="lesson"><option value="">Ninguna</option>${options}</select></label>
          <label>Tu código <textarea name="code" rows="6" maxlength="20000" spellcheck="false" class="tutor__code"></textarea></label>
          <label>Mensaje de error <textarea name="error" rows="3" maxlength="4000" spellcheck="false" class="tutor__code"></textarea></label>
        </details>
        <div class="tutor__actions">
          <button class="btn btn--primary" type="submit">Preguntar</button>
          <button class="btn btn--ghost" type="button" data-tutor-reset>Nueva conversación</button>
        </div>
      </form>
      <p class="account-card__meta">Solo se envía lo que escribes aquí y, si eliges una lección, tu progreso en ella.
        No se guarda en tu cuenta: el servidor conserva tus últimas consultas en memoria temporal.</p>
    </section>`;
}

function addMessage(html, from) {
  const item = document.createElement("li");
  item.className = `assistant__msg assistant__msg--${from}`;
  item.innerHTML = html;
  $("#tutor-messages").append(item);
  item.scrollIntoView({ block: "nearest" });
}

function setStatus(text, problem = false) {
  const status = $("#tutor-status");
  status.textContent = text;
  status.dataset.problem = String(problem);
}

async function ask(form) {
  const fields = form.elements;
  const question = fields.question.value.trim();
  if (!question) return;
  const query = { question, lessonSlug: fields.lesson.value, code: fields.code.value, error: fields.error.value };
  const button = form.querySelector('[type="submit"]');
  addMessage(`<p>${escapeHtml(question)}</p>`, "user");
  button.disabled = true;
  setStatus("Pregunta enviada. El tutor está pensando…");
  try {
    requestId += 1;
    const response = await request("POST", TUTOR_PATH, {
      json: sendMessageRequest(query, { contextId, id: requestId }),
      headers: { "A2A-Version": A2A_VERSION },
    });
    const result = readTaskResult(response);
    if (result.contextId) contextId = result.contextId;
    if (result.text) addMessage(renderMarkdown(result.text), "bot");
    setStatus(result.label, !result.ok);
    if (result.ok) fields.question.value = "";
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    button.disabled = false;
  }
}

/** Abre la sección. `lessons`: [{ slug, title }] para elegir sobre qué lección se pregunta. */
export async function openTutor(lessons, { moveFocus = true } = {}) {
  const view = $("#tutor-view");
  const available = await tutorAvailable;
  const user = available ? (state.user?.id ?? null) : "sin-tutor";
  if (renderedFor !== user) {
    renderedFor = user;
    contextId = null;
    view.innerHTML = !available ? unavailableHtml() : user === null ? signedOutHtml() : chatHtml(lessons);
  }
  if (moveFocus) $("#tutor-title").focus();
}

export function initTutor() {
  const view = $("#tutor-view");
  view.addEventListener("submit", (event) => {
    if (event.target.id !== "tutor-form") return;
    event.preventDefault();
    ask(event.target);
  });
  view.addEventListener("click", (event) => {
    if (event.target.closest("[data-open-account]")) openAccount();
    if (event.target.closest("[data-tutor-reset]")) {
      contextId = null;
      $("#tutor-messages").innerHTML = "";
      setStatus("Conversación nueva.");
      $("#tutor-form").elements.question.focus();
    }
  });
  tutorAvailable.then((available) => {
    $("#tutor-nav").hidden = !available;
  });
}
