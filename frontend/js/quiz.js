/* Mini-quiz de 3 preguntas por lección, con explicación de cada respuesta. */

import { recordQuiz, game } from "./game.js";
import { escapeHtml, renderMarkdown } from "./markdown.js";

const $ = (selector) => document.querySelector(selector);
let lesson = null;

function render() {
  const best = game.quiz[lesson.slug];
  $("#panel-quiz").innerHTML = `
    <form class="quiz" id="quiz-form" novalidate>
      <p class="quiz__intro">Comprueba lo que has aprendido. Cada pregunta explica por qué la respuesta es correcta.
        ${best !== undefined ? `<strong>Mejor resultado: ${best}/3</strong>` : ""}</p>
      ${lesson.quiz
        .map(
          (question, qi) => `
        <fieldset class="quiz__q" data-q="${qi}">
          <legend><span class="quiz__num">${qi + 1}</span> ${renderMarkdown(question.q).replace(/^<p>|<\/p>$/g, "")}</legend>
          ${question.code ? `<pre class="quiz__code" tabindex="0"><code>${escapeHtml(question.code)}</code></pre>` : ""}
          <div class="quiz__options">
            ${question.options
              .map(
                (option, oi) => `
              <label class="quiz__option">
                <input type="radio" name="q${qi}" value="${oi}">
                <span>${renderMarkdown(option).replace(/^<p>|<\/p>$/g, "")}</span>
              </label>`,
              )
              .join("")}
          </div>
          <div class="quiz__feedback" hidden></div>
        </fieldset>`,
        )
        .join("")}
      <p class="quiz__message" id="quiz-message" role="alert"></p>
      <div class="quiz__actions">
        <button class="btn btn--primary" type="submit" id="quiz-submit">Comprobar respuestas</button>
        <button class="btn btn--ghost" type="button" id="quiz-retry" hidden>Volver a intentarlo</button>
      </div>
      <p class="quiz__score" id="quiz-score" role="status"></p>
    </form>`;

  $("#quiz-form").addEventListener("submit", grade);
  $("#quiz-retry").addEventListener("click", () => {
    render();
    $("#panel-quiz input[type=radio]")?.focus();
  });
}

function grade(event) {
  event.preventDefault();
  const form = event.target;
  const answers = lesson.quiz.map((_, qi) => form.elements[`q${qi}`].value);
  if (answers.some((value) => value === "")) {
    $("#quiz-message").textContent = "Responde las 3 preguntas antes de comprobar.";
    return;
  }
  $("#quiz-message").textContent = "";

  let correct = 0;
  lesson.quiz.forEach((question, qi) => {
    const ok = Number(answers[qi]) === question.answer;
    if (ok) correct += 1;
    const fieldset = form.querySelector(`[data-q="${qi}"]`);
    fieldset.dataset.result = ok ? "ok" : "ko";
    fieldset.querySelectorAll(".quiz__option").forEach((label, oi) => {
      if (oi === question.answer) label.dataset.correct = "true";
    });
    const feedback = fieldset.querySelector(".quiz__feedback");
    feedback.hidden = false;
    feedback.innerHTML = `<p class="quiz__verdict">${ok ? "✓ Correcto" : "✗ Incorrecto"}</p>${renderMarkdown(question.explain)}`;
  });
  form.querySelectorAll("input").forEach((input) => {
    input.disabled = true;
  });

  const messages = ["¡A repasar la teoría!", "Vas por buen camino.", "¡Casi perfecto!", "¡Perfecto! Dominas esta lección."];
  $("#quiz-score").innerHTML = `<strong>${correct}/3</strong> · ${messages[correct]}`;
  $("#quiz-submit").hidden = true;
  $("#quiz-retry").hidden = false;
  $("#quiz-score").focus?.();
  recordQuiz(lesson.slug, correct);
}

export function setQuizLesson(next) {
  lesson = next;
  render();
}
