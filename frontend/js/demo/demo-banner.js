/* Franja fija del modo demostración: deja claro en todas las pantallas que los datos son ficticios
   y permite reiniciar o salir. Fuera de la demo no hace nada. */

import { exitDemo, isDemo, resetDemo } from "./demo-mode.js";

export function initDemoBanner() {
  const banner = document.querySelector("#demo-banner");
  if (!banner) return;
  banner.hidden = !isDemo;
  document.documentElement.toggleAttribute("data-demo", isDemo);
  if (!isDemo) return;
  banner.addEventListener("click", (event) => {
    const action = event.target.closest("[data-demo-action]")?.dataset.demoAction;
    if (action === "reset") resetDemo();
    if (action === "exit") exitDemo();
  });
}
