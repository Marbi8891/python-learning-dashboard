import { AI_ACADEMY_COURSES, aiCourseLessons } from "./ai-academy-data.js";
const read=(key)=>{try{return JSON.parse(localStorage.getItem(key)||"{}")}catch{return{}}};
const courseState=(id)=>read(`pld:course:${id}`);
const getJson=async url=>{try{const r=await fetch(url);if(!r.ok)return null;return await r.json()}catch{return null}};
const lessonsIn=data=>(data?.modules||[]).flatMap(m=>m.lessons||[]);
const metric=(done,total,label)=>({done:Math.max(0,done),total:Math.max(0,total),label,percent:total?Math.round(done/total*100):0});
async function python(){
 const data=await getJson("data/learning.json"), concepts=data?.concepts||[];
 const state=read("pld:learn"), progress=state.concepts||{};
 const done=concepts.filter(c=>progress[c.id]&&(progress[c.id].read||progress[c.id].box>=2)).length;
 return metric(done,concepts.length,"conceptos");
}
async function daw(){
 const ids=["programacion","sql","entornos","marcas","js","java"],sets=await Promise.all(ids.map(id=>getJson(`data/courses/${id}/lessons.json`)));
 let done=0,total=0;
 ids.forEach((id,i)=>{const list=lessonsIn(sets[i]);total+=list.length;const saved=courseState(id).done||{};done+=list.filter(l=>saved[l.slug]).length});
 return metric(done,total,"lecciones DAW");
}
async function excel(){
 const data=await getJson("data/academia/excel/lessons.json"),list=lessonsIn(data),saved=courseState("excel").done||{};
 return metric(list.filter(l=>saved[l.slug]).length,list.length,"unidades Excel");
}
async function web(){
 const ids=["marcas","js"],sets=await Promise.all(ids.map(id=>getJson(`data/courses/${id}/lessons.json`)));
 let done=0,total=0;ids.forEach((id,i)=>{const list=lessonsIn(sets[i]);total+=list.length;const saved=courseState(id).done||{};done+=list.filter(l=>saved[l.slug]).length});
 return metric(done,total,"lecciones web");
}
async function cyber(){
 const course=await getJson("data/cybersecurity/course.json"),state=read("pld:cybersecurity:v1"),weeks=course?.weeks||[];
 const done=weeks.filter(w=>state.weeks?.[w.id]?.done||state.completed?.includes(w.id)).length;
 return metric(done,weeks.length,"semanas");
}
function ai(){
 const saved=read("pld:ai-academy:progress");let done=0,total=0;
 for(const course of AI_ACADEMY_COURSES){const lessons=aiCourseLessons(course);total+=lessons.length;done+=(saved[course.id]||[]).length}
 return metric(done,total,"temas IA");
}
export async function pathProgress(id){
 try{switch(id){case"python-developer":return await python();case"daw-developer":return await daw();case"web-developer":return await web();case"cybersecurity":return await cyber();case"ai-engineer":return ai();case"excel-professional":return await excel();default:return null}}catch{return null}
}
