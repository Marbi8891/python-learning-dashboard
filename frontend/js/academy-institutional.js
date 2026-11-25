/* PLD ACADEMY — Institutional MVP.
 * This prototype stores demo workspace data locally. It is not multi-tenant production storage.
 */
const STORAGE_KEY = "pld-academy-institutional-demo-v1";

const seed = {
  organization: { name: "Centro de Formación PLD", type: "Centro de formación", academicYear: "2026–2027" },
  groups: [
    { id: "g-daw1", name: "1.º DAW A", program: "Desarrollo de Aplicaciones Web", subject: "Programación", teacher: "María García", students: 28 },
    { id: "g-dam1", name: "1.º DAM B", program: "Desarrollo de Aplicaciones Multiplataforma", subject: "Programación", teacher: "Carlos Ruiz", students: 24 },
    { id: "g-boot", name: "Bootcamp Python", program: "Python Developer", subject: "Python", teacher: "Ana López", students: 16 },
  ],
  assignments: [
    { id: "a-1", title: "Funciones en Python", groupId: "g-dam1", type: "Práctica", due: "2026-12-02", completed: 17, total: 24, status: "published" },
    { id: "a-2", title: "DOM y eventos", groupId: "g-daw1", type: "Actividad", due: "2026-12-04", completed: 12, total: 28, status: "published" },
    { id: "a-3", title: "Proyecto: gestor de tareas CLI", groupId: "g-boot", type: "Proyecto", due: "2026-12-10", completed: 8, total: 16, status: "published" },
  ],
  activityLog: [],
};

function readState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (saved && saved.organization && Array.isArray(saved.groups) && Array.isArray(saved.assignments)) return saved;
  } catch {}
  return structuredClone(seed);
}
let state = readState();
let activeTab = "overview";
let activeRole = "admin";

const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));
const groupName = (id) => state.groups.find((g) => g.id === id)?.name || "Grupo eliminado";
const persist = () => { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (error) { console.warn("Academy demo storage unavailable", error); } };\nconst newId = () => globalThis.crypto?.randomUUID?.() ?? `demo-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

function metric(label, value, note, icon) {
  return `<article class="academy-stat"><span class="academy-stat__icon" aria-hidden="true">${icon}</span><div><p>${esc(label)}</p><strong>${esc(value)}</strong><small>${esc(note)}</small></div></article>`;
}
function navItem(id, label, icon) {
  return `<button class="academy-nav__item ${activeTab === id ? "is-active" : ""}" type="button" data-academy-tab="${id}" aria-current="${activeTab === id ? "page" : "false"}"><span aria-hidden="true">${icon}</span>${label}</button>`;
}
function overview() {
  const studentTotal = state.groups.reduce((sum, g) => sum + Number(g.students || 0), 0);
  const completion = state.assignments.length ? Math.round(state.assignments.reduce((sum, a) => sum + (a.total ? a.completed / a.total : 0), 0) / state.assignments.length * 100) : 0;
  return `
    <div class="academy-page-head"><div><p class="academy-eyebrow">Panel institucional</p><h1 id="academy-title" tabindex="-1">Buenos días</h1><p>Resumen académico de ${esc(state.organization.name)}.</p></div><button class="academy-button academy-button--primary" data-academy-action="new-assignment">＋ Crear actividad</button></div>
    <div class="academy-stats">${metric("Grupos activos", state.groups.length, "Este curso académico", "▦")}${metric("Alumnos", studentTotal, "Matriculados en grupos", "♙")}${metric("Actividades", state.assignments.length, "Publicadas o en preparación", "☷")}${metric("Entrega media", `${completion}%`, "Progreso de actividades", "↗")}</div>
    <div class="academy-grid academy-grid--main"><section class="academy-card"><div class="academy-card__head"><div><h2>Grupos del centro</h2><p>Resumen de las aulas activas</p></div><button class="academy-link" data-academy-tab="groups">Ver todos →</button></div><div class="academy-group-list">${state.groups.map(g => `<article class="academy-group"><span class="academy-group__avatar">${esc(g.name.slice(0,2))}</span><div class="academy-group__body"><strong>${esc(g.name)}</strong><small>${esc(g.subject)} · ${esc(g.teacher)}</small></div><span class="academy-group__count">${esc(g.students)} alumnos</span></article>`).join("") || '<p class="academy-empty">Todavía no hay grupos. Crea el primero en Grupos.</p>'}</div></section>
    <section class="academy-card"><div class="academy-card__head"><div><h2>Actividad reciente</h2><p>Estado de las entregas</p></div></div><div class="academy-activity-list">${state.assignments.slice(0,4).map(a => `<article><div><strong>${esc(a.title)}</strong><small>${esc(groupName(a.groupId))} · Fecha límite ${esc(a.due || "Sin fecha")}</small></div><span class="academy-pill">${a.completed}/${a.total}</span></article>`).join("") || '<p class="academy-empty">No hay actividades creadas.</p>'}</div></section></div>
    <section class="academy-card"><div class="academy-card__head"><div><h2>Seguimiento docente</h2><p>Indicadores para orientar el apoyo al alumnado. No son calificaciones automáticas.</p></div></div><div class="academy-insight"><span aria-hidden="true">◎</span><div><strong>Revisa el progreso por grupo</strong><p>Consulta las actividades con menor porcentaje de entrega y decide si conviene reforzar contenidos o ampliar el plazo.</p></div><button class="academy-link" data-academy-tab="analytics">Abrir análisis →</button></div></section>`;
}
function groupsView() {
  return `<div class="academy-page-head"><div><p class="academy-eyebrow">Organización académica</p><h1 id="academy-title" tabindex="-1">Grupos</h1><p>Gestiona las aulas, programas y responsables.</p></div><button class="academy-button academy-button--primary" data-academy-action="new-group">＋ Crear grupo</button></div><section class="academy-card"><div class="academy-table-wrap"><table class="academy-table"><thead><tr><th>Grupo</th><th>Programa</th><th>Asignatura</th><th>Profesor</th><th>Alumnos</th></tr></thead><tbody>${state.groups.map(g => `<tr><td><strong>${esc(g.name)}</strong></td><td>${esc(g.program)}</td><td>${esc(g.subject)}</td><td>${esc(g.teacher)}</td><td>${esc(g.students)}</td></tr>`).join("")}</tbody></table></div>${state.groups.length ? "" : '<p class="academy-empty">Crea tu primer grupo.</p>'}</section>`;
}
function assignmentsView() {
  return `<div class="academy-page-head"><div><p class="academy-eyebrow">Aula virtual</p><h1 id="academy-title" tabindex="-1">Actividades</h1><p>Publica tareas, prácticas y proyectos para tus grupos.</p></div><button class="academy-button academy-button--primary" data-academy-action="new-assignment">＋ Nueva actividad</button></div><section class="academy-card"><div class="academy-table-wrap"><table class="academy-table"><thead><tr><th>Actividad</th><th>Grupo</th><th>Tipo</th><th>Entrega</th><th>Completada</th><th>Estado</th></tr></thead><tbody>${state.assignments.map(a => `<tr><td><strong>${esc(a.title)}</strong></td><td>${esc(groupName(a.groupId))}</td><td>${esc(a.type)}</td><td>${esc(a.due || "Sin fecha")}</td><td><div class="academy-progress"><span style="width:${a.total ? Math.min(100, Math.round(a.completed/a.total*100)) : 0}%"></span></div><small>${a.completed} / ${a.total}</small></td><td><span class="academy-pill academy-pill--${esc(a.status)}">${a.status === "published" ? "Publicada" : "Borrador"}</span></td></tr>`).join("")}</tbody></table></div></section>`;
}
function analyticsView() {
  return `<div class="academy-page-head"><div><p class="academy-eyebrow">Datos del centro</p><h1 id="academy-title" tabindex="-1">Seguimiento</h1><p>Indicadores agregados de actividad. Los datos de esta demo son de ejemplo.</p></div></div><div class="academy-stats">${metric("Actividades asignadas", state.assignments.length, "En los grupos", "☷")}${metric("Entregas registradas", state.assignments.reduce((s,a)=>s+a.completed,0), "Datos de demostración", "✓")}${metric("Entregas pendientes", state.assignments.reduce((s,a)=>s+(a.total-a.completed),0), "Estimación agregada", "◷")}${metric("Grupos", state.groups.length, "Activos", "▦")}</div><section class="academy-card"><h2>Actividad por grupo</h2><div class="academy-analytics-list">${state.groups.map(g => {const acts=state.assignments.filter(a=>a.groupId===g.id);const done=acts.reduce((s,a)=>s+a.completed,0);const total=acts.reduce((s,a)=>s+a.total,0);const percent=total?Math.round(done/total*100):0;return `<article><div class="academy-analytics-list__head"><strong>${esc(g.name)}</strong><span>${percent}% de entregas</span></div><div class="academy-progress academy-progress--large"><span style="width:${percent}%"></span></div><small>${acts.length} actividades · ${g.students} alumnos</small></article>`}).join("")}</div></section>`;
}
function settingsView() {
  return `<div class="academy-page-head"><div><p class="academy-eyebrow">Administración</p><h1 id="academy-title" tabindex="-1">Centro y configuración</h1><p>Datos del espacio institucional.</p></div></div><section class="academy-card academy-settings"><form id="academy-org-form"><label>Nombre del centro<input name="name" maxlength="120" required value="${esc(state.organization.name)}"></label><label>Tipo de institución<input name="type" maxlength="80" value="${esc(state.organization.type)}"></label><label>Curso académico<input name="academicYear" maxlength="20" value="${esc(state.organization.academicYear)}"></label><button class="academy-button academy-button--primary" type="submit">Guardar cambios</button></form><div class="academy-demo-note"><strong>Prototipo institucional</strong><p>En esta versión los datos se guardan en este navegador. Todavía no hay aislamiento multi-centro, cuentas de docentes, matrículas reales ni sincronización con backend.</p><button class="academy-button academy-button--secondary" data-academy-action="reset-demo">Restablecer datos demo</button></div></section>`;
}
function modalForm(type) {
  if (type === "group") return `<dialog class="academy-dialog" aria-labelledby="academy-dialog-title"><form id="academy-group-form" method="dialog"><header><h2 id="academy-dialog-title">Crear grupo</h2><button type="button" class="academy-close" data-academy-action="close-modal" aria-label="Cerrar">×</button></header><label>Nombre del grupo<input name="name" required maxlength="80" placeholder="Ej. 1.º DAW A"></label><label>Programa<input name="program" required maxlength="120" placeholder="Programa formativo"></label><label>Asignatura<input name="subject" required maxlength="100" placeholder="Asignatura"></label><label>Profesor responsable<input name="teacher" required maxlength="100" placeholder="Nombre del docente"></label><label>Alumnos<input name="students" type="number" min="0" max="5000" required value="0"></label><footer><button class="academy-button academy-button--secondary" type="button" data-academy-action="close-modal">Cancelar</button><button class="academy-button academy-button--primary" type="submit">Crear grupo</button></footer></form></dialog>`;
  return `<dialog class="academy-dialog" aria-labelledby="academy-dialog-title"><form id="academy-assignment-form" method="dialog"><header><h2 id="academy-dialog-title">Nueva actividad</h2><button type="button" class="academy-close" data-academy-action="close-modal" aria-label="Cerrar">×</button></header><label>Título<input name="title" required maxlength="160" placeholder="Nombre de la actividad"></label><label>Grupo<select name="groupId" required>${state.groups.map(g=>`<option value="${esc(g.id)}">${esc(g.name)}</option>`).join("")}</select></label><label>Tipo<select name="type"><option>Práctica</option><option>Actividad</option><option>Examen</option><option>Proyecto</option></select></label><label>Fecha límite<input name="due" type="date"></label><label>Estado<select name="status"><option value="published">Publicar</option><option value="draft">Guardar como borrador</option></select></label><footer><button class="academy-button academy-button--secondary" type="button" data-academy-action="close-modal">Cancelar</button><button class="academy-button academy-button--primary" type="submit">Guardar actividad</button></footer></form></dialog>`;
}
function render() {
  const tabContent = { overview, groups: groupsView, assignments: assignmentsView, analytics: analyticsView, settings: settingsView }[activeTab]();
  const tabs = [["overview","Resumen","⌂"],["groups","Grupos","▦"],["assignments","Actividades","☷"],["analytics","Seguimiento","↗"],["settings","Centro","⚙"]];
  return `<div class="academy-shell"><aside class="academy-rail"><div class="academy-brand"><span class="academy-brand__mark">A</span><div><strong>PLD ACADEMY</strong><small>Education workspace</small></div></div><div class="academy-org"><span class="academy-org__label">Institución activa</span><strong>${esc(state.organization.name)}</strong><small>${esc(state.organization.academicYear)}</small></div><nav class="academy-nav" aria-label="Academy"><span class="academy-nav__label">Workspace</span>${tabs.map(([id,label,icon])=>navItem(id,label,icon)).join("")}</nav><div class="academy-rail__footer"><span class="academy-avatar">AD</span><div><strong>Administrador demo</strong><small>Rol: ${activeRole === "admin" ? "Administrador" : activeRole === "teacher" ? "Profesor" : "Alumno"}</small></div></div></aside><div class="academy-workspace"><header class="academy-topbar"><span>Academy / ${esc(tabs.find(t=>t[0]===activeTab)?.[1]||"Resumen")}</span><label class="academy-role-switch">Vista de demo<select id="academy-role"><option value="admin" ${activeRole==="admin"?"selected":""}>Administrador</option><option value="teacher" ${activeRole==="teacher"?"selected":""}>Profesor</option><option value="student" ${activeRole==="student"?"selected":""}>Alumno</option></select></label></header><main class="academy-main">${activeRole==="student"?studentView():activeRole==="teacher"?teacherView():tabContent}</main></div></div>`;
}
function studentView() {
  return `<div class="academy-page-head"><div><p class="academy-eyebrow">Espacio del alumno</p><h1 id="academy-title" tabindex="-1">Mi aprendizaje</h1><p>Actividades asignadas y progreso personal.</p></div></div><section class="academy-card"><h2>Mis actividades</h2><div class="academy-activity-list">${state.assignments.map(a=>`<article><div><strong>${esc(a.title)}</strong><small>${esc(groupName(a.groupId))} · Fecha límite ${esc(a.due||"Sin fecha")}</small></div><span class="academy-pill">${a.completed}/${a.total} completadas</span></article>`).join("")||'<p>No tienes actividades.</p>'}</div></section><section class="academy-card"><h2>Mi ruta de aprendizaje</h2><p>El contenido del centro se conectará con las rutas, lecciones y ejercicios existentes en PLD Learning.</p><a class="academy-button academy-button--primary" href="#/aprender">Continuar en PLD Learning →</a></section>`;
}
function teacherView() {
  return `<div class="academy-page-head"><div><p class="academy-eyebrow">Workspace docente</p><h1 id="academy-title" tabindex="-1">Mis clases</h1><p>Revisa las actividades de tus grupos.</p></div><button class="academy-button academy-button--primary" data-academy-action="new-assignment">＋ Asignar actividad</button></div><section class="academy-card"><h2>Grupos asignados</h2><div class="academy-group-list">${state.groups.map(g=>`<article class="academy-group"><span class="academy-group__avatar">${esc(g.name.slice(0,2))}</span><div class="academy-group__body"><strong>${esc(g.name)}</strong><small>${esc(g.subject)} · ${esc(g.program)}</small></div><span class="academy-group__count">${g.students} alumnos</span></article>`).join("")}</div></section><section class="academy-card"><h2>Actividades a revisar</h2><div class="academy-activity-list">${state.assignments.map(a=>`<article><div><strong>${esc(a.title)}</strong><small>${esc(groupName(a.groupId))}</small></div><span class="academy-pill">${a.total-a.completed} pendientes</span></article>`).join("")}</div></section>`;
}
function mountModal(type) {
  const old = document.querySelector(".academy-dialog"); old?.remove();
  document.querySelector("#academy-view")?.insertAdjacentHTML("beforeend", modalForm(type));
  const dialog = document.querySelector(".academy-dialog");\n  try { dialog?.showModal(); } catch { dialog?.setAttribute("open", ""); }\n  dialog?.querySelector("input")?.focus();
}
function showToast(text) {
  let toast = document.querySelector(".academy-toast");
  if (!toast) { toast = document.createElement("div"); toast.className = "academy-toast"; toast.setAttribute("role","status"); document.querySelector("#academy-view")?.append(toast); }
  toast.textContent = text;
}
function handleClick(event) {
  const tab = event.target.closest("[data-academy-tab]");
  if (tab) { activeTab = tab.dataset.academyTab; document.querySelector("#academy-view").innerHTML = render(); return; }
  const action = event.target.closest("[data-academy-action]")?.dataset.academyAction;
  if (!action) return;
  if (action === "new-group") mountModal("group");
  if (action === "new-assignment") mountModal("assignment");
  if (action === "close-modal") document.querySelector(".academy-dialog")?.remove();
  if (action === "reset-demo") { state = structuredClone(seed); persist(); activeTab="overview"; document.querySelector("#academy-view").innerHTML=render(); showToast("Datos de demostración restaurados."); }
}
function handleSubmit(event) {
  if (event.target.id === "academy-group-form") {
    event.preventDefault(); const data = new FormData(event.target);
    const group = {id: newId(), name:data.get("name").trim(), program:data.get("program").trim(), subject:data.get("subject").trim(), teacher:data.get("teacher").trim(), students:Number(data.get("students"))||0};
    state.groups.push(group); persist(); activeTab="groups"; document.querySelector("#academy-view").innerHTML=render(); showToast("Grupo creado."); return;
  }
  if (event.target.id === "academy-assignment-form") {
    event.preventDefault(); const data = new FormData(event.target);
    state.assignments.unshift({id:newId(), title:data.get("title").trim(), groupId:data.get("groupId"), type:data.get("type"), due:data.get("due"), completed:0, total:state.groups.find(g=>g.id===data.get("groupId"))?.students||0, status:data.get("status")});
    persist(); activeTab="assignments"; document.querySelector("#academy-view").innerHTML=render(); showToast("Actividad guardada."); return;
  }
  if (event.target.id === "academy-org-form") {
    event.preventDefault(); const data=new FormData(event.target); state.organization={name:data.get("name").trim(),type:data.get("type").trim(),academicYear:data.get("academicYear").trim()}; persist(); document.querySelector("#academy-view").innerHTML=render(); showToast("Configuración guardada.");
  }
}
function handleChange(event) {
  if (event.target.id === "academy-role") { activeRole=event.target.value; document.querySelector("#academy-view").innerHTML=render(); }
}
let initialized = false;
export function initAcademy() {
  if (initialized) return; initialized = true;
  const root = document.querySelector("#academy-view");
  root.addEventListener("click", handleClick);
  root.addEventListener("submit", handleSubmit);
  root.addEventListener("change", handleChange);
}
export function renderAcademy() { return render(); }
export function openAcademy() {
  initAcademy();
  const root = document.querySelector("#academy-view");
  root.innerHTML = render();
  document.title = "PLD ACADEMY · Centros educativos";
  root.querySelector("h1")?.focus();
}
