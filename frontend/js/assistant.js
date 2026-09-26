/* Asistente de la lección: respuestas preparadas por lección, pista y siguiente tema.
   No es una IA: todo el contenido está revisado en data/lessons.json. */

import { escapeHtml, renderMarkdown } from "./markdown.js";

const $ = (selector) => document.querySelector(selector);
let context = { lesson: null, nextLesson: null, goTo: () => {} };

function addMessage(html, from) {
  const item = document.createElement("li");
  item.className = `assistant__msg assistant__msg--${from}`;
  item.innerHTML = html;
  $("#assistant-messages").append(item);
  item.scrollIntoView({ block: "nearest" });
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
  $("#assistant-messages").innerHTML = "";
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
}
