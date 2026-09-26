/* Certificado de finalización (no oficial) que se imprime o guarda como PDF desde el navegador. */

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
