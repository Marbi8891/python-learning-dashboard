/* Centro de aprendizaje (#/cursos): una tarjeta por curso con su progreso y sus lecciones.
   Lee el progreso de los almacenes de siempre (también el de Alex en la demo); no guarda nada. */

import { escapeHtml } from "../markdown.js";
import { state } from "../store.js";
import { courseState } from "../course-store.js";
import { cyber } from "../cybersecurity-store.js";
import { isWeekDone } from "../cybersecurity-data.js";
import { learning, loadLearningContent } from "../learn/learn-store.js";
import { allStats } from "../learn/mastery.js";
import { HUB_COURSES, courseCard, lessonsOf } from "./hub-data.js";

const $ = (selector) => document.querySelector(selector);

const URLS = {
  pcap: "data/lessons.json",
  daw: (id) => `data/courses/${id}/lessons.json`,
  cyber: "data/cybersecurity/course.json",
};

let loading = null;

function fetchJson(url) {
  return fetch(url).then((r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });
}

/** Datos de cada curso. Un curso que no carga se queda sin datos («En desarrollo» o «no disponible»), sin romper los demás. */
function loadAll() {
  loading ??= Promise.all(
    HUB_COURSES.map((course) => {
      const request =
        course.source === "concepts"
          ? loadLearningContent()
          : fetchJson(course.source === "daw" ? URLS.daw(course.id) : URLS[course.source]);
      return request.then(
        (data) => ({ id: course.id, data, failed: false }),
        () => ({ id: course.id, data: null, failed: true }),
      );
    }),
  ).then((list) => new Map(list.map((item) => [item.id, item])));
  return loading;
}

function cardsFrom(loaded) {
  return HUB_COURSES.map((course) => {
    const { data, failed } = loaded.get(course.id);
    if (course.source === "concepts") {
      const stats = data ? allStats(data, learning) : new Map();
      return { ...courseCard(course, lessonsOf(course, data?.data), (id) => stats.get(id)?.status === "dominado"), failed };
    }
    const isDone = {
      pcap: (slug) => state.completed.has(slug),
      daw: (slug) => Boolean(courseState(course.id).done?.[slug]),
      cyber: (slug) => isWeekDone(cyber, slug),
    }[course.source];
    return { ...courseCard(course, lessonsOf(course, data), isDone), failed };
  });
}

function cardHtml(card) {
  const titleId = `hub-${card.id}-title`;
  if (!card.available) {
    return `
      <article class="hub-card" aria-labelledby="${titleId}">
        <h2 class="hub-card__title" id="${titleId}">${escapeHtml(card.title)}</h2>
        <p class="hub-card__subtitle">${escapeHtml(card.subtitle)}</p>
        <p class="hub-card__status">${card.failed ? "No se ha podido cargar. Comprueba la conexión y recarga la página." : "En desarrollo: todavía no tiene lecciones."}</p>
      </article>`;
  }
  const [one, many] = card.unit;
  return `
    <article class="hub-card" aria-labelledby="${titleId}">
      <h2 class="hub-card__title" id="${titleId}"><a href="${card.href}">${escapeHtml(card.title)}</a></h2>
      <p class="hub-card__subtitle">${escapeHtml(card.subtitle)}</p>
      <div class="hub-card__progress">
        <progress max="${card.total}" value="${card.done}" aria-labelledby="${titleId}-meter">${card.percent} %</progress>
        <p class="hub-card__meta" id="${titleId}-meter">${card.done} de ${card.total} ${card.total === 1 ? one : many} ${escapeHtml(card.doneLabel)} · ${card.percent} %</p>
      </div>
      <p class="hub-card__actions">
        <a class="btn btn--primary" href="${card.next ? card.next.href : card.href}">${card.done === 0 ? "Empezar" : card.next ? "Continuar" : "Repasar"}${card.next && card.done ? `<span class="visually-hidden">: ${escapeHtml(card.next.title)}</span>` : ""}</a>
        ${card.extra ? `<a class="btn btn--ghost" href="${card.extra.href}">${escapeHtml(card.extra.label)}</a>` : ""}
      </p>
      <details class="hub-card__lessons">
        <summary>Ver ${card.total} ${card.total === 1 ? one : many}</summary>
        <ol>${card.lessons
          .map((l) => `<li${l.done ? ' class="is-done"' : ""}><a href="${l.href}">${escapeHtml(l.title)}</a>${l.done ? `<span class="hub-card__done"> ✓<span class="visually-hidden"> (${escapeHtml(card.doneLabel.replace(/s$/, ""))})</span></span>` : ""}</li>`)
          .join("")}</ol>
      </details>
    </article>`;
}

/** Pinta el centro de aprendizaje en #hub-view. */
export async function openHub({ moveFocus = true } = {}) {
  const view = $("#hub-view");
  if (!view.querySelector(".hub-grid")) view.innerHTML = `<p class="dash-status" role="status">Cargando los cursos…</p>`;
  const loaded = await loadAll();
  if (!location.hash.startsWith("#/cursos")) return;
  const cards = cardsFrom(loaded);
  view.innerHTML = `
    <header class="lab__head">
      <p class="eyebrow">Centro de aprendizaje</p>
      <h1 class="profile-hero__title" id="hub-title" tabindex="-1">Cursos</h1>
      <p class="lab__lead">Todos los cursos en un sitio, con lo que llevas hecho en cada uno y sus lecciones. El progreso se guarda en este navegador${state.user ? " y en tu cuenta" : ""}.</p>
    </header>
    <div class="hub-grid">${cards.map(cardHtml).join("")}</div>
    <p class="account-card__meta">También hay <a href="#/daw">más módulos de DAW</a> (Entornos de desarrollo y Lenguajes de marcas), <a href="#/academia/excel">Excel profesional</a> y un <a href="#/laboratorio">laboratorio de Python</a> para practicar.</p>`;
  if (moveFocus) $("#hub-title").focus();
}
