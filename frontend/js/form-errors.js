/* Campos con error en los formularios (AUD-023, WCAG 3.3.1 y 4.1.2).

   El mensaje de error ya se lee por role="alert" o role="status", pero no decía a qué campo se
   refería. Aquí se marca cada campo con aria-invalid="true", se enlaza con el mensaje
   (aria-describedby) y se lleva el foco al primero, para corregirlo sin buscarlo. */

/**
 * @param {HTMLFormElement} form
 * @param {string[]} names nombres de los campos con error; vacío solo limpia las marcas anteriores
 * @param {string} messageId id del elemento con el mensaje de error
 */
export function markInvalid(form, names, messageId) {
  for (const input of form.querySelectorAll("[aria-invalid]")) {
    input.removeAttribute("aria-invalid");
    const rest = (input.getAttribute("aria-describedby") ?? "").split(" ").filter((id) => id && id !== messageId);
    if (rest.length) input.setAttribute("aria-describedby", rest.join(" "));
    else input.removeAttribute("aria-describedby");
  }
  const invalid = [...new Set(names)]
    .map((name) => form.elements.namedItem(name))
    .filter((el) => el && el.tagName === "INPUT");
  for (const input of invalid) {
    input.setAttribute("aria-invalid", "true");
    const ids = (input.getAttribute("aria-describedby") ?? "").split(" ").filter(Boolean);
    input.setAttribute("aria-describedby", [...ids, messageId].join(" "));
  }
  invalid[0]?.focus();
}

/** Campos de un error de la API: los que trae un 422 de validación y los que añade quien llama. */
export const errorFields = (error, extra = []) => [...(error?.fields ?? []), ...extra];

const TYPED = "form[id] input:not([type=checkbox]):not([type=radio]):not([type=file]):not([type=hidden])[name], form[id] textarea[name]";

/**
 * Lo que el alumno está escribiendo en los formularios de `container`, para no perderlo cuando la
 * vista se repinta entera en segundo plano (llega el progreso de la cuenta, cambia el perfil…).
 * Sin esto, por ejemplo, la contraseña actual escrita en «Mi perfil» se borraba a mitad.
 * Devuelve una función que lo vuelve a poner en los mismos campos del HTML nuevo.
 * @param {ParentNode} container
 * @returns {(next: ParentNode) => void}
 */
export function keepTyped(container) {
  const typed = [...container.querySelectorAll(TYPED)]
    .filter((field) => field.value !== field.defaultValue)
    .map((field) => [field.form.id, field.name, field.value]);
  return (next) => {
    for (const [formId, name, value] of typed) {
      const field = next.querySelector(`form[id="${CSS.escape(formId)}"] [name="${CSS.escape(name)}"]`);
      if (field) field.value = value;
    }
  };
}
