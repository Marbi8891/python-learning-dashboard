import { AI_ACADEMY_TRACKS, AI_ACADEMY_COURSES, aiCourseById, aiCourseLessons } from "./ai-academy-data.js";
import { escapeHtml } from "./markdown.js";

const ROOT="#/ai-academy";
const PROGRESS_KEY="pld:ai-academy:progress";
const $=(s,root=document)=>root.querySelector(s);
const readProgress=()=>{try{return JSON.parse(localStorage.getItem(PROGRESS_KEY)||"{}")}catch{return{}}};
const saveProgress=(value)=>{try{localStorage.setItem(PROGRESS_KEY,JSON.stringify(value))}catch{}};
const progressFor=(courseId)=>readProgress()[courseId]||[];
const totalLessons=(course)=>aiCourseLessons(course).length;
const courseProgress=(course)=>Math.round(progressFor(course.id).length/totalLessons(course)*100);
const courseHref=(id)=>`${ROOT}/curso/${encodeURIComponent(id)}`;

function courseCard(course){
 const done=progressFor(course.id).length, total=totalLessons(course);
 return `<article class="ai-course-card">
  <div class="ai-course-card__top"><span class="ai-course-number">${course.number}</span><span class="ai-course-tag">${escapeHtml(course.level)}</span></div>
  <h3><a href="${courseHref(course.id)}">${escapeHtml(course.title)}</a></h3>
  <p>${escapeHtml(course.description)}</p>
  <div class="ai-course-card__meta"><span>${course.hours} h estimadas</span><span>${done}/${total} temas</span></div>
  <div class="ai-meter" role="progressbar" aria-label="Progreso de ${escapeHtml(course.title)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${courseProgress(course)}"><span style="width:${courseProgress(course)}%"></span></div>
  <a class="btn btn--secondary ai-course-card__link" href="${courseHref(course.id)}">Ver temario <span aria-hidden="true">→</span></a>
 </article>`;
}
function trackCard(track){
 const courses=track.courseIds.map(aiCourseById).filter(Boolean), done=courses.reduce((n,c)=>n+progressFor(c.id).length,0), total=courses.reduce((n,c)=>n+totalLessons(c),0);
 return `<article class="ai-track-card"><div class="ai-track-card__head"><span class="ai-track-card__level">${escapeHtml(track.level)}</span><span>${track.hours} h</span></div><h3>${escapeHtml(track.title)}</h3><p>${escapeHtml(track.description)}</p><div class="ai-track-card__progress"><span>${done} de ${total} temas completados</span><span>${total?Math.round(done/total*100):0}%</span></div><div class="ai-meter"><span style="width:${total?Math.round(done/total*100):0}%"></span></div><div class="ai-track-card__courses">${courses.map(c=>`<a href="${courseHref(c.id)}">${escapeHtml(c.title)}</a>`).join("")}</div></article>`;
}
function renderCatalog(){
 const done=AI_ACADEMY_COURSES.reduce((n,c)=>n+progressFor(c.id).length,0), total=AI_ACADEMY_COURSES.reduce((n,c)=>n+totalLessons(c),0);
 return `<div class="page ai-academy" id="ai-academy-page">
 <header class="ai-academy-hero"><div class="ai-academy-hero__copy"><p class="eyebrow">Python Learning Dashboard · Academy</p><h1 id="ai-academy-title">AI Academy</h1><p>Aprende a utilizar la IA, desarrollar aplicaciones y desplegar sistemas inteligentes. Sigue una ruta completa o estudia cursos por separado.</p><div class="ai-academy-hero__actions"><a class="btn btn--primary" href="#ai-academy-tracks">Explorar itinerarios</a><a class="btn btn--secondary" href="#ai-academy-courses">Ver cursos</a></div></div><div class="ai-academy-hero__stats"><div><strong>20</strong><span>cursos</span></div><div><strong>330 h</strong><span>programa completo</span></div><div><strong>${total?Math.round(done/total*100):0}%</strong><span>progreso personal</span></div></div></header>
 <div class="ai-academy-note" role="status"><strong>Currículo inicial.</strong> Los temarios están publicados; las lecciones, laboratorios y evaluaciones se irán desarrollando y habilitando por etapas. El progreso se guarda en este navegador.</div>
 <section id="ai-academy-tracks" class="ai-academy-section"><div class="ai-section-heading"><div><p class="eyebrow">Rutas formativas</p><h2>Elige tu itinerario</h2></div><p>Los cursos pueden compartirse entre rutas.</p></div><div class="ai-track-grid">${AI_ACADEMY_TRACKS.map(trackCard).join("")}</div></section>
 <section id="ai-academy-courses" class="ai-academy-section"><div class="ai-section-heading"><div><p class="eyebrow">Catálogo</p><h2>Todos los cursos</h2></div><label class="ai-search-label">Buscar curso<input id="ai-academy-search" type="search" placeholder="Ej. agentes, Python, RAG…" autocomplete="off"></label></div><div class="ai-course-grid" id="ai-course-grid">${AI_ACADEMY_COURSES.map(courseCard).join("")}</div><p class="ai-empty" id="ai-course-empty" hidden>No hay cursos que coincidan con la búsqueda.</p></section>
 <section class="ai-academy-section ai-academy-final"><p class="eyebrow">Aprendizaje basado en proyectos</p><h2>Termina construyendo una solución</h2><p>El itinerario culmina en un proyecto con código, arquitectura, pruebas, evaluación de calidad, controles de seguridad, documentación y una demo.</p><a class="btn btn--primary" href="${courseHref("ai-20")}">Ver proyecto Capstone</a></section></div>`;
}
function renderCourse(course){
 const lessons=aiCourseLessons(course), completed=new Set(progressFor(course.id));
 const grouped=course.modules.map((module,moduleIndex)=>`<section class="ai-module"><header><span class="ai-module__index">M${String(moduleIndex+1).padStart(2,"0")}</span><div><h2>Unidad ${moduleIndex+1}</h2><p>${module.length} temas</p></div></header><ol class="ai-lesson-list">${module.map(title=>{const lesson=lessons.find(x=>x.title===title);return `<li><label class="ai-lesson-item"><input type="checkbox" data-ai-lesson="${lesson.id}" ${completed.has(lesson.id)?"checked":""}><span class="ai-lesson-item__title">${escapeHtml(title)}</span><span class="ai-lesson-item__status">${completed.has(lesson.id)?"Completado":"Temario"}</span></label></li>`}).join("")}</ol></section>`).join("");
 return `<div class="page ai-academy ai-course-detail"><a class="ai-back" href="${ROOT}">← Volver a AI Academy</a><header class="ai-course-hero"><p class="eyebrow">Curso ${course.number} · ${escapeHtml(course.category)}</p><h1>${escapeHtml(course.title)}</h1><p>${escapeHtml(course.description)}</p><div class="ai-course-hero__facts"><span>${course.hours} horas estimadas</span><span>${escapeHtml(course.level)}</span><span>${lessons.length} temas en el temario</span></div><div class="ai-meter ai-meter--large"><span id="ai-course-meter" style="width:${courseProgress(course)}%"></span></div><p id="ai-course-progress-text">${progressFor(course.id).length} de ${lessons.length} temas marcados como completados</p></header><div class="ai-academy-note"><strong>Temario disponible, lecciones en desarrollo.</strong> Marcar un tema sirve como seguimiento personal; no equivale a superar una evaluación ni acredita que el contenido esté impartido.</div><div class="ai-course-layout"><aside class="ai-course-summary"><h2>Sobre este curso</h2><p>Esta versión muestra el índice curricular. En próximas iteraciones cada tema tendrá lección, ejemplos, práctica, quiz y recursos revisados.</p><div class="ai-course-summary__stats"><span><strong>${course.hours}</strong> horas</span><span><strong>${lessons.length}</strong> temas</span><span><strong>${courseProgress(course)}%</strong> progreso</span></div><button class="btn btn--secondary" id="ai-course-reset" type="button">Reiniciar progreso del curso</button></aside><div class="ai-course-modules">${grouped}</div></div></div>`;
}
function openCourse(route){
 const id=decodeURIComponent(route.slice((ROOT+"/curso/").length)), course=aiCourseById(id);
 if(!course)return false;
 $("#ai-academy-view").innerHTML=renderCourse(course);
 $("#ai-academy-view").querySelectorAll("[data-ai-lesson]").forEach(input=>input.addEventListener("change",()=>{
  const current=readProgress(), list=new Set(current[course.id]||[]);
  input.checked?list.add(input.dataset.aiLesson):list.delete(input.dataset.aiLesson);
  current[course.id]=[...list];saveProgress(current);refreshCourseProgress(course);
 }));
 $("#ai-course-reset").addEventListener("click",()=>{const current=readProgress();delete current[course.id];saveProgress(current);openCourse(location.hash)});
 $("#ai-academy-view").querySelector("#ai-course-progress-text").textContent=`${progressFor(course.id).length} de ${totalLessons(course)} temas marcados como completados`;
 return true;
}
function refreshCourseProgress(course){
 const pct=courseProgress(course), meter=$("#ai-course-meter"), text=$("#ai-course-progress-text");
 if(meter)meter.style.width=`${pct}%`;
 if(text)text.textContent=`${progressFor(course.id).length} de ${totalLessons(course)} temas marcados como completados`;
 $("#ai-academy-view").querySelectorAll("[data-ai-lesson]").forEach(input=>{input.nextElementSibling?.nextElementSibling&&(input.nextElementSibling.nextElementSibling.textContent=input.checked?"Completado":"Temario")});
}
export function renderAIacademy(route){
 const root=$("#ai-academy-view");
 if(!root)return;
 if(route.startsWith(ROOT+"/curso/")){if(!openCourse(route))root.innerHTML=renderCatalog();return}
 root.innerHTML=renderCatalog();
 const search=$("#ai-academy-search");
 search?.addEventListener("input",()=>{
  const q=search.value.trim().toLocaleLowerCase("es");
  let visible=0;
  $("#ai-course-grid").querySelectorAll(".ai-course-card").forEach(card=>{
   const match=card.textContent.toLocaleLowerCase("es").includes(q);card.hidden=!match;if(match)visible++;
  });
  $("#ai-course-empty").hidden=visible>0;
 });
}
