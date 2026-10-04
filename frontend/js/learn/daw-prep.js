/* Preparación DAW (#/daw, ADR-0031 fase 2): competencias, qué reforzar antes de avanzar,
   actividades con formato de examen y simulacros. */

import { allStats } from "./mastery.js";
import { buildExam, competencyAdvice, competencyStats, examByCompetency, examMinutes, examReadiness } from "./exam.js";
import { selectExercises } from "./recommend.js";
import { escapeHtml, meter, percent, STATUS } from "./ui.js";

/** Actividades de examen: tipos de ejercicio, tamaño y tiempo (null = sin tiempo). */
export const EXAM_ACTIVITIES = [
  { id: "cronometrados", label: "Ejercicios cronometrados", text: "8 ejercicios variados en 20 minutos, con corrección al momento.", kinds: null, size: 8, minutes: 20 },
  { id: "problemas", label: "Problemas completos", text: "Programas desde cero, corregidos con tests, como en el examen.", kinds: ["code"], size: 3, minutes: null, minLevel: 2 },
  { id: "lectura", label: "Lectura de código", text: "¿Qué muestra este programa? Trazas a mano.", kinds: ["output"], size: 6, minutes: null },
  { id: "errores", label: "Detectar errores", text: "Encuentra la línea que falla y por qué.", kinds: ["bug"], size: 6, minutes: null },
  { id: "algoritmos", label: "Del enunciado al algoritmo", text: "Ordena pseudocódigo y tradúcelo a Python.", kinds: ["order", "code"], size: 4, minutes: null, concepts: ["algoritmos", "pseudocodigo"] },
];

const formatDay = (iso) => new Date(iso).toLocaleDateString("es-ES", { day: "numeric", month: "short" });

/** Conceptos de DAW sobre los que practicar: los empezados (o, si no hay, los primeros de la ruta). */
export function dawScope(index, stats) {
  const ids = index.data.daw.flatMap((c) => c.concepts);
  const started = ids.filter((id) => stats.get(id).attempted > 0 || stats.get(id).status === "leido");
  return started.length ? started : index.path.filter((id) => ids.includes(id)).slice(0, 3);
}

/** Ejercicios de una actividad de examen. */
export function activityExercises(index, state, activity) {
  const stats = allStats(index, state);
  const scope = activity.concepts ?? dawScope(index, stats);
  let list = selectExercises(index, state, scope, activity.size * 3, { kinds: activity.kinds });
  list = list.filter((e) => e.daw && (!activity.minLevel || e.level >= activity.minLevel));
  return list.slice(0, activity.size);
}

export function renderDawPrep(index, state) {
  const stats = allStats(index, state);
  const competencies = competencyStats(index, stats);
  const advice = competencyAdvice(index, competencies);
  const readiness = examReadiness(competencies);
  const studied = buildExam(index, state, { scope: "studied" });
  const full = buildExam(index, state, { scope: "all" });
  const last = state.exams.at(-1);

  const cards = competencies
    .map((c) => {
      const tip = advice.find((a) => a.before === c.id);
      const concepts = c.concepts
        .map((id) => {
          const s = stats.get(id);
          return `<li class="lx-row"><a href="#/teoria/${id}">${escapeHtml(index.concepts.get(id).title)}</a><span class="lx-status" data-status="${s.status}">${STATUS[s.status].short}</span></li>`;
        })
        .join("");
      return `
        <section class="lx-panel lx-competency" aria-labelledby="comp-${c.id}">
          <h2 class="lx-panel__title" id="comp-${c.id}">${escapeHtml(c.title)}</h2>
          <p class="lx-muted">${escapeHtml(c.summary)}</p>
          <p><strong>${percent(c.score)}</strong> de dominio · ${c.mastered}/${c.concepts.length} conceptos dominados</p>
          ${meter(c.score, `Dominio de ${c.title}`)}
          ${tip ? `<p class="lx-warning">${escapeHtml(tip.text)}</p>` : ""}
          <details class="lx-details"><summary>Conceptos</summary><ul class="lx-list lx-list--pad">${concepts}</ul></details>
          ${
            c.started && c.weakest.length
              ? `<p class="lx-muted">Lo más flojo: ${escapeHtml(c.weakest.map((id) => index.concepts.get(id).title).join(" y "))}.</p>
                 <button class="btn btn--ghost" type="button" data-daw-prep="reinforce" data-concepts="${c.weakest.join(",")}">Reforzar lo más flojo<span class="visually-hidden"> de ${escapeHtml(c.title)}</span></button>`
              : ""
          }
        </section>`;
    })
    .join("");

  const activities = EXAM_ACTIVITIES.map((a) => {
    const count = activityExercises(index, state, a).length;
    return `<li class="lx-card"><h3 class="lx-card__title">${a.label}</h3><p class="lx-muted">${a.text}</p>
      <button class="btn btn--ghost" type="button" data-daw-prep="activity" data-activity="${a.id}"${count ? "" : " disabled"}>${count ? "Empezar" : "Disponible al avanzar en la ruta"}<span class="visually-hidden">: ${a.label}</span></button></li>`;
  }).join("");

  const history = state.exams
    .slice()
    .reverse()
    .slice(0, 8)
    .map((e) => `<li class="lx-row"><span>${formatDay(e.date)} · ${e.kind === "daw-completo" ? "Temario completo" : "Lo estudiado"}</span><span class="lx-row__value">${e.correct} de ${e.total} · ${percent(e.total ? e.correct / e.total : 0)} · ${Math.round(e.seconds / 60)} min</span></li>`)
    .join("");
  const lastBreakdown = last
    ? examByCompetency(index, last)
        .filter((c) => c.total)
        .map((c) => `<li class="lx-row"><span>${escapeHtml(c.title)}</span><span class="lx-row__value">${c.ok} de ${c.total}</span></li>`)
        .join("")
    : "";

  return `
    <header class="lx-head">
      <p class="eyebrow">Programación · 1.º DAW</p>
      <h1 class="lx-title" id="learn-title" tabindex="-1">Preparación DAW</h1>
      <p class="lx-lead">Organizado por competencias. Python es el lenguaje para desarrollar la lógica que pide el módulo de Programación.</p>
      <ul class="lx-facts">
        <li><strong>${percent(readiness)}</strong> de preparación estimada</li>
        <li><strong>${state.exams.length}</strong> simulacros hechos</li>
        ${last ? `<li>Último: <strong>${percent(last.total ? last.correct / last.total : 0)}</strong></li>` : ""}
      </ul>
      <p class="lx-muted">La preparación es orientativa: el dominio de cada competencia ponderado por su peso en el simulacro.</p>
    </header>

    <section class="lx-section" aria-labelledby="lx-exam-title">
      <h2 class="lx-section__title" id="lx-exam-title">Simulacro de examen</h2>
      <p class="lx-muted">Preguntas de todas las competencias y 1-2 problemas de escribir código. Sin corrección hasta el final, con tiempo límite. Los fallos quedan registrados como errores para repasarlos.</p>
      <div class="lx-actions">
        <button class="btn btn--primary" type="button" data-daw-prep="exam" data-scope="studied"${studied.length >= 4 ? "" : " disabled"}>Simulacro de lo estudiado (${studied.length} preguntas · ${examMinutes(studied)} min)</button>
        <button class="btn btn--ghost" type="button" data-daw-prep="exam" data-scope="all">Simulacro del temario completo (${full.length} preguntas · ${examMinutes(full)} min)</button>
      </div>
      ${studied.length < 4 ? '<p class="lx-muted">El simulacro de lo estudiado se activa cuando hayas practicado algunos conceptos.</p>' : ""}
    </section>

    <div class="lx-grid">${cards}</div>

    <section class="lx-section" aria-labelledby="lx-acts-title">
      <h2 class="lx-section__title" id="lx-acts-title">Preparación de examen</h2>
      <ul class="lx-cards">${activities}</ul>
    </section>

    ${
      history
        ? `<div class="lx-grid lx-grid--2">
            <section class="lx-panel" aria-labelledby="lx-hist-title"><h2 class="lx-panel__title" id="lx-hist-title">Tus simulacros</h2><ul class="lx-list">${history}</ul></section>
            <section class="lx-panel" aria-labelledby="lx-last-title"><h2 class="lx-panel__title" id="lx-last-title">Último simulacro por competencia</h2><ul class="lx-list">${lastBreakdown}</ul></section>
          </div>`
        : ""
    }

    <section class="lx-section" aria-labelledby="lx-more-title">
      <h2 class="lx-section__title" id="lx-more-title">Temario del centro y otros módulos</h2>
      <ul>
        <li><a href="#/daw/programacion">Programación por unidades de trabajo (UT1-UT9)</a>: teoría y preguntas de cada UT, con su propio progreso (compartido con la app).</li>
        <li><a href="#/daw/cursos">Otros módulos de DAW</a>: Bases de datos, Entornos de desarrollo, JavaScript y Java.</li>
      </ul>
    </section>`;
}
