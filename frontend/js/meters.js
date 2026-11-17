/* Barras de progreso sin estilos en línea (RT-004): la CSP no permite style="…" (sin 'unsafe-inline').
   Las vistas pintan <span data-meter="42"> y aquí se pasa a la variable CSS --value: 42% con el CSSOM,
   que la CSP sí permite. Un MutationObserver lo hace con todo lo que se pinte después, antes de que
   el navegador lo dibuje. */

const SELECTOR = "[data-meter]";

function apply(element) {
  const value = Number(element.dataset.meter);
  element.style.setProperty("--value", `${Number.isFinite(value) ? Math.min(100, Math.max(0, value)) : 0}%`);
}

/** Aplica el valor a `root` y a sus descendientes con data-meter. */
export function applyMeters(root = document) {
  if (root.matches?.(SELECTOR)) apply(root);
  for (const element of root.querySelectorAll?.(SELECTOR) ?? []) apply(element);
}

/** Vigila el documento entero: cualquier barra que aparezca o cambie de valor se actualiza. */
export function watchMeters(root = document.documentElement) {
  applyMeters(root);
  new MutationObserver((records) => {
    for (const record of records) {
      if (record.type === "attributes") apply(record.target);
      else for (const node of record.addedNodes) if (node.nodeType === 1) applyMeters(node);
    }
  }).observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ["data-meter"] });
}
