/* «Mi cuenta» (ADR-0025): área privada de la persona con sesión iniciada.
   1. Plan de estudio: fecha de examen por curso, repasos pendientes y meta diaria.
   2. Progreso en todos los cursos (web y app juntos) e historial de simulacros.
   3. Logros y certificados.
   4. Perfil y seguridad: nombre, contraseña y actividad reciente de la cuenta.
   Los datos que dependen del banco de preguntas o del servidor se rellenan cuando llegan. */

import { request, setToken } from "./api.js";
import { certificateStatus, courseCertificateStatus } from "./certificate.js";
import { courseBlockStats, courseReadiness, courseState, DAW_COURSES, loadCourseBank, saveCourse } from "./course-store.js";
import { BADGES, game, levelInfo, streak } from "./game.js";
import { escapeHtml } from "./markdown.js";
import { blockStats, examsPassed, isoDay, pcap, questionsMastered, readiness, savePcap } from "./pcap-store.js";
import { badgesHtml } from "./profile.js";
import { state, updateUser } from "./store.js";

const MEMBER_SINCE = new Intl.DateTimeFormat("es-ES", { month: "long", year: "numeric" });
const WHEN = new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
const DAY = new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "short", year: "numeric" });
const GOALS = [10, 20, 30, 50];
const DEFAULT_GOAL = 20;
const $ = (selector) => document.querySelector(selector);

/** Todos los cursos con su estado y sus rutas: el PCAP y los de DAW. */
const COURSES = [
  { id: "pcap", title: "Python · PCAP", subtitle: "Certificación PCAP-31-03", home: "#/pcap", review: "#/pcap/repaso", practice: (b) => `#/pcap/practica/${b}` },
  ...DAW_COURSES.map((c) => ({
    ...c,
    home: `#/daw/${c.id}`,
    review: `#/daw/${c.id}/practica/repaso`,
    practice: (b) => `#/daw/${c.id}/practica/${b}`,
  })),
];
const stateOf = (id) => (id === "pcap" ? pcap : courseState(id));
const saveOf = (id) => (id === "pcap" ? savePcap() : saveCourse(id));

const ACTIVITY = {
  login: "Inicio de sesión",
  login_failed: "Intento de inicio de sesión con contraseña incorrecta",
  password_changed: "Contraseña cambiada desde Mi cuenta",
  password_reset: "Contraseña restablecida con el enlace del email",
  logout_all: "Sesión cerrada en todos los dispositivos",
  name_changed: "Nombre cambiado",
};

const initials = (name) =>
  name
    .split(/\s+/)
    .map((word) => word.match(/\p{L}/u)?.[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

/** Días que faltan hasta una fecha «AAAA-MM-DD» (negativo si ya pasó). */
function daysUntil(day) {
  const [y, m, d] = day.split("-").map(Number);
  const [ty, tm, td] = isoDay().split("-").map(Number);
  return Math.round((Date.UTC(y, m - 1, d) - Date.UTC(ty, tm - 1, td)) / 86_400_000);
}

const dueToday = (s) => Object.values(s.srs).filter((item) => item.due <= isoDay()).length;

/** Preguntas distintas practicadas hoy en todos los cursos (su último intento es de hoy). */
function practicedToday() {
  const today = isoDay();
  return COURSES.reduce(
    (sum, c) => sum + Object.values(stateOf(c.id).srs).filter((item) => item.last && isoDay(new Date(item.last)) === today).length,
    0,
  );
}

/** Sin sesión no hay datos privados que mostrar: solo la invitación a entrar. */
function signedOut(apiEnabled) {
  return `
    <header class="profile-hero">
      <p class="eyebrow">Mi cuenta</p>
      <h1 class="profile-hero__title" id="private-title" tabindex="-1">Tu área privada</h1>
      <p class="profile-hero__note">${
        apiEnabled
          ? "Inicia sesión para ver tu cuenta y sincronizar tu progreso en todos tus dispositivos."
          : "Esta versión funciona sin cuenta: tu progreso se guarda solo en este navegador."
      }</p>
      ${apiEnabled ? `<p><button class="btn btn--primary" type="button" data-open-account>Iniciar sesión o crear cuenta</button></p>` : ""}
    </header>`;
}

/* ---------- 1. Plan de estudio ---------- */

function planHtml() {
  const goal = pcap.plan.dailyGoal ?? DEFAULT_GOAL;
  const done = practicedToday();
  const days = streak();
  const pct = Math.min(100, Math.round((done / goal) * 100));
  const rows = COURSES.map((c) => {
    const s = stateOf(c.id);
    const date = s.plan?.examDate ?? "";
    const left = date ? daysUntil(date) : null;
    const due = dueToday(s);
    const when = left === null ? "—" : left > 1 ? `${left} días` : left === 1 ? "Mañana" : left === 0 ? "¡Hoy!" : "Ya pasó";
    return `
      <tr>
        <th scope="row"><a href="${c.home}">${escapeHtml(c.title)}</a></th>
        <td><input type="date" data-exam-date="${c.id}" value="${escapeHtml(date)}" aria-label="Fecha del examen de ${escapeHtml(c.title)}"></td>
        <td>${when}</td>
        <td>${due ? `<a href="${c.review}">${due} por repasar</a>` : "Al día"}</td>
      </tr>`;
  }).join("");
  return `
    <section class="course-section" aria-labelledby="plan-title">
      <h2 class="section-title" id="plan-title">Mi plan de estudio</h2>
      <div class="goal">
        <label>Meta diaria
          <select data-daily-goal>${GOALS.map((g) => `<option value="${g}"${g === goal ? " selected" : ""}>${g} preguntas</option>`).join("")}</select>
        </label>
        <div class="meter meter--gold" role="progressbar" aria-label="Meta de hoy" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}">
          <span class="meter__fill" style="--value: ${pct}%"></span>
        </div>
        <p class="account-card__meta">Hoy llevas <strong>${done}</strong> de ${goal} preguntas${done >= goal ? " · ¡meta cumplida!" : ""}. Racha: ${days} ${days === 1 ? "día" : "días"}.</p>
      </div>
      <div class="table-wrap">
        <table class="history">
          <caption class="visually-hidden">Fecha de examen y repasos pendientes de cada curso</caption>
          <thead><tr><th scope="col">Curso</th><th scope="col">Fecha del examen</th><th scope="col">Faltan</th><th scope="col">Repaso de hoy</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      <p class="account-card__meta">El repaso espaciado te vuelve a preguntar lo que fallaste y lo que está a punto de olvidarse. Con 10-15 minutos al día basta.</p>
    </section>`;
}

/* ---------- 2. Progreso en todos los cursos ---------- */

function progressHtml() {
  const cards = COURSES.map((c) => {
    const s = stateOf(c.id);
    const answered = Object.keys(s.answers).length;
    const best = s.exams.length ? Math.max(...s.exams.map((e) => e.score)) : null;
    return `
      <li class="course-progress" data-course-card="${c.id}">
        <p class="course-progress__title"><a href="${c.home}">${escapeHtml(c.title)}</a> <span class="account-card__meta">${escapeHtml(c.subtitle)}</span></p>
        <p class="account-card__meta">${answered} preguntas respondidas · ${s.exams.length} ${s.exams.length === 1 ? "simulacro" : "simulacros"}${best === null ? "" : ` (mejor: ${best} %)`}</p>
        <div data-course-detail><p class="account-card__meta">Calculando tu dominio…</p></div>
      </li>`;
  }).join("");

  const exams = COURSES.flatMap((c) => stateOf(c.id).exams.map((e) => ({ ...e, course: c.title })))
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 10);
  const history = exams.length
    ? `<div class="table-wrap"><table class="history">
        <caption class="visually-hidden">Últimos simulacros de todos los cursos</caption>
        <thead><tr><th scope="col">Fecha</th><th scope="col">Curso</th><th scope="col">Nota</th><th scope="col">Aciertos</th><th scope="col">Tiempo</th></tr></thead>
        <tbody>${exams
          .map(
            (e) => `<tr><td>${DAY.format(new Date(e.date))}</td><td>${escapeHtml(e.course)}</td><td><strong>${e.score} %</strong></td>
              <td>${e.correct}/${e.total}</td><td>${Math.floor(e.seconds / 60)} min</td></tr>`,
          )
          .join("")}</tbody></table></div>`
    : `<p class="empty-state">Aún no has hecho ningún simulacro. Pruébalo en <a href="#/pcap/simulacro">el PCAP</a> o en la app Android, en cualquier curso.</p>`;

  return `
    <section class="course-section" aria-labelledby="progress-title">
      <h2 class="section-title" id="progress-title">Mi progreso en todos los cursos</h2>
      <p class="account-card__meta">Incluye lo que haces en la web y en la app Android. ${questionsMastered()} preguntas del PCAP dominadas · ${examsPassed()} simulacros del PCAP aprobados.</p>
      <ul class="course-progress-list">${cards}</ul>
      <h3 class="section-subtitle">Últimos simulacros</h3>
      ${history}
    </section>`;
}

/** Dominio y tema más flojo de cada curso: necesitan el banco de preguntas. */
async function fillCourse(c) {
  const bank = await loadCourseBank(c.id);
  const blocks = bank.exam.blocks;
  const stats = c.id === "pcap" ? blockStats(bank.questions, blocks) : courseBlockStats(c.id, bank);
  const score = c.id === "pcap" ? readiness(stats, blocks) : courseReadiness(stats, blocks);
  const tried = blocks.filter((b) => stats[b.slug].answered > 0).sort((a, b) => stats[a.slug].rate - stats[b.slug].rate);
  const weak = tried[0];
  const untried = blocks.find((b) => stats[b.slug].answered === 0);
  let tip = "Vas bien en todos los temas. Haz un simulacro para comprobarlo.";
  if (weak && stats[weak.slug].rate < 0.8) {
    tip = `Tu tema más flojo: <strong>${escapeHtml(weak.title.es)}</strong> (${Math.round(stats[weak.slug].rate * 100)} % de acierto). <a href="${c.practice(weak.slug)}">Practicarlo</a>`;
  } else if (untried) {
    tip = `Siguiente tema sin empezar: <strong>${escapeHtml(untried.title.es)}</strong>. <a href="${c.practice(untried.slug)}">Empezar</a>`;
  }
  const detail = document.querySelector(`[data-course-card="${c.id}"] [data-course-detail]`);
  if (!detail) return;
  detail.innerHTML = `
    <div class="meter" role="progressbar" aria-label="Dominio de ${escapeHtml(c.title)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${score}">
      <span class="meter__fill" style="--value: ${score}%"></span>
    </div>
    <p class="account-card__meta">Dominio: <strong>${score} %</strong> · ${tip}</p>`;
  if (c.id !== "pcap") fillCertificate(c, courseCertificateStatus(c.id, bank));
}

/* ---------- 3. Logros y certificados ---------- */

function achievementsHtml(content) {
  const pcapCert = certificateStatus(content);
  const certs = COURSES.map((c) => {
    if (c.id === "pcap") {
      return `<li data-done="${pcapCert.ok}"><strong>${escapeHtml(c.title)}</strong>: ${
        pcapCert.ok
          ? `<a href="#/certificado">ver y descargar</a>`
          : `te faltan ${pcapCert.lessons - pcapCert.done} lecciones${pcapCert.best >= 70 ? "" : " y aprobar un simulacro"}`
      }</li>`;
    }
    return `<li data-cert="${c.id}" data-done="false"><strong>${escapeHtml(c.title)}</strong>: <span data-cert-status>comprobando…</span></li>`;
  }).join("");
  const level = levelInfo();
  return `
    <section class="course-section" aria-labelledby="achievements-title">
      <h2 class="section-title" id="achievements-title">Logros y certificados</h2>
      <p class="account-card__meta">Nivel ${level.number} · ${escapeHtml(level.name)} · ${level.xp} XP · ${game.badges.length} de ${BADGES.length} logros.</p>
      <h3 class="section-subtitle">Certificados de finalización</h3>
      <ul class="checklist cert-requirements">${certs}</ul>
      <p class="account-card__meta">Son certificados no oficiales de este proyecto. En los cursos de DAW se consiguen con un dominio del 70 % y al menos 5 preguntas de cada bloque.</p>
      <h3 class="section-subtitle">Logros</h3>
      <ul class="badges__list" tabindex="0" aria-label="Logros">${badgesHtml()}</ul>
    </section>`;
}

function fillCertificate(c, status) {
  const item = document.querySelector(`[data-cert="${c.id}"]`);
  if (!item) return;
  item.dataset.done = String(status.ok);
  const missing = status.missing.length;
  item.querySelector("[data-cert-status]").innerHTML = status.ok
    ? `<a href="#/certificado/${c.id}">ver y descargar</a>`
    : `dominio ${status.score} % de 70 %${missing ? ` · faltan preguntas en ${missing} ${missing === 1 ? "bloque" : "bloques"}` : ""}`;
}

/* ---------- 4. Perfil y seguridad ---------- */

function securityHtml(user) {
  return `
    <section class="course-section" aria-labelledby="security-title">
      <h2 class="section-title" id="security-title">Perfil y seguridad</h2>
      <div class="course-columns">
        <form class="plan-form account-form" id="name-form">
          <h3 class="section-subtitle">Tu nombre</h3>
          <label>Nombre que se muestra <input name="display_name" maxlength="80" autocomplete="nickname" value="${escapeHtml(user.display_name)}" required></label>
          <button class="btn btn--ghost" type="submit">Guardar nombre</button>
          <p class="form-message" role="status"></p>
        </form>
        <form class="plan-form account-form" id="password-form">
          <h3 class="section-subtitle">Cambiar la contraseña</h3>
          <label>Contraseña actual <input name="current_password" type="password" autocomplete="current-password" maxlength="128" required></label>
          <label>Nueva contraseña (mínimo 8 caracteres) <input name="new_password" type="password" autocomplete="new-password" minlength="8" maxlength="128" required></label>
          <label>Repite la nueva <input name="confirm_password" type="password" autocomplete="new-password" minlength="8" maxlength="128" required></label>
          <button class="btn btn--ghost" type="submit">Cambiar contraseña</button>
          <p class="form-message" role="status"></p>
        </form>
      </div>
      <h3 class="section-subtitle">Actividad reciente de la cuenta</h3>
      <div id="account-activity"><p class="account-card__meta">Cargando…</p></div>
      <p class="account-card__meta">Si ves un inicio de sesión que no reconoces, cambia la contraseña: se cerrarán todas las demás sesiones.</p>
      <h3 class="section-subtitle">Mis datos</h3>
      <p>Tu progreso y tus ejercicios se guardan en tu cuenta, en servidores de la UE. Puedes descargar todos tus datos, cerrar sesión en todos tus dispositivos o borrar la cuenta cuando quieras.</p>
      <p>
        <button class="btn btn--ghost" type="button" data-open-account>Descargar datos, cerrar sesión o borrar la cuenta</button>
        <a href="privacidad.html">Política de privacidad</a>
      </p>
    </section>`;
}

async function fillActivity() {
  if (!$("#account-activity")) return;
  let html;
  try {
    const events = await request("GET", "/api/users/me/activity");
    html = events.length
      ? `<ul class="activity-list">${events
          .map(
            (e) => `<li data-kind="${escapeHtml(e.kind)}"><strong>${escapeHtml(ACTIVITY[e.kind] ?? e.kind)}</strong>
              <span class="account-card__meta">${WHEN.format(new Date(e.created_at))} · ${escapeHtml(e.device)}</span></li>`,
          )
          .join("")}</ul>`
      : `<p class="account-card__meta">Todavía no hay actividad registrada.</p>`;
  } catch {
    html = `<p class="account-card__meta">No se ha podido cargar la actividad.</p>`;
  }
  const slot = $("#account-activity"); // la página puede haberse repintado mientras llegaba
  if (slot) slot.innerHTML = html;
}

/* ---------- Página ---------- */

/** @param {object} content { order, lessons, modules }  @param {boolean} apiEnabled */
export function renderPrivate(content, apiEnabled) {
  const user = state.user;
  if (!user) return signedOut(apiEnabled);

  const total = content.order.length;
  const done = state.completed.size;
  const next = content.order.find((slug) => !state.completed.has(slug));
  const since = MEMBER_SINCE.format(new Date(user.created_at));

  // Lo que llega después (bancos de preguntas y actividad) se pinta cuando la página ya está puesta
  setTimeout(() => {
    for (const c of COURSES) fillCourse(c).catch(() => {});
    fillActivity();
  });

  return `
    <header class="profile-hero">
      <p class="eyebrow">Mi cuenta</p>
      <div class="account-card">
        <span class="account-card__avatar" aria-hidden="true">${escapeHtml(initials(user.display_name))}</span>
        <div>
          <h1 class="profile-hero__title" id="private-title" tabindex="-1">${escapeHtml(user.display_name)}</h1>
          <p class="account-card__meta">${escapeHtml(user.email)} · miembro desde ${since}</p>
        </div>
      </div>
      <p class="account-card__meta">${done} de ${total} lecciones de Python completadas.
        ${next ? `<a href="#/leccion/${next}">Continuar: ${escapeHtml(content.lessons.get(next).title)}</a>` : "¡Has completado todas!"}</p>
    </header>
    ${planHtml()}
    ${progressHtml()}
    ${achievementsHtml(content)}
    ${securityHtml(user)}`;
}

/** Mensaje dentro de un formulario (lo lee el lector de pantalla por role="status"). */
function formMessage(form, text, ok = false) {
  const box = form.querySelector(".form-message");
  box.textContent = text;
  box.dataset.ok = String(ok);
}

/**
 * Acciones de «Mi cuenta». Se enganchan una vez al contenedor, que se repinta entero.
 * @param {{ toast: (message: string) => void, refresh: () => void }} options
 */
export function initPrivate({ toast, refresh }) {
  const view = $("#private-view");

  view.addEventListener("change", (event) => {
    const input = event.target;
    if (input.matches("[data-exam-date]")) {
      const id = input.dataset.examDate;
      const value = input.value;
      if (value && !/^\d{4}-\d{2}-\d{2}$/.test(value)) return;
      const s = stateOf(id);
      s.plan = { ...s.plan, examDate: value || null };
      saveOf(id);
      toast(value ? "Fecha del examen guardada." : "Fecha del examen quitada.");
      refresh();
      view.querySelector(`[data-exam-date="${id}"]`)?.focus(); // el foco no se pierde al repintar
    } else if (input.matches("[data-daily-goal]")) {
      const goal = Number(input.value);
      if (!GOALS.includes(goal)) return;
      pcap.plan.dailyGoal = goal;
      savePcap();
      toast(`Meta diaria: ${goal} preguntas.`);
      refresh();
      view.querySelector("[data-daily-goal]")?.focus();
    }
  });

  view.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!["name-form", "password-form"].includes(form.id)) return;
    event.preventDefault();
    const data = new FormData(form);
    if (form.id === "password-form" && data.get("new_password") !== data.get("confirm_password")) {
      formMessage(form, "Las dos contraseñas nuevas no coinciden.");
      return;
    }
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    try {
      if (form.id === "name-form") {
        const user = await request("PATCH", "/api/users/me", { json: { display_name: data.get("display_name") } });
        updateUser(user);
        toast("Nombre guardado.");
      } else {
        const token = await request("POST", "/api/users/me/password", {
          json: { current_password: data.get("current_password"), new_password: data.get("new_password") },
        });
        // Esta sesión sigue (con la cookie renovada o, sin cookie, el token nuevo); las demás se han cerrado
        setToken(token.access_token);
        form.reset();
        toast("Contraseña cambiada. Se han cerrado las sesiones de tus otros dispositivos.");
        refresh();
      }
    } catch (error) {
      if (form.isConnected) formMessage(form, error.message);
    } finally {
      button.disabled = false;
    }
  });
}
