/* Panel del alumno (ADR-0035): #/panel y #/panel/<sección>.

   Un único espacio para la persona con sesión iniciada: resumen, cursos, progreso, actividad,
   planificación, logros y perfil. No es una segunda app: reutiliza los datos y las piezas que ya
   existen (progreso por conceptos, PCAP, cursos de DAW, XP y logros, «Mi cuenta») y añade lo que
   solo está en el servidor con /api/v1/dashboard (una petición) y su historial paginado.
   Nunca inventa datos: lo que no se puede calcular se dice («aún no hay…») en vez de estimarlo. */

import { exportMyData, logout } from "./account.js";
import { request } from "./api.js";
import {
  dailySeries,
  examSummary,
  latestActivity,
  lastPractice,
  parseServerDate,
  PANEL_ROUTE,
  recurringErrors,
  safePercent,
  SECTIONS,
  sectionFromRoute,
} from "./dashboard-data.js";
import { BADGES, game, levelInfo, streak } from "./game.js";
import { dailyBudget } from "./learn/learn-app.js";
import { learning, loadLearningContent } from "./learn/learn-store.js";
import { activeErrors, allStats, lastActivity } from "./learn/mastery.js";
import { fitPlanToBudget, todayPlan } from "./learn/recommend.js";
import { escapeHtml, renderInline } from "./learn/ui.js";
import { currentPrefs } from "./prefs.js";
import {
  achievementsHtml,
  COURSES,
  examHistoryHtml,
  fillActivity,
  fillCourse,
  initials,
  planHtml,
  securityHtml,
  signedOut,
  stateOf,
} from "./private.js";
import { activityHtml } from "./profile.js";
import { state, subscribe } from "./store.js";

const FEED_PAGE = 10;
const CHART_DAYS = 30;
const TODAY = new Intl.DateTimeFormat("es-ES", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
const WHEN = new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
const SHORT_DAY = new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "short" });
const MEMBER_SINCE = new Intl.DateTimeFormat("es-ES", { month: "long", year: "numeric" });
const METHOD = { google: "Google", password: "Email y contraseña" };
const THEME = { auto: "automático", light: "claro", dark: "oscuro" };
const FONT = { normal: "normal", grande: "grande", "muy-grande": "muy grande" };
const $ = (selector) => document.querySelector(selector);

/* ---------- Datos: servidor y contenido ---------- */

const remote = {
  data: null, // respuesta de /api/v1/dashboard
  feed: [], // historial de aprendizaje ya cargado
  total: 0,
  error: null,
  feedError: null,
  loading: false,
  feedLoading: false,
  version: 0, // sube con cada cambio de progreso: los datos quedan anticuados
  loaded: -1, // versión de los datos que hay
};
let index = null; // contenido del núcleo por conceptos (learning.json)
let indexFailed = false;
let refreshView = () => {};

function reset() {
  Object.assign(remote, { data: null, feed: [], total: 0, error: null, feedError: null, loaded: -1 });
  remote.version += 1;
}

const utcOffset = () => -new Date().getTimezoneOffset();

async function load() {
  if (remote.loading) return;
  remote.loading = true;
  const version = remote.version;
  try {
    const [data, page] = await Promise.all([
      request("GET", `/api/v1/dashboard?utc_offset_minutes=${utcOffset()}`),
      request("GET", `/api/v1/dashboard/activity?limit=${FEED_PAGE}&offset=0`),
    ]);
    if (!state.user) return; // se cerró la sesión mientras llegaba
    Object.assign(remote, { data, feed: page.items, total: page.total, error: null, feedError: null });
  } catch (error) {
    remote.error = error.message;
  } finally {
    remote.loading = false;
    remote.loaded = version;
    paint();
  }
}

async function loadMore() {
  if (remote.feedLoading) return;
  remote.feedLoading = true;
  paint();
  try {
    const page = await request("GET", `/api/v1/dashboard/activity?limit=${FEED_PAGE}&offset=${remote.feed.length}`);
    remote.feed.push(...page.items);
    remote.total = page.total;
    remote.feedError = null;
  } catch (error) {
    remote.feedError = error.message;
  } finally {
    remote.feedLoading = false;
    paint();
    $("#dash-feed li:last-child a")?.focus(); // el foco sigue en la lista, no vuelve al principio
  }
}

/** Pide lo que falte. Se llama al pintar: solo hace algo si los datos están anticuados. */
function ensureData() {
  if (!index && !indexFailed) {
    loadLearningContent()
      .then((content) => {
        index = content;
      })
      .catch(() => {
        indexFailed = true;
      })
      .finally(paint);
  }
  if (remote.loaded !== remote.version && !remote.loading) load();
}

/** Repinta solo el contenido de la sección (no la cabecera ni el menú, donde puede estar el foco). */
function paint() {
  const body = $("#dash-body");
  if (!body || !state.user || !location.hash.startsWith(PANEL_ROUTE)) return;
  const section = sectionFromRoute(location.hash);
  body.innerHTML = bodyHtml(section);
  afterPaint(section);
}

/* ---------- Piezas comunes ---------- */

const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;

function ago(date, now = new Date()) {
  const days = Math.round((new Date(now.toDateString()) - new Date(date.toDateString())) / 86_400_000);
  if (days <= 0) return "hoy";
  if (days === 1) return "ayer";
  return `hace ${days} días`;
}

function meter(value, label) {
  const pct = Math.max(0, Math.min(100, value));
  return `<div class="meter" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}">
    <span class="meter__fill" style="--value: ${pct}%"></span></div>`;
}

function kpi(label, value, hint = "") {
  return `<div class="kpi"><dt>${label}</dt><dd><span class="kpi__value">${value}</span>${hint ? `<span class="visually-hidden">. </span><span class="kpi__hint">${hint}</span>` : ""}</dd></div>`;
}

const pending = () => `<span class="dash-pending">…<span class="visually-hidden">cargando</span></span>`;

const conceptTitle = (id) => index?.concepts.get(id)?.title ?? id;

function stats() {
  return index ? allStats(index, learning) : null;
}

/** Cursos del catálogo con su estado y si se han empezado. */
function courseList(srv) {
  const conceptStats = stats();
  const learnStarted = learning.log.length > 0 || Object.values(learning.concepts).some((c) => c.read || c.placed);
  const pcapLessons = srv?.lessons;
  const list = [
    {
      id: "learn",
      title: "Python desde cero",
      subtitle: "Núcleo por conceptos · preparación de Programación de DAW",
      started: learnStarted,
      continueHref: "#/aprender",
      contentsHref: "#/teoria",
      contentsLabel: "Teoría por conceptos",
      last: learning.log.at(-1)?.at ?? null,
      conceptStats,
    },
    {
      id: "pcap-curso",
      title: "Curso PCAP",
      subtitle: "Lecciones con consola, ejercicio corregido, quiz y reto",
      started: Boolean(pcapLessons?.completed || srv?.exercises.attempts),
      continueHref: pcapLessons?.next_lesson ? `#/leccion/${encodeURIComponent(pcapLessons.next_lesson.slug)}` : "#/inicio",
      contentsHref: "#/inicio",
      contentsLabel: "Temario del curso",
      last: [pcapLessons?.last_completed_at, srv?.exercises.last_attempt_at].map(parseServerDate).filter(Boolean).sort((a, b) => b - a)[0] ?? null,
      lessons: pcapLessons,
    },
    ...COURSES.map((c) => {
      const s = stateOf(c.id);
      return {
        id: c.id,
        title: c.id === "pcap" ? "Examen PCAP" : c.title,
        subtitle: c.subtitle,
        started: Object.keys(s.answers).length > 0 || s.exams.length > 0,
        continueHref: c.home,
        contentsHref: c.home,
        contentsLabel: c.id === "pcap" ? "Zona de examen" : "Temario del curso",
        last: lastPractice(s),
        bank: s,
      };
    }),
  ];
  return list.map((c) => ({ ...c, lastDate: c.last instanceof Date ? c.last : c.last ? new Date(c.last) : null }));
}

/* ---------- Cabecera y menú ---------- */

function headerHtml(user) {
  const now = new Date();
  return `
    <header class="profile-hero dash-hero">
      <div class="dash-hero__row">
        <div class="account-card">
          <span class="account-card__avatar" aria-hidden="true">${escapeHtml(initials(user.display_name) || "?")}</span>
          <div>
            <p class="eyebrow">Mi panel · <time datetime="${now.toISOString().slice(0, 10)}">${escapeHtml(TODAY.format(now))}</time></p>
            <h1 class="profile-hero__title" id="private-title" tabindex="-1">Hola, ${escapeHtml(user.display_name)}</h1>
            <p class="account-card__meta">Tu espacio de estudio: lo que llevas hecho y lo siguiente que te toca.</p>
          </div>
        </div>
        <div class="dash-hero__actions">
          <a class="btn btn--ghost" href="${PANEL_ROUTE}/perfil">Mi perfil y cuenta</a>
          <button class="btn btn--ghost" type="button" data-panel="logout">Cerrar sesión</button>
        </div>
      </div>
    </header>`;
}

function navHtml(section) {
  return `
    <nav class="dash-nav" aria-label="Secciones del panel">
      <ul>${SECTIONS.map(
        (s) => `<li><a href="${PANEL_ROUTE}/${s.id}"${s.id === section ? ' aria-current="page"' : ""}>${s.label}</a></li>`,
      ).join("")}</ul>
    </nav>`;
}

function statusHtml() {
  if (remote.error) {
    return `<div class="dash-alert" role="alert">
      <p><strong>No se ha podido cargar parte de tu panel.</strong> ${escapeHtml(remote.error)}</p>
      <p>Lo que depende de este navegador sigue visible. <button class="btn btn--ghost" type="button" data-panel="retry">Reintentar</button></p>
    </div>`;
  }
  if (!remote.data && remote.loading) {
    return `<p class="dash-status" role="status">Cargando tu panel… La primera vez el servidor puede tardar hasta un minuto en despertar.</p>`;
  }
  return "";
}

/* ---------- Resumen ---------- */

function summaryHtml() {
  const srv = remote.data;
  const courses = courseList(srv);
  const known = srv ? courses : courses.filter((c) => c.id !== "pcap-curso");
  const active = known.filter((c) => c.started).length;
  const s = stats();
  const mastered = s ? [...s.values()].filter((x) => x.status === "dominado").length : null;
  const lessons = srv?.lessons;
  const lessonPct = lessons ? safePercent(lessons.completed, lessons.total) : null;
  const practiced = Object.keys(learning.ex).length;
  const exams = examSummary({ learnExams: learning.exams, courseExams: COURSES.flatMap((c) => stateOf(c.id).exams) });
  const level = levelInfo();
  const days = streak();
  return `
    <section class="course-section" aria-labelledby="dash-kpis-title">
      <h2 class="section-title" id="dash-kpis-title">Resumen académico</h2>
      <dl class="kpis dash-kpis">
        ${kpi("Cursos activos", srv ? `${active}<small>/${courses.length}</small>` : pending(), "Con alguna actividad tuya")}
        ${kpi("Lecciones del curso PCAP", lessons ? `${lessons.completed}<small>/${lessons.total}</small>` : pending(), lessonPct === null ? "" : `${lessonPct} % del curso completado`)}
        ${kpi("Conceptos dominados", s ? `${mastered}<small>/${s.size}</small>` : indexFailed ? "—" : pending(), s ? `${safePercent(mastered, s.size)} % del núcleo de Python` : "")}
        ${kpi(
          "Ejercicios practicados",
          `${practiced}`,
          srv ? `del núcleo por conceptos · ${plural(srv.exercises.attempts, "intento", "intentos")} en el curso PCAP` : "del núcleo por conceptos",
        )}
        ${kpi("Simulacros", `${exams.count}`, exams.best === null ? "Aún no has hecho ninguno" : `Mejor nota: ${exams.best} %`)}
        ${kpi("Nivel", `${level.number}`, `${escapeHtml(level.name)} · ${level.xp} XP`)}
        ${kpi("Racha", `${days}<small> ${days === 1 ? "día" : "días"}</small>`, days ? "Días seguidos estudiando" : "Estudia hoy para empezar una racha")}
        ${kpi("Logros", `${game.badges.length}<small>/${BADGES.length}</small>`, `<a href="${PANEL_ROUTE}/logros">Ver mis logros</a>`)}
      </dl>
      <p class="account-card__meta">El tiempo de estudio no se muestra porque la web no lo mide de forma fiable.</p>
    </section>
    ${continueHtml(courses)}`;
}

function continueHtml(courses) {
  const srv = remote.data;
  // Primero lo más concreto (la lección o el concepto): con la misma fecha gana sobre el curso
  const candidates = [];
  const first = remote.feed[0];
  if (first) {
    const at = parseServerDate(first.at);
    const href = first.kind === "attempt" ? `#/leccion/${encodeURIComponent(first.lesson_slug)}` : courses[1].continueHref;
    const label = first.kind === "attempt" ? `Ejercicio de la lección «${first.lesson_title}»` : `Lección «${first.lesson_title}» completada`;
    candidates.push({ at, label, href });
  }
  const learnLast = index ? lastActivity(index, learning) : null;
  if (learnLast) {
    candidates.push({ at: new Date(learnLast.at), label: `Concepto «${conceptTitle(learnLast.concept)}»`, href: `#/teoria/${encodeURIComponent(learnLast.concept)}` });
  }
  candidates.push(...courses.filter((c) => c.lastDate).map((c) => ({ at: c.lastDate, label: c.title, href: c.continueHref })));
  const last = latestActivity(candidates);

  const plan = index ? todayPlan(index, learning) : [];
  const step = plan[0];
  const nextLesson = srv?.lessons.next_lesson;

  if (!last) {
    return `
      <section class="course-section dash-continue" aria-labelledby="dash-continue-title">
        <h2 class="section-title" id="dash-continue-title">Empieza a aprender</h2>
        <div class="dash-grid">
          <article class="dash-card dash-card--highlight">
            <h3 class="dash-card__title">¿Por dónde empiezo?</h3>
            <p>Todavía no hay actividad en tu cuenta. Empieza por «Aprender»: te propone un plan corto y, si ya sabes algo de Python, una prueba de nivel de unos 15 minutos.</p>
            <p class="dash-card__actions"><a class="btn btn--primary" href="#/aprender">Empezar a aprender</a> <a href="#/bienvenida">¿Cómo funciona?</a></p>
          </article>
          <article class="dash-card">
            <h3 class="dash-card__title">¿Preparas el examen PCAP?</h3>
            <p>El curso PCAP tiene lecciones con consola de Python, ejercicio corregido, quiz y reto.</p>
            <p class="dash-card__actions"><a class="btn btn--ghost" href="#/inicio">Ver el curso PCAP</a></p>
          </article>
        </div>
      </section>`;
  }

  const recommended = step
    ? `<h3 class="dash-card__title">Siguiente paso recomendado</h3>
       <p><strong>${escapeHtml(conceptTitle(step.concept))}</strong></p>
       <p class="account-card__meta">${escapeHtml(step.reason)}</p>
       <p class="dash-card__actions"><a class="btn btn--ghost" href="#/aprender">Ir al plan de hoy</a></p>`
    : nextLesson
      ? `<h3 class="dash-card__title">Siguiente paso recomendado</h3>
         <p>Siguiente lección del curso PCAP: <strong>${escapeHtml(nextLesson.title)}</strong></p>
         <p class="dash-card__actions"><a class="btn btn--ghost" href="#/leccion/${encodeURIComponent(nextLesson.slug)}">Abrir la lección</a></p>`
      : `<h3 class="dash-card__title">Siguiente paso recomendado</h3><p>${index ? "Has dominado el temario. Repasa o haz un simulacro en <a href=\"#/daw\">DAW</a>." : "Calculando…"}</p>`;
  return `
    <section class="course-section dash-continue" aria-labelledby="dash-continue-title">
      <h2 class="section-title" id="dash-continue-title">Continuar aprendiendo</h2>
      <div class="dash-grid">
        <article class="dash-card dash-card--highlight">
          <h3 class="dash-card__title">Donde lo dejaste</h3>
          <p><strong>${escapeHtml(last.label)}</strong></p>
          <p class="account-card__meta">Última actividad: ${ago(last.at)} (<time datetime="${last.at.toISOString()}">${escapeHtml(WHEN.format(last.at))}</time>)</p>
          <p class="dash-card__actions"><a class="btn btn--primary" href="${last.href}">Continuar aprendiendo</a></p>
        </article>
        <article class="dash-card">${recommended}</article>
      </div>
      ${nextLesson && step ? `<p class="account-card__meta">En el curso PCAP, tu siguiente lección es <a href="#/leccion/${encodeURIComponent(nextLesson.slug)}">${escapeHtml(nextLesson.title)}</a>.</p>` : ""}
    </section>`;
}

/* ---------- Mis cursos ---------- */

function courseCardHtml(c) {
  let progress = "";
  if (c.id === "learn") {
    const s = c.conceptStats;
    if (s) {
      const all = [...s.values()];
      const mastered = all.filter((x) => x.status === "dominado").length;
      const started = all.filter((x) => x.attempted > 0 && x.status !== "dominado").length;
      progress = `${meter(safePercent(mastered, all.length), `Conceptos dominados de ${c.title}`)}
        <p class="account-card__meta">${mastered} de ${all.length} conceptos dominados · ${started} en curso · ${all.length - mastered - started} sin empezar</p>`;
    } else {
      progress = `<p class="account-card__meta">${indexFailed ? "No se pudo cargar el temario de conceptos." : "Calculando tu progreso…"}</p>`;
    }
  } else if (c.id === "pcap-curso") {
    const l = c.lessons;
    progress = l
      ? `${meter(safePercent(l.completed, l.total), `Lecciones completadas de ${c.title}`)}
        <p class="account-card__meta">${l.completed} de ${l.total} lecciones completadas · ${l.total - l.completed} pendientes</p>`
      : `<p class="account-card__meta">${remote.error ? "No disponible ahora mismo." : "Cargando…"}</p>`;
  } else {
    const answered = Object.keys(c.bank.answers).length;
    progress = `<p class="account-card__meta">${plural(answered, "pregunta respondida", "preguntas respondidas")} · ${plural(c.bank.exams.length, "simulacro", "simulacros")}</p>
      <div data-course-detail><p class="account-card__meta">Calculando tu dominio…</p></div>`;
  }
  const last = c.lastDate
    ? `Última actividad: ${ago(c.lastDate)}`
    : c.started
      ? "Última actividad: sin fecha registrada"
      : "Aún no has empezado este curso";
  return `
    <li class="course-progress dash-course" data-course-card="${c.id}">
      <h3 class="course-progress__title">${escapeHtml(c.title)} <span class="account-card__meta">${escapeHtml(c.subtitle)}</span></h3>
      ${progress}
      <p class="account-card__meta">${last}</p>
      <p class="dash-card__actions">
        <a class="btn ${c.started ? "btn--primary" : "btn--ghost"}" href="${c.continueHref}">${c.started ? "Continuar aprendiendo" : "Empezar"}<span class="visually-hidden">: ${escapeHtml(c.title)}</span></a>
        <a href="${c.contentsHref}">${c.contentsLabel}<span class="visually-hidden"> de ${escapeHtml(c.title)}</span></a>
      </p>
    </li>`;
}

function coursesHtml() {
  const courses = courseList(remote.data);
  const started = courses.filter((c) => c.started);
  const rest = courses.filter((c) => !c.started);
  return `
    <section class="course-section" aria-labelledby="dash-courses-title">
      <h2 class="section-title" id="dash-courses-title">Mis cursos</h2>
      ${started.length ? `<ul class="course-progress-list">${started.map(courseCardHtml).join("")}</ul>` : `<p class="empty-state">Aún no has empezado ningún curso. Te recomendamos empezar por <a href="#/aprender">Python desde cero</a>.</p>`}
    </section>
    ${
      rest.length
        ? `<section class="course-section" aria-labelledby="dash-more-title">
            <h2 class="section-title" id="dash-more-title">Otros cursos disponibles</h2>
            <ul class="course-progress-list">${rest.map(courseCardHtml).join("")}</ul>
          </section>`
        : ""
    }`;
}

/* ---------- Mi progreso ---------- */

function chartHtml(series) {
  const max = Math.max(...series.map((d) => d.total));
  const total = series.reduce((sum, d) => sum + d.total, 0);
  const activeDays = series.filter((d) => d.total > 0).length;
  const caption = `Actividad diaria en los últimos ${series.length} días: ${plural(total, "actividad", "actividades")} en ${plural(activeDays, "día", "días")}`;
  if (!total) return `<p class="empty-state">Aún no hay actividad en los últimos ${series.length} días. Cuando completes lecciones o ejercicios, aparecerá aquí tu evolución.</p>`;
  const width = 600;
  const height = 160;
  const gap = 2;
  const bar = width / series.length - gap;
  const bars = series
    .map((d, i) => {
      const h = d.total ? Math.max(4, (d.total / max) * (height - 24)) : 0;
      const x = i * (bar + gap);
      const label = `${SHORT_DAY.format(new Date(`${d.day}T12:00:00`))}: ${plural(d.total, "actividad", "actividades")}`;
      return `<g class="dash-chart__day"><title>${escapeHtml(label)}</title>
        <rect class="dash-chart__hit" x="${x}" y="0" width="${bar + gap}" height="${height}"></rect>
        ${h ? `<rect class="dash-chart__bar" x="${x}" y="${height - h}" width="${bar}" height="${h}" rx="2"></rect>` : ""}</g>`;
    })
    .join("");
  const first = SHORT_DAY.format(new Date(`${series[0].day}T12:00:00`));
  const rows = series
    .filter((d) => d.total)
    .reverse()
    .map((d) => `<tr><th scope="row">${escapeHtml(SHORT_DAY.format(new Date(`${d.day}T12:00:00`)))}</th><td>${d.lessons}</td><td>${d.attempts}</td><td>${d.concepts}</td><td>${d.total}</td></tr>`)
    .join("");
  return `
    <figure class="dash-chart">
      <svg viewBox="0 0 ${width} ${height + 2}" role="img" aria-label="${escapeHtml(caption)}" preserveAspectRatio="none">
        <line class="dash-chart__base" x1="0" x2="${width}" y1="${height + 1}" y2="${height + 1}"></line>
        ${bars}
      </svg>
      <figcaption class="dash-chart__axis"><span>${escapeHtml(first)}</span><span>Máximo: ${max} en un día</span><span>Hoy</span></figcaption>
    </figure>
    <p class="account-card__meta">${escapeHtml(caption)}.</p>
    <details class="dash-details">
      <summary>Ver los datos en una tabla</summary>
      <div class="table-wrap" tabindex="0" role="region" aria-label="Actividad diaria">
        <table class="history">
          <thead><tr><th scope="col">Día</th><th scope="col">Lecciones completadas</th><th scope="col">Intentos (curso PCAP)</th><th scope="col">Ejercicios por conceptos</th><th scope="col">Total</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </details>`;
}

function progressHtml() {
  const srv = remote.data;
  const series = dailySeries({ serverDaily: srv?.daily ?? [], learnLog: learning.log, days: CHART_DAYS });
  const s = stats();
  const all = s ? [...s.values()] : [];
  const mastered = all.filter((x) => x.status === "dominado");
  const weak = all
    .filter((x) => x.attempted > 0 && x.status !== "dominado")
    .sort((a, b) => a.score - b.score)
    .slice(0, 6);
  const active = index ? new Set(activeErrors(learning).map((e) => e.id)) : new Set();
  const errors = index ? recurringErrors(learning.errors).filter((e) => index.errors.has(e.id)) : [];
  const exercises = srv?.exercises;
  const learnExams = learning.exams
    .slice(-5)
    .reverse()
    .map((e) => `<li class="activity-list__row"><span>${escapeHtml(SHORT_DAY.format(new Date(e.date)))} · ${e.correct} de ${e.total}</span><strong>${safePercent(e.correct, e.total) ?? 0} %</strong></li>`)
    .join("");
  return `
    <section class="course-section" aria-labelledby="dash-evolution-title">
      <h2 class="section-title" id="dash-evolution-title">Evolución</h2>
      ${srv || remote.error ? chartHtml(series) : `<p class="dash-status">Cargando…</p>`}
    </section>
    <div class="course-columns">
      <section class="course-section" aria-labelledby="dash-mastered-title">
        <h2 class="section-title" id="dash-mastered-title">Temas dominados</h2>
        ${
          !s
            ? `<p class="account-card__meta">${indexFailed ? "No se pudo cargar el temario de conceptos." : "Calculando…"}</p>`
            : mastered.length
              ? `<ul class="dash-tags">${mastered.map((x) => `<li><a href="#/teoria/${encodeURIComponent(x.id)}">${escapeHtml(conceptTitle(x.id))}</a></li>`).join("")}</ul>`
              : `<p class="empty-state">Aún no dominas ningún concepto. Un concepto se domina al acertar la mayoría de sus ejercicios, incluido alguno de aplicación.</p>`
        }
      </section>
      <section class="course-section" aria-labelledby="dash-weak-title">
        <h2 class="section-title" id="dash-weak-title">Necesitan refuerzo</h2>
        ${
          !s
            ? `<p class="account-card__meta">Calculando…</p>`
            : weak.length
              ? `<ul class="module-progress-list">${weak
                  .map(
                    (x) => `<li class="module-progress"><a class="module-progress__name" href="#/teoria/${encodeURIComponent(x.id)}">${escapeHtml(conceptTitle(x.id))}</a>
                      <span class="module-progress__count">${Math.round(x.score * 100)} %</span>${meter(Math.round(x.score * 100), `Dominio de ${conceptTitle(x.id)}`)}</li>`,
                  )
                  .join("")}</ul>`
              : `<p class="empty-state">Nada pendiente de reforzar entre los conceptos que has empezado.</p>`
        }
      </section>
    </div>
    <section class="course-section" aria-labelledby="dash-errors-title">
      <h2 class="section-title" id="dash-errors-title">Errores recurrentes</h2>
      ${
        errors.length
          ? `<ul class="activity-list">${errors
              .map((e) => {
                const info = index.errors.get(e.id);
                return `<li><strong>${renderInline(info.label)}</strong><span class="account-card__meta">${escapeHtml(conceptTitle(info.concept))} · ${e.n} veces · ${active.has(e.id) ? "pendiente de corregir" : "corregido"}</span></li>`;
              })
              .join("")}</ul>
             <p><a href="#/practicar">Practicar mis errores</a></p>`
          : `<p class="empty-state">Todavía no hay datos suficientes: aquí aparecen los errores que cometas dos veces o más.</p>`
      }
    </section>
    <section class="course-section" aria-labelledby="dash-results-title">
      <h2 class="section-title" id="dash-results-title">Resultados de tests y ejercicios</h2>
      <p>${
        exercises
          ? exercises.attempts
            ? `Curso PCAP: ${plural(exercises.passed, "intento superado", "intentos superados")} de ${exercises.attempts} (${safePercent(exercises.passed, exercises.attempts)} %), en ${plural(exercises.lessons_passed, "lección", "lecciones")}.`
            : "Curso PCAP: aún no has comprobado ningún ejercicio."
          : remote.error
            ? "Los resultados del curso PCAP no están disponibles ahora mismo."
            : "Cargando los resultados del curso PCAP…"
      }</p>
      <h3 class="section-subtitle">Simulacros de DAW (núcleo por conceptos)</h3>
      ${learnExams ? `<ul class="activity-list">${learnExams}</ul>` : `<p class="empty-state">Aún no has hecho ningún simulacro de DAW. <a href="#/daw">Hacer uno</a></p>`}
      <h3 class="section-subtitle">Simulacros del PCAP y de los cursos</h3>
      ${examHistoryHtml()}
      <p class="account-card__meta">Más detalle: <a href="#/progreso">dominio por concepto</a> · <a href="#/perfil">historial por lección del curso PCAP</a>.</p>
    </section>`;
}

/* ---------- Actividad ---------- */

function feedItemHtml(item) {
  const at = parseServerDate(item.at);
  const href = `#/leccion/${encodeURIComponent(item.lesson_slug)}`;
  const what =
    item.kind === "lesson_completed"
      ? "Lección completada"
      : item.passed
        ? "Ejercicio superado"
        : "Ejercicio sin superar";
  return `<li data-kind="${item.kind === "attempt" && !item.passed ? "attempt_failed" : escapeHtml(item.kind)}">
    <span><strong>${what}</strong>: <a href="${href}">${escapeHtml(item.lesson_title)}</a></span>
    <span class="account-card__meta">${at ? `<time datetime="${at.toISOString()}">${escapeHtml(WHEN.format(at))}</time>` : ""}</span></li>`;
}

function activitySectionHtml() {
  const feed = remote.feed.length
    ? `<ul class="activity-list" id="dash-feed">${remote.feed.map(feedItemHtml).join("")}</ul>
       <p class="account-card__meta">Mostrando ${remote.feed.length} de ${remote.total}.</p>
       ${remote.feedError ? `<p class="form-message" role="alert">No se pudieron cargar más: ${escapeHtml(remote.feedError)}</p>` : ""}
       ${remote.feed.length < remote.total ? `<button class="btn btn--ghost" type="button" data-panel="more"${remote.feedLoading ? " disabled" : ""}>${remote.feedLoading ? "Cargando…" : "Cargar más"}</button>` : ""}`
    : remote.data
      ? `<p class="empty-state">Aún no has completado lecciones ni comprobado ejercicios del curso PCAP con tu cuenta.</p>`
      : `<p class="account-card__meta">${remote.error ? "No disponible ahora mismo." : "Cargando…"}</p>`;
  const recent = index
    ? learning.log
        .slice(-8)
        .reverse()
        .map((entry) => {
          const ex = index.exercises.get(entry.ex);
          if (!ex) return "";
          const at = new Date(entry.at);
          return `<li data-kind="${entry.ok ? "ok" : "attempt_failed"}"><span><strong>${entry.ok ? "Correcto" : "Incorrecto"}</strong>: <a href="#/teoria/${encodeURIComponent(ex.concept)}">${escapeHtml(conceptTitle(ex.concept))}</a></span>
            <span class="account-card__meta"><time datetime="${at.toISOString()}">${escapeHtml(WHEN.format(at))}</time></span></li>`;
        })
        .join("")
    : "";
  return `
    <section class="course-section" aria-labelledby="dash-days-title">
      <h2 class="section-title" id="dash-days-title">Días con actividad</h2>
      ${activityHtml()}
    </section>
    <div class="course-columns">
      <section class="course-section" aria-labelledby="dash-feed-title">
        <h2 class="section-title" id="dash-feed-title">Historial del curso PCAP</h2>
        ${feed}
      </section>
      <section class="course-section" aria-labelledby="dash-learnlog-title">
        <h2 class="section-title" id="dash-learnlog-title">Últimos ejercicios por conceptos</h2>
        ${recent ? `<ul class="activity-list">${recent}</ul>` : `<p class="empty-state">${index || indexFailed ? "Aún no has hecho ejercicios del núcleo por conceptos." : "Cargando…"} <a href="#/aprender">Empezar</a></p>`}
      </section>
    </div>`;
}

/* ---------- Planificación ---------- */

function planningHtml() {
  let today = `<p class="account-card__meta">${indexFailed ? "No se pudo cargar el plan de hoy." : "Calculando tu plan de hoy…"}</p>`;
  if (index) {
    const s = allStats(index, learning);
    const budget = fitPlanToBudget(todayPlan(index, learning, new Date(), s), dailyBudget());
    const due = [...s.values()].filter((x) => x.due).length;
    today = budget.items.length
      ? `<ol class="activity-list dash-plan">${budget.items
          .map((item) => `<li><strong>${escapeHtml(conceptTitle(item.concept))}</strong><span class="account-card__meta">${escapeHtml(item.reason)} · unos ${item.minutes} min</span></li>`)
          .join("")}</ol>
         <p class="account-card__meta">Plan para ${budget.availableMinutes} minutos (lo cambias en Aprender): ${budget.plannedMinutes} min previstos${budget.deferredCount ? ` y ${plural(budget.deferredCount, "tarea", "tareas")} para otro día` : ""}. ${due ? `${plural(due, "concepto con repaso pendiente", "conceptos con repaso pendiente")}.` : "Sin repasos de conceptos pendientes."}</p>`
      : `<p class="empty-state">No hay nada pendiente para hoy. Haz un simulacro o repasa lo que quieras en <a href="#/practicar">Practicar</a>.</p>`;
  }
  return `
    <section class="course-section" aria-labelledby="dash-today-title">
      <h2 class="section-title" id="dash-today-title">Objetivo de hoy</h2>
      ${today}
      <p><a class="btn btn--primary" href="#/aprender">Abrir el plan de hoy</a></p>
    </section>
    ${planHtml()}`;
}

/* ---------- Logros ---------- */

function achievementsSectionHtml(content) {
  const level = levelInfo();
  const days = streak();
  const total = content.order.length;
  return `
    <section class="course-section" aria-labelledby="dash-motivation-title">
      <h2 class="section-title" id="dash-motivation-title">Tu motivación</h2>
      <dl class="kpis">
        ${kpi("Puntos XP", `${level.xp}`, level.next ? `${level.next.xp - level.xp} XP para «${escapeHtml(level.next.name)}»` : "Nivel máximo")}
        ${kpi("Nivel", `${level.number}`, escapeHtml(level.name))}
        ${kpi("Racha", `${days}<small> ${days === 1 ? "día" : "días"}</small>`)}
        ${kpi("Retos superados", `${game.challenges.length}<small>/${total}</small>`, "Retos extra del curso PCAP")}
      </dl>
      <p class="account-card__meta">El XP, la racha y los logros se guardan en tu cuenta y se ven igual en todos tus navegadores.</p>
    </section>
    ${achievementsHtml(content)}`;
}

/* ---------- Mi perfil ---------- */

function profileHtml(user) {
  const method = remote.data?.user.sign_in_method;
  const prefs = currentPrefs();
  return `
    <section class="course-section" aria-labelledby="dash-account-title">
      <h2 class="section-title" id="dash-account-title">Datos de la cuenta</h2>
      <dl class="dash-facts">
        <div><dt>Nombre</dt><dd>${escapeHtml(user.display_name)}</dd></div>
        <div><dt>Correo</dt><dd>${escapeHtml(user.email)}</dd></div>
        <div><dt>Último acceso con</dt><dd>${method ? METHOD[method] : remote.data ? "Sin registrar todavía" : "…"}</dd></div>
        <div><dt>Miembro desde</dt><dd>${escapeHtml(MEMBER_SINCE.format(parseServerDate(user.created_at) ?? new Date()))}</dd></div>
      </dl>
    </section>
    <section class="course-section" aria-labelledby="dash-prefs-title">
      <h2 class="section-title" id="dash-prefs-title">Preferencias y accesibilidad</h2>
      <p>Tema ${THEME[prefs.theme] ?? "automático"} · letra ${FONT[prefs.font] ?? "normal"}. Se guardan en este navegador.</p>
      <p><button class="btn btn--ghost" type="button" data-panel="appearance">Cambiar tema y tamaño de letra</button></p>
    </section>
    ${securityHtml(user, { google: method === "google" })}
    <section class="course-section" aria-labelledby="dash-data-title">
      <h2 class="section-title" id="dash-data-title">Privacidad y gestión de datos</h2>
      <p>Descarga una copia de todos tus datos (RGPD) o gestiona la sesión y el borrado de la cuenta, que pide confirmación con la contraseña.</p>
      ${method === "google" ? `<p class="account-card__meta">Si siempre entras con Google y quieres borrar la cuenta, primero elige una contraseña con «¿Has olvidado tu contraseña?» en el inicio de sesión.</p>` : ""}
      <p class="dash-card__actions">
        <button class="btn btn--ghost" type="button" data-panel="export">Descargar mis datos (JSON)</button>
        <a href="privacidad.html">Política de privacidad</a>
      </p>
      <p class="form-message" id="dash-export-message" role="status"></p>
    </section>`;
}

/* ---------- Página ---------- */

function bodyHtml(section, content = lastContent) {
  const user = state.user;
  const html = {
    resumen: summaryHtml,
    cursos: coursesHtml,
    progreso: progressHtml,
    actividad: activitySectionHtml,
    planificacion: planningHtml,
    logros: () => achievementsSectionHtml(content),
    perfil: () => profileHtml(user),
  }[section]();
  return `${statusHtml()}${html}`;
}

/** Lo que llega después (dominio de los cursos y actividad de la cuenta) se rellena al pintar. */
function afterPaint(section) {
  if (section === "cursos" || section === "logros") for (const c of COURSES) fillCourse(c).catch(() => {});
  if (section === "perfil") fillActivity();
}

let lastContent = null;

/**
 * Página completa del panel. Sin sesión, solo la invitación a entrar: nunca datos privados.
 * @param {object} content { order, lessons, modules } del curso PCAP  @param {boolean} apiEnabled
 */
export function renderDashboard(content, apiEnabled) {
  lastContent = content;
  const user = state.user;
  if (!user) return signedOut(apiEnabled);
  const section = sectionFromRoute(location.hash);
  ensureData();
  setTimeout(() => afterPaint(section));
  return `
    ${headerHtml(user)}
    ${navHtml(section)}
    <div class="dash-body" id="dash-body">${bodyHtml(section, content)}</div>`;
}

/** Título de la pestaña del navegador según la sección. */
export function dashboardTitle() {
  const section = SECTIONS.find((s) => s.id === sectionFromRoute(location.hash));
  return `${section.label} · Mi panel · Python Learning Dashboard`;
}

/**
 * Acciones del panel. Se enganchan una vez al contenedor, que se repinta entero.
 * @param {{ refresh: () => void, toast: (message: string) => void }} options
 */
export function initDashboard({ refresh, toast }) {
  refreshView = refresh;
  subscribe((change) => {
    if (change.type === "user" && !state.user) reset(); // al salir no queda nada de la cuenta
    else if (change.type === "progress" || change.type === "user") remote.version += 1; // anticuados
  });
  // El aspecto se cambia en su diálogo: al cerrarlo, «Mi perfil» muestra los valores nuevos
  $("#appearance-dialog").addEventListener("close", paint);
  $("#private-view").addEventListener("click", async (event) => {
    const target = event.target.closest("[data-panel]");
    if (!target) return;
    switch (target.dataset.panel) {
      case "logout":
        target.disabled = true;
        await logout();
        break;
      case "retry":
        remote.error = null;
        remote.version += 1;
        refreshView();
        break;
      case "more":
        loadMore();
        break;
      case "appearance":
        $("#appearance-button").click();
        break;
      case "export": {
        const message = $("#dash-export-message");
        try {
          await exportMyData();
          toast("Descarga de tus datos preparada.");
          if (message) message.textContent = "";
        } catch (error) {
          if (message) message.textContent = error.message;
        }
        break;
      }
      default:
        break;
    }
  });
}
