/* Búsqueda de lecciones en la barra lateral (curso PCAP).
   matchesQuery es pura (se prueba con node --test); initLessonFilter conecta el buscador con el DOM
   sin regenerar la lista: solo oculta lo que no coincide y abre los módulos con resultados. */

/** Minúsculas y sin tildes: «función», «Funcion» y «FUNCIÓN» se buscan igual. */
export const normalize = (text) =>
  String(text ?? "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim();

/** ¿Contiene el texto todas las palabras de la búsqueda, en cualquier orden? */
export function matchesQuery(query, ...fields) {
  const words = normalize(query).split(/\s+/).filter(Boolean);
  const haystack = normalize(fields.join(" "));
  return words.every((word) => haystack.includes(word));
}

const savedOpen = new Map(); // módulos abiertos por el alumno antes de buscar

function apply(input, pendingOnly) {
  const query = input.value;
  const searching = Boolean(normalize(query)) || pendingOnly;
  let shown = 0;
  for (const module of document.querySelectorAll("#modules .module")) {
    if (searching && !savedOpen.has(module)) savedOpen.set(module, module.open);
    const moduleName = module.querySelector(".module__name")?.textContent ?? "";
    let matches = 0;
    for (const link of module.querySelectorAll(".lesson[data-slug]")) {
      const name = link.querySelector(".lesson__name")?.textContent ?? "";
      const visible = matchesQuery(query, name, link.dataset.slug, moduleName) && !(pendingOnly && link.dataset.status === "completed");
      link.closest("li").hidden = !visible;
      if (visible) matches += 1;
    }
    shown += matches;
    module.hidden = matches === 0;
    if (searching) module.open = matches > 0;
    else if (savedOpen.has(module)) module.open = savedOpen.get(module);
  }
  if (!searching) savedOpen.clear();
  const status = document.querySelector("#lesson-filter-status");
  status.textContent = searching ? (shown ? `${shown} ${shown === 1 ? "lección" : "lecciones"}` : "Ninguna lección coincide") : "";
}

export function initLessonFilter() {
  const input = document.querySelector("#lesson-filter");
  const pending = document.querySelector("#lesson-filter-pending");
  if (!input || !pending) return;
  const update = () => apply(input, pending.checked);
  input.addEventListener("input", update);
  pending.addEventListener("change", update);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && input.value) {
      event.stopPropagation(); // que Escape borre la búsqueda y no cierre el menú móvil
      input.value = "";
      update();
    }
  });
}
