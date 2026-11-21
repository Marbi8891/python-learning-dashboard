/* Tutor IA: llamadas al backend de PLD con el cliente común (api.js).

   Sin tokens nuevos ni almacenamiento: la sesión es la cookie HttpOnly de siempre. El navegador
   nunca habla con NEXARO ni conoce su dirección. */

import { ApiError, request, serverInfo } from "../api.js";

// El modelo local puede tardar: el backend espera hasta 120 s sin recibir datos de NEXARO
const ASK_TIMEOUT_MS = 150_000;

/** ¿Ofrece la IA este servidor? Lo dice /health, sin llamar a NEXARO. */
export async function aiOffered() {
  const info = await serverInfo;
  return info?.ai === true;
}

/** Estado del tutor: "available", "unavailable", "off", "login" o "error". */
export async function aiStatus() {
  try {
    const status = await request("GET", "/api/v1/ai/status");
    if (!status.enabled) return "off";
    return status.available ? "available" : "unavailable";
  } catch (error) {
    return error instanceof ApiError && error.status === 401 ? "login" : "error";
  }
}

/** Pregunta al tutor. `signal` cancela la espera (cambio de lección); hay un tope de tiempo. */
export async function askAi(mode, body, signal) {
  const controller = new AbortController();
  const abort = () => controller.abort(signal?.reason);
  signal?.addEventListener("abort", abort, { once: true });
  const timer = setTimeout(() => controller.abort(new DOMException("timeout", "TimeoutError")), ASK_TIMEOUT_MS);
  try {
    return await request("POST", `/api/v1/ai/${mode}`, { json: body, signal: controller.signal });
  } catch (error) {
    if (controller.signal.aborted) throw controller.signal.reason ?? error;
    throw error;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", abort);
  }
}
