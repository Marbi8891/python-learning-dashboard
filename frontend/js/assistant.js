/* Asistente de la lección.
   - Respuestas preparadas por lección, pista y siguiente tema (revisadas en data/lessons.json).
   - Si el servidor tiene tutor con IA (/api/health → tutor), el alumno puede además escribir
     cualquier duda. La responde una IA a través de la API (POST /api/v1/tutor/ask): la clave del
     proveedor nunca llega al navegador. Se avisa siempre de que contesta una IA (RIA, art. 50.1). */

import { ApiError, request, serverInfo } from "./api.js";
import { openAccount } from "./account.js";
import { escapeHtml, renderMarkdown } from "./markdown.js";
import { state } from "./store.js";

const $ = (selector) => document.querySelector(selector);
let context = { lesson: null, nextLesson: null, goTo: () => {} };
// Conversación con el tutor de la lección abierta (solo en memoria; se vacía al cambiar de lección)
let history = [];
let tutorOn = false;
let asking = false;

const HISTORY_TURNS = 6;
const CODE_CHARS = 4000;
const ERROR_CHARS = 2000;
const TUTOR_NOTE =
  "Las respuestas a lo que escribes las genera una IA: puede equivocarse, compruébalo en la teoría. " +
  "No escribas datos personales.";

function addMessage(html, from) {
  const item = document.createElement("li");
  item.className = `assistant__msg assistant__msg--${from}`;
  item.innerHTML = html;
  $("#assistant-messages").append(item);
  item.scrollIntoView({ block: "nearest" });
  return item;
}

function renderSuggestions() {
  const { lesson, nextLesson } = context;
  const chips = lesson.assistant.faq.map(
    (item, index) => `<button type="button" class="chip" data-faq="${index}">${escapeHtml(item.q)}</button>`,
  );
  chips.push('<button type="button" class="chip" data-hint>Dame una pista del ejercicio</button>');
  if (nextLesson) {
    chips.push(
      `<button type="button" class="chip chip--next" data-next>Siguiente tema: ${escapeHtml(nextLesson.title)} →</button>`,
    );
  }
  $("#assistant-suggestions").innerHTML = chips.join("");
}

export function setAssistantLesson(lesson, nextLesson, goTo) {
  context = { lesson, nextLesson, goTo };
  history = [];
  $("#assistant-messages").replaceChildren();
  const invite = tutorOn ? " Elige una pregunta o escribe tu duda abajo." : "";
  addMessage(`<p>Estás en <strong>${escapeHtml(lesson.title)}</strong>. ¿En qué te ayudo?${invite}</p>`, "bot");
  renderSuggestions();
}

function toggle(open) {
  const panel = $("#assistant-panel");
  panel.hidden = !open;
  $("#assistant-toggle").setAttribute("aria-expanded", String(open));
  if (open) panel.querySelector(".chip")?.focus();
  else $("#assistant-toggle").focus();
}

/** Código del editor y último error de la consola, si el alumno ha dejado marcada la casilla. */
function consoleContext() {
  if (!$("#assistant-attach")?.checked) return {};
  const code = $("#console-editor")?.value.trim();
  const box = $("#console-output");
  const errorBox = box?.dataset.state === "error" ? box.querySelector(".console__error") : null;
  const error = errorBox?.textContent.replace(/^Error/, "").trim();
  return {
    ...(code ? { code: code.slice(0, CODE_CHARS) } : {}),
    ...(error ? { error: error.slice(-ERROR_CHARS) } : {}),
  };
}

function askToSignIn() {
  const item = addMessage(
    "<p>Para preguntar al tutor con IA necesitas iniciar sesión (la cuenta es gratis). Mientras, puedes usar las preguntas sugeridas.</p>" +
      '<p><button type="button" class="chip" data-sign-in>Iniciar sesión</button></p>',
    "bot",
  );
  item.querySelector("[data-sign-in]").addEventListener("click", () => openAccount("login"));
}

async function askTutor(question) {
  addMessage(`<p>${escapeHtml(question)}</p>`, "user");
  if (!state.user) {
    askToSignIn();
    return;
  }
  asking = true;
  $("#assistant-send").disabled = true;
  const pending = addMessage('<p class="assistant__thinking">Pensando…</p>', "bot");
  pending.setAttribute("aria-busy", "true");
  try {
    const { answer } = await request("POST", "/api/v1/tutor/ask", {
      json: { question, lesson_slug: context.lesson?.slug ?? null, history, ...consoleContext() },
    });
    pending.innerHTML = renderMarkdown(answer);
    history = [...history, { role: "user", content: question }, { role: "assistant", content: answer.slice(0, 3000) }].slice(
      -HISTORY_TURNS,
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      pending.remove();
      askToSignIn();
    } else {
      pending.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
      pending.classList.add("assistant__msg--error");
    }
  } finally {
    pending.removeAttribute("aria-busy");
    asking = false;
    $("#assistant-send").disabled = false;
  }
}

function enableTutor() {
  tutorOn = true;
  $("#assistant-form").hidden = false;
  $("#assistant-note").textContent = TUTOR_NOTE;
}

export function initAssistant() {
  $("#assistant-toggle").addEventListener("click", () => toggle($("#assistant-panel").hidden));
  $("#assistant-close").addEventListener("click", () => toggle(false));
  $("#assistant-panel").addEventListener("keydown", (event) => {
    if (event.key === "Escape") toggle(false);
  });

  $("#assistant-suggestions").addEventListener("click", (event) => {
    const chip = event.target.closest(".chip");
    if (!chip) return;
    const { lesson, nextLesson } = context;
    if (chip.dataset.faq !== undefined) {
      const item = lesson.assistant.faq[Number(chip.dataset.faq)];
      addMessage(`<p>${escapeHtml(item.q)}</p>`, "user");
      addMessage(renderMarkdown(item.a), "bot");
    } else if (chip.hasAttribute("data-hint")) {
      addMessage("<p>Dame una pista del ejercicio</p>", "user");
      addMessage(renderMarkdown(lesson.assistant.hint), "bot");
    } else if (chip.hasAttribute("data-next") && nextLesson) {
      context.goTo(nextLesson.slug);
    }
  });

  const input = $("#assistant-input");
  $("#assistant-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question || asking) return;
    input.value = "";
    askTutor(question);
  });
  // Enter envía; Mayús+Enter hace un salto de línea
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      $("#assistant-form").requestSubmit();
    }
  });

  serverInfo.then((info) => {
    if (info?.tutor) enableTutor();
  });
}
