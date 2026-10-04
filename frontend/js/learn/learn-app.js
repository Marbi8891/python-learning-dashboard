/* Núcleo educativo en la web (ADR-0031): Aprender (Hoy), Teoría, Practicar y Progreso.

   Rutas:
     #/aprender             ¿Qué estudio ahora?
     #/teoria               índice de conceptos por área
     #/teoria/<concepto>    explicación, ejemplo línea a línea, errores habituales y práctica
     #/practicar            repaso, mis errores, por tipo de actividad y por concepto
     #/progreso             dominio por concepto, errores y actividad
     #/sesion               sesión de estudio en curso (session-view.js) */

import { learning, loadLearningContent, onLearningChange, saveLearning } from "./learn-store.js";
import { activeErrors, allStats, areaSummary, daysBetween, lastActivity, markRead } from "./mastery.js";
import { missingPrerequisites, selectExercises, todayPlan } from "./recommend.js";
import { activityExercises, EXAM_ACTIVITIES, renderDawPrep } from "./daw-prep.js";
import { buildDiagnostic, buildExam, examMinutes } from "./exam.js";
import {
  initSessionEvents,
  renderSession,
  setSessionIndex,
  startErrorPractice,
  startPlanItem,
  startSession,
} from "./session-view.js";
import { codeBlock, errorExplanation, escapeHtml, KIND_LABEL, meter, percent, renderInline, renderMarkdown, STATUS, statusBadge } from "./ui.js";

const $ = (selector) => document.querySelector(selector);
const root = () => $("#learn-view");

let index = null;
let lessonTheory = new Map(); // slug -> lección de lessons.json (teoría reutilizada)

const title = (id) => index.concepts.get(id)?.title ?? id;
const ACTION = { review: "Repasar", errors: "Corregir errores", practice: "Practicar", learn: "Aprender", reinforce: "Reforzar" };

function ago(iso, now = new Date()) {
  const days = daysBetween(iso, now);
  if (days === 0) return "hoy";
  if (days === 1) return "ayer";
  return `hace ${days} días`;
}

const formatDay = (iso) => new Date(iso).toLocaleDateString("es-ES", { day: "numeric", month: "short" });

/* ---------- Aprender: ¿qué estudio ahora? ---------- */

function renderToday() {
  const now = new Date();
  const stats = allStats(index, learning, now);
  const plan = todayPlan(index, learning, now, stats);
  const all = [...stats.values()];
  const mastered = all.filter((s) => s.status === "dominado").length;
  const weak = all.filter((s) => s.attempted > 0 && s.status !== "dominado").sort((a, b) => a.score - b.score).slice(0, 3);
  const due = all.filter((s) => s.due);
  const last = lastActivity(index, learning);
  const date = now.toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long" });
  const items = plan
    .map(
      (item, i) => `
      <li class="lx-plan__item" data-type="${item.type}">
        <span class="lx-plan__n" aria-hidden="true">${i + 1}</span>
        <div class="lx-plan__body">
          <p class="lx-plan__action">${ACTION[item.type]}</p>
          <h3 class="lx-plan__title">${escapeHtml(title(item.concept))}</h3>
          <p class="lx-plan__reason">${escapeHtml(item.reason)}</p>
        </div>
        <div class="lx-plan__go">
          <button class="btn ${i === 0 ? "btn--primary" : "btn--ghost"}" type="button" data-learn="plan" data-type="${item.type}" data-concept="${escapeHtml(item.concept)}"${item.errors ? ` data-errors="${escapeHtml(item.errors.join(","))}"` : ""}>Empezar<span class="visually-hidden">: ${ACTION[item.type]} ${escapeHtml(title(item.concept))}</span></button>
          <a class="lx-plan__theory" href="#/teoria/${escapeHtml(item.concept)}">Teoría<span class="visually-hidden"> de ${escapeHtml(title(item.concept))}</span></a>
        </div>
      </li>`,
    )
    .join("");
  return `
    <header class="lx-head">
      <p class="eyebrow">Hoy · ${escapeHtml(date)}</p>
      <h1 class="lx-title" id="learn-title" tabindex="-1">¿Qué estudio ahora?</h1>
      <p class="lx-lead">Un plan corto según lo que ya dominas, lo que toca repasar y los errores que has cometido.</p>
    </header>
    <section class="lx-section" aria-labelledby="lx-plan-title">
      <h2 class="visually-hidden" id="lx-plan-title">Plan de hoy</h2>
      ${items ? `<ol class="lx-plan">${items}</ol>` : `<p>Has dominado todo el temario. Haz un <a href="#/daw">simulacro de DAW</a> o repasa en <a href="#/practicar">Practicar</a>.</p>`}
    </section>
    ${
      learning.log.length === 0
        ? `<section class="lx-panel lx-diagnostic" aria-labelledby="lx-diag-title">
            <h2 class="lx-panel__title" id="lx-diag-title">¿Ya sabes algo de Python?</h2>
            <p>Haz la prueba de nivel: una pregunta de cada concepto (unos 15 minutos). Lo que aciertes no te bloqueará y la ruta empezará donde lo necesitas.</p>
            <button class="btn btn--ghost" type="button" data-learn="diagnostic">Hacer la prueba de nivel</button>
          </section>`
        : ""
    }
    <details class="lx-details lx-route">
      <summary>Tu ruta personal (${mastered} de ${all.length} dominados)</summary>
      ${routeHtml(stats)}
    </details>
    <div class="lx-grid">
      <section class="lx-panel" aria-labelledby="lx-weak-title">
        <h2 class="lx-panel__title" id="lx-weak-title">Puntos débiles</h2>
        ${
          weak.length
            ? `<ul class="lx-list">${weak.map((s) => `<li class="lx-row"><a href="#/teoria/${s.id}">${escapeHtml(title(s.id))}</a>${meter(s.score, `Dominio de ${title(s.id)}`)}<span class="lx-row__value">${percent(s.score)}</span></li>`).join("")}</ul>`
            : '<p class="lx-muted">Aún no hay datos: aparecerán cuando practiques.</p>'
        }
      </section>
      <section class="lx-panel" aria-labelledby="lx-due-title">
        <h2 class="lx-panel__title" id="lx-due-title">Repasos pendientes</h2>
        ${
          due.length
            ? `<ul class="lx-list">${due.map((s) => `<li class="lx-row"><a href="#/teoria/${s.id}">${escapeHtml(title(s.id))}</a><span class="lx-row__value">desde ${formatDay(s.nextReview)}</span></li>`).join("")}</ul>
               <button class="btn btn--ghost" type="button" data-learn="review-all">Repasar todo (${due.length})</button>`
            : '<p class="lx-muted">Nada pendiente. Los conceptos vuelven cuando toca: a 1, 3, 7, 14 y 30 días.</p>'
        }
      </section>
      <section class="lx-panel" aria-labelledby="lx-progress-title">
        <h2 class="lx-panel__title" id="lx-progress-title">Progreso</h2>
        <p><strong>${mastered}</strong> de ${all.length} conceptos dominados</p>
        ${meter(mastered / all.length, "Conceptos dominados")}
        <p class="lx-muted">${last ? `Última actividad: ${ago(last.at)}, ${escapeHtml(title(last.concept))}.` : "Todavía no has empezado."}</p>
        <a href="#/progreso">Ver el progreso completo</a>
      </section>
    </div>`;
}

/** La ruta recomendada con el estado de cada concepto y qué lo bloquea. */
function routeHtml(stats) {
  const next = index.path.find((id) => stats.get(id).attempted === 0 && !stats.get(id).placed);
  const items = index.path
    .map((id) => {
      const s = stats.get(id);
      const missing = missingPrerequisites(index, stats, id);
      let note = STATUS[s.status].short;
      if (s.placed && s.status !== "dominado") note = "Superado en la prueba de nivel";
      if (id === next) note = missing.length ? `Siguiente · antes refuerza ${missing.map(title).join(" y ")}` : "Siguiente";
      return `<li class="lx-route__item" data-status="${id === next ? "next" : s.status}"><a href="#/teoria/${id}">${escapeHtml(title(id))}</a> <span class="lx-muted">· ${escapeHtml(note)}</span></li>`;
    })
    .join("");
  return `<ol class="lx-route__list">${items}</ol>`;
}

/* ---------- Teoría ---------- */

function renderTheoryIndex() {
  const stats = allStats(index, learning);
  const areas = areaSummary(index, stats)
    .map(
      (area) => `
      <section class="lx-section" aria-labelledby="area-${area.id}">
        <h2 class="lx-section__title" id="area-${area.id}">${escapeHtml(area.title)} <span class="lx-muted">· ${area.mastered}/${area.total} dominados</span></h2>
        <p class="lx-muted">${escapeHtml(area.summary)}</p>
        <ol class="lx-concepts">
          ${area.ids
            .map((id) => {
              const concept = index.concepts.get(id);
              return `<li class="lx-concept"><a class="lx-concept__link" href="#/teoria/${id}">${escapeHtml(concept.title)}</a>
                <span class="lx-concept__summary">${renderInline(concept.summary)}</span>
                <span class="lx-concept__status">${statusBadge(stats.get(id))}</span></li>`;
            })
            .join("")}
        </ol>
      </section>`,
    )
    .join("");
  return `
    <header class="lx-head">
      <p class="eyebrow">Teoría</p>
      <h1 class="lx-title" id="learn-title" tabindex="-1">Conceptos de programación</h1>
      <p class="lx-lead">Cada concepto tiene explicación, un ejemplo comentado línea a línea, cuándo usarlo, los errores habituales y ejercicios. Están en el orden recomendado.</p>
    </header>
    ${areas}`;
}

function theoryText(concept) {
  if (concept.theory) return renderMarkdown(concept.theory);
  return (concept.lessons ?? []).map((slug) => renderMarkdown(lessonTheory.get(slug)?.theory ?? "")).join("");
}

function renderConcept(id) {
  const concept = index.concepts.get(id);
  const stats = allStats(index, learning);
  const s = stats.get(id);
  const missing = missingPrerequisites(index, stats, id);
  const lines = concept.example.lines.map(([n, text]) => `<li><span class="lx-line-ref">Línea ${n}</span> ${renderInline(text)}</li>`).join("");
  const errors = concept.errors
    .map((error) => `<details class="lx-details"><summary>${renderInline(error.label)}</summary>${errorExplanation(error, { heading: "p" })}</details>`)
    .join("");
  const lessons = (concept.lessons ?? [])
    .filter((slug) => lessonTheory.has(slug))
    .map((slug) => `<li><a href="#/leccion/${slug}">Lección «${escapeHtml(lessonTheory.get(slug).title)}»</a>: consola de Python, ejercicio corregido, quiz y reto</li>`)
    .join("");
  const exercises = index.byConcept.get(id);
  const kinds = [...new Set(exercises.map((e) => KIND_LABEL[e.kind]))].join(", ");
  const position = index.path.indexOf(id);
  const prev = index.path[position - 1];
  const next = index.path[position + 1];
  return `
    <p class="daw-crumb"><a href="#/teoria">Teoría</a> › ${escapeHtml(index.areas.find((a) => a.id === concept.area).title)}</p>
    <header class="lx-head">
      <p class="eyebrow">Concepto ${position + 1} de ${index.path.length} · ${concept.daw === 3 ? "Imprescindible para DAW" : "Importante para DAW"}</p>
      <h1 class="lx-title" id="learn-title" tabindex="-1">${escapeHtml(concept.title)}</h1>
      <p class="lx-lead">${renderInline(concept.summary)}</p>
      <p class="lx-badges">${statusBadge(s)} ${s.attempted ? `<span class="lx-muted">${percent(s.score)} de dominio</span>` : ""}</p>
      ${
        concept.requires.length
          ? `<p class="lx-muted">Antes conviene dominar: ${concept.requires.map((r) => `<a href="#/teoria/${r}">${escapeHtml(title(r))}</a>`).join(", ")}.</p>`
          : ""
      }
      ${missing.length ? `<p class="lx-warning">Necesitas reforzar ${missing.map((r) => escapeHtml(title(r))).join(" y ")} antes de pasar a este concepto.</p>` : ""}
    </header>
    <section class="lx-section prose" aria-labelledby="lx-expl">
      <h2 class="lx-section__title" id="lx-expl">Explicación</h2>
      ${theoryText(concept)}
    </section>
    <section class="lx-section" aria-labelledby="lx-example">
      <h2 class="lx-section__title" id="lx-example">Ejemplo, línea a línea</h2>
      ${codeBlock(concept.example.code, { numbered: true, label: "Código de ejemplo" })}
      ${concept.example.stdin ? `<p class="lx-note">Con la entrada: <code>${escapeHtml(concept.example.stdin.trim().replace(/\n/g, " ⏎ "))}</code></p>` : ""}
      <ol class="lx-lines">${lines}</ol>
      ${concept.example.output ? `<p class="lx-note">Salida:</p><pre class="lx-output" tabindex="0">${escapeHtml(concept.example.output)}</pre>` : ""}
    </section>
    <section class="lx-section" aria-labelledby="lx-when">
      <h2 class="lx-section__title" id="lx-when">Cuándo usarlo</h2>
      <p>${renderInline(concept.when)}</p>
    </section>
    <section class="lx-section" aria-labelledby="lx-errors">
      <h2 class="lx-section__title" id="lx-errors">Errores habituales</h2>
      ${errors}
    </section>
    <section class="lx-section" aria-labelledby="lx-practice">
      <h2 class="lx-section__title" id="lx-practice">Comprueba que lo entiendes</h2>
      <p class="lx-muted">${exercises.length} ejercicios (${escapeHtml(kinds)}). La práctica elige primero lo que no dominas.</p>
      <div class="lx-actions">
        <button class="btn btn--primary" type="button" data-learn="short" data-concept="${id}">Ejercicio corto (3)</button>
        <button class="btn btn--ghost" type="button" data-learn="plan" data-type="practice" data-concept="${id}">Práctica completa</button>
        ${s.status === "nuevo" ? `<button class="btn btn--ghost" type="button" data-learn="read" data-concept="${id}">He leído la teoría</button>` : ""}
      </div>
      ${lessons ? `<h3 class="lx-h4">Para practicar con la consola</h3><ul>${lessons}</ul>` : ""}
      ${concept.ut ? `<p class="lx-muted">En el temario de Programación de DAW: <a href="#/daw/programacion">${escapeHtml(concept.ut.replace("prog-ut", "UT"))}</a>.</p>` : ""}
    </section>
    ${
      concept.related?.length
        ? `<section class="lx-section" aria-labelledby="lx-related"><h2 class="lx-section__title" id="lx-related">Relacionado</h2>
            <ul class="lx-inline-list">${concept.related.map((r) => `<li><a href="#/teoria/${r}">${escapeHtml(title(r))}</a></li>`).join("")}</ul></section>`
        : ""
    }
    <nav class="daw-pager" aria-label="Conceptos">
      ${prev ? `<a class="btn btn--ghost" href="#/teoria/${prev}">← ${escapeHtml(title(prev))}</a>` : "<span></span>"}
      ${next ? `<a class="btn btn--ghost" href="#/teoria/${next}">${escapeHtml(title(next))} →</a>` : "<span></span>"}
    </nav>`;
}

/* ---------- Practicar ---------- */

const ACTIVITIES = [
  { id: "lectura", label: "Lectura de código", text: "Di qué muestra un programa: trazas a mano.", kinds: ["output"] },
  { id: "errores", label: "Detectar errores", text: "Encuentra la línea que falla y por qué.", kinds: ["bug"] },
  { id: "completar", label: "Completar y ordenar código", text: "Huecos y líneas desordenadas.", kinds: ["fill", "order"] },
  { id: "escribir", label: "Escribir programas", text: "Desde cero, corregidos con tests.", kinds: ["code"] },
  { id: "preguntas", label: "Preguntas de concepto", text: "Comprensión y casos límite.", kinds: ["choice"] },
];

/** Conceptos en los que tiene sentido practicar: los empezados y el siguiente de la ruta. */
function practiceScope(stats) {
  const started = index.path.filter((id) => stats.get(id).attempted > 0 || stats.get(id).status === "leido");
  const firstNew = index.path.find((id) => !started.includes(id));
  return started.length ? started : [firstNew].filter(Boolean);
}

function renderPractice() {
  const now = new Date();
  const stats = allStats(index, learning, now);
  const due = [...stats.values()].filter((s) => s.due);
  const errors = activeErrors(learning, now);
  const scope = practiceScope(stats);
  const options = index.path.map((id) => `<option value="${id}">${escapeHtml(title(id))} · ${STATUS[stats.get(id).status].short}</option>`).join("");
  return `
    <header class="lx-head">
      <p class="eyebrow">Practicar</p>
      <h1 class="lx-title" id="learn-title" tabindex="-1">Practicar</h1>
      <p class="lx-lead">Cada fallo se explica y vuelve más tarde con un ejercicio parecido. La práctica evita repetir lo que ya dominas.</p>
    </header>
    <div class="lx-grid lx-grid--2">
      <section class="lx-panel" aria-labelledby="lx-review-title">
        <h2 class="lx-panel__title" id="lx-review-title">Repaso de hoy</h2>
        ${due.length ? `<p>${due.length} ${due.length === 1 ? "concepto pendiente" : "conceptos pendientes"}: ${due.map((s) => escapeHtml(title(s.id))).join(", ")}.</p><button class="btn btn--primary" type="button" data-learn="review-all">Empezar el repaso</button>` : '<p class="lx-muted">No hay repasos pendientes hoy.</p>'}
      </section>
      <section class="lx-panel" aria-labelledby="lx-concept-title">
        <h2 class="lx-panel__title" id="lx-concept-title">Por concepto</h2>
        <form class="lx-inline-form" id="lx-concept-form">
          <label class="visually-hidden" for="lx-concept-select">Concepto</label>
          <select id="lx-concept-select">${options}</select>
          <button class="btn btn--ghost" type="submit">Practicar</button>
        </form>
      </section>
    </div>
    <section class="lx-section" aria-labelledby="lx-errors-title">
      <h2 class="lx-section__title" id="lx-errors-title">Mis errores</h2>
      ${
        errors.length
          ? `<ul class="lx-list">${errors
              .map((e) => {
                const info = index.errors.get(e.id);
                if (!info) return "";
                return `<li class="lx-row lx-row--error"><span><strong>${renderInline(info.label)}</strong><br><span class="lx-muted">${escapeHtml(title(info.concept))} · ${e.n} ${e.n === 1 ? "vez" : "veces"} · ${ago(e.last)}</span></span>
                  <button class="btn btn--ghost" type="button" data-learn="error" data-id="${escapeHtml(e.id)}">Practicar este error</button></li>`;
              })
              .join("")}</ul>`
          : '<p class="lx-muted">No tienes errores pendientes. Un error deja de estar aquí cuando aciertas dos ejercicios que lo detectan.</p>'
      }
    </section>
    <section class="lx-section" aria-labelledby="lx-activity-title">
      <h2 class="lx-section__title" id="lx-activity-title">Por tipo de actividad</h2>
      <p class="lx-muted">Sobre los conceptos que ya has empezado: ${scope.map((id) => escapeHtml(title(id))).join(", ")}.</p>
      <ul class="lx-cards">
        ${ACTIVITIES.map((a) => {
          const available = selectExercises(index, learning, scope, 6, { kinds: a.kinds, now }).length;
          return `<li class="lx-card"><h3 class="lx-card__title">${a.label}</h3><p class="lx-muted">${a.text}</p>
            <button class="btn btn--ghost" type="button" data-learn="activity" data-activity="${a.id}"${available ? "" : " disabled"}>${available ? `Practicar (${available})` : "Aún no hay ejercicios"}</button></li>`;
        }).join("")}
      </ul>
    </section>`;
}

/* ---------- Progreso ---------- */

function renderProgress() {
  const now = new Date();
  const stats = allStats(index, learning, now);
  const all = [...stats.values()];
  const count = (status) => all.filter((s) => s.status === status).length;
  const errors = Object.entries(learning.errors)
    .filter(([id]) => index.errors.has(id))
    .sort((a, b) => b[1].n - a[1].n)
    .slice(0, 8);
  const active = new Set(activeErrors(learning, now).map((e) => e.id));
  const areas = areaSummary(index, stats)
    .map(
      (area) => `
      <section class="lx-section" aria-labelledby="pa-${area.id}">
        <h2 class="lx-section__title" id="pa-${area.id}">${escapeHtml(area.title)} <span class="lx-muted">· ${area.mastered}/${area.total}</span></h2>
        <div class="table-wrap" tabindex="0"><table class="lx-table">
          <thead><tr><th scope="col">Concepto</th><th scope="col">Estado</th><th scope="col">Dominio</th><th scope="col">Última vez</th><th scope="col">Próximo repaso</th></tr></thead>
          <tbody>${area.ids
            .map((id) => {
              const s = stats.get(id);
              return `<tr><th scope="row"><a href="#/teoria/${id}">${escapeHtml(title(id))}</a></th><td>${statusBadge(s)}</td>
                <td>${meter(s.score, `Dominio de ${title(id)}`)} <span class="lx-row__value">${percent(s.score)}</span></td>
                <td>${s.last ? ago(s.last, now) : "—"}</td><td>${s.nextReview ? formatDay(s.nextReview) : "—"}</td></tr>`;
            })
            .join("")}</tbody>
        </table></div>
      </section>`,
    )
    .join("");
  const log = learning.log
    .slice(-12)
    .reverse()
    .map((entry) => {
      const ex = index.exercises.get(entry.ex);
      if (!ex) return "";
      return `<li class="lx-row"><span>${entry.ok ? "✓" : "✗"}<span class="visually-hidden">${entry.ok ? " Correcto" : " Incorrecto"}</span> ${escapeHtml(KIND_LABEL[ex.kind])} · ${escapeHtml(title(ex.concept))}</span><span class="lx-row__value">${formatDay(entry.at)}</span></li>`;
    })
    .join("");
  const exams = learning.exams
    .slice()
    .reverse()
    .map((e) => `<li class="lx-row"><span>${formatDay(e.date)} · ${e.correct} de ${e.total}</span><span class="lx-row__value">${percent(e.total ? e.correct / e.total : 0)} · ${Math.round(e.seconds / 60)} min</span></li>`)
    .join("");
  return `
    <header class="lx-head">
      <p class="eyebrow">Progreso</p>
      <h1 class="lx-title" id="learn-title" tabindex="-1">Tu progreso</h1>
      <p class="lx-lead">Un concepto está dominado cuando aciertas la mayoría de sus ejercicios, incluido alguno de aplicación, y no tienes errores pendientes en él.</p>
      <ul class="lx-facts">
        <li><strong>${count("dominado")}</strong> dominados</li>
        <li><strong>${count("progreso") + count("aprendiendo")}</strong> en curso</li>
        <li><strong>${count("nuevo") + count("leido")}</strong> sin practicar</li>
        <li><strong>${active.size}</strong> errores pendientes</li>
      </ul>
    </header>
    ${areas}
    <div class="lx-grid lx-grid--2">
      <section class="lx-panel" aria-labelledby="lx-freq-title">
        <h2 class="lx-panel__title" id="lx-freq-title">Errores más frecuentes</h2>
        ${
          errors.length
            ? `<ul class="lx-list">${errors.map(([id, e]) => `<li class="lx-row"><span>${renderInline(index.errors.get(id).label)}</span><span class="lx-row__value">${e.n}× · ${active.has(id) ? "pendiente" : "corregido"}</span></li>`).join("")}</ul>`
            : '<p class="lx-muted">Sin errores registrados todavía.</p>'
        }
      </section>
      <section class="lx-panel" aria-labelledby="lx-log-title">
        <h2 class="lx-panel__title" id="lx-log-title">Actividad reciente</h2>
        ${log ? `<ul class="lx-list">${log}</ul>` : '<p class="lx-muted">Aún no has hecho ningún ejercicio.</p>'}
      </section>
    </div>
    ${exams ? `<section class="lx-section" aria-labelledby="lx-exams-title"><h2 class="lx-section__title" id="lx-exams-title">Simulacros</h2><ul class="lx-list">${exams}</ul></section>` : ""}
    <div class="lx-actions"><button class="btn btn--ghost" type="button" data-learn="diagnostic">Repetir la prueba de nivel</button></div>
    <p class="lx-muted">Los logros, el XP y la racha del curso PCAP siguen en <a href="#/perfil">Mi aprendizaje</a>.</p>`;
}

/* ---------- Acciones ---------- */

function startReviewAll() {
  const stats = allStats(index, learning);
  const due = [...stats.values()].filter((s) => s.due).map((s) => s.id);
  const exercises = due.flatMap((id) => selectExercises(index, learning, [id], 2)).map((e) => e.id);
  startSession({ kind: "review", title: "Repaso de hoy", exercises });
}

function onDawClick(target) {
  switch (target.dataset.dawPrep) {
    case "exam": {
      const all = target.dataset.scope === "all";
      const exercises = buildExam(index, learning, { scope: all ? "all" : "studied" });
      startSession({
        kind: "exam",
        title: all ? "Simulacro DAW · temario completo" : "Simulacro DAW · lo estudiado",
        exercises: exercises.map((e) => e.id),
        timeLimit: examMinutes(exercises) * 60,
        meta: { examKind: all ? "daw-completo" : "daw-estudiado" },
      });
      break;
    }
    case "activity": {
      const activity = EXAM_ACTIVITIES.find((a) => a.id === target.dataset.activity);
      startSession({
        kind: "practice",
        title: activity.label,
        exercises: activityExercises(index, learning, activity).map((e) => e.id),
        timeLimit: activity.minutes ? activity.minutes * 60 : null,
      });
      break;
    }
    case "reinforce": {
      const concepts = target.dataset.concepts.split(",");
      const exercises = selectExercises(index, learning, concepts, 5).map((e) => e.id);
      startSession({ kind: "practice", title: `Reforzar: ${concepts.map(title).join(" y ")}`, exercises });
      break;
    }
    default:
      break;
  }
}

function onClick(event) {
  const daw = event.target.closest("[data-daw-prep]");
  if (daw && index) {
    onDawClick(daw);
    return;
  }
  const target = event.target.closest("[data-learn]");
  if (!target || !index) return;
  const { concept } = target.dataset;
  switch (target.dataset.learn) {
    case "plan":
      startPlanItem(target.dataset.type, concept, { errors: target.dataset.errors?.split(",") ?? [] });
      break;
    case "short":
      markRead(learning, concept);
      saveLearning();
      startSession({ kind: "practice", title: `Ejercicio corto: ${title(concept)}`, exercises: selectExercises(index, learning, [concept], 3).map((e) => e.id), concept });
      break;
    case "read":
      markRead(learning, concept);
      saveLearning();
      break;
    case "review-all":
      startReviewAll();
      break;
    case "diagnostic":
      startSession({ kind: "diagnostic", title: "Prueba de nivel", exercises: buildDiagnostic(index).map((e) => e.id) });
      break;
    case "error":
      startErrorPractice(target.dataset.id);
      break;
    case "activity": {
      const activity = ACTIVITIES.find((a) => a.id === target.dataset.activity);
      const scope = practiceScope(allStats(index, learning));
      const exercises = selectExercises(index, learning, scope, 6, { kinds: activity.kinds }).map((e) => e.id);
      startSession({ kind: "practice", title: activity.label, exercises });
      break;
    }
    default:
      break;
  }
}

function onSubmit(event) {
  if (event.target.id !== "lx-concept-form") return;
  event.preventDefault();
  startPlanItem("practice", $("#lx-concept-select").value);
}

/* ---------- Pintado y rutas ---------- */

let listening = false;

async function ensureContent() {
  if (index) return;
  const [content, lessons] = await Promise.all([loadLearningContent(), fetch("data/lessons.json").then((r) => (r.ok ? r.json() : { modules: [] }))]);
  index = content;
  lessonTheory = new Map(lessons.modules.flatMap((m) => m.lessons.map((l) => [l.slug, l])));
  setSessionIndex(index);
}

/** Vista del núcleo educativo según la ruta. Devuelve la clave del menú que corresponde. */
export async function openLearn(route, { moveFocus = true } = {}) {
  if (!listening) {
    root().addEventListener("click", onClick);
    root().addEventListener("submit", onSubmit);
    initSessionEvents();
    onLearningChange(() => {
      // Al llegar progreso (p. ej. de la cuenta) se repinta. La sesión se pinta sola: nunca se repinta encima
      if (location.hash.startsWith("#/sesion")) return;
      if (isLearnRoute(location.hash)) render(location.hash);
    });
    listening = true;
  }
  try {
    await ensureContent();
  } catch {
    root().innerHTML = `<p class="empty-state" id="learn-title" tabindex="-1">No se pudo cargar el contenido. Comprueba la conexión y recarga.</p>`;
    return;
  }
  if (location.hash !== route) return; // el alumno se fue mientras cargaba
  render(route);
  if (moveFocus) $("#learn-title")?.focus();
}

function render(route) {
  const [, section, arg] = route.split("/").map(decodeURIComponent); // "#/teoria/bucles"
  if (section === "sesion") {
    renderSession();
    return;
  }
  let html;
  if (section === "teoria") html = arg && index.concepts.has(arg) ? renderConcept(arg) : renderTheoryIndex();
  else if (section === "practicar") html = renderPractice();
  else if (section === "progreso") html = renderProgress();
  else if (section === "daw") html = renderDawPrep(index, learning);
  else html = renderToday();
  root().innerHTML = html;
}

export const LEARN_ROUTES = ["#/aprender", "#/teoria", "#/practicar", "#/progreso", "#/sesion"];

/** ¿La ruta es del núcleo educativo? `#/daw` es la Preparación DAW; `#/daw/<curso>` sigue en daw.js. */
export const isLearnRoute = (hash) => hash === "#/daw" || LEARN_ROUTES.some((r) => hash === r || hash.startsWith(`${r}/`));

/** Clave del menú principal para una ruta del núcleo. */
export function learnNavKey(hash) {
  if (hash.startsWith("#/teoria")) return "teoria";
  if (hash.startsWith("#/practicar")) return "practicar";
  if (hash.startsWith("#/progreso")) return "progreso";
  if (hash.startsWith("#/daw")) return "daw";
  return "aprender";
}
