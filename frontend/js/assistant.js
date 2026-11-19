/* Asistente de la lección: respuestas preparadas por lección, pista y siguiente tema (revisadas en
   data/lessons.json). Si el servidor tiene configurado NEXARO, ofrece además un tutor con IA que guía
   con pistas sin dar la solución (docs/TUTOR.md). */

import { request, serverInfo } from "./api.js";
import { escapeHtml, renderMarkdown } from "./markdown.js";

const $ = (selector) => document.querySelector(selector);
let context = { lesson: null, nextLesson: null, goTo: () => {} };
// Conversación del tutor (firmada por el servidor para este alumno); una por lección
let tutorConversation = null;
let tutorBusy = false;
// Un modelo local en CPU tarda: el backend espera hasta 200 s a NEXARO (TUTOR_TIMEOUT_SECONDS)
const TUTOR_TIMEOUT_MS = 210_000;

const TUTOR_STATES = {
  checking: "Comprobando el tutor…",
  online: "Tutor conectado (NEXARO en este equipo)",
  offline: "Tutor no disponible: NEXARO no responde (apagado o sin modelo). El resto de la lección funciona igual.",
  error: "No se pudo comprobar el tutor.",
  login: "Inicia sesión para usar el tutor.",
};

function setTutorState(state) {
  const line = $("#tutor-status");
  line.dataset.state = state;
  line.textContent = TUTOR_STATES[state];
  // Reintentar solo tiene sentido si no está conectado; preguntar, solo si lo está
  $("#tutor-retry").hidden = state === "online" || state === "checking";
  $("#tutor-send").disabled = state !== "online" || tutorBusy;
}

async function checkTutor() {
  setTutorState("checking");
  try {
    const { available } = await request("GET", "/api/tutor/status");
    setTutorState(available ? "online" : "offline");
  } catch (error) {
    setTutorState(error.status === 401 ? "login" : "error");
  }
}

const TUTOR_NOTE =
  "Respuestas preparadas para cada lección. El tutor usa NEXARO Personal AI en este equipo: recibe tu pregunta, el ejercicio y, si lo marcas, tu código. Puede equivocarse.";

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
  tutorConversation = null;
  $("#assistant-messages").replaceChildren();
  addMessage(`<p>Estás en <strong>${escapeHtml(lesson.title)}</strong>. ¿En qué te ayudo?</p>`, "bot");
  renderSuggestions();
}

function toggle(open) {
  const panel = $("#assistant-panel");
  panel.hidden = !open;
  $("#assistant-toggle").setAttribute("aria-expanded", String(open));
  if (open) panel.querySelector(".chip")?.focus();
  else $("#assistant-toggle").focus();
}

async function askTutor(event) {
  event.preventDefault();
  const question = $("#tutor-question").value.trim();
  if (!question || tutorBusy) return;
  tutorBusy = true;
  $("#tutor-send").disabled = true;
  addMessage(`<p>${escapeHtml(question)}</p>`, "user");
  const reply = addMessage("<p>Pensando…</p>", "bot");
  reply.setAttribute("aria-busy", "true");
  try {
    const answer = await request("POST", "/api/tutor", {
      signal: AbortSignal.timeout(TUTOR_TIMEOUT_MS),
      json: {
        lesson: context.lesson.slug,
        question,
        code: $("#tutor-code").checked ? $("#console-editor").value : "",
        conversation: tutorConversation,
      },
    });
    tutorConversation = answer.conversation;
    reply.innerHTML = renderMarkdown(answer.answer);
    $("#tutor-question").value = "";
  } catch (error) {
    tutorConversation = null; // si NEXARO perdió la conversación, la siguiente empieza otra
    const timedOut = error.name === "TimeoutError";
    const message =
      error.status === 401
        ? "Inicia sesión para preguntar al tutor."
        : timedOut
          ? "El tutor ha tardado demasiado. Vuelve a probar con una pregunta más corta."
          : error.message;
    reply.innerHTML = `<p>${escapeHtml(message)}</p>`;
    if (error.status === 503 || error.status === 0) setTutorState("offline");
  } finally {
    reply.removeAttribute("aria-busy");
    tutorBusy = false;
    $("#tutor-send").disabled = $("#tutor-status").dataset.state !== "online";
  }
}

async function initTutor() {
  const info = await serverInfo;
  if (!info?.tutor) return;
  $("#tutor-form").hidden = false;
  $("#assistant-note").textContent = TUTOR_NOTE;
  $("#tutor-form").addEventListener("submit", askTutor);
  $("#tutor-retry").addEventListener("click", checkTutor);
  checkTutor();
  // Enter envía, Mayús+Enter salta de línea (como el resto de chats)
  $("#tutor-question").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      $("#tutor-form").requestSubmit();
    }
  });
}

export function initAssistant() {
  initTutor();
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
}
