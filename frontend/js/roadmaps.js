/* Roadmaps hub: V1 routes users through existing PLD learning resources.
   Progress is stored locally until account sync is added. */
const KEY = "pld:roadmaps:v1";
const ROUTES = [
 {id:"python",title:"Python desde cero",category:"Programación",level:"Principiante",duration:"6–8 semanas",desc:"Domina los fundamentos de Python y construye una base para automatización o desarrollo.",icon:"PY",href:"#/aprender",skills:["Python","Lógica"],nodes:[
  ["Primeros pasos","Conoce el entorno, print(), comentarios y cómo ejecutar código.","#/teoria","Abrir teoría"],
  ["Variables y tipos","Números, texto, booleanos y conversiones.","#/leccion/variables","Practicar variables"],
  ["Condicionales","Comparaciones, if, elif, else y lógica booleana.","#/teoria","Estudiar conceptos"],
  ["Bucles","for, while, range, break y continue.","#/teoria","Practicar bucles"],
  ["Colecciones","Listas, tuplas, conjuntos y diccionarios.","#/practicar","Resolver ejercicios"],
  ["Funciones","Parámetros, retorno y reutilización.","#/practicar","Practicar funciones"],
  ["Archivos y excepciones","Lectura, escritura y gestión de errores.","#/practicar","Practicar"],
  ["Programación orientada a objetos","Clases, objetos, métodos y relaciones.","#/poo","Abrir POO"],
  ["Proyecto final","Construye una pequeña aplicación integrando lo aprendido.","#/daw","Ver DAW"]
 ]},
 {id:"pcap",title:"Preparación PCAP",category:"Certificación",level:"Intermedio",duration:"8–12 semanas",desc:"Organiza el estudio de Python y practica los bloques del examen con ejercicios y simulacros.",icon:"PC",href:"#/inicio",skills:["Python","Examen"],nodes:[
  ["Sintaxis y fundamentos","Tipos, operadores, expresiones y flujo.","#/inicio","Curso PCAP"],
  ["Control de flujo","Condiciones, bucles y lógica.","#/inicio","Curso PCAP"],
  ["Colecciones y cadenas","Listas, tuplas, diccionarios y strings.","#/inicio","Curso PCAP"],
  ["Funciones y módulos","Parámetros, alcance, módulos y paquetes.","#/inicio","Curso PCAP"],
  ["Excepciones","Manejo y jerarquía de errores.","#/inicio","Curso PCAP"],
  ["POO","Clases, atributos, métodos y herencia.","#/inicio","Curso PCAP"],
  ["Simulacros","Practica con tiempo y revisa tus errores.","#/pcap","Realizar simulacro"]
 ]},
 {id:"daw",title:"Programación de DAW",category:"Formación profesional",level:"FP",duration:"Curso académico",desc:"Refuerza las competencias del módulo de Programación con teoría, ejercicios y evaluación.",icon:"DA",href:"#/daw/programacion",skills:["0485","Python","Java"],nodes:[
  ["Lógica y algoritmos","Pseudocódigo y resolución de problemas.","#/daw/programacion","Abrir módulo"],
  ["Sintaxis y tipos","Variables, tipos, expresiones y entrada/salida.","#/daw/programacion","Abrir módulo"],
  ["Estructuras de control","Condiciones y estructuras repetitivas.","#/daw/programacion","Abrir módulo"],
  ["Estructuras de datos","Arrays, colecciones y operaciones.","#/daw/programacion","Abrir módulo"],
  ["Métodos y modularidad","Diseño, parámetros y organización.","#/daw/programacion","Abrir módulo"],
  ["POO","Clases, objetos, relaciones y principios.","#/daw/programacion","Abrir módulo"],
  ["Evaluación","Comprueba resultados de aprendizaje y prepara pruebas.","#/daw","Preparar DAW"]
 ]},
 {id:"web",title:"Desarrollo web",category:"Desarrollo",level:"Principiante",duration:"12–16 semanas",desc:"Una ruta desde HTML y CSS hasta JavaScript, APIs y una aplicación desplegada.",icon:"WEB",href:"#/daw/cursos",skills:["HTML","CSS","JavaScript"],nodes:[
  ["HTML","Estructura, semántica, formularios y accesibilidad.","#/daw/cursos","Explorar cursos"],
  ["CSS","Diseño responsive, Flexbox, Grid y estilos.","#/daw/cursos","Explorar cursos"],
  ["JavaScript","Variables, funciones, arrays, objetos y DOM.","#/daw/js","JavaScript"],
  ["Asincronía y APIs","Fetch, promesas, JSON y APIs.","#/daw/js","JavaScript"],
  ["Backend y bases de datos","HTTP, servidor, SQL y persistencia.","#/daw/cursos","Explorar módulos"],
  ["Proyecto web","Desarrolla y publica una aplicación completa.","#/daw/cursos","Ver módulos DAW"]
 ]}
];
const esc = v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function read(){try{return JSON.parse(localStorage.getItem(KEY)||"{}")}catch{return {}}}
let progress=read();
function stats(r){const done=new Set(progress[r.id]||[]);return {done,total:r.nodes.length,pct:Math.round(done.size/r.nodes.length*100),next:r.nodes.find(n=>!done.has(n[0]))}}
function card(r){const p=stats(r);return `<article class="rm-card"><div class="rm-card__top"><span class="rm-icon">${esc(r.icon)}</span><span class="rm-category">${esc(r.category)}</span></div><h2><a href="#/roadmaps/${r.id}">${esc(r.title)}</a></h2><p>${esc(r.desc)}</p><div class="rm-meta">${esc(r.level)} · ${esc(r.duration)}</div><div class="rm-progress"><div class="rm-progress__labels"><span>Progreso</span><strong>${p.done.size}/${p.total} · ${p.pct}%</strong></div><div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${p.pct}"><span class="meter__fill" data-meter="${p.pct}"></span></div></div><a class="btn btn--primary" href="#/roadmaps/${r.id}">${p.done.size?"Continuar ruta":"Empezar ruta"} →</a><small class="rm-next">${p.next?"Siguiente: "+esc(p.next[0]):"Ruta completada"}</small></article>`}
function overview(){const active=ROUTES.map(r=>({r,p:stats(r)})).filter(x=>x.p.done.size).sort((a,b)=>b.p.pct-a.p.pct);return `<header class="rm-hero"><p class="eyebrow">Tu centro de aprendizaje</p><h1 id="roadmaps-title" tabindex="-1">Roadmaps</h1><p class="rm-lead">Elige un objetivo. Sigue una ruta paso a paso y utiliza los cursos, ejercicios y herramientas de PLD para avanzar.</p>${active.length?'<div class="rm-resume"><span>Continúa donde lo dejaste</span><a href="#/roadmaps/'+active[0].r.id+'">'+esc(active[0].r.title)+' · '+active[0].p.pct+'% →</a></div>':''}</header><section class="rm-section"><div class="rm-section__head"><div><h2>Elige tu objetivo</h2><p>Rutas organizadas por objetivo y nivel.</p></div><span>${ROUTES.length} rutas</span></div><div class="rm-grid">${ROUTES.map(card).join("")}</div></section><section class="rm-how"><h2>Cómo funcionan</h2><ol><li><strong>Elige un objetivo</strong><span>Selecciona una ruta adecuada a tu meta.</span></li><li><strong>Avanza por etapas</strong><span>Usa los recursos, ejercicios y evaluaciones de cada etapa.</span></li><li><strong>Marca tu progreso</strong><span>Guarda tus pasos completados y retoma cuando quieras.</span></li></ol><p class="rm-note">Versión inicial: el progreso se guarda en este navegador. La sincronización con cuenta se añadirá después.</p></section>`}
function detail(r){const p=stats(r);const nodes=r.nodes.map((n,i)=>{const done=p.done.has(n[0]),locked=i>0&&!p.done.has(r.nodes[i-1][0]);return `<article class="rm-node" data-state="${done?"done":locked?"locked":"current"}"><div class="rm-node__rail"><span class="rm-node__marker">${done?"✓":i+1}</span>${i<r.nodes.length-1?'<span class="rm-node__line"></span>':''}</div><div class="rm-node__body"><p class="rm-node__eyebrow">Etapa ${i+1} · ${done?"Completada":locked?"Bloqueada por prerrequisito":"Disponible"}</p><h3>${esc(n[1])}</h3><p>${esc(n[2])}</p><div class="rm-node__actions"><a class="btn btn--ghost" href="${esc(n[3])}">${esc(n[4])} ↗</a><button class="btn ${done?"btn--ghost":"btn--primary"}" data-rm-toggle="${esc(n[0])}" ${locked?"disabled":""}>${done?"Desmarcar":"Marcar completada"}</button></div></div></article>`}).join("");return `<header class="rm-detail-hero"><a class="rm-back" href="#/roadmaps">← Todas las rutas</a><p class="eyebrow">${esc(r.category)} · ${esc(r.level)}</p><h1 id="roadmaps-title" tabindex="-1">${esc(r.title)}</h1><p class="rm-lead">${esc(r.desc)}</p><div class="rm-detail-stats"><span>${p.done.size} de ${p.total} etapas completadas</span><strong>${p.pct}%</strong></div><div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${p.pct}"><span class="meter__fill" data-meter="${p.pct}"></span></div><div class="rm-tags">${r.skills.map(s=>'<span>'+esc(s)+'</span>').join("")}</div></header><section class="rm-timeline" aria-label="Etapas de la ruta">${nodes}</section><footer class="rm-detail-footer"><a class="btn btn--ghost" href="#/roadmaps">← Volver al catálogo</a><span>${p.next?"Siguiente: "+esc(p.next[0]):"Ruta completada. Buen trabajo."}</span></footer>`}
export function openRoadmaps(hash=location.hash){const root=document.querySelector("#roadmaps-view");if(!root)return;const id=hash.slice("#/roadmaps/".length).split(/[?&]/)[0];const r=ROUTES.find(x=>x.id===id);root.innerHTML=id&&r?detail(r):overview();root.querySelectorAll("[data-rm-toggle]").forEach(btn=>btn.addEventListener("click",()=>{const r=ROUTES.find(x=>x.id===id);if(!r)return;const set=new Set(progress[id]||[]);const nodeId=btn.dataset.rmToggle;if(set.has(nodeId)){const i=r.nodes.findIndex(n=>n[0]===nodeId);set.delete(nodeId);r.nodes.slice(i+1).forEach(n=>set.delete(n[0]))}else set.add(nodeId);progress[id]=[...set];try{localStorage.setItem(KEY,JSON.stringify(progress))}catch{}openRoadmaps(location.hash)}));document.title=(r?.title||"Roadmaps")+" · Python Learning Dashboard";root.querySelector("#roadmaps-title")?.focus({preventScroll:true})}
