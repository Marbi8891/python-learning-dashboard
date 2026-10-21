/* Copia de seguridad del progreso en un archivo JSON (exportar e importar sin cuenta).
   Funciones puras (sin DOM ni localStorage): las usa progress-transfer.js y se prueban con node --test.

   Archivo (versión 1):
   {
     format: "pld-progress", version: 1, exportedAt: ISO,
     data: {
       completed: [slug…],              lecciones del curso PCAP completadas (pld:completed)
       learn:   { … },                  núcleo educativo por conceptos (pld:learn, mastery.js)
       pcap:    { … },                  zona de examen PCAP (pld:pcap)
       game:    { … },                  XP, racha y logros (pld:game, game-data.js)
       courses: { [id]: { … } }         cursos de DAW (pld:course:<id>)
     }
   }

   Lo importado solo se lee con JSON.parse y pasa por los mismos limpiadores que los datos de
   localStorage y de la cuenta (ADR-0022): nunca se ejecuta ni se pinta sin validar. */

import { cleanGame } from "./game-data.js";
import { cleanLearning } from "./learn/mastery.js";
import { cleanProgress } from "./progress-guard.js";

export const FORMAT = "pld-progress";
export const VERSION = 1;
/** Un progreso real ocupa decenas de KB; 2 MB deja margen sin aceptar archivos absurdos. */
export const MAX_BYTES = 2_000_000;

const ID = /^[a-z0-9][a-z0-9_-]{0,60}$/;
const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);

/** Error con un mensaje pensado para el alumno. */
export class ProgressFileError extends Error {}

/** Arma el archivo con lo que hay en este navegador. */
export function buildProgressFile({ completed = [], learn, pcap, game, courses = {} }, now = new Date()) {
  return {
    format: FORMAT,
    version: VERSION,
    exportedAt: now.toISOString(),
    data: { completed: [...completed], learn, pcap, game, courses },
  };
}

/**
 * Lee y valida un archivo de progreso. Devuelve solo las partes presentes, ya limpias:
 * { completed?, learn?, pcap?, game?, courses? }. Lanza ProgressFileError si no es válido.
 * @param {string} text contenido del archivo
 * @param {string[]} courseIds ids de los cursos de DAW que conoce la web
 */
export function parseProgressFile(text, courseIds = []) {
  if (typeof text !== "string" || !text.trim()) throw new ProgressFileError("El archivo está vacío.");
  if (text.length > MAX_BYTES) throw new ProgressFileError("El archivo es demasiado grande para ser una copia del progreso (máximo 2 MB).");
  let file;
  try {
    file = JSON.parse(text);
  } catch {
    throw new ProgressFileError("El archivo no es un JSON válido.");
  }
  if (!isObject(file) || file.format !== FORMAT) {
    throw new ProgressFileError("Este archivo no es una copia del progreso de Python Learning Dashboard.");
  }
  if (!Number.isInteger(file.version) || file.version < 1) throw new ProgressFileError("La versión del archivo no es válida.");
  if (file.version > VERSION) {
    throw new ProgressFileError("El archivo se creó con una versión más nueva de la web. Recarga la página e inténtalo otra vez.");
  }
  const data = isObject(file.data) ? file.data : {};
  const parts = {};
  if (Array.isArray(data.completed)) parts.completed = [...new Set(data.completed.filter((slug) => typeof slug === "string" && ID.test(slug)))];
  if (isObject(data.learn)) parts.learn = cleanLearning(data.learn);
  if (isObject(data.pcap)) parts.pcap = cleanProgress(data.pcap);
  if (isObject(data.game)) parts.game = cleanGame(data.game);
  if (isObject(data.courses)) {
    const courses = {};
    for (const id of courseIds) if (isObject(data.courses[id])) courses[id] = cleanProgress(data.courses[id]);
    if (Object.keys(courses).length) parts.courses = courses;
  }
  if (!Object.keys(parts).length) throw new ProgressFileError("El archivo no contiene progreso que se pueda importar.");
  return parts;
}

/** Resumen legible de lo que trae un archivo ya validado (para el mensaje final). */
export function describeParts(parts) {
  const items = [];
  if (parts.completed?.length) items.push(`${parts.completed.length} lecciones completadas`);
  if (parts.learn) items.push(`${Object.keys(parts.learn.ex).length} ejercicios del núcleo educativo`);
  if (parts.pcap) items.push(`${Object.keys(parts.pcap.answers ?? {}).length} preguntas del PCAP`);
  if (parts.courses) items.push(`${Object.keys(parts.courses).length} cursos de DAW`);
  if (parts.game) items.push("logros y racha");
  return items.join(", ");
}
