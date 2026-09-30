/* Limpieza del progreso que llega de fuera: localStorage (lo puede tocar cualquiera con acceso al
   navegador) o la copia de la cuenta. Deja solo los tipos esperados para que ningún dato
   manipulado acabe convertido en HTML (ADR-0022). */

const DAY = /^\d{4}-\d{2}-\d{2}$/;
const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const isNumber = (value) => typeof value === "number" && Number.isFinite(value);
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);

function answers(value) {
  const clean = {};
  if (!isObject(value)) return clean;
  for (const [id, history] of Object.entries(value)) {
    if (Array.isArray(history)) clean[id] = history.filter((ok) => typeof ok === "boolean");
  }
  return clean;
}

function exams(value) {
  if (!Array.isArray(value)) return [];
  return value.filter(
    (exam) =>
      isObject(exam) &&
      typeof exam.date === "string" &&
      ISO.test(exam.date) &&
      ["correct", "total", "score", "seconds"].every((field) => isNumber(exam[field])),
  );
}

function srs(value) {
  const clean = {};
  if (!isObject(value)) return clean;
  for (const [id, item] of Object.entries(value)) {
    if (isObject(item) && isNumber(item.box) && DAY.test(item.due ?? "")) clean[id] = item;
  }
  return clean;
}

/** Devuelve una copia con los campos conocidos validados; los demás se conservan tal cual. */
export function cleanProgress(value) {
  if (!isObject(value)) return {};
  const clean = { ...value };
  if ("answers" in value) clean.answers = answers(value.answers);
  if ("exams" in value) clean.exams = exams(value.exams);
  if ("srs" in value) clean.srs = srs(value.srs);
  if ("known" in value) clean.known = Array.isArray(value.known) ? value.known.filter((id) => typeof id === "string") : [];
  if ("bestCombo" in value) clean.bestCombo = isNumber(value.bestCombo) ? value.bestCombo : 0;
  if ("lang" in value) clean.lang = value.lang === "en" ? "en" : "es";
  if ("flags" in value) clean.flags = isObject(value.flags) ? value.flags : {};
  if ("plan" in value) {
    const date = value.plan?.examDate;
    const goal = value.plan?.dailyGoal;
    clean.plan = { examDate: typeof date === "string" && DAY.test(date) ? date : null };
    // Meta diaria de «Mi cuenta» (ADR-0025): solo en el plan del PCAP, que comparten todos los cursos
    if (Number.isInteger(goal) && goal >= 1 && goal <= 200) clean.plan.dailyGoal = goal;
  }
  return clean;
}
