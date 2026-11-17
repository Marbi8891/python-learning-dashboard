/* Cerrar un diálogo modal al pulsar fuera (MWG-08). Los diálogos sin formularios llevan closedby="any";
   este respaldo hace lo mismo en los navegadores que aún no lo entienden (Safari). El diálogo de la
   cuenta no lo usa: un toque fuera no debe borrar lo que se está escribiendo. */

/** Si el navegador no entiende closedby, cierra `dialog` al pulsar en su fondo oscuro. */
export function lightDismiss(dialog) {
  if ("closedBy" in HTMLDialogElement.prototype) return;
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return; // un clic dentro del contenido
    const box = dialog.getBoundingClientRect();
    const inside = box.top <= event.clientY && event.clientY <= box.bottom && box.left <= event.clientX && event.clientX <= box.right;
    if (!inside) dialog.close();
  });
}
