/* Zona de examen PCAP: panel de preparación, simulacro cronometrado, práctica por bloque y fichas.
   Rutas: #/pcap · #/pcap/simulacro · #/pcap/practica/<bloque> · #/pcap/fichas[/<bloque>] */

import hljs from "../vendor/highlight/core.min.js";
import { recordPcap } from "./game.js";
import { escapeHtml, renderInline } from "./markdown.js";
import { blockStats, pcap, readiness, recordAnswer, savePcap } from "./pcap-store.js";

const DATA_URL = "data/pcap.json";
const PRACTICE_SIZE = 10;
const READY = { readiness: 80, blockRate: 0.6, blockAnswered: 5, lastExam: 75 };
const MASTERED = { answered: 10, rate: 0.9 };

const $ = (selector) => document.querySelector(selector);
const root = () => $("#pcap-view");

let data = null;
let loading = null;
let lessonsByBlock = {};
let session = null; // simulacro, práctica o fichas en curso
let ticker = null;

/* ---------- Utilidades ---------- */

const t = (value) => (typeof value === "string" ? value : value[pcap.lang]);
const md = (text) => renderInline(text);
const block = (slug) => data.exam.blocks.find((b) => b.slug === slug);
const same = (a, b) => a.length === b.length && a.every((x) => b.includes(x));
const pad = (n) => String(n).padStart(2, "0");
const clock = (seconds) => `${pad(Math.floor(seconds / 60))}:${pad(Math.max(0, seconds) % 60)}`;
const percent = (value) => `${Math.round(value * 100)} %`;

function shuffle(list) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function code(source) {
  if (!source) return "";
  const html = hljs.highlight(source, { language: "python" }).value;
  return `<pre class="quiz__code" tabindex="0" aria-label="Código"><code>${html}</code></pre>`;
}

function langSwitch() {
  return `
    <fieldset class="lang-switch">
      <legend>Idioma de las preguntas</legend>
      <label><input type="radio" name="pcap-lang" value="es"${pcap.lang === "es" ? " checked" : ""}> Español</label>
      <label><input type="radio" name="pcap-lang" value="en"${pcap.lang === "en" ? " checked" : ""}> English (como el examen)</label>
    </fieldset>`;
}

function meter(value, label, gold = false) {
  const pct = Math.round((value ?? 0) * 100);
  return `<span class="meter${gold ? " meter--gold" : ""}" role="progressbar" aria-label="${escapeHtml(label)}"
    aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}"><span class="meter__fill" style="--value: ${pct}%"></span></span>`;
}

/* ---------- Preparación y logros ---------- */

function status() {
  const stats = blockStats(data.questions, data.exam.blocks);
  const score = readiness(stats, data.exam.blocks);
  const lastExam = pcap.exams.at(-1);
  const weak = data.exam.blocks.filter(
    (b) => stats[b.slug].answered < READY.blockAnswered || stats[b.slug].rate < READY.blockRate,
  );
  const ready = score >= READY.readiness && !weak.length && lastExam?.score >= READY.lastExam;
  return { stats, score, lastExam, weak, ready };
}

/** Actualiza los indicadores que usan los logros y avisa a la gamificación. */
function commit(events = []) {
  const { stats, ready } = status();
  pcap.flags.mastered ||= data.exam.blocks.some(
    (b) => stats[b.slug].answered >= MASTERED.answered && stats[b.slug].rate >= MASTERED.rate,
  );
  pcap.flags.ready ||= ready;
  pcap.flags.allCards ||= data.cards.every((card) => pcap.known.includes(card.id));
  savePcap();
  recordPcap(events);
}

/* ---------- Panel ---------- */

function renderPanel() {
  const { stats, score, lastExam, weak, ready } = status();
  const advice = ready
    ? "Cumples los criterios: preparación del 80 % o más, todos los bloques por encima del 60 % y el último simulacro con 75 % o más."
    : [
        score < READY.readiness && `sube tu preparación al ${READY.readiness} % (ahora ${score} %)`,
        weak.length && `practica ${weak.map((b) => b.title.es).join(", ")} (mínimo ${READY.blockAnswered} preguntas y 60 % de acierto)`,
        !(lastExam?.score >= READY.lastExam) && `aprueba un simulacro con ${READY.lastExam} % o más`,
      ]
        .filter(Boolean)
        .join("; ");

  const blocks = data.exam.blocks
    .map((b) => {
      const s = stats[b.slug];
      const lesson = lessonsByBlock[b.slug];
      return `
        <li class="block-row">
          <div class="block-row__head">
            <span class="block-row__name">${escapeHtml(b.title.es)}</span>
            <span class="block-row__weight">${b.weight} % del examen</span>
          </div>
          ${meter(s.rate, `Acierto en ${b.title.es}`)}
          <div class="block-row__foot">
            <span>${s.answered ? `${percent(s.rate)} de acierto · ${s.answered} preguntas respondidas` : "Sin datos todavía"}</span>
            <span class="block-row__actions">
              ${lesson ? `<a href="#/leccion/${lesson}">Teoría</a>` : ""}
              <a class="btn btn--ghost" href="#/pcap/practica/${b.slug}">Practicar</a>
            </span>
          </div>
        </li>`;
    })
    .join("");

  const history = pcap.exams
    .slice(-8)
    .reverse()
    .map(
      (e) => `<tr><td>${new Date(e.date).toLocaleDateString("es-ES", { day: "numeric", month: "short" })}</td>
        <td>${e.score} %</td><td>${e.correct}/${e.total}</td><td>${clock(e.seconds)}</td>
        <td class="${e.score >= data.exam.pass ? "is-pass" : "is-fail"}">${e.score >= data.exam.pass ? "Aprobado" : "No aprobado"}</td></tr>`,
    )
    .join("");

  return `
    <header class="course-hero">
      <p class="eyebrow">Examen ${data.exam.code} · Python Institute</p>
      <h1 class="course-hero__title" id="pcap-title" tabindex="-1">Prepara el <em>examen PCAP</em></h1>
      <p class="course-hero__lead">${data.exam.questions} preguntas · ${data.exam.minutes} minutos · ${data.exam.pass} % para aprobar.
        ${data.questions.length} preguntas originales de práctica con el mismo formato y reparto del temario que el examen oficial.</p>
      <div class="course-hero__cta">
        <a class="btn btn--primary btn--lg" href="#/pcap/simulacro">Hacer un simulacro →</a>
        <a class="btn btn--ghost btn--lg" href="#/pcap/fichas">Fichas de repaso</a>
      </div>
      ${langSwitch()}
    </header>

    <section class="course-section" aria-labelledby="pcap-ready-title">
      <h2 class="section-title" id="pcap-ready-title">Tu preparación</h2>
      <div class="readiness" data-ready="${ready}">
        <div class="readiness__score"><strong>${score} %</strong><span>preparación estimada</span></div>
        <div class="readiness__text">
          ${meter(score / 100, "Preparación estimada", true)}
          <p><strong>${ready ? "Listo para examinarte." : "Aún no."}</strong> ${ready ? advice : `Para estar listo: ${advice}.`}</p>
          <p class="readiness__note">Es tu acierto en cada bloque ponderado por su peso en el examen. Orientativo: no es una predicción oficial.</p>
        </div>
      </div>
      <ul class="block-list">${blocks}</ul>
    </section>

    <section class="course-section" aria-labelledby="pcap-history-title">
      <h2 class="section-title" id="pcap-history-title">Simulacros</h2>
      ${
        history
          ? `<div class="table-wrap" tabindex="0" role="region" aria-labelledby="pcap-history-title"><table class="history">
          <thead><tr><th scope="col">Fecha</th><th scope="col">Nota</th><th scope="col">Aciertos</th><th scope="col">Tiempo</th><th scope="col">Resultado</th></tr></thead>
          <tbody>${history}</tbody></table></div>`
          : `<p class="empty-state">Todavía no has hecho ningún simulacro. Cuando domines algún bloque, pruébate con uno completo.</p>`
      }
    </section>`;
}

/* ---------- Pregunta (común a simulacro y práctica) ---------- */

function questionHtml(q, chosen, { number, reveal = false } = {}) {
  const multi = q.answer.length > 1;
  const type = multi ? "checkbox" : "radio";
  // Las de «elige dos» ya lo dicen en el enunciado, como en el examen real
  const limit = multi && !/\((Elige|Choose)/.test(t(q.q))
    ? ` <span class="exam-choose">(${pcap.lang === "en" ? `Choose ${q.answer.length}.` : `Elige ${q.answer.length}.`})</span>`
    : "";
  const result = reveal ? (same(chosen, q.answer) ? "ok" : "ko") : null;
  const options = q.options
    .map(
      (option, i) => `
      <label class="quiz__option"${reveal && q.answer.includes(i) ? ' data-correct="true"' : ""}>
        <input type="${type}" name="pcap-option-${q.id}" value="${i}"${chosen.includes(i) ? " checked" : ""}${reveal ? " disabled" : ""}>
        ${typeof option === "string" ? `<code class="opt-code">${escapeHtml(option)}</code>` : `<span>${md(t(option))}</span>`}
      </label>`,
    )
    .join("");
  return `
    <fieldset class="quiz__q exam-q"${result ? ` data-result="${result}"` : ""} data-limit="${q.answer.length}">
      <legend>${number ? `<span class="quiz__num">${number}</span> ` : ""}${md(t(q.q))}${limit}</legend>
      ${code(q.code)}
      <div class="quiz__options">${options}</div>
      ${
        reveal
          ? `<div class="quiz__feedback" tabindex="-1"><p class="quiz__verdict">${result === "ok" ? "¡Correcto!" : "No es correcta."}</p><p>${md(t(q.explain))}</p></div>`
          : ""
      }
    </fieldset>`;
}

function chosenFrom(form) {
  return [...form.querySelectorAll('input[name^="pcap-option"]:checked')].map((input) => Number(input.value));
}

/* ---------- Simulacro ---------- */

function startExam() {
  const items = data.exam.blocks.flatMap((b) =>
    shuffle(data.questions.filter((q) => q.block === b.slug)).slice(0, b.items),
  );
  session = {
    kind: "exam",
    items: shuffle(items).map((q) => ({ q, chosen: [], flagged: false })),
    index: 0,
    started: Date.now(),
    deadline: Date.now() + data.exam.minutes * 60_000,
    announced: new Set(),
    result: null,
  };
  clearInterval(ticker);
  ticker = setInterval(tick, 1000);
}

function tick() {
  if (session?.kind !== "exam" || session.result) return clearInterval(ticker);
  const left = Math.round((session.deadline - Date.now()) / 1000);
  const timer = $("#exam-timer");
  if (timer) {
    timer.textContent = clock(left);
    timer.dataset.low = String(left <= 300);
  }
  const minutes = Math.ceil(left / 60);
  if ([10, 5, 1].includes(minutes) && !session.announced.has(minutes)) {
    session.announced.add(minutes);
    const live = $("#exam-announce");
    if (live) live.textContent = `Quedan ${minutes} ${minutes === 1 ? "minuto" : "minutos"}.`;
  }
  if (left <= 0) finishExam();
}

function finishExam() {
  clearInterval(ticker);
  const blocks = {};
  let correct = 0;
  for (const item of session.items) {
    const ok = same(item.chosen, item.q.answer);
    item.ok = ok;
    correct += ok;
    recordAnswer(item.q.id, ok);
    const tally = (blocks[item.q.block] ??= [0, 0]);
    tally[0] += ok;
    tally[1] += 1;
  }
  const total = session.items.length;
  const score = Math.round((correct / total) * 100);
  const seconds = Math.min(Math.round((Date.now() - session.started) / 1000), data.exam.minutes * 60);
  session.result = { date: new Date().toISOString(), correct, total, score, seconds, blocks };
  pcap.exams.push(session.result);
  if (pcap.exams.length > 30) pcap.exams.shift();
  commit([`Simulacro terminado: ${score} %${score >= data.exam.pass ? " · ¡aprobado!" : ""}`]);
  if (location.hash.startsWith("#/pcap/simulacro")) render(location.hash, { focus: true });
}

function renderExamIntro() {
  const b = data.exam.blocks.map((x) => `<li>${escapeHtml(x.title.es)}: ${x.items} preguntas (${x.weight} %)</li>`).join("");
  return `
    <header class="profile-hero">
      <p class="eyebrow"><a href="#/pcap">Examen PCAP</a> · Simulacro</p>
      <h1 class="profile-hero__title" id="pcap-title" tabindex="-1">Simulacro de examen</h1>
    </header>
    <section class="course-section exam-intro">
      <ul class="checklist">
        <li>${data.exam.questions} preguntas elegidas al azar con el reparto oficial del temario:</li>
      </ul>
      <ul class="exam-intro__blocks">${b}</ul>
      <ul class="checklist">
        <li>${data.exam.minutes} minutos. Al acabar el tiempo se corrige automáticamente.</li>
        <li>Aprobado con ${data.exam.pass} %. Las de «elige dos» solo cuentan si aciertas las dos.</li>
        <li>Puedes marcar preguntas para revisarlas y moverte entre ellas.</li>
        <li>Las respuestas y explicaciones se muestran al terminar.</li>
      </ul>
      ${langSwitch()}
      <button class="btn btn--primary btn--lg" type="button" data-pcap="start-exam">Empezar el simulacro</button>
    </section>`;
}

function renderExamQuestion() {
  const item = session.items[session.index];
  const unanswered = session.items.filter((i) => !i.chosen.length).length;
  const left = Math.round((session.deadline - Date.now()) / 1000);
  const grid = session.items
    .map((it, i) => {
      const state = [i === session.index && "current", it.chosen.length && "answered", it.flagged && "flagged"]
        .filter(Boolean)
        .join(" ");
      const label = `Pregunta ${i + 1}${it.chosen.length ? ", respondida" : ""}${it.flagged ? ", marcada" : ""}`;
      return `<li><button type="button" class="exam-grid__item" data-go="${i}" data-state="${state}" aria-label="${label}"${i === session.index ? ' aria-current="step"' : ""}>${i + 1}</button></li>`;
    })
    .join("");
  return `
    <div class="exam-bar">
      <span class="exam-bar__title" id="pcap-title" tabindex="-1">Pregunta ${session.index + 1} de ${session.items.length}</span>
      <span class="exam-bar__timer">Tiempo: <span id="exam-timer" role="timer" data-low="${left <= 300}">${clock(left)}</span></span>
      <p class="visually-hidden" id="exam-announce" aria-live="polite"></p>
    </div>
    <form class="exam-form" id="exam-form">
      ${questionHtml(item.q, item.chosen, { number: session.index + 1 })}
      <div class="exam-actions">
        <button class="btn btn--ghost" type="button" data-pcap="prev"${session.index === 0 ? " disabled" : ""}>← Anterior</button>
        <button class="btn btn--ghost" type="button" data-pcap="flag" aria-pressed="${item.flagged}">${item.flagged ? "Desmarcar" : "Marcar para revisar"}</button>
        ${
          session.index < session.items.length - 1
            ? `<button class="btn btn--primary" type="button" data-pcap="next">Siguiente →</button>`
            : `<button class="btn btn--primary" type="button" data-pcap="ask-finish">Terminar examen</button>`
        }
      </div>
    </form>
    <nav class="exam-nav" aria-label="Preguntas del simulacro">
      <ol class="exam-grid">${grid}</ol>
      <p class="exam-nav__legend">${session.items.length - unanswered} respondidas · ${session.items.filter((i) => i.flagged).length} marcadas</p>
      <button class="btn btn--ghost" type="button" data-pcap="ask-finish">Terminar examen</button>
      <div class="exam-confirm" id="exam-confirm" role="alertdialog" aria-labelledby="exam-confirm-text" hidden>
        <p id="exam-confirm-text">${unanswered ? `Te quedan ${unanswered} preguntas sin responder. ` : ""}¿Terminar y corregir el simulacro?</p>
        <button class="btn btn--primary" type="button" data-pcap="finish">Sí, terminar</button>
        <button class="btn btn--ghost" type="button" data-pcap="cancel-finish">Seguir con el examen</button>
      </div>
    </nav>`;
}

function renderExamResult() {
  const r = session.result;
  const passed = r.score >= data.exam.pass;
  const blocks = data.exam.blocks
    .map((b) => {
      const [ok, total] = r.blocks[b.slug] ?? [0, 0];
      return `<li class="module-progress"><span class="module-progress__name">${escapeHtml(b.title.es)}</span>
        <span class="module-progress__count">${ok}/${total}</span>${meter(total ? ok / total : 0, b.title.es)}</li>`;
    })
    .join("");
  const review = session.items
    .map(
      (item, i) => `
      <details class="review-item" data-ok="${item.ok}">
        <summary><span class="review-item__mark" aria-hidden="true">${item.ok ? "✓" : "✗"}</span>
          <span class="visually-hidden">${item.ok ? "Correcta" : "Incorrecta"}:</span>
          <span>${i + 1}. ${md(t(item.q.q))} <span class="review-item__block">${escapeHtml(block(item.q.block).title.es)}</span></span></summary>
        ${questionHtml(item.q, item.chosen, { reveal: true })}
      </details>`,
    )
    .join("");
  return `
    <header class="profile-hero">
      <p class="eyebrow"><a href="#/pcap">Examen PCAP</a> · Resultado</p>
      <h1 class="profile-hero__title" id="pcap-title" tabindex="-1">${r.score} % · <em>${passed ? "Aprobado" : "No aprobado"}</em></h1>
      <p class="course-hero__lead">${r.correct} de ${r.total} correctas en ${clock(r.seconds)}. Para aprobar hace falta un ${data.exam.pass} %.</p>
      <div class="course-hero__cta">
        <button class="btn btn--primary" type="button" data-pcap="new-exam">Nuevo simulacro</button>
        <a class="btn btn--ghost" href="#/pcap">Volver al panel</a>
      </div>
    </header>
    <section class="course-section" aria-labelledby="exam-blocks-title">
      <h2 class="section-title" id="exam-blocks-title">Por bloque</h2>
      <ul class="module-progress-list">${blocks}</ul>
    </section>
    <section class="course-section" aria-labelledby="exam-review-title">
      <div class="section-head">
        <h2 class="section-title" id="exam-review-title">Revisión</h2>
        <label class="section-head__meta"><input type="checkbox" id="only-wrong"> Ver solo las falladas</label>
      </div>
      <div class="review-list" id="review-list">${review}</div>
    </section>`;
}

/* ---------- Práctica por bloque ---------- */

function startPractice(slug) {
  const pool = data.questions.filter((q) => q.block === slug);
  const fresh = shuffle(pool.filter((q) => !pcap.answers[q.id]));
  const failed = shuffle(pool.filter((q) => pcap.answers[q.id]?.at(-1) === false));
  const rest = shuffle(pool.filter((q) => pcap.answers[q.id]?.at(-1) === true));
  session = {
    kind: "practice",
    block: slug,
    items: [...failed, ...fresh, ...rest].slice(0, PRACTICE_SIZE).map((q) => ({ q, chosen: [] })),
    index: 0,
    checked: false,
    correct: 0,
    combo: 0,
    masteredBefore: Object.values(pcap.answers).filter((h) => h.includes(true)).length,
  };
}

function renderPractice() {
  const b = block(session.block);
  const head = `
    <div class="exam-bar">
      <span class="exam-bar__title" id="pcap-title" tabindex="-1">Práctica · ${escapeHtml(b.title.es)}</span>
      <span>Pregunta ${Math.min(session.index + 1, session.items.length)} de ${session.items.length}</span>
      <span class="combo" data-hot="${session.combo >= 3}" aria-live="polite">Racha: ${session.combo}</span>
    </div>`;
  if (session.index >= session.items.length) {
    const gained = (Object.values(pcap.answers).filter((h) => h.includes(true)).length - session.masteredBefore) * 5;
    return `${head}
      <section class="course-section practice-end">
        <h2 class="section-title">${session.correct} de ${session.items.length} correctas</h2>
        <p>${gained ? `+${gained} XP por preguntas nuevas acertadas. ` : ""}Tu mejor racha: ${pcap.bestCombo} aciertos seguidos.</p>
        <div class="course-hero__cta">
          <button class="btn btn--primary" type="button" data-pcap="again">Otra tanda de ${escapeHtml(b.title.es)}</button>
          <a class="btn btn--ghost" href="#/pcap">Volver al panel</a>
        </div>
      </section>`;
  }
  const item = session.items[session.index];
  return `${head}
    <form class="exam-form" id="practice-form">
      ${questionHtml(item.q, item.chosen, { number: session.index + 1, reveal: session.checked })}
      <div class="exam-actions">
        ${
          session.checked
            ? `<button class="btn btn--primary" type="button" data-pcap="practice-next">${session.index + 1 < session.items.length ? "Siguiente →" : "Ver resultado"}</button>`
            : `<button class="btn btn--primary" type="button" data-pcap="check">Comprobar</button>`
        }
      </div>
      <p class="quiz__message" id="practice-message" role="alert"></p>
    </form>
    ${langSwitch()}`;
}

function checkPractice() {
  const item = session.items[session.index];
  if (!item.chosen.length) {
    $("#practice-message").textContent = "Elige una respuesta.";
    return;
  }
  const ok = same(item.chosen, item.q.answer);
  recordAnswer(item.q.id, ok);
  session.checked = true;
  session.correct += ok;
  session.combo = ok ? session.combo + 1 : 0;
  pcap.bestCombo = Math.max(pcap.bestCombo, session.combo);
  commit();
}

/* ---------- Fichas ---------- */

function startCards(slug) {
  const deck = data.cards.filter((c) => !slug || c.block === slug);
  session = {
    kind: "cards",
    block: slug,
    deck: [...shuffle(deck.filter((c) => !pcap.known.includes(c.id))), ...shuffle(deck.filter((c) => pcap.known.includes(c.id)))],
    index: 0,
    flipped: false,
  };
}

function renderCards() {
  const known = data.cards.filter((c) => pcap.known.includes(c.id)).length;
  const chips = [["", "Todas"], ...data.exam.blocks.map((b) => [b.slug, b.title.es])]
    .map(
      ([slug, title]) =>
        `<a class="chip"${(session.block ?? "") === slug ? ' aria-current="page"' : ""} href="#/pcap/fichas${slug ? `/${slug}` : ""}">${escapeHtml(title)}</a>`,
    )
    .join("");
  const card = session.deck[session.index % session.deck.length];
  const isKnown = pcap.known.includes(card.id);
  return `
    <header class="profile-hero">
      <p class="eyebrow"><a href="#/pcap">Examen PCAP</a> · Fichas</p>
      <h1 class="profile-hero__title" id="pcap-title" tabindex="-1">Fichas de repaso</h1>
      <p class="course-hero__lead">${known} de ${data.cards.length} fichas dominadas.</p>
      <nav class="chips" aria-label="Filtrar fichas por bloque">${chips}</nav>
    </header>
    <section class="course-section">
      <article class="flashcard" data-flipped="${session.flipped}">
        <p class="flashcard__meta">${escapeHtml(block(card.block).title.es)} · ${(session.index % session.deck.length) + 1}/${session.deck.length}${isKnown ? " · dominada" : ""}</p>
        <h2 class="flashcard__front">${md(t(card.front))}</h2>
        ${
          session.flipped
            ? `<div class="flashcard__back" id="card-back" tabindex="-1"><p>${md(t(card.back))}</p>${code(card.code)}</div>`
            : ""
        }
        <div class="exam-actions">
          ${
            session.flipped
              ? `<button class="btn btn--primary" type="button" data-pcap="card-known">Lo sé →</button>
                 <button class="btn btn--ghost" type="button" data-pcap="card-again">Repasar otra vez</button>`
              : `<button class="btn btn--primary" type="button" data-pcap="card-flip">Ver respuesta</button>`
          }
        </div>
      </article>
      ${langSwitch()}
    </section>`;
}

/* ---------- Render y eventos ---------- */

function render(route, { focus = false } = {}) {
  const [, , view, arg] = route.split("/"); // "#/pcap/<view>/<arg>"
  let html;
  if (view === "simulacro") {
    html = session?.kind !== "exam" ? renderExamIntro() : session.result ? renderExamResult() : renderExamQuestion();
  } else if (view === "practica" && block(arg)) {
    if (session?.kind !== "practice" || session.block !== arg) startPractice(arg);
    html = renderPractice();
  } else if (view === "fichas") {
    const slug = block(arg) ? arg : null;
    if (session?.kind !== "cards" || session.block !== slug) startCards(slug);
    html = renderCards();
  } else {
    html = renderPanel();
  }
  root().innerHTML = html;
  if (focus) $("#pcap-title")?.focus();
}

function onClick(event) {
  const target = event.target.closest("[data-pcap], [data-go]");
  if (!target) return;
  const rerender = (focus = true) => render(location.hash, { focus });
  if (target.dataset.go !== undefined) {
    session.index = Number(target.dataset.go);
    return rerender();
  }
  switch (target.dataset.pcap) {
    case "start-exam":
    case "new-exam":
      startExam();
      return rerender();
    case "prev":
      session.index -= 1;
      return rerender();
    case "next":
      session.index += 1;
      return rerender();
    case "flag":
      session.items[session.index].flagged = !session.items[session.index].flagged;
      return rerender(false);
    case "ask-finish":
      $("#exam-confirm").hidden = false;
      return $('#exam-confirm [data-pcap="finish"]').focus();
    case "cancel-finish":
      $("#exam-confirm").hidden = true;
      return undefined;
    case "finish":
      return finishExam();
    case "check":
      checkPractice();
      render(location.hash);
      return $(".quiz__feedback")?.focus();
    case "practice-next":
      session.index += 1;
      session.checked = false;
      return rerender();
    case "again":
      startPractice(session.block);
      return rerender();
    case "card-flip":
      session.flipped = true;
      render(location.hash);
      return $("#card-back")?.focus();
    case "card-known":
    case "card-again": {
      const card = session.deck[session.index % session.deck.length];
      const known = target.dataset.pcap === "card-known";
      pcap.known = pcap.known.filter((id) => id !== card.id);
      if (known) pcap.known.push(card.id);
      commit();
      session.index += 1;
      session.flipped = false;
      return rerender();
    }
    default:
      return undefined;
  }
}

function onChange(event) {
  const input = event.target;
  if (input.name === "pcap-lang") {
    pcap.lang = input.value;
    savePcap();
    render(location.hash);
    document.querySelector(`input[name="pcap-lang"][value="${pcap.lang}"]`)?.focus();
    return;
  }
  if (input.name.startsWith("pcap-option") && session?.items) {
    const form = input.closest("form");
    const item = session.items[session.index];
    const limit = Number(form.querySelector("fieldset").dataset.limit);
    let chosen = chosenFrom(form);
    if (chosen.length > limit) {
      input.checked = false; // «elige dos»: no deja marcar una tercera
      chosen = chosenFrom(form);
    }
    item.chosen = chosen;
    if (session.kind === "exam") {
      const button = document.querySelector(`[data-go="${session.index}"]`);
      if (button) button.dataset.state = `current${chosen.length ? " answered" : ""}${item.flagged ? " flagged" : ""}`;
    }
  }
  if (input.id === "only-wrong") {
    $("#review-list").dataset.onlyWrong = String(input.checked);
  }
}

/**
 * Muestra la zona PCAP. Carga el banco de preguntas la primera vez.
 * @param {string} route  el hash actual (#/pcap...)
 * @param {object} modules módulos de lecciones, para enlazar cada bloque con su teoría
 */
export async function openPcap(route, modules, { moveFocus = true } = {}) {
  if (!data) {
    root().innerHTML = `<p class="empty-state" id="pcap-title" tabindex="-1">Cargando el banco de preguntas…</p>`;
    try {
      loading ??= fetch(DATA_URL).then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      });
      data = await loading;
    } catch {
      loading = null;
      root().innerHTML = `<p class="empty-state" id="pcap-title" tabindex="-1">No se pudo cargar el banco de preguntas. Recarga la página.</p>`;
      return;
    }
    lessonsByBlock = Object.fromEntries(modules.map((m) => [m.slug, m.lessons[0]?.slug]));
    root().addEventListener("click", onClick);
    root().addEventListener("change", onChange);
  }
  if (!location.hash.startsWith("#/pcap")) return; // el alumno se fue mientras cargaba
  render(route, { focus: moveFocus });
}
