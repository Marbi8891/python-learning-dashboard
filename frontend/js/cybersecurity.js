import { escapeHtml, renderMarkdown, safeUrl } from "./markdown.js";

const COURSE_URL = "data/cybersecurity/course.json";
const STORAGE_KEY = "pld:cybersecurity:v1";
const $ = (selector) => document.querySelector(selector);
let coursePromise;
let course;
let state = { completed: [], quizScores: {} };
let activeQuiz = null;

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    state = {
      completed: Array.isArray(saved.completed) ? saved.completed.filter((id) => /^semana-\\d{2}$/.test(id)) : [],
      quizScores: saved.quizScores && typeof saved.quizScores === "object" ? saved.quizScores : {},
    };
  } catch { state = { completed: [], quizScores: {} }; }
}
function saveState() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch { /* almacenamiento no disponible */ }
}
function progress() { return Math.round((state.completed.length / course.weeks.length) * 100); }
function weekLink(week) { return `#/ciberseguridad/${week.id}`; }
function header() {
  const pct = progress();
  return `<header class="cyber-hero"><p class="eyebrow">Itinerario formativo · 320 horas</p><h1 id="cyber-title">${escapeHtml(course.title)}</h1><p class="cyber-lead">${escapeHtml(course.subtitle)}</p><div class="cyber-stats"><span><strong>16</strong> semanas</span><span><strong>20</strong> horas/semana</span><span><strong>2</strong> itinerarios técnicos</span></div><div class="cyber-progress" role="progressbar" aria-label="Progreso del curso" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}"><span style="width:${pct}%"></span></div><p class="cyber-progress-label">${state.completed.length} de 16 semanas completadas · ${pct}%</p></header>`;
}
function catalog() {
  return `${header()}<section class="cyber-section"><h2>Cómo se organiza</h2><div class="cyber-grid"><article class="cyber-card"><h3>Red Team</h3><p>${escapeHtml(course.tracks[0])}</p></article><article class="cyber-card"><h3>Blue Team</h3><p>${escapeHtml(course.tracks[1])}</p></article><article class="cyber-card"><h3>Python</h3><p>${escapeHtml(course.tracks[2])}</p></article></div></section><section class="cyber-section"><h2>Entorno de prácticas</h2><ul>${course.environment.map((x)=>`<li>${escapeHtml(x)}</li>`).join("")}</ul><p class="cyber-warning"><strong>Seguridad:</strong> las máquinas vulnerables deben permanecer en una red interna aislada. Solo se prueban sistemas propios o expresamente autorizados.</p></section><section class="cyber-section"><div class="cyber-section-head"><div><h2>Plan de estudios</h2><p>Selecciona una semana para consultar clases, prácticas y entregables.</p></div></div><div class="cyber-weeks">${course.weeks.map((w)=>`<a class="cyber-week ${state.completed.includes(w.id)?"is-done":""}" href="${weekLink(w)}"><span class="cyber-week-number">${String(w.number).padStart(2,"0")}</span><span class="cyber-week-main"><strong>${escapeHtml(w.title)}</strong><small>20 horas · ${escapeHtml(w.goal)}</small></span><span class="cyber-week-state">${state.completed.includes(w.id)?"Completada":"Ver semana"} →</span></a>`).join("")}</div></section><section class="cyber-section"><h2>Evaluación</h2><div class="cyber-assessment">${course.assessment.map((x)=>`<div><span>${escapeHtml(x.name)}</span><strong>${x.weight}%</strong></div>`).join("")}</div><p class="cyber-note">Criterio recomendado: nota final mínima de 7/10 y entrega del proyecto final. El progreso se guarda en este navegador; todavía no se sincroniza con la cuenta.</p></section><section class="cyber-section"><h2>Bibliografía y documentación</h2><ul class="cyber-resources"><li><a href="https://nostarch.com/Pentesting" target="_blank" rel="noopener noreferrer">Penetration Testing — Georgia Weidman</a></li><li><a href="https://nostarch.com/metasploit-2nd-edition" target="_blank" rel="noopener noreferrer">Metasploit: The Penetration Tester's Guide, 2nd edition</a></li><li><a href="https://nmap.org/book/" target="_blank" rel="noopener noreferrer">Nmap Network Scanning</a></li><li><a href="https://owasp.org/www-project-web-security-testing-guide/" target="_blank" rel="noopener noreferrer">OWASP Web Security Testing Guide</a></li><li><a href="https://portswigger.net/web-security" target="_blank" rel="noopener noreferrer">PortSwigger Web Security Academy</a></li><li><a href="https://attack.mitre.org/" target="_blank" rel="noopener noreferrer">MITRE ATT&CK</a></li><li><a href="https://docs.python.org/3/" target="_blank" rel="noopener noreferrer">Python Documentation</a></li><li><a href="https://www.kali.org/docs/" target="_blank" rel="noopener noreferrer">Kali Linux Documentation</a></li></ul></section>`;
}
function weekPage(week) {
  const score = state.quizScores[week.id];
  return `${header()}<nav class="cyber-breadcrumb"><a href="#/ciberseguridad">← Volver al curso</a><span>Semana ${week.number} de 16</span></nav><article class="cyber-detail"><p class="eyebrow">Semana ${String(week.number).padStart(2,"0")} · 20 horas</p><h1 id="cyber-title">${escapeHtml(week.title)}</h1><p class="cyber-lead">${escapeHtml(week.goal)}</p><section><h2>Contenidos</h2><ul>${week.topics.map((x)=>`<li>${escapeHtml(x)}</li>`).join("")}</ul></section><section><h2>Laboratorios y ejercicios</h2><ol>${week.labs.map((x)=>`<li>${escapeHtml(x)}</li>`).join("")}</ol></section><section><h2>Entregables</h2><ul>${week.deliverables.map((x)=>`<li>${escapeHtml(x)}</li>`).join("")}</ul></section><section><h2>Evaluación</h2><p>${escapeHtml(week.assessment)}</p></section><section><h2>Bibliografía y documentación</h2><ul>${week.resources.map((x)=>`<li>${escapeHtml(x)}</li>`).join("")}</ul></section><section class="cyber-quiz"><h2>Comprobación de conocimientos</h2><p>Responde a las tres preguntas. Necesitas al menos 2 aciertos para aprobar.</p>${week.quiz.map((q,i)=>`<fieldset><legend>${i+1}. ${escapeHtml(q.question)}</legend>${q.options.map((o,j)=>`<label><input type="radio" name="cyber-q-${i}" value="${j}"> ${escapeHtml(o)}</label>`).join("")}</fieldset>`).join("")}<button class="btn btn--primary" type="button" data-cyber-action="quiz" data-week="${week.id}">Corregir cuestionario</button><p class="cyber-quiz-result" role="status">${score === undefined ? "" : `Último resultado: ${score}/3`}</p></section><div class="cyber-complete"><span>${state.completed.includes(week.id)?"Semana completada":"Completa la semana al superar el cuestionario y marcar los entregables"}</span><button class="btn ${state.completed.includes(week.id)?"btn--ghost":"btn--success"}" type="button" data-cyber-action="complete" data-week="${week.id}" ${score === undefined || score < 2 ? "disabled" : ""}>${state.completed.includes(week.id)?"Marcar como pendiente":"Marcar semana como completada"}</button></div><nav class="cyber-week-nav"><a href="${week.number>1?weekLink(course.weeks[week.number-2]):"#/ciberseguridad"}">← Semana anterior</a><a href="${week.number<16?weekLink(course.weeks[week.number]):"#/ciberseguridad"}">${week.number<16?"Semana siguiente →":"Volver al curso"}</a></nav></article>`;
}
function render(hash) {
  const match = hash.match(/^#\\/ciberseguridad\\/(semana-\\d{2})$/);
  const week = match ? course.weeks.find((item)=>item.id===match[1]) : null;
  const root = $("#cyber-view");
  if (match && !week) { root.innerHTML = `<h1 id="cyber-title">Semana no encontrada</h1><a href="#/ciberseguridad">Volver al curso</a>`; return; }
  root.innerHTML = week ? weekPage(week) : catalog();
  document.title = week ? `Semana ${week.number} · Ciberseguridad · Python Learning Dashboard` : "Curso de Ciberseguridad · Python Learning Dashboard";
  root.querySelector("#cyber-title")?.focus({ preventScroll: true });
}
export async function openCyber(hash, { moveFocus = true } = {}) {
  loadState();
  coursePromise ??= fetch(COURSE_URL).then((r)=>{ if(!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); });
  try { course = await coursePromise; render(hash); }
  catch (error) { $("#cyber-view").innerHTML = `<h1 id="cyber-title">No se pudo cargar el curso</h1><p>Comprueba la conexión y vuelve a intentarlo. ${escapeHtml(error.message)}</p>`; }
}
export function initCyber() {
  $("#cyber-view").addEventListener("click",(event)=>{
    const button=event.target.closest("[data-cyber-action]"); if(!button||!course)return;
    const week=course.weeks.find((w)=>w.id===button.dataset.week); if(!week)return;
    if(button.dataset.cyberAction==="quiz"){
      const selected=week.quiz.map((_,i)=>$("#cyber-view input[name='cyber-q-"+i+"']:checked"));
      if(selected.some((x)=>!x)){ $("#cyber-view .cyber-quiz-result").textContent="Responde las tres preguntas antes de corregir."; return; }
      const score=selected.reduce((n,input,i)=>n+(Number(input.value)===week.quiz[i].answer?1:0),0);
      state.quizScores[week.id]=score; saveState();
      $("#cyber-view .cyber-quiz-result").textContent=`Resultado: ${score}/3. ${score>=2?"Cuestionario superado. Ya puedes marcar la semana como completada.":"Necesitas al menos 2 aciertos. Repasa los contenidos y vuelve a intentarlo."}`;
      const complete=$("#cyber-view [data-cyber-action='complete']"); if(complete)complete.disabled=score<2;
    }
    if(button.dataset.cyberAction==="complete"){
      if((state.quizScores[week.id]??0)<2)return;
      state.completed=state.completed.includes(week.id)?state.completed.filter((x)=>x!==week.id):[...state.completed,week.id]; saveState(); render(location.hash);
    }
  });
}
