/* Tutor IA dentro del panel del asistente de cada lección.

   - Solo aparece si el servidor ofrece la IA (/health → ai) y la comprueba con sesión iniciada.
     Sin servidor, sin IA o sin conexión, el resto del asistente funciona igual que siempre.
   - El código solo viaja si el alumno marca la casilla (o pulsa «Revisar mi código», que lo dice).
   - Las respuestas se pintan con el Markdown seguro (escapa todo el HTML) y llevan la etiqueta
     «IA · no es la corrección oficial»: nunca cambian el progreso. */

import { escapeHtml, renderMarkdown } from "../markdown.js";
import { lastRunError } from "../console.js";
import { language } from "../i18n.js";
import { state, subscribe } from "../store.js";
import { aiOffered, aiStatus, askAi } from "./ai-api.js";
import { buildRequest, createConversation, errorText, remember, STATUS_TEXT } from "./ai-logic.js";

const $ = (selector) => document.querySelector(selector);
const ASKED = {
  chat: null, // se muestra la pregunta
  hint: "Pedir pista",
  "explain-error": "Explicar mi error",
  "review-code": "Revisar mi código",
};

let addMessage = () => null;
let lessonSlug = null;
let conversation = createConversation();
let pending = null;
let status = "checking";

function setBusy(busy) {
  const form = $("#assistant-ai-form");
  const focused = document.activeElement;
  $("#assistant-messages").setAttribute("aria-busy", String(busy));
  for (const control of form.elements) control.disabled = busy || status !== "available";
  // Un control desactivado pierde el foco (y Escape dejaría de cerrar el panel): pasa a la
  // conversación, que es donde aparece la respuesta
  if (focused?.disabled && form.contains(focused)) $("#assistant-messages").focus();
}

function setStatus(next) {
  status = next;
  const box = $("#assistant-ai-status");
  box.textContent = STATUS_TEXT[next];
  box.dataset.state = next;
  $("#assistant-ai-retry").hidden = !["unavailable", "error"].includes(next);
  setBusy(Boolean(pending));
}

/** Vuelve a mirar si el tutor está disponible (al abrir el panel, al iniciar sesión, Reintentar). */
export async function refreshAiPanel() {
  const section = $("#assistant-ai");
  if (!section) return;
  if (!(await aiOffered())) {
    section.hidden = true;
    return;
  }
  section.hidden = false;
  if (!state.user) {
    setStatus("login");
    return;
  }
  setStatus("checking");
  const result = await aiStatus();
  if (result === "off") section.hidden = true;
  else setStatus(result);
}

/** Lección nueva: se cancela la pregunta en curso y se empieza otra conversación. */
export function setAiLesson(lesson) {
  pending?.abort();
  pending = null;
  lessonSlug = lesson.slug;
  conversation = createConversation();
  if ($("#assistant-ai-form")) setBusy(false);
}

async function ask(mode) {
  if (pending || status !== "available" || !lessonSlug) return;
  const field = $("#assistant-ai-question");
  const { body, problem } = buildRequest(mode, {
    lessonSlug,
    question: field.value,
    code: $("#console-editor")?.value ?? "",
    sendCode: $("#assistant-ai-code").checked,
    error: lastRunError(),
    locale: language,
    conversation,
  });
  if (problem) {
    addMessage(`<p>${escapeHtml(problem)}</p>`, "bot");
    return;
  }
  addMessage(`<p>${escapeHtml(ASKED[mode] ?? body.question)}</p>`, "user");
  const reply = addMessage("<p>El tutor IA está pensando…</p>", "bot");
  const controller = new AbortController();
  pending = controller;
  setBusy(true);
  try {
    const result = await askAi(mode, body, controller.signal);
    if (controller.signal.aborted) return; // el alumno cambió de lección
    reply.classList.add("assistant__msg--ai");
    reply.innerHTML = `<p class="assistant__ai-badge">IA · no es la corrección oficial</p>${renderMarkdown(result.answer)}`;
    remember(conversation, mode, body.question ?? "", result.answer);
    if (mode === "chat") field.value = "";
  } catch (error) {
    if (controller.signal.aborted && pending !== controller) return;
    reply.innerHTML = `<p>${escapeHtml(errorText(error))}</p>`;
    if (error?.status === 401) setStatus("login");
    else if (error?.status === 503 || error?.status === 404) setStatus("unavailable");
  } finally {
    if (pending === controller) {
      pending = null;
      setBusy(false);
    }
  }
}

export function initAiPanel({ onMessage }) {
  addMessage = onMessage;
  const form = $("#assistant-ai-form");
  if (!form) return;
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    ask("chat");
  });
  form.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-mode]");
    if (button && button.type === "button") ask(button.dataset.mode);
  });
  $("#assistant-ai-retry").addEventListener("click", () => refreshAiPanel());
  subscribe((change) => {
    if (change.type === "user") refreshAiPanel();
  });
  refreshAiPanel();
}
