// Utilidades de los tests unitarios: el contenido real (learning.json) y un generador aleatorio fijo.
import { readFileSync } from "node:fs";
import { buildIndex, emptyLearning } from "../../frontend/js/learn/mastery.js";

export const data = JSON.parse(readFileSync(new URL("../../frontend/data/learning.json", import.meta.url), "utf8"));
export const index = buildIndex(data);
export const fresh = () => emptyLearning();
export const NOW = new Date("2026-10-04T10:00:00");
export const daysAgo = (n) => new Date(NOW.getTime() - n * 86_400_000);

/** Generador pseudoaleatorio con semilla (resultados reproducibles). */
export function seeded(seed = 1) {
  let value = seed;
  return () => {
    value = (value * 1103515245 + 12345) % 2 ** 31;
    return value / 2 ** 31;
  };
}

export const exercisesOf = (concept) => index.byConcept.get(concept);
