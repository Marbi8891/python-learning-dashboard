/* Los repintados en segundo plano (llega el progreso de la cuenta, los datos del panel…) sustituyen el
   HTML de la vista. Sin esto, lo que el alumno está escribiendo en un formulario se perdería a medias:
   el nombre nuevo volvería al antiguo y se enviaría ese, o desaparecería el mensaje de error que estaba
   leyendo. Se conserva, en cada formulario con id, lo que el alumno ha cambiado respecto a lo pintado,
   el mensaje del formulario y los campos marcados como erróneos (form-errors.js).

   Solo para repintados que el alumno no ha pedido: cuando él guarda algo, la vista nueva manda. */

/**
 * Selector para volver a encontrar, después de repintar, el control de `container` que tiene el foco:
 * por id, por su nombre dentro de un formulario con id (los campos de contraseña no tienen id) o por su
 * primer atributo data-. Sin esto, lo que el alumno teclea justo durante el repintado se pierde.
 * @returns {string | null}
 */
export function focusSelector(container) {
  const active = document.activeElement;
  if (!active || active === document.body || !container.contains(active)) return null;
  if (active.id) return `#${CSS.escape(active.id)}`;
  if (active.name && active.form?.id) return `form[id="${CSS.escape(active.form.id)}"] [name="${CSS.escape(active.name)}"]`;
  const data = [...active.attributes].find((a) => a.name.startsWith("data-"));
  return data ? `${active.tagName.toLowerCase()}[${data.name}="${CSS.escape(data.value)}"]` : null;
}

/** @param {Element} container  @param {() => void} repaint sustituye el contenido de `container` */
export function keepForms(container, repaint) {
  const saved = [...container.querySelectorAll("form[id]")].map((form) => ({
    id: form.id,
    fields: [...form.elements]
      // Como keepTyped (form-errors.js): un input file no admite que se le asigne valor y uno hidden no lo escribe el alumno
      .filter((el) => el.name && el.type !== "file" && el.type !== "hidden" && (el.type === "checkbox" || el.type === "radio" ? el.checked !== el.defaultChecked : "defaultValue" in el && el.value !== el.defaultValue))
      .map((el) => ({ name: el.name, value: el.value, checked: el.checked, radio: el.type === "radio" })),
    invalid: [...form.querySelectorAll("[aria-invalid]")].map((el) => ({ name: el.name, describedby: el.getAttribute("aria-describedby") })),
    message: form.querySelector(".form-message"),
  }));
  repaint();
  for (const s of saved) {
    const form = container.querySelector(`#${CSS.escape(s.id)}`);
    if (!form) continue;
    for (const f of s.fields) {
      const el = f.radio ? form.querySelector(`input[type=radio][name="${CSS.escape(f.name)}"][value="${CSS.escape(f.value)}"]`) : form.elements.namedItem(f.name);
      if (!el || el instanceof RadioNodeList) continue;
      if (el.type === "checkbox" || el.type === "radio") el.checked = f.checked;
      else el.value = f.value;
    }
    for (const f of s.invalid) {
      const el = form.elements.namedItem(f.name);
      if (!el || el instanceof RadioNodeList) continue;
      el.setAttribute("aria-invalid", "true");
      if (f.describedby) el.setAttribute("aria-describedby", f.describedby);
    }
    const box = form.querySelector(".form-message");
    if (box && s.message?.textContent) {
      box.textContent = s.message.textContent;
      if (s.message.dataset.ok) box.dataset.ok = s.message.dataset.ok;
    }
  }
}
