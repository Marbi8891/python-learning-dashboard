/* Guarda la preparación del PCAP en la cuenta (ADR-0010).
   Al iniciar sesión fusiona la copia de la cuenta con la local; después sube cada cambio. */

import { request } from "./api.js";
import { mergePcap, onPcapSave, pcap, savePcap } from "./pcap-store.js";
import { state, subscribe } from "./store.js";

const DEBOUNCE_MS = 1500; // agrupa los cambios seguidos (p. ej. una tanda de práctica) en un envío
let timer = null;
let merging = false;

async function push() {
  try {
    await request("PUT", "/api/pcap-state", { json: { data: pcap } });
  } catch (error) {
    console.warn("No se pudo guardar la preparación en la cuenta:", error.message);
  }
}

/** @param {() => void} onMerged se llama cuando llega la copia de la cuenta (para repintar) */
export function initPcapSync(onMerged) {
  onPcapSave(() => {
    if (!state.user || merging) return;
    clearTimeout(timer);
    timer = setTimeout(push, DEBOUNCE_MS);
  });
  subscribe(async (change) => {
    if (change.type !== "user" || !state.user) return;
    merging = true;
    try {
      const remote = await request("GET", "/api/pcap-state");
      mergePcap(remote.data);
      savePcap();
      await push();
      onMerged();
    } catch (error) {
      console.warn("No se pudo sincronizar la preparación del PCAP:", error.message);
    } finally {
      merging = false;
    }
  });
}
