/* Certificado de finalización (no oficial) que se imprime o guarda como PDF desde el navegador. */

import { courseBlockStats, courseReadiness, DAW_COURSES, loadCourseBank } from "./course-store.js";
import { escapeHtml } from "./markdown.js";
import { pcap } from "./pcap-store.js";
import { state } from "./store.js";

const NAME_KEY = "pld:cert-name";
const PASS = 70;
const OUT_OF_EXAM = "especializacion";

function savedName() {
  try {
    return localStorage.getItem(NAME_KEY) ?? "";
  } catch {
    return "";
  }
}

export function saveCertificateName(name) {
  try {
    localStorage.setItem(NAME_KEY, name);
  } catch {
    // sin almacenamiento: el nombre dura hasta recargar
  }
}

/** Requisitos: todas las lecciones del examen y al menos un simulacro aprobado. */
export function certificateStatus(content) {
  const lessons = content.modules.filter((m) => m.slug !== OUT_OF_EXAM).flatMap((m) => m.lessons.map((l) => l.slug));
  const done = lessons.filter((slug) => state.completed.has(slug)).length;
  const best = Math.max(0, ...pcap.exams.map((exam) => exam.score));
  return { lessons: lessons.length, done, best, ok: done === lessons.length && best >= PASS };
}

export function renderCertificate(content) {
  const status = certificateStatus(content);
  const header = `
    <header class="profile-hero no-print">
      <p class="eyebrow"><a href="#/perfil">Mi aprendizaje</a> · Certificado</p>
      <h1 class="profile-hero__title" id="certificate-title" tabindex="-1">Certificado de finalización</h1>
    </header>`;

  if (!status.ok) {
    return `${header}
      <section class="course-section">
        <p>Para conseguirlo necesitas:</p>
        <ul class="checklist cert-requirements">
          <li data-done="${status.done === status.lessons}">Completar las ${status.lessons} lecciones del temario del examen (llevas ${status.done}).</li>
          <li data-done="${status.best >= PASS}">Aprobar un simulacro con ${PASS} % o más (tu mejor nota: ${status.best} %).</li>
        </ul>
        <div class="course-hero__cta">
          <a class="btn btn--primary" href="#/inicio">Seguir con el curso</a>
          <a class="btn btn--ghost" href="#/pcap/simulacro">Hacer un simulacro</a>
        </div>
      </section>`;
  }

  const name = state.user?.display_name ?? savedName();
  const date = new Date().toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" });
  return `${header}
    <section class="course-section no-print">
      <form class="plan-form" id="certificate-form">
        <label>Nombre en el certificado <input name="cert-name" maxlength="80" value="${escapeHtml(name)}" required${state.user ? " readonly" : ""}></label>
        <button class="btn btn--ghost" type="submit">Actualizar</button>
        <button class="btn btn--primary" type="button" data-action="print-certificate">Descargar en PDF o imprimir</button>
      </form>
      <p class="readiness__note">En la ventana de impresión elige «Guardar como PDF».</p>
    </section>

    <article class="certificate" aria-label="Certificado">
      <p class="certificate__brand">Python Learning Dashboard</p>
      <p class="certificate__eyebrow">Certificado de finalización</p>
      <p class="certificate__lead">Se certifica que</p>
      <h2 class="certificate__name">${escapeHtml(name || "—")}</h2>
      <p class="certificate__text">ha completado el curso <em>${escapeHtml(content.course.title)}</em>:
        ${status.lessons} lecciones del temario del examen PCAP-31-03 con ejercicios corregidos,
        y ha aprobado un simulacro de examen con un <strong>${status.best} %</strong>.</p>
      <p class="certificate__date">${date}</p>
      <p class="certificate__disclaimer">Documento de un proyecto educativo. No es una certificación oficial
        del Python Institute ni la sustituye.</p>
    </article>`;
}

/* ---------- Certificados de los cursos de DAW (ADR-0025) ---------- */

export const COURSE_PASS = 70; // dominio mínimo del curso, en %
export const COURSE_BLOCK_ANSWERED = 5; // preguntas respondidas como mínimo en cada bloque

/** Requisitos: dominio del curso del 70 % o más y al menos 5 preguntas respondidas en cada bloque. */
export function courseCertificateStatus(id, bank) {
  const stats = courseBlockStats(id, bank);
  const score = courseReadiness(stats, bank.exam.blocks);
  const missing = bank.exam.blocks.filter((b) => stats[b.slug].answered < COURSE_BLOCK_ANSWERED);
  const answered = Object.values(stats).reduce((sum, s) => sum + s.answered, 0);
  return { score, missing, answered, ok: score >= COURSE_PASS && missing.length === 0 };
}

/** #/certificado/<curso>: se pinta cuando llega el banco del curso. */
export function renderCourseCertificate(id) {
  const course = DAW_COURSES.find((c) => c.id === id);
  if (!course) {
    return `<header class="profile-hero"><h1 class="profile-hero__title" id="certificate-title" tabindex="-1">Certificado no encontrado</h1>
      <p><a href="#/cuenta">Volver a Mi cuenta</a></p></header>`;
  }
  loadCourseBank(id)
    .then((bank) => {
      const slot = document.querySelector("#course-certificate");
      if (slot?.dataset.course === id) slot.innerHTML = courseCertificateBody(course, courseCertificateStatus(id, bank), bank);
    })
    .catch(() => {
      const slot = document.querySelector("#course-certificate");
      if (slot) slot.innerHTML = `<p class="empty-state">No se ha podido cargar el curso. Comprueba la conexión y recarga.</p>`;
    });
  return `
    <header class="profile-hero no-print">
      <p class="eyebrow"><a href="#/cuenta">Mi cuenta</a> · Certificado</p>
      <h1 class="profile-hero__title" id="certificate-title" tabindex="-1">Certificado · ${escapeHtml(course.title)}</h1>
    </header>
    <div id="course-certificate" data-course="${escapeHtml(id)}"><p class="empty-state">Comprobando tu progreso…</p></div>`;
}

function courseCertificateBody(course, status, bank) {
  if (!status.ok) {
    return `
      <section class="course-section">
        <p>Para conseguirlo necesitas:</p>
        <ul class="checklist cert-requirements">
          <li data-done="${status.score >= COURSE_PASS}">Un dominio del curso del ${COURSE_PASS} % o más (llevas ${status.score} %).</li>
          <li data-done="${status.missing.length === 0}">Responder al menos ${COURSE_BLOCK_ANSWERED} preguntas de cada bloque${
            status.missing.length ? ` (te faltan: ${status.missing.map((b) => escapeHtml(b.title.es)).join(", ")})` : ""
          }.</li>
        </ul>
        <div class="course-hero__cta"><a class="btn btn--primary" href="#/daw/${escapeHtml(course.id)}">Seguir con el curso</a></div>
      </section>`;
  }
  const name = state.user?.display_name ?? savedName();
  const date = new Date().toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" });
  return `
    <section class="course-section no-print">
      <p><button class="btn btn--primary" type="button" data-action="print-certificate">Descargar en PDF o imprimir</button></p>
      <p class="readiness__note">En la ventana de impresión elige «Guardar como PDF».</p>
    </section>
    <article class="certificate" aria-label="Certificado">
      <p class="certificate__brand">Python Learning Dashboard</p>
      <p class="certificate__eyebrow">Certificado de finalización</p>
      <p class="certificate__lead">Se certifica que</p>
      <h2 class="certificate__name">${escapeHtml(name || "—")}</h2>
      <p class="certificate__text">ha completado el curso <em>${escapeHtml(course.title)}</em> (${escapeHtml(course.subtitle)})
        con un dominio del <strong>${status.score} %</strong> sobre ${bank.questions.length} preguntas comprobadas,
        repartidas en ${bank.exam.blocks.length} bloques.</p>
      <p class="certificate__date">${date}</p>
      <p class="certificate__disclaimer">Documento de un proyecto educativo. No es un título oficial ni sustituye
        a la evaluación del centro.</p>
    </article>`;
}
