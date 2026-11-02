/* Guarda la preparación del PCAP en la cuenta.
   Al iniciar sesión fusiona la copia de la cuenta con la local; después sube cada cambio.
   No sube nada hasta que esa fusión sale bien (sync-gate.js), para no pisar la copia de la cuenta. */

import { request } from "./api.js";
import { mergePcap, onPcapSave, pcap, savePcap } from "./pcap-store.js";
import { state, subscribe } from "./store.js";
import { createDocSync } from "./doc-sync.js";
import { createSyncGate } from "./sync-gate.js";

const DEBOUNCE_MS = 1500; // agrupa los cambios seguidos (p. ej. una tanda de práctica) en un envío
let timer = null;
let gate = null;

function mergeRemote(remote) {
  mergePcap(remote.data);
  savePcap();
}

// Sube con la versión leída: si otra pestaña guardó antes (409), relee, fusiona y reintenta
const doc = createDocSync({
  path: "/api/pcap-state",
  request,
  data: () => pcap,
  merge: mergeRemote,
  valid: () => gate?.ready === true,
});

async function push() {
  timer = null;
  if (!gate?.ready) return;
  try {
    await doc.push();
  } catch (error) {
    console.warn("No se pudo guardar la preparación en la cuenta:", error.message);
  }
}

/** Sube ya el cambio pendiente (antes de cerrar sesión). Si aún no se había fusionado, lo intenta. */
export async function flushPcapSync() {
  if (!state.user || !gate) return;
  if (!gate.ready) {
    await gate.sync(); // al salir bien, sube el documento fusionado
    return;
  }
  if (!timer) return;
  clearTimeout(timer);
  await push();
}

/** @param {() => void} onMerged se llama cuando llega la copia de la cuenta (para repintar) */
export function initPcapSync(onMerged) {
  gate = createSyncGate({
    name: "la preparación del PCAP",
    active: () => Boolean(state.user),
    load: () => request("GET", "/api/pcap-state"),
    merge: (remote) => {
      mergeRemote(remote);
      doc.adopt(remote);
    },
    onSynced: async () => {
      clearTimeout(timer);
      await push();
      onMerged();
    },
  });
  onPcapSave(() => {
    if (!state.user || !gate.ready) return;
    clearTimeout(timer);
    timer = setTimeout(push, DEBOUNCE_MS);
  });
  subscribe((change) => {
    if (change.type === "user") gate.restart();
  });
}
