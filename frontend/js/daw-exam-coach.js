/* DAW Exam Coach: personal study workspace for 2nd-year DAW.
   Local-first storage. No external AI/provider calls are made from this module. */
const KEY = "pld.dawExamCoach.v1";
const MODULES = [
 {id:"DWEC",name:"Desarrollo Web en Entorno Cliente",color:"blue",topics:["JavaScript moderno y tipos","Funciones, arrays y objetos","DOM y selección de elementos","Eventos y propagación","Formularios y validación","Web Storage","Fetch y APIs","Promesas y async/await","JSON y módulos ES","Testing y depuración"]},
 {id:"DWES",name:"Desarrollo Web en Entorno Servidor",color:"green",topics:["Arquitectura cliente-servidor","PHP y sintaxis","Formularios y validación","Sesiones y cookies","SQL y persistencia","MVC y rutas","APIs REST","Autenticación y autorización","Seguridad web","Testing backend"]},
 {id:"DIW",name:"Diseño de Interfaces Web",color:"purple",topics:["HTML semántico","CSS y selectores","Flexbox","CSS Grid","Responsive design","Accesibilidad WCAG","Usabilidad y UX","Formularios accesibles","Optimización","Prototipado y evaluación"]},
 {id:"DAW",name:"Despliegue de Aplicaciones Web",color:"orange",topics:["Linux y permisos","DNS y dominios","HTTP y HTTPS/TLS","Apache y Nginx","Configuración de servidores","Despliegue de aplicaciones","Docker y contenedores","CI/CD","Logs y monitorización","Copias de seguridad y seguridad"]}
];
const SOURCES=[
 ["rSainz21/DAW2","https://github.com/rSainz21/DAW2","Material de 2.º DAW · curso 2026–27"],
 ["DanielGodoyDAW/2-DAW-PUBLICO","https://github.com/DanielGodoyDAW/2-DAW-PUBLICO","Prácticas y ejercicios"],
 ["Mboza28/DAW_2","https://github.com/Mboza28/DAW_2","JavaScript, backend, bases de datos y Docker"],
 ["BertoMP/temario-daw","https://github.com/BertoMP/temario-daw","Temario general DAW"],
 ["jamj2000/DAW2-DAW-Apuntes","https://github.com/jamj2000/DAW2-DAW-Apuntes","Despliegue"],
 ["rosepac/daw-temario","https://github.com/rosepac/daw-temario","Material de consulta; revisar licencia"],
 ["statickidz/TemarioDAW","https://github.com/statickidz/TemarioDAW","Apuntes y ejercicios; revisar licencia"],
 ["ApuntesDAM.com","https://apuntesdam.com/","Ejercicios y simulacros"],
 ["fp-informatica/material-formativo","https://github.com/fp-informatica/material-formativo","Índice de recursos FP"]
];
const $ = (s,r=document)=>r.querySelector(s);
const esc = (s="")=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function load(){try{return JSON.parse(localStorage.getItem(KEY))||{mastery:{},sources:[],errors:[],sessions:[],tasks:[],minutes:90};}catch{return {mastery:{},sources:[],errors:[],sessions:[],tasks:[],minutes:90};}}
let data=load();
function save(){localStorage.setItem(KEY,JSON.stringify(data));}
function topicKey(m,t){return m+"::"+t;}
function score(m){const ts=MODULES.find(x=>x.id===m).topics;return Math.round(ts.reduce((a,t)=>a+(Number(data.mastery[topicKey(m,t)]||0)),0)/ts.length);}
function allScore(){return Math.round(MODULES.reduce((s,m)=>s+score(m),0)/MODULES.length);}
function dueErrors(){return data.errors.filter(e=>!e.done);}
function todayPlan(){
 const weak=MODULES.flatMap(m=>m.topics.map(t=>({module:m.id,topic:t,level:Number(data.mastery[topicKey(m.id,t)]||0)}))).sort((a,b)=>a.level-b.level).slice(0,3);
 const review=dueErrors().slice(0,2);
 return [...weak.map(x=>({type:"study",...x,reason:x.level===0?"Tema sin evaluar":"Dominio bajo"})),...review.map(e=>({type:"error",topic:e.topic,module:e.module,reason:"Repasar error pendiente"}))].slice(0,5);
}
function render(){
 const root=$("#daw-view"); if(!root)return;
 const plan=todayPlan();
 root.innerHTML=`
 <div class="dawcoach">
 <header class="dawcoach-head"><div><p class="dawcoach-eyebrow">TU ESPACIO DE ESTUDIO · 2.º DAW</p><h1 id="daw2-title" tabindex="-1">DAW Exam Coach</h1><p>Organiza el temario, estudia tus puntos débiles y practica para los exámenes.</p></div>
 <div class="dawcoach-score"><strong>${allScore()}%</strong><span>dominio estimado</span><div class="dawcoach-bar"><i style="width:${allScore()}%"></i></div></div></header>
 <section class="dawcoach-grid dawcoach-stats">
 ${MODULES.map(m=>`<article class="dawcoach-card"><div class="dawcoach-card-top"><span class="dawcoach-chip ${m.color}">${m.id}</span><strong>${score(m.id)}%</strong></div><h2>${esc(m.name)}</h2><div class="dawcoach-bar"><i style="width:${score(m.id)}%"></i></div><button class="dawcoach-link" data-module="${m.id}">Ver temas <span aria-hidden="true">→</span></button></article>`).join("")}
 </section>
 <section class="dawcoach-section"><div class="dawcoach-section-head"><div><h2>Plan de hoy</h2><p>Prioriza temas que aún no has evaluado o que tienes más flojos.</p></div><label>Tiempo disponible <select id="dawcoach-minutes"><option value="30" ${data.minutes==30?"selected":""}>30 min</option><option value="60" ${data.minutes==60?"selected":""}>1 hora</option><option value="90" ${data.minutes==90?"selected":""}>1 h 30 min</option><option value="120" ${data.minutes==120?"selected":""}>2 horas</option><option value="180" ${data.minutes==180?"selected":""}>3 horas</option></select></label></div>
 <ol class="dawcoach-plan">${plan.length?plan.map((p,i)=>`<li><span class="dawcoach-plan-num">${i+1}</span><div><strong>${esc(p.module)} · ${esc(p.topic)}</strong><small>${esc(p.reason)}</small></div><button data-plan-topic="${esc(p.module)}" data-plan-name="${esc(p.topic)}">Abrir</button></li>`).join(""):'<li class="dawcoach-empty">¡Todo revisado! Añade temas o errores para crear tu siguiente sesión.</li>'}</ol><button class="dawcoach-primary" id="start-session">Registrar sesión de estudio</button></section>
 <section class="dawcoach-section"><div class="dawcoach-section-head"><div><h2>Temario y dominio</h2><p>Marca el nivel que realmente tienes. El progreso se guarda en este dispositivo.</p></div></div><div class="dawcoach-modules" id="dawcoach-module-content"></div></section>
 <section class="dawcoach-section dawcoach-two"><div><h2>Biblioteca personal</h2><p>Importa materiales propios para tenerlos organizados. Los archivos se almacenan en este navegador.</p><form id="source-form"><label>Archivo <input type="file" id="source-file" accept=".txt,.md,.json,.html,.csv,.pdf" required></label><label>Módulo <select id="source-module"><option value="">Sin asignar</option>${MODULES.map(m=>`<option>${m.id}</option>`).join("")}</select></label><button class="dawcoach-primary" type="submit">Importar archivo</button></form><ul class="dawcoach-source-list">${data.sources.map((s,i)=>`<li><div><strong>${esc(s.name)}</strong><small>${esc(s.module||"Sin módulo")} · ${Math.round(s.size/1024*10)/10} KB</small></div><button data-delete-source="${i}" aria-label="Eliminar ${esc(s.name)}">Eliminar</button></li>`).join("")||'<li class="dawcoach-empty">Aún no has importado archivos.</li>'}</ul></div><div><h2>Fuentes de referencia</h2><p>Enlaces para consultar. Comprueba las licencias antes de reutilizar o redistribuir contenido.</p><ul class="dawcoach-source-list">${SOURCES.map(s=>`<li><div><strong>${esc(s[0])}</strong><small>${esc(s[2])}</small></div><a href="${esc(s[1])}" target="_blank" rel="noopener noreferrer">Abrir ↗</a></li>`).join("")}</ul></div></section>
 <section class="dawcoach-section dawcoach-two"><div><h2>Registro de errores</h2><form id="error-form"><label>Módulo <select id="error-module" required>${MODULES.map(m=>`<option>${m.id}</option>`).join("")}</select></label><label>Tema <input id="error-topic" placeholder="Tema o pregunta" required></label><label>¿Qué falló? <textarea id="error-note" rows="2" placeholder="Explica qué necesitas recordar"></textarea></label><button class="dawcoach-primary">Guardar error</button></form><ul class="dawcoach-error-list">${data.errors.map((e,i)=>`<li class="${e.done?"done":""}"><div><strong>${esc(e.module)} · ${esc(e.topic)}</strong><small>${esc(e.note||"Pendiente de revisar")}</small></div><button data-error-done="${i}">${e.done?"Reabrir":"Revisado"}</button><button data-error-delete="${i}" aria-label="Eliminar error">×</button></li>`).join("")||'<li class="dawcoach-empty">Todavía no hay errores registrados.</li>'}</ul></div><div><h2>Práctica rápida</h2><p>Elige un módulo para crear una sesión de repaso con preguntas que tú mismo puedas ampliar. La versión inicial genera tarjetas de autoevaluación, no respuestas inventadas.</p><div class="dawcoach-practice-buttons">${MODULES.map(m=>`<button data-quiz="${m.id}">Repasar ${m.id}</button>`).join("")}</div><div id="dawcoach-quiz" aria-live="polite"></div></div></section>
 <section class="dawcoach-section"><h2>Sesiones registradas</h2><p>El registro ayuda a medir constancia, no sustituye la evaluación de dominio.</p><div class="dawcoach-session-summary"><strong>${data.sessions.length}</strong> sesiones · <strong>${data.sessions.reduce((n,s)=>n+s.minutes,0)}</strong> minutos acumulados</div><ul>${data.sessions.slice(-5).reverse().map(s=>`<li>${new Date(s.date).toLocaleString("es-ES")} · ${s.minutes} min · ${esc(s.focus)}</li>`).join("")||"<li>No hay sesiones registradas.</li>"}</ul></section>
 <p class="dawcoach-footnote">Los materiales, progreso y errores se guardan localmente. No se envían a ningún servicio externo.</p></div>`;
 renderTopics();
 bind();
}
function renderTopics(){
 const box=$("#dawcoach-module-content"); if(!box)return;
 box.innerHTML=MODULES.map(m=>`<details class="dawcoach-topic-module" id="topics-${m.id}"><summary><span class="dawcoach-chip ${m.color}">${m.id}</span><strong>${esc(m.name)}</strong><span>${score(m.id)}%</span></summary><div class="dawcoach-topic-list">${m.topics.map(t=>{const v=Number(data.mastery[topicKey(m.id,t)]||0);return `<div class="dawcoach-topic"><span>${esc(t)}</span><div class="dawcoach-level" role="group" aria-label="Dominio de ${esc(t)}"><button data-level="${m.id}" data-topic="${esc(t)}" data-value="0" class="${v===0?"active":""}" title="Sin evaluar">—</button><button data-level="${m.id}" data-topic="${esc(t)}" data-value="1" class="${v===1?"active":""}" title="Lo estoy aprendiendo">1</button><button data-level="${m.id}" data-topic="${esc(t)}" data-value="2" class="${v===2?"active":""}" title="Lo entiendo">2</button><button data-level="${m.id}" data-topic="${esc(t)}" data-value="3" class="${v===3?"active":""}" title="Lo domino">3</button></div></div>`}).join("")}</div></details>`).join("");
}
function bind(){
 $("#dawcoach-minutes")?.addEventListener("change",e=>{data.minutes=Number(e.target.value);save();render();});
 document.querySelectorAll("[data-module]").forEach(b=>b.onclick=()=>{const d=$("#topics-"+b.dataset.module);d.open=true;d.scrollIntoView({behavior:"smooth",block:"start"});});
 document.querySelectorAll("[data-level]").forEach(b=>b.onclick=()=>{data.mastery[topicKey(b.dataset.level,b.dataset.topic)]=Number(b.dataset.value)*33.333;save();render();$("#topics-"+b.dataset.level).open=true;});
 document.querySelectorAll("[data-plan-topic]").forEach(b=>b.onclick=()=>{const mod=b.dataset.planTopic;$("#topics-"+mod).open=true;document.querySelectorAll("[data-topic]").forEach(x=>{if(x.dataset.topic===b.dataset.planName)x.scrollIntoView({behavior:"smooth",block:"center"});});});
 $("#start-session")?.addEventListener("click",()=>{const p=todayPlan();data.sessions.push({date:new Date().toISOString(),minutes:data.minutes,focus:p.map(x=>x.module+" "+x.topic).join("; ")||"Repaso libre"});save();render();});
 $("#source-form")?.addEventListener("submit",async e=>{e.preventDefault();const f=$("#source-file").files[0];if(!f)return;if(f.size>15*1024*1024){alert("El archivo supera el límite de 15 MB.");return;}const textTypes=["text/","application/json"];let textContent="";if(textTypes.some(t=>f.type.startsWith(t))||/\.(txt|md|json|csv|html)$/i.test(f.name)){textContent=await f.text();}data.sources.push({name:f.name,size:f.size,type:f.type,module:$("#source-module").value,added:new Date().toISOString(),text:textContent.slice(0,500000)});save();render();});
 $("#error-form")?.addEventListener("submit",e=>{e.preventDefault();data.errors.push({module:$("#error-module").value,topic:$("#error-topic").value.trim(),note:$("#error-note").value.trim(),done:false,date:new Date().toISOString()});save();render();});
 document.querySelectorAll("[data-delete-source]").forEach(b=>b.onclick=()=>{data.sources.splice(Number(b.dataset.deleteSource),1);save();render();});
 document.querySelectorAll("[data-error-done]").forEach(b=>b.onclick=()=>{data.errors[Number(b.dataset.errorDone)].done=!data.errors[Number(b.dataset.errorDone)].done;save();render();});
 document.querySelectorAll("[data-error-delete]").forEach(b=>b.onclick=()=>{data.errors.splice(Number(b.dataset.errorDelete),1);save();render();});
 document.querySelectorAll("[data-quiz]").forEach(b=>b.onclick=()=>createQuiz(b.dataset.quiz));
}
const FLASHCARDS={
 DWEC:[["¿Qué diferencia hay entre let y const?","let permite reasignar; const impide reasignar la referencia. En ambos casos el alcance es de bloque."],["¿Qué es el DOM?","La representación estructurada del documento HTML que JavaScript puede consultar y modificar."],["¿Para qué sirve addEventListener?","Registrar un manejador para un evento sin sobrescribir otros manejadores."],["¿Qué devuelve fetch()?","Una Promise que se resuelve con un objeto Response; hay que comprobar status y procesar el cuerpo."],["¿Qué hace async/await?","Permite escribir el manejo de Promises con una sintaxis secuencial; await pausa esa función async."]],
 DWES:[["¿Qué diferencia hay entre GET y POST?","GET solicita/consulta recursos y sus parámetros suelen ir en URL; POST envía datos en el cuerpo. No es una frontera de seguridad por sí sola."],["¿Qué es una sesión?","Estado asociado a un usuario que el servidor mantiene entre solicitudes, normalmente mediante un identificador en una cookie."],["¿Por qué validar en servidor?","El cliente puede manipularse; la validación del servidor es obligatoria para confiar en los datos."],["¿Qué es una API REST?","Una interfaz HTTP orientada a recursos que usa métodos, estados y representaciones de forma coherente."],["¿Qué es SQL injection?","Manipular una consulta mediante datos no confiables; se evita con consultas parametrizadas y validación adecuada."]],
 DIW:[["¿Para qué sirve HTML semántico?","Describe el significado y la estructura del contenido, mejorando accesibilidad y mantenimiento."],["¿Qué diferencia hay entre Flexbox y Grid?","Flexbox se orienta principalmente a una dimensión; Grid permite organizar filas y columnas a la vez."],["¿Qué significa responsive?","Adaptar la interfaz a diferentes tamaños, dispositivos y condiciones de visualización."],["¿Qué es contraste suficiente?","Una relación de luminancia entre texto y fondo que permita leerlo; WCAG define umbrales según el tamaño y nivel."],["¿Qué es una etiqueta label?","Relaciona una descripción con un control de formulario y mejora su nombre accesible."]],
 DAW:[["¿Qué hace DNS?","Traduce nombres de dominio a registros que permiten localizar servicios."],["¿Qué diferencia hay entre HTTP y HTTPS?","HTTPS cifra y autentica la conexión HTTP mediante TLS."],["¿Qué es un contenedor?","Un proceso aislado que comparte el kernel del host y empaqueta aplicación y dependencias."],["¿Qué son variables de entorno?","Configuración proporcionada al proceso; no deben usarse para exponer secretos en logs o repositorios."],["¿Qué debe contener un despliegue seguro?","Configuración reproducible, TLS, permisos mínimos, secretos protegidos, logs, backups y verificación."]]
};
function createQuiz(moduleId){
 const cards=FLASHCARDS[moduleId];let index=0;let reveal=false;const box=$("#dawcoach-quiz");
 const draw=()=>{const [q,a]=cards[index];box.innerHTML=`<article class="dawcoach-flashcard"><small>${moduleId} · tarjeta ${index+1}/${cards.length}</small><h3>${esc(q)}</h3>${reveal?`<p>${esc(a)}</p><div><button id="card-wrong">Repasar de nuevo</button><button id="card-right">La sabía</button></div>`:'<button id="card-reveal" class="dawcoach-primary">Mostrar respuesta</button>'}</article>`;$("#card-reveal")?.addEventListener("click",()=>{reveal=true;draw();});$("#card-wrong")?.addEventListener("click",()=>{data.errors.push({module:moduleId,topic:q,note:"Tarjeta de repaso",done:false,date:new Date().toISOString()});save();next();});$("#card-right")?.addEventListener("click",next);};
 const next=()=>{index++;reveal=false;if(index>=cards.length){box.innerHTML='<p class="dawcoach-success">Repaso completado. Los fallos se han añadido a tu registro.</p>';return;}draw();};draw();
}
export function openDawExamCoach(){render();}
export function renderDawExamCoach(){return '<div class="dawcoach"><p>Abriendo tu espacio de estudio…</p></div>';}
