/* Objetivo económico del itinerario profesional (DEC-012, D3). Funciones puras: no tocan el DOM ni el
   almacenamiento, así que se prueban con node --test.

   Estos datos NO se suben a la cuenta: solo viven en el navegador (FINANCE_KEY) y se pueden exportar
   e importar en JSON. Cerrar sesión no los borra (LOCAL_ONLY_KEYS de local-owner.js, DEC-012 opción C)
   y, si entra otra cuenta en el mismo navegador, se apartan para su dueño como el resto del progreso.

   Conceptos que no se mezclan nunca:
   - salary:   salario BRUTO anual por cuenta ajena;
   - revenue:  FACTURACIÓN anual de la actividad propia (sin IVA);
   - expenses: GASTOS anuales del negocio (incluida la cuota de autónomo, si la hay);
   - profit  = revenue − expenses: BENEFICIO antes de impuestos (puede ser negativo);
   - combined = salary + profit: ingreso combinado antes de impuestos. Nunca salary + revenue.
   No se calcula el IRPF: depende de la situación personal y sería inventar.

   Documento: { v: 1, targets: { combined, salary, at } | null, years: { "AAAA": { salary, revenue, expenses, at } } } */

export const FORMAT = "pld-career-finance";
export const FINANCE_KEY = "pld:career-finance";
export const MAX_AMOUNT = 10_000_000;
export const MAX_YEARS = 40;
const YEAR = /^20\d{2}$/;
const ISO = /^\d{4}-\d{2}-\d{2}T[\d:.+-]+Z?$/;
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const isIso = (value) => typeof value === "string" && ISO.test(value);
const later = (a, b) => ((a?.at ?? "") >= (b?.at ?? "") ? a : b);

/** Importe válido en euros (entero de 0 a MAX_AMOUNT) o null si no lo es. */
export const amount = (value) => (Number.isInteger(value) && value >= 0 && value <= MAX_AMOUNT ? value : null);

export const emptyFinance = () => ({ v: 1, targets: null, years: {} });

function cleanYear(raw) {
  if (!isObject(raw) || !isIso(raw.at)) return null;
  const year = { salary: amount(raw.salary) ?? 0, revenue: amount(raw.revenue) ?? 0, expenses: amount(raw.expenses) ?? 0, at: raw.at };
  return year;
}

export function cleanFinance(value) {
  const doc = emptyFinance();
  if (!isObject(value)) return doc;
  if (isObject(value.targets) && isIso(value.targets.at)) {
    doc.targets = { combined: amount(value.targets.combined), salary: amount(value.targets.salary), at: value.targets.at };
  }
  if (isObject(value.years)) {
    for (const [year, raw] of Object.entries(value.years).slice(0, MAX_YEARS)) {
      const clean = YEAR.test(year) ? cleanYear(raw) : null;
      if (clean) doc.years[year] = clean;
    }
  }
  return doc;
}

/** Objetivo combinado y salario bruto objetivo (null = sin objetivo). */
export function setTargets(doc, { combined = null, salary = null }, now = new Date()) {
  doc.targets = { combined: amount(combined), salary: amount(salary), at: now.toISOString() };
}

/** Datos reales o previstos de un año. Devuelve false si el año o algún importe no es válido. */
export function setYear(doc, year, { salary = 0, revenue = 0, expenses = 0 }, now = new Date()) {
  const key = String(year);
  const values = [salary, revenue, expenses].map(amount);
  if (!YEAR.test(key) || values.includes(null)) return false;
  if (!doc.years[key] && Object.keys(doc.years).length >= MAX_YEARS) return false;
  doc.years[key] = { salary: values[0], revenue: values[1], expenses: values[2], at: now.toISOString() };
  return true;
}

/** Quita un año. Son datos solo de este navegador: no hace falta marcarlo como borrado para otra copia. */
export function removeYear(doc, year) {
  delete doc.years[String(year)];
}

/** Evolución anual, del año más antiguo al más reciente, con la distancia al objetivo combinado. */
export function projection(doc) {
  const target = doc.targets?.combined ?? null;
  let previous = null;
  return Object.keys(doc.years)
    .sort()
    .map((year) => {
      const { salary, revenue, expenses } = doc.years[year];
      const profit = revenue - expenses;
      const combined = salary + profit;
      const row = {
        year: Number(year),
        salary,
        revenue,
        expenses,
        profit,
        combined,
        gap: target === null ? null : target - combined,
        reached: target !== null && combined >= target,
        growth: previous === null || previous === 0 ? null : (combined - previous) / Math.abs(previous),
      };
      previous = combined;
      return row;
    });
}

/** Fusiona sin borrar nada: por año y para los objetivos gana lo cambiado más tarde. */
export function mergeFinance(local, remote) {
  const other = cleanFinance(remote);
  if (other.targets) local.targets = local.targets ? later(local.targets, other.targets) : other.targets;
  for (const [year, data] of Object.entries(other.years)) {
    if (local.years[year]) local.years[year] = later(local.years[year], data);
    else if (Object.keys(local.years).length < MAX_YEARS) local.years[year] = data;
  }
  return local;
}

/** Texto JSON para descargar (copia de seguridad o cambio de navegador). */
export const exportFinance = (doc, now = new Date()) => JSON.stringify({ format: FORMAT, v: 1, exportedAt: now.toISOString(), data: cleanFinance(doc) }, null, 1);

/**
 * Importa una exportación fusionándola con lo que hay (no borra nada).
 * @returns {{ok: true, years: number} | {ok: false, error: string}}
 */
export function importFinance(doc, text) {
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    return { ok: false, error: "El archivo no es JSON válido." };
  }
  if (!isObject(parsed) || parsed.format !== FORMAT || parsed.v !== 1 || !isObject(parsed.data)) {
    return { ok: false, error: "El archivo no es una exportación de datos económicos de PLD." };
  }
  const clean = cleanFinance(parsed.data);
  mergeFinance(doc, clean);
  return { ok: true, years: Object.keys(clean.years).length };
}
