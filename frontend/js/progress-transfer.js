/* Exportar e importar el progreso de este navegador («Mi aprendizaje»).
   Sirve para cambiar de navegador o de equipo sin cuenta, o para guardar una copia.
   Importar FUSIONA con lo que ya hay (las mismas reglas que al sincronizar con la cuenta):
   nunca borra progreso. El formato y la validación están en progress-file.js. */

import { DAW_COURSES, courseState, flushCourseSync, mergeCourse, saveCourse } from "./course-store.js";
import { flushGameSync, game, refreshGame } from "./game.js";
import { mergeGame } from "./game-data.js";
import { flushLearnSync, learning, saveLearning } from "./learn/learn-store.js";
import { mergeLearning } from "./learn/mastery.js";
import { flushPcapSync } from "./pcap-sync.js";
import { mergePcap, pcap, savePcap } from "./pcap-store.js";
import { MAX_BYTES, ProgressFileError, buildProgressFile, describeParts, parseProgressFile } from "./progress-file.js";
import { setCompleted, state } from "./store.js";

const FLASH_KEY = "pld:flash"; // el mismo aviso tras recargar que usa account.js
const COURSE_IDS = DAW_COURSES.map((c) => c.id);

function download(data, filename) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
  Object.assign(document.createElement("a"), { href: url, download: filename }).click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function exportProgress(now = new Date()) {
  const courses = Object.fromEntries(COURSE_IDS.map((id) => [id, courseState(id)]));
  const file = buildProgressFile({ completed: state.completed, learn: learning, pcap, game, courses }, now);
  download(file, `progreso-python-learning-${now.toISOString().slice(0, 10)}.json`);
}

/** Fusiona un archivo ya validado con el progreso local (y la cuenta, si hay sesión). */
async function applyParts(parts) {
  if (parts.learn) {
    mergeLearning(learning, parts.learn);
    saveLearning();
  }
  if (parts.pcap) {
    mergePcap(parts.pcap);
    savePcap();
  }
  for (const [id, data] of Object.entries(parts.courses ?? {})) {
    mergeCourse(id, data);
    saveCourse(id);
  }
  for (const slug of parts.completed ?? []) if (!state.completed.has(slug)) await setCompleted(slug, true);
  if (parts.game) mergeGame(game, parts.game);
  refreshGame(); // recalcula logros con todo lo importado y guarda
  // Con sesión, que la cuenta reciba ya los cambios antes de recargar
  await Promise.allSettled([flushLearnSync(), flushPcapSync(), flushCourseSync(), flushGameSync()]);
}

async function importProgress(input, message) {
  const file = input.files?.[0];
  input.value = ""; // permite volver a elegir el mismo archivo
  if (!file) return;
  try {
    if (file.size > MAX_BYTES) throw new ProgressFileError("El archivo es demasiado grande para ser una copia del progreso (máximo 2 MB).");
    const parts = parseProgressFile(await file.text(), COURSE_IDS);
    message.dataset.ok = "true";
    message.textContent = "Importando…";
    await applyParts(parts);
    try {
      sessionStorage.setItem(FLASH_KEY, `Progreso importado y fusionado con el de este navegador: ${describeParts(parts)}.`);
    } catch {
      // sin almacenamiento: se recarga igualmente
    }
    location.reload(); // todas las vistas leen el progreso nuevo
  } catch (error) {
    delete message.dataset.ok;
    message.textContent = error instanceof ProgressFileError ? error.message : `No se pudo importar: ${error.message}`;
  }
}

export function initProgressTransfer() {
  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-progress-export]")) exportProgress();
  });
  document.addEventListener("change", (event) => {
    if (event.target.id === "progress-import") importProgress(event.target, document.querySelector("#progress-import-message"));
  });
}
