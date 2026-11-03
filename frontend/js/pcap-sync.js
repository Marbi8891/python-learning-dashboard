/* Guarda la preparación del PCAP en la cuenta.
   Al iniciar sesión fusiona la copia de la cuenta con la local; después sube cada cambio.
   No sube nada hasta que esa fusión sale bien (sync-gate.js), para no pisar la copia de la cuenta.
   El estado de la subida y los reintentos están en uploader.js. */

import { request } from "./api.js";
import { mergePcap, onPcapSave, pcap, savePcap } from "./pcap-store.js";
import { state, subscribe } from "./store.js";
import { createDocSync } from "./doc-sync.js";
import { createSyncGate } from "./sync-gate.js";
import { createUploader } from "./uploader.js";

let gate = null;
let uploader = null;

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

/** Sube ya el cambio pendiente (antes de cerrar sesión). Devuelve si la cuenta lo tiene todo. */
export async function flushPcapSync() {
  if (!state.user || !uploader) return true;
  return uploader.flush();
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
    onSynced: () => {
      uploader.changed(); // sube el resultado de la fusión
      onMerged();
    },
  });
  uploader = createUploader({
    name: "pcap",
    label: "la preparación del PCAP",
    gate,
    push: () => doc.push(),
  });
  onPcapSave(() => {
    if (state.user) uploader.changed();
  });
  subscribe((change) => {
    if (change.type !== "user") return;
    if (state.user) uploader.sessionStarted();
    else uploader.sessionEnded();
    gate.restart();
  });
}
