/* Local NEXARO bridge. Messages are sent only on explicit user submission. */
const DEFAULT_URL="http://127.0.0.1:8001";
const LOGIN_URL=DEFAULT_URL+"/#/login";
const q=(s,r=document)=>r.querySelector(s);
export function initLocalAI(){
 if(document.getElementById("pld-local-ai"))return;
 const root=document.createElement("div");root.id="pld-local-ai";
 root.innerHTML=`<button class="pld-ai-launch" id="pld-ai-launch" aria-expanded="false" aria-controls="pld-ai-panel">✦ NEXARO AI</button>
 <section class="pld-ai-panel" id="pld-ai-panel" hidden aria-label="NEXARO AI local">
 <header><div><b>NEXARO AI</b><small id="pld-ai-status">Desconectado</small></div><div><a href="${LOGIN_URL}" target="_blank" rel="noopener">Login ↗</a><button id="pld-ai-close" aria-label="Cerrar">×</button></div></header>
 <div class="pld-ai-connection"><label for="pld-ai-url">Servidor local</label><input id="pld-ai-url" type="url" value="${DEFAULT_URL}"><button id="pld-ai-connect">Conectar</button></div>
 <ol id="pld-ai-messages" aria-live="polite"><li class="bot">Conecta con tu IA local. Solo se envía lo que escribas al pulsar Enviar.</li></ol>
 <form id="pld-ai-form"><textarea id="pld-ai-input" rows="3" placeholder="Pregunta sobre Python, tu código o una lección…" required></textarea><div class="pld-ai-actions"><label><input id="pld-ai-context" type="checkbox"> Añadir contexto de la lección</label><button type="submit">Enviar</button></div></form></section>`;
 document.body.append(root);
 const panel=q("#pld-ai-panel",root),launch=q("#pld-ai-launch",root),status=q("#pld-ai-status",root),messages=q("#pld-ai-messages",root),input=q("#pld-ai-input",root);
 let base=DEFAULT_URL,connected=false;
 const show=v=>{panel.hidden=!v;launch.setAttribute("aria-expanded",String(v));if(v)input.focus()};
 launch.onclick=()=>show(panel.hidden);q("#pld-ai-close",root).onclick=()=>show(false);
 const say=(text,kind="bot")=>{const li=document.createElement("li");li.className=kind;li.textContent=String(text);messages.append(li);messages.scrollTop=messages.scrollHeight};
 const state=(text,ok=false)=>{status.textContent=text;status.dataset.connected=ok?"true":"false"};
 async function connect(){
  base=q("#pld-ai-url",root).value.trim().replace(/\/$/,"");
  if(!/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(base)){connected=false;state("URL local no válida");return}
  state("Comprobando…");
  for(const path of ["/api/health","/health"]){try{const r=await fetch(base+path,{credentials:"include",signal:AbortSignal.timeout(5000)});if(r.ok){connected=true;state("Conectado",true);say("Conectado a "+base);return}}catch{}}
  connected=false;state("No disponible");say("No se conecta. Comprueba que NEXARO esté activo y permita CORS desde GitHub Pages.","system");
 }
 q("#pld-ai-connect",root).onclick=connect;q("#pld-ai-url",root).onchange=()=>{connected=false;state("Pendiente")};
 q("#pld-ai-form",root).onsubmit=async e=>{
  e.preventDefault();const text=input.value.trim();if(!text)return;if(!connected){say("Conecta primero con NEXARO.","system");return}
  input.value="";say(text,"user");const send=q("button[type=submit]",e.currentTarget);send.disabled=true;send.textContent="Enviando…";
  const body={message:text,prompt:text,source:"python-learning-dashboard"};
  if(q("#pld-ai-context",root).checked)body.context={app:"Python Learning Dashboard",url:location.href,lesson:q("#lesson-title")?.textContent?.trim()||null,topic:q("#lesson-crumb")?.textContent?.trim()||null};
  let answer=null,err=null;
  for(const path of ["/api/chat","/chat"]){try{const r=await fetch(base+path,{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify(body),signal:AbortSignal.timeout(60000)});if(r.status===404||r.status===405)continue;const d=await r.json();if(!r.ok)throw Error(d.detail||d.message||"HTTP "+r.status);answer=d.response??d.answer??d.message??d.content??d.output??d.text??JSON.stringify(d);break}catch(ex){err=ex}}
  say(answer??("Error al enviar: "+(err?.message||"API de chat no encontrada. Revisa la ruta y autenticación de NEXARO.")),answer?"bot":"system");send.disabled=false;send.textContent="Enviar";input.focus();
 };
}