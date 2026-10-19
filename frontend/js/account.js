/* Diálogo de cuenta: login, registro, recuperación, perfil, exportación y borrado. */

import { ApiError, apiEnabled, request, serverInfo } from "./api.js";
import { escapeHtml } from "./markdown.js";
import { flushCourseSync } from "./course-store.js";
import { flushGameSync } from "./game.js";
import { flushPcapSync } from "./pcap-sync.js";
import { flushLearnSync } from "./learn/learn-store.js";
import { clearLocalData, endSession, startSession, state, subscribe } from "./store.js";

const FLASH_KEY = "pld:flash";

const $ = (selector) => document.querySelector(selector);
let showToast = () => {};

const dialog = () => $("#account-dialog");

function showView(name) {
  for (const view of dialog().querySelectorAll("[data-view]")) {
    view.hidden = view.dataset.view !== name;
  }
  const googleLogin = dialog().querySelector("[data-google-login]");
  if (googleLogin) {
    googleLogin.hidden = name !== "login" || !googleEnabled;
    if (!googleLogin.hidden) showGoogleButton($("#google-signin"));
  }
  setMessage("");
  const heading = dialog().querySelector(`[data-view="${name}"] h2`);
  $("#account-title").textContent = heading?.dataset.title ?? "Tu cuenta";
  dialog().querySelector(`[data-view="${name}"] input, [data-view="${name}"] button`)?.focus();
}

function setMessage(text, kind = "error") {
  const box = $("#account-message");
  box.textContent = text;
  box.dataset.kind = kind;
  box.hidden = !text;
}

const SLOW_MS = 4000;

async function submitting(form, action) {
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  setMessage("Conectando con el servidor…", "info");
  // El servidor gratuito se duerme sin uso y tarda hasta un minuto en despertar
  const slow = setTimeout(
    () => setMessage("El servidor se está despertando: la primera vez puede tardar hasta un minuto. No cierres esta ventana.", "info"),
    SLOW_MS,
  );
  try {
    await action(new FormData(form));
  } catch (error) {
    setMessage(error.message);
  } finally {
    clearTimeout(slow);
    button.disabled = false;
  }
}

/** Cierra la sesión y borra de este navegador los datos personales (equipos compartidos).
    Se recarga la página para que tampoco quede nada en memoria; el aviso se muestra al volver. */
async function leave(message) {
  // La cookie de sesión es HttpOnly: solo la API puede borrarla
  await request("POST", "/api/auth/logout", { auth: false }).catch(() => {});
  endSession();
  clearLocalData();
  try {
    sessionStorage.setItem(FLASH_KEY, `${message} Tus datos se han borrado de este navegador.`);
  } catch {
    // sin almacenamiento: se recarga igualmente
  }
  location.reload();
}

/** Aviso pendiente de la página anterior (tras cerrar sesión o borrar la cuenta). */
export function takeFlash() {
  try {
    const message = sessionStorage.getItem(FLASH_KEY);
    sessionStorage.removeItem(FLASH_KEY);
    return message;
  } catch {
    return null;
  }
}

/** Sin SMTP en el servidor no se pueden enviar enlaces: se ofrece el contacto en su lugar. */
async function setupPasswordRecovery() {
  const info = await serverInfo;
  if (!info || info.email) return;
  const contact = window.PLD_CONFIG?.contactEmail;
  const form = $("#forgot-form");
  form.querySelector("label").hidden = true;
  form.querySelector("button[type=submit]").hidden = true;
  form.querySelector("p").innerHTML = contact
    ? `La recuperación por email aún no está activa. Escribe desde el email de tu cuenta a <a href="mailto:${escapeHtml(contact)}">${escapeHtml(contact)}</a> y te enviaremos un enlace para elegir otra contraseña.`
    : "La recuperación por email aún no está activa.";
}

/** La API deja la sesión en una cookie HttpOnly (ADR-0033). Si el navegador no la guarda
    (bloquea las cookies de terceros, como Safari), se pide el token y vive solo en memoria. */
async function login(email, password) {
  const form = { username: email, password };
  await request("POST", "/api/auth/login", { form, auth: false });
  try {
    await startSession();
  } catch (error) {
    if (!(error instanceof ApiError && error.status === 401)) throw error;
    const { access_token: token } = await request("POST", "/api/auth/login", { form, auth: false, cookie: false });
    await startSession(token);
  }
}

async function loginWithGoogle(credential) {
  if (!$("#google-privacy").checked) {
    setMessage("Acepta la política de privacidad para continuar con Google.");
    return;
  }
  const payload = { credential, accept_privacy: true };
  await request("POST", "/api/auth/google", { json: payload, auth: false });
  try {
    await startSession();
  } catch (error) {
    if (!(error instanceof ApiError && error.status === 401)) throw error;
    const { access_token: token } = await request("POST", "/api/auth/google", {
      json: payload, auth: false, cookie: false,
    });
    await startSession(token);
  }
  dialog().close();
  showToast(`¡Hola, ${state.user.display_name}! Tu progreso está sincronizado.`);
}

const GOOGLE_IDENTITY_URL = "https://accounts.google.com/gsi/client";
// Hay botón de Google si config.js tiene el Client ID y el servidor no dice que le falta el suyo
let googleEnabled = Boolean(window.PLD_CONFIG?.googleClientId);
let googleIdentity = null;

/** Google Identity se descarga solo al abrir el login o el borrado de la cuenta: quien solo
    visita la web no envía su IP a Google ni recibe sus cookies. */
function loadGoogleIdentity() {
  googleIdentity ??= new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) {
      resolve(window.google.accounts.id);
      return;
    }
    const script = Object.assign(document.createElement("script"), { src: GOOGLE_IDENTITY_URL, async: true });
    script.addEventListener("load", () => {
      if (window.google?.accounts?.id) resolve(window.google.accounts.id);
      else reject(new Error("Google no está disponible ahora mismo."));
    });
    script.addEventListener("error", () => {
      script.remove();
      reject(new Error("No se ha podido conectar con Google. Revisa tu conexión o usa tu email."));
    });
    document.head.append(script);
  }).catch((error) => {
    googleIdentity = null; // se puede reintentar al volver a abrir el diálogo
    throw error;
  }).then((id) => {
    id.initialize({
      client_id: window.PLD_CONFIG.googleClientId,
      // Un solo callback: con sesión abierta, Google confirma el borrado; sin ella, inicia sesión
      callback: async ({ credential }) => {
        if (!credential) {
          setMessage("Google no ha devuelto una credencial válida.");
          return;
        }
        try {
          if (state.user) await deleteWithGoogle(credential);
          else await loginWithGoogle(credential);
        } catch (error) {
          setMessage(error.message);
        }
      },
      auto_select: false,
      cancel_on_tap_outside: true,
    });
    return id;
  });
  return googleIdentity;
}

async function showGoogleButton(target) {
  if (!target || target.dataset.rendered === "true") return;
  let id;
  try {
    id = await loadGoogleIdentity();
  } catch (error) {
    setMessage(error.message);
    return;
  }
  if (target.dataset.rendered === "true") return;
  id.renderButton(target, {
    type: "standard", theme: "outline", size: "large",
    text: "continue_with", shape: "rectangular", width: 280,
    logo_alignment: "left",
  });
  target.dataset.rendered = "true";
}

async function deleteWithGoogle(credential) {
  await request("POST", "/api/users/me/delete", { json: { google_credential: credential } });
  await leave("Tu cuenta y todos sus datos se han borrado.");
}

/** Si el servidor dice que no tiene GOOGLE_CLIENT_ID, el botón solo daría un error: se oculta. */
async function initGoogleSignIn() {
  if (!googleEnabled) return;
  const danger = $(".account__danger");
  danger.addEventListener("toggle", () => {
    danger.querySelector("[data-google-delete]").hidden = !googleEnabled;
    if (danger.open && googleEnabled) showGoogleButton($("#google-delete"));
  });
  const info = await serverInfo;
  if (info && info.google === false) {
    googleEnabled = false;
    dialog().querySelector("[data-google-login]").hidden = true;
    danger.querySelector("[data-google-delete]").hidden = true;
  }
}

function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  Object.assign(document.createElement("a"), { href: url, download: filename }).click();
  URL.revokeObjectURL(url);
}

function renderAccountButton() {
  const button = $("#account-button");
  button.hidden = !apiEnabled;
  $("#account-label").textContent = state.user ? state.user.display_name : "Iniciar sesión";
  button.setAttribute("aria-label", state.user ? `Tu cuenta: ${state.user.display_name}` : "Iniciar sesión");
}

export function openAccount(view) {
  if (!dialog().open) dialog().showModal();
  showView(view ?? (state.user ? "profile" : "login"));
  if (state.user) {
    $("#profile-name").textContent = state.user.display_name;
    $("#profile-email").textContent = state.user.email;
  }
}

const INVALID_RESET_LINK = "Este enlace de recuperación no es válido o ha caducado. Pide uno nuevo.";

/** Enlace del email de recuperación: #/restablecer?token=...
    Sin token (enlace cortado al copiarlo) se ofrece pedir otro directamente. */
export function openPasswordReset(token) {
  if (!token) {
    openAccount("forgot");
    setMessage(INVALID_RESET_LINK);
    return;
  }
  openAccount("reset");
  $("#reset-token").value = token;
}

/** Descarga todos los datos de la cuenta en JSON (RGPD). Lanza ApiError si falla. */
export async function exportMyData() {
  downloadJson(await request("GET", "/api/users/me/export"), "mis-datos-python-learning.json");
}

/** Cierra la sesión (desde el diálogo de la cuenta o desde el panel del alumno). */
export async function logout({ everywhere = false } = {}) {
  await Promise.allSettled([flushPcapSync(), flushCourseSync(), flushLearnSync(), flushGameSync()]); // nada se queda sin subir
  if (everywhere) await request("POST", "/api/auth/logout-all").catch(() => {});
  await leave(everywhere ? "Sesión cerrada en todos tus dispositivos." : "Sesión cerrada.");
}

export function initAccount({ toast }) {
  showToast = toast;
  renderAccountButton();
  setupPasswordRecovery();
  initGoogleSignIn();
  subscribe((change) => {
    if (change.type === "profile") renderAccountButton(); // nombre cambiado en «Mi cuenta»
    if (change.type !== "user") return;
    renderAccountButton();
    if (change.expired) showToast("Tu sesión ha caducado. Vuelve a iniciar sesión.");
  });

  $("#account-button").addEventListener("click", () => openAccount());
  $("#account-close").addEventListener("click", () => dialog().close());
  for (const link of dialog().querySelectorAll("[data-go]")) {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      showView(link.dataset.go);
    });
  }

  $("#login-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitting(event.target, async (data) => {
      await login(data.get("email"), data.get("password"));
      dialog().close();
      showToast(`¡Hola, ${state.user.display_name}! Tu progreso está sincronizado.`);
    });
  });

  $("#register-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitting(event.target, async (data) => {
      await request("POST", "/api/auth/register", {
        auth: false,
        json: {
          email: data.get("email"),
          password: data.get("password"),
          display_name: data.get("display_name"),
          accept_privacy: data.get("accept_privacy") === "on",
        },
      });
      await login(data.get("email"), data.get("password"));
      dialog().close();
      showToast("Cuenta creada. Tu progreso se guardará en la nube.");
    });
  });

  $("#forgot-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitting(event.target, async (data) => {
      const response = await request("POST", "/api/auth/password-reset/request", {
        auth: false,
        json: { email: data.get("email") },
      });
      setMessage(response.detail, "success");
    });
  });

  $("#reset-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitting(event.target, async (data) => {
      if (data.get("new_password") !== data.get("confirm_password")) {
        throw new Error("Las dos contraseñas no coinciden.");
      }
      await request("POST", "/api/auth/password-reset/confirm", {
        auth: false,
        json: { token: data.get("token"), new_password: data.get("new_password") },
      });
      event.target.reset();
      endSession();
      showView("login");
      setMessage("Tu contraseña se ha actualizado correctamente. Ya puedes iniciar sesión.", "success");
    });
  });

  $("#export-button").addEventListener("click", async () => {
    try {
      await exportMyData();
    } catch (error) {
      setMessage(error.message);
    }
  });

  $("#logout-button").addEventListener("click", () => logout({ everywhere: $("#logout-everywhere").checked }));

  $("#delete-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitting(event.target, async (data) => {
      await request("POST", "/api/users/me/delete", { json: { password: data.get("password") } });
      await leave("Tu cuenta y todos sus datos se han borrado.");
    });
  });
}
