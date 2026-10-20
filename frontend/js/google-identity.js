/* Google Identity Services bajo demanda: el script de Google solo se descarga cuando alguien abre
   el inicio de sesión o confirma el borrado de su cuenta, no en cada visita (ni Google recibe la IP
   de quien solo estudia ni deja nada en su navegador sin que lo pida). */

const SCRIPT_URL = "https://accounts.google.com/gsi/client";
const TIMEOUT_MS = 15000;

let loading = null;
let onCredential = () => {};

/** Carga el script una sola vez e inicializa el cliente. Resuelve con `google.accounts.id`. */
export function loadGoogleIdentity() {
  const clientId = window.PLD_CONFIG?.googleClientId;
  if (!clientId) return Promise.reject(new Error("El inicio de sesión con Google no está configurado."));
  loading ??= new Promise((resolve, reject) => {
    const fail = () => {
      loading = null; // se puede reintentar más tarde (sin conexión, bloqueador…)
      reject(new Error("No se ha podido cargar Google. Revisa tu conexión e inténtalo de nuevo."));
    };
    const timer = window.setTimeout(fail, TIMEOUT_MS);
    const script = Object.assign(document.createElement("script"), { src: SCRIPT_URL, async: true });
    script.addEventListener("error", () => { window.clearTimeout(timer); script.remove(); fail(); });
    script.addEventListener("load", () => {
      window.clearTimeout(timer);
      const id = window.google?.accounts?.id;
      if (!id) return fail();
      // Un solo cliente por página: cada botón decide qué hacer con la credencial (ver renderGoogleButton)
      id.initialize({
        client_id: clientId,
        callback: ({ credential }) => onCredential(credential),
        auto_select: false,
        cancel_on_tap_outside: true,
      });
      resolve(id);
    });
    document.head.append(script);
  });
  return loading;
}

/** Pinta el botón de Google en `target` (una vez) y hace que la próxima credencial vaya a
    `handler`. El botón vive en un iframe de Google, así que el último botón mostrado decide: el de
    iniciar sesión y el de confirmar el borrado nunca están a la vez en pantalla. */
export async function renderGoogleButton(target, handler, { text = "continue_with" } = {}) {
  const id = await loadGoogleIdentity();
  onCredential = handler;
  if (target.dataset.rendered === "true") return;
  id.renderButton(target, {
    type: "standard", theme: "outline", size: "large",
    text, shape: "rectangular", width: 280,
    logo_alignment: "left",
  });
  target.dataset.rendered = "true";
}
