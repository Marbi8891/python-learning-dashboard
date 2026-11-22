/* Modo demostración: funciones puras (sin DOM, red ni almacenamiento real), probadas con node --test.

   Los datos de Alex Developer (data/demo/alex.json, generado por scripts/demo/build_demo.py) llevan
   fechas absolutas alrededor de un día de referencia (`anchor`). Al entrar en la demo se desplazan
   todas para que `anchor` sea hoy: la forma es siempre la misma (racha, historial, repasos que tocan),
   así que la demo es reproducible y nunca sale caducada. */

/** Prefijo de todas las claves de la demo en sessionStorage. Nunca coincide con «pld:». */
export const DEMO_PREFIX = "pld:demo:";
/** Marca de que esta pestaña está en modo demo. */
export const DEMO_FLAG = `${DEMO_PREFIX}active`;

const DAY = /^(\d{4})-(\d{2})-(\d{2})$/;
const DATE_TIME = /^(\d{4})-(\d{2})-(\d{2})T/;

/** Día local en formato AAAA-MM-DD. */
export const localDay = (date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

/** Días de calendario entre dos días «AAAA-MM-DD» (b - a). */
export function daysBetween(a, b) {
  const [ya, ma, da] = a.split("-").map(Number);
  const [yb, mb, db] = b.split("-").map(Number);
  return Math.round((Date.UTC(yb, mb - 1, db) - Date.UTC(ya, ma - 1, da)) / 86_400_000);
}

function shiftDay(day, days) {
  const [y, m, d] = day.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d + days)).toISOString().slice(0, 10);
}

/** Desplaza `days` días una fecha «AAAA-MM-DD» o ISO con hora; cualquier otro texto queda igual. */
export function shiftText(text, days) {
  if (DAY.test(text)) return shiftDay(text, days);
  if (DATE_TIME.test(text)) {
    const time = Date.parse(text);
    if (Number.isNaN(time)) return text;
    return new Date(time + days * 86_400_000).toISOString();
  }
  return text;
}

/** Copia de `value` con todas las fechas (valores y claves de objeto) desplazadas `days` días. */
export function shiftDates(value, days) {
  if (typeof value === "string") return shiftText(value, days);
  if (Array.isArray(value)) return value.map((item) => shiftDates(item, days));
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [DAY.test(key) ? shiftDay(key, days) : key, shiftDates(item, days)]));
  }
  return value;
}

/**
 * Claves y valores que hay que guardar para sembrar la demo, con las fechas ya llevadas a hoy.
 * @param {{ anchor: string, storage: Record<string, unknown> }} fixture  @param {Date} now
 * @returns {[string, string][]} pares [clave sin prefijo, JSON]
 */
export function seedEntries(fixture, now = new Date()) {
  if (!fixture || typeof fixture.anchor !== "string" || !DAY.test(fixture.anchor) || !fixture.storage) {
    throw new Error("Los datos de la demo no tienen el formato esperado");
  }
  const days = daysBetween(fixture.anchor, localDay(now));
  return Object.entries(fixture.storage).map(([key, value]) => [key, JSON.stringify(shiftDates(value, days))]);
}

/** Perfil y actividad de Alex con las fechas llevadas a hoy. */
export function demoProfile(fixture, now = new Date()) {
  const days = daysBetween(fixture.anchor, localDay(now));
  return shiftDates({ profile: fixture.profile, feed: fixture.feed }, days);
}

/**
 * Almacén con la misma interfaz que localStorage, sobre otro almacén y con un prefijo.
 * En la demo va sobre sessionStorage: lo de la demo nunca se mezcla con el progreso real (pld:*).
 */
export class PrefixedStorage {
  constructor(backing, prefix) {
    this.backing = backing;
    this.prefix = prefix;
  }

  getItem(key) {
    return this.backing.getItem(this.prefix + key);
  }

  setItem(key, value) {
    this.backing.setItem(this.prefix + key, String(value));
  }

  removeItem(key) {
    this.backing.removeItem(this.prefix + key);
  }

  /** Claves propias, sin el prefijo (como Object.keys(localStorage)). */
  keys() {
    const keys = [];
    for (let i = 0; i < this.backing.length; i += 1) {
      const key = this.backing.key(i);
      if (key?.startsWith(this.prefix)) keys.push(key.slice(this.prefix.length));
    }
    return keys;
  }

  get length() {
    return this.keys().length;
  }

  key(index) {
    return this.keys()[index] ?? null;
  }

  /** Borra todas las claves con el prefijo. */
  clear() {
    for (const key of this.keys()) this.removeItem(key);
  }
}

/** Claves de un almacén (localStorage o PrefixedStorage). */
export const storageKeys = (storage) => (typeof storage.keys === "function" ? storage.keys() : Object.keys(storage));

/**
 * Respuesta de /api/v1/dashboard construida en el navegador para la demo, con la misma forma que la
 * del servidor (DashboardOut en backend/app/schemas.py). Las lecciones salen del progreso de la
 * pestaña; los intentos, de la actividad ficticia de Alex.
 * @param {{ profile: object, feed: object[], completed: Set<string>, modules: object[], now?: Date }} input
 */
export function demoDashboard({ profile, feed = [], completed, modules = [], now = new Date() }) {
  const all = modules.flatMap((m) => m.lessons.map((l) => ({ slug: l.slug, title: l.title })));
  const attempts = feed.filter((item) => item.kind === "attempt");
  const latest = (items) => items.map((item) => item.at).sort().at(-1) ?? null;
  const next = all.find((l) => !completed.has(l.slug)) ?? null;
  const daily = new Map();
  for (const item of feed) {
    const key = localDay(new Date(item.at));
    const row = daily.get(key) ?? { day: key, lessons_completed: 0, attempts: 0, passed: 0 };
    if (item.kind === "lesson_completed") row.lessons_completed += 1;
    else {
      row.attempts += 1;
      if (item.passed) row.passed += 1;
    }
    daily.set(key, row);
  }
  return {
    user: { display_name: profile.display_name, email: "", created_at: profile.created_at, sign_in_method: null },
    lessons: {
      total: all.length,
      completed: all.filter((l) => completed.has(l.slug)).length,
      last_completed_at: latest(feed.filter((item) => item.kind === "lesson_completed")),
      next_lesson: next,
      modules: modules.map((m) => ({ slug: m.slug, title: m.title, total: m.lessons.length, completed: m.lessons.filter((l) => completed.has(l.slug)).length })),
    },
    exercises: {
      attempts: attempts.length,
      passed: attempts.filter((item) => item.passed).length,
      lessons_tried: new Set(attempts.map((item) => item.lesson_slug)).size,
      lessons_passed: new Set(attempts.filter((item) => item.passed).map((item) => item.lesson_slug)).size,
      last_attempt_at: latest(attempts),
    },
    daily: [...daily.values()].sort((a, b) => (a.day < b.day ? -1 : 1)),
    synced: [],
    generated_at: now.toISOString(),
  };
}
