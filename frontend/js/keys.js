/* Tecla modificadora de los atajos según el sistema: ⌘ (Cmd) en Mac, iPhone y iPad; Ctrl en el resto.
   Los atajos ya aceptan las dos (ctrlKey || metaKey); esto solo cambia lo que se enseña. */

const platform = globalThis.navigator?.userAgentData?.platform || globalThis.navigator?.platform || globalThis.navigator?.userAgent || "";

export const IS_APPLE = /Mac|iPhone|iPad|iPod/i.test(platform);

/** Texto plano: «⌘ Cmd» o «Ctrl». */
export const MOD_KEY = IS_APPLE ? "⌘ Cmd" : "Ctrl";

/** HTML del atajo para ejecutar: <kbd>⌘ Cmd</kbd>+<kbd>Enter</kbd>. */
export const RUN_KEYS_HTML = `<kbd>${MOD_KEY}</kbd>+<kbd>Enter</kbd>`;
