/* =========================================================
   app.js — carga el contenido y coordina los módulos
   ========================================================= */

import hljs from "../vendor/highlight/core.min.js";
import python from "../vendor/highlight/python.min.js";
import { initAccount, openPasswordReset } from "./account.js";
import { initAssistant, setAssistantLesson } from "./assistant.js";
import { celebrate } from "./celebrate.js";
import {
  checkCode,
  initConsole,
  loadExample,
  loadStarter,
  setLesson as setConsoleLesson,
  setRunListener,
} from "./console.js";
import {
  BADGES,
  game,
  initGame,
  levelInfo,
  recordChallenge,
  recordExercise,
  recordRun,
  streak,
  subscribe as onGame,
} from "./game.js";
import { escapeHtml, renderMarkdown } from "./markdown.js";
import { setQuizLesson } from "./quiz.js";
import { recordAttempt, restoreSession, setCompleted, state, subscribe } from "./store.js";

hljs.registerLanguage("python", python);

const DATA_URL = "data/lessons.json";
const ROUTE_PREFIX = "#/leccion/";
const RESET_ROUTE = "#/restablecer";
const mobile = window.matchMedia("(max-width: 900px)");

const content = {
  modules: [],
  lessons: new Map(), // slug -> { ...lesson, module, index }
  order: [], // slugs en el orden de la ruta
  current: null,
};

const $ = (selector) => document.querySelector(selector);
const currentLesson = () => content.lessons.get(content.current);
const lessonAt = (index) => content.lessons.get(content.order[index]);

/* ---------- Avisos ---------- */

// Cola de avisos: si llegan varios a la vez (XP + logro + nivel), se muestran uno tras otro
const toastQueue = [];
let toastBusy = false;
function showToast(message) {
  toastQueue.push(message);
  if (!toastBusy) nextToast();
}
function nextToast() {
  const toast = $("#toast");
  const message = toastQueue.shift();
  if (!message) {
    toastBusy = false;
    return;
  }
  toastBusy = true;
  toast.textContent = message;
  toast.classList.add("toast--visible");
  setTimeout(() => {
    toast.classList.remove("toast--visible");
    setTimeout(nextToast, 250);
  }, 2600);
}

/* ---------- Barra lateral ---------- */

function renderSidebar() {
  $("#modules").innerHTML = content.modules
    .map(
      (module) => `
      <details class="module" data-module="${module.slug}">
        <summary class="module__summary">
          <span class="module__name">${escapeHtml(module.title)}</span>
          <span class="module__count"></span>
        </summary>
        <ol class="lessons">
          ${module.lessons
            .map(
              (lesson) => `
            <li><a class="lesson" href="${ROUTE_PREFIX}${lesson.slug}" data-slug="${lesson.slug}">
              <span class="lesson__icon" aria-hidden="true"></span>
              <span class="lesson__name">${escapeHtml(lesson.title)}</span>
              <span class="lesson__badge" aria-hidden="true">En curso</span>
              <span class="lesson__state visually-hidden"></span>
            </a></li>`,
            )
            .join("")}
        </ol>
      </details>`,
    )
    .join("");
}

const STATE_TEXT = {
  completed: "(Completado)",
  locked: "(Recomendado: completa antes la lección anterior)",
  active: "",
  available: "",
};

// Actualiza estados sin regenerar el HTML (respeta los módulos que el usuario abrió).
function updateSidebar() {
  for (const link of document.querySelectorAll(".lesson[data-slug]")) {
    const lesson = content.lessons.get(link.dataset.slug);
    const previous = lessonAt(lesson.index - 1);
    let status = "available";
    if (lesson.slug === content.current) status = "active";
    else if (state.completed.has(lesson.slug)) status = "completed";
    // Bloqueo orientativo: se puede abrir igualmente, pero se recomienda seguir el orden
    else if (previous && !state.completed.has(previous.slug)) status = "locked";

    link.dataset.status = status;
    link.querySelector(".lesson__state").textContent = STATE_TEXT[status];
    if (status === "active") link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }

  for (const module of content.modules) {
    const details = document.querySelector(`.module[data-module="${module.slug}"]`);
    const done = module.lessons.filter((l) => state.completed.has(l.slug)).length;
    details.querySelector(".module__count").textContent = `${done}/${module.lessons.length}`;
    if (module.lessons.some((l) => l.slug === content.current)) details.open = true;
  }
  updateProgressRing();
}

function updateProgressRing() {
  const module = currentLesson()?.module;
  if (!module) return;
  const done = module.lessons.filter((l) => state.completed.has(l.slug)).length;
  const percent = Math.round((done / module.lessons.length) * 100);
  const ring = $("#progress");
  ring.style.setProperty("--progress", percent);
  ring.setAttribute("aria-valuenow", percent);
  ring.setAttribute("aria-label", `Progreso del módulo ${module.title}`);
  $("#progress-value").textContent = `${percent}%`;
  $("#progress-module").textContent = `${module.title} · ${done}/${module.lessons.length}`;
}

/* ---------- Contenido de la lección ---------- */

function renderSources(sources = []) {
  if (!sources.length) return "";
  const items = sources
    .map(
      (s) =>
        `<li><a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.title)}</a></li>`,
    )
    .join("");
  return `
    <section class="sources" aria-labelledby="sources-title">
      <h2 class="sources__title" id="sources-title">Fuentes y ampliación</h2>
      <ul>${items}</ul>
      <p class="sources__note">Explicación propia basada en estas fuentes. Consúltalas para profundizar.</p>
    </section>`;
}

function renderLesson(lesson) {
  const prev = lessonAt(lesson.index - 1);
  const next = lessonAt(lesson.index + 1);

  document.title = `${lesson.title} · Python Learning Dashboard`;
  $("#lesson-crumb").textContent = lesson.module.title;
  $("#lesson-title").textContent = lesson.title;

  $("#panel-theory").innerHTML = `
    <div class="prose">${renderMarkdown(lesson.theory)}</div>

    <figure class="code-block">
      <figcaption class="code-block__bar">
        <span class="code-block__file">${lesson.slug}.py</span>
        <span class="code-block__actions">
          <button class="btn btn--ghost" type="button" data-action="copy">Copiar al portapapeles</button>
          <button class="btn btn--ghost" type="button" data-action="to-console">Probar en la consola</button>
          <button class="btn btn--primary" type="button" data-action="pycharm">Abrir en PyCharm</button>
        </span>
      </figcaption>
      <pre tabindex="0" aria-label="Código de ejemplo"><code class="language-python">${escapeHtml(lesson.example_code)}</code></pre>
    </figure>

    <div class="hint" id="pycharm-hint" hidden>
      <p class="hint__title">Código copiado. Para abrirlo en PyCharm:</p>
      <ol>
        <li>Clic derecho en la carpeta de la lección → <strong>New → Python File</strong> → <code>${lesson.slug}</code>.</li>
        <li>Pega con <kbd>Ctrl</kbd>+<kbd>V</kbd>.</li>
        <li>Ejecuta con <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>F10</kbd>.</li>
      </ol>
      <p>¿Prefieres el archivo? <a href="#" data-action="download">Descargar ${lesson.slug}.py</a></p>
    </div>

    ${renderSources(lesson.sources)}`;

  $("#panel-practice").innerHTML = `
    <div class="prose exercise">${renderMarkdown(lesson.exercise)}</div>
    <p class="practice-note">Escribe tu solución en la <a href="#console-title">Consola Interactiva</a> y pulsa «Comprobar solución».</p>
    <div class="practice-actions">
      <button class="btn btn--ghost" type="button" data-action="load-starter">Cargar plantilla en la consola</button>
      <button class="btn btn--primary" type="button" id="check-button" data-action="check">Comprobar solución</button>
      <button class="btn" type="button" id="complete-button" data-action="toggle-complete"></button>
    </div>
    <div class="check" id="check-result" role="status" tabindex="-1" hidden></div>

    ${renderChallenge(lesson.challenge)}

    <nav class="lesson-nav" aria-label="Lecciones adyacentes">
      ${prev ? `<a class="btn btn--ghost" href="${ROUTE_PREFIX}${prev.slug}">← ${escapeHtml(prev.title)}</a>` : "<span></span>"}
      ${next ? `<a class="btn btn--ghost" href="${ROUTE_PREFIX}${next.slug}">${escapeHtml(next.title)} →</a>` : ""}
    </nav>`;

  updateCompleteButton();
  hljs.highlightElement($("#panel-theory pre code"));
}

function renderChallenge(challenge) {
  if (!challenge) return "";
  const stars = "★".repeat(challenge.stars) + "☆".repeat(3 - challenge.stars);
  return `
    <section class="challenge" aria-labelledby="challenge-title">
      <header class="challenge__head">
        <h2 id="challenge-title">Reto extra: ${escapeHtml(challenge.title)}</h2>
        <span class="challenge__stars" role="img" aria-label="Dificultad ${challenge.stars} de 3">${stars}</span>
        <span class="challenge__done" id="challenge-done" hidden>Superado</span>
      </header>
      <div class="prose">${renderMarkdown(challenge.exercise)}</div>
      <details class="challenge__hint"><summary>Ver pista</summary>${renderMarkdown(challenge.hint)}</details>
      <div class="practice-actions">
        <button class="btn btn--ghost" type="button" data-action="load-challenge">Cargar reto en la consola</button>
        <button class="btn btn--primary" type="button" id="challenge-button" data-action="check-challenge">Comprobar reto</button>
      </div>
      <div class="check" id="challenge-result" role="status" tabindex="-1" hidden></div>
    </section>`;
}

function updateChallengeDone() {
  const done = $("#challenge-done");
  if (done) done.hidden = !game.challenges.includes(content.current);
}

function updateCompleteButton() {
  const button = $("#complete-button");
  if (!button) return;
  const done = state.completed.has(content.current);
  button.textContent = done ? "Marcar como pendiente" : "Marcar como completada";
  button.className = `btn ${done ? "btn--ghost" : "btn--success"}`;
}

/* ---------- Pestañas (patrón ARIA tabs) ---------- */

function selectTab(tab, { focus = false } = {}) {
  for (const t of document.querySelectorAll('[role="tab"]')) {
    const selected = t === tab;
    t.setAttribute("aria-selected", String(selected));
    t.tabIndex = selected ? 0 : -1;
    document.getElementById(t.getAttribute("aria-controls")).hidden = !selected;
  }
  if (focus) tab.focus();
}

function initTabs() {
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  for (const tab of tabs) {
    tab.addEventListener("click", () => selectTab(tab));
    tab.addEventListener("keydown", (event) => {
      const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
      if (!step) return;
      const nextIndex = (tabs.indexOf(tab) + step + tabs.length) % tabs.length;
      selectTab(tabs[nextIndex], { focus: true });
    });
  }
}

/* ---------- Acciones ---------- */

async function copyExample() {
  try {
    await navigator.clipboard.writeText(currentLesson().example_code);
    return true;
  } catch {
    showToast("No se pudo copiar automáticamente: selecciona el código y pulsa Ctrl+C");
    return false;
  }
}

function downloadExample() {
  const lesson = currentLesson();
  const blob = new Blob([`${lesson.example_code}\n`], { type: "text/x-python" });
  const url = URL.createObjectURL(blob);
  Object.assign(document.createElement("a"), { href: url, download: `${lesson.slug}.py` }).click();
  URL.revokeObjectURL(url);
}

async function onCheckResult(result, code) {
  const slug = content.current;
  recordExercise(slug, result.passed);
  await recordAttempt(slug, code, result.passed);
  if (result.passed) {
    showToast("¡Ejercicio superado! Lección completada.");
    celebrate();
  }
}

function onChallengeResult(result) {
  if (!result.passed) return;
  recordChallenge(content.current, currentLesson().challenge.stars);
  showToast("¡Reto superado!");
  celebrate();
}

function initActions() {
  $("#main").addEventListener("click", async (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const slug = content.current;

    switch (target.dataset.action) {
      case "copy":
        if (await copyExample()) showToast("Código copiado al portapapeles");
        break;
      case "pycharm":
        // Una web no puede abrir PyCharm con código nuevo: copiamos y guiamos al usuario.
        await copyExample();
        $("#pycharm-hint").hidden = false;
        break;
      case "download":
        event.preventDefault();
        downloadExample();
        break;
      case "to-console":
        loadExample();
        $("#console-editor").focus();
        break;
      case "load-starter":
        loadStarter();
        break;
      case "check":
        checkCode({
          checks: currentLesson().checks,
          button: $("#check-button"),
          box: $("#check-result"),
          onResult: onCheckResult,
        });
        break;
      case "load-challenge":
        loadStarter("challenge");
        break;
      case "check-challenge":
        checkCode({
          checks: currentLesson().challenge.checks,
          button: $("#challenge-button"),
          box: $("#challenge-result"),
          onResult: onChallengeResult,
        });
        break;
      case "toggle-complete": {
        const done = !state.completed.has(slug);
        await setCompleted(slug, done);
        showToast(done ? "¡Lección completada!" : "Lección marcada como pendiente");
        break;
      }
    }
  });
}

/* ---------- Menú lateral en móvil ---------- */

function setMenu(open) {
  document.body.classList.toggle("nav-open", open);
  $("#menu-toggle").setAttribute("aria-expanded", String(open));
  // En móvil, con el menú cerrado, sus enlaces no deben recibir el foco
  $("#sidebar").inert = mobile.matches && !open;
  if (open) $("#sidebar .lesson[aria-current]")?.focus();
}

function initMobileMenu() {
  $("#menu-toggle").addEventListener("click", () => setMenu(!document.body.classList.contains("nav-open")));
  $("#sidebar-backdrop").addEventListener("click", () => setMenu(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && document.body.classList.contains("nav-open")) {
      setMenu(false);
      $("#menu-toggle").focus();
    }
  });
  mobile.addEventListener("change", () => setMenu(false));
  setMenu(false);
}

/* ---------- Navegación por hash ---------- */

function defaultSlug() {
  return content.order.find((slug) => !state.completed.has(slug)) ?? content.order[0];
}

function goTo(slug) {
  location.hash = `${ROUTE_PREFIX}${slug}`;
}

function navigate({ moveFocus = true } = {}) {
  if (location.hash.startsWith(RESET_ROUTE)) {
    const token = new URLSearchParams(location.hash.split("?")[1] ?? "").get("token");
    history.replaceState(null, "", `${ROUTE_PREFIX}${defaultSlug()}`);
    if (token) openPasswordReset(token);
  }

  const requested = decodeURIComponent(location.hash.slice(ROUTE_PREFIX.length));
  const slug =
    location.hash.startsWith(ROUTE_PREFIX) && content.lessons.has(requested) ? requested : defaultSlug();
  if (location.hash !== `${ROUTE_PREFIX}${slug}`) history.replaceState(null, "", `${ROUTE_PREFIX}${slug}`);

  content.current = slug;
  const lesson = currentLesson();
  renderLesson(lesson);
  updateSidebar();
  selectTab($("#tab-theory"));
  setConsoleLesson(lesson);
  setQuizLesson(lesson);
  updateChallengeDone();
  setAssistantLesson(lesson, lessonAt(lesson.index + 1), goTo);
  if (mobile.matches) setMenu(false);
  if (moveFocus) $("#lesson-title").focus();
  window.scrollTo({ top: 0 });
}

/* ---------- XP, nivel, racha y logros ---------- */

function updateGameCard() {
  const level = levelInfo();
  $("#xp-level").textContent = `Nivel ${level.number} · ${level.name}`;
  $("#xp-total").textContent = `${level.xp} XP`;
  $("#xp-next").textContent = level.next ? `${level.next.xp - level.xp} XP para «${level.next.name}»` : "¡Nivel máximo!";
  const bar = $("#xp-bar");
  bar.style.setProperty("--xp", `${level.progress}%`);
  bar.setAttribute("aria-valuenow", level.progress);
  const days = streak();
  $("#xp-streak").textContent = days === 1 ? "Racha: 1 día" : `Racha: ${days} días`;
  $("#badges-count").textContent = `${game.badges.length}/${BADGES.length}`;
}

function renderBadges() {
  $("#badges-list").innerHTML = BADGES.map((badge) => {
    const unlocked = game.badges.includes(badge.id);
    return `
      <li class="badge" data-unlocked="${unlocked}">
        <span class="badge__icon" aria-hidden="true">${escapeHtml(badge.icon)}</span>
        <span class="badge__text">
          <strong>${escapeHtml(badge.name)}</strong>
          <span>${escapeHtml(badge.goal)}</span>
          <span class="visually-hidden">${unlocked ? "(Conseguido)" : "(Pendiente)"}</span>
        </span>
      </li>`;
  }).join("");
}

function initGameUi() {
  onGame(({ events, unlocked, levelUp, level }) => {
    updateGameCard();
    updateChallengeDone();
    if ($("#badges-dialog").open) renderBadges();
    for (const message of events) showToast(message);
    for (const badge of unlocked) showToast(`Logro desbloqueado: ${badge.name}`);
    if (levelUp) showToast(`¡Subes a nivel ${level.number}: ${level.name}!`);
    if (unlocked.length || levelUp) celebrate();
  });
  setRunListener(recordRun);
  $("#badges-button").addEventListener("click", () => {
    renderBadges();
    $("#badges-dialog").showModal();
  });
  $("#badges-close").addEventListener("click", () => $("#badges-dialog").close());
}

/* ---------- Arranque ---------- */

function indexLessons(modules) {
  for (const module of modules) {
    for (const lesson of module.lessons) {
      content.lessons.set(lesson.slug, { ...lesson, module, index: content.order.length });
      content.order.push(lesson.slug);
    }
  }
}

function showLoadError() {
  $("#lesson-title").textContent = "No se pudo cargar el contenido";
  $("#panel-theory").innerHTML = `
    <div class="hint">
      <p>Si abriste <code>index.html</code> con doble clic, el navegador bloquea la lectura de <code>data/lessons.json</code>.
      Sírvelo con un servidor local desde la carpeta <code>frontend</code>:</p>
      <pre><code>python -m http.server 5500</code></pre>
      <p>y abre <a href="http://localhost:5500">http://localhost:5500</a>.</p>
    </div>`;
}

async function init() {
  initTabs();
  initActions();
  initMobileMenu();
  initConsole();
  initAssistant();
  initAccount({ toast: showToast });

  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    content.modules = (await response.json()).modules;
  } catch (error) {
    console.error("Error cargando las lecciones:", error);
    showLoadError();
    return;
  }

  indexLessons(content.modules);
  renderSidebar();
  initGameUi();
  initGame([...content.lessons.values()]);
  navigate({ moveFocus: false });
  window.addEventListener("hashchange", () => navigate());
  subscribe(() => {
    updateSidebar();
    updateCompleteButton();
  });
  restoreSession();
}

init();
