/* Programming Path practice catalog + persisted evidence helpers.
   Activities are content; completion and evidence live in the existing career roadmap document. */
function safeHttpsUrl(value) {\n  if (typeof value !== "string" || !value.trim() || value.length > 240) return null;\n  try {\n    const url = new URL(value.trim());\n    if (url.protocol !== "https:" || url.username || url.password || !url.hostname.includes(".")) return null;\n    return url.href.length <= 240 ? url.href : null;\n  } catch { return null; }\n}

const ID = /^[a-z0-9][a-z0-9.-]{0,60}$/;
const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

export function cleanPracticeEntry(raw) {
  if (!isObject(raw) || typeof raw.done !== "boolean" || typeof raw.at !== "string" || !ISO.test(raw.at)) return null;
  const url = safeHttpsUrl(raw.url);
  const note = typeof raw.note === "string" ? raw.note.replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, 1000) : "";
  return { done: raw.done, url, note, at: raw.at };
}

export function cleanPracticeMap(raw) {
  const out = {};
  if (!isObject(raw)) return out;
  for (const [id, value] of Object.entries(raw)) if (ID.test(id)) {
    const entry = cleanPracticeEntry(value);
    if (entry) out[id] = entry;
  }
  return out;
}

export function setPractice(progress, id, { done = false, url = "", note = "" } = {}, now = new Date()) {
  if (!ID.test(id)) return false;
  const entry = cleanPracticeEntry({ done: Boolean(done), url, note, at: now.toISOString() });
  if (!entry) return false;
  progress.practice ??= {};
  progress.practice[id] = entry;
  return true;
}

export function mergePractice(local, remote) {
  const clean = cleanPracticeMap(remote);
  for (const [id, entry] of Object.entries(clean)) {
    if (!local[id] || entry.at > local[id].at) local[id] = entry;
  }
  return local;
}

export function practiceStats(activities = [], progress = {}) {
  const total = activities.length;
  const done = activities.filter((a) => progress[a.id]?.done).length;
  return { total, done, remaining: total - done, ratio: total ? done / total : 0 };
}
