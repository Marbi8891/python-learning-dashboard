/* Diálogo de cuenta: login, registro, recuperación, perfil, exportación y borrado. */

import { errorFields, markInvalid } from "./form-errors.js";
import { ApiError, apiEnabled, request, serverInfo } from "./api.js";
import { escapeHtml } from "./markdown.js";
import { renderGoogleButton } from "./google-identity.js";
import { flushCourseSync } from "./course-store.js";
import { flushGameSync } from "./game.js";
import { flushPcapSync } from "./pcap-sync.js";
import { flushLearnSync } from "./learn/learn-store.js";
import { clearLocalData, endSession, flushLessonsSync, startSession, state, subscribe } from "./store.js";
import { failedStores, onSyncStateChange, unsavedStores } from "./sync-status.js";

const FLASH_KEY = "pld:flash";

const $ = (selector) => document.querySelector(selector);
let showToast = () => {};

const dialog = () => $("#account-dialog");

function showView(name) {
  for (const view of dialog().querySelectorAll("[data-view]")) {
    view.hidden = view.dataset.view !== name;
  }
  // Con la sesión abierta no hay botón de entrar con Google: el de la pantalla de borrado es el único
  const withGoogle = googleAvailable() && !state.user;
  const googleLogin = dialog().querySelector("[data-google-login]");
  if (googleLogin) googleLogin.hidden = name !== "login" || !withGoogle;
  setMessage("");
  for (const form of dialog().querySelectorAll("form")) markInvalid(form, [], MESSAGE_ID); // el mensaje de error ya no está
  if (name === "login" && withGoogle) showGoogleButton($("#google-signin"), loginWithGoogle);
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

const MESSAGE_ID = "account-message";

/** Envía un formulario de la cuenta. `fieldsFor(error)` dice qué campos causaron un error que el
    servidor no asocia a ninguno (p. ej. «Ese email ya está registrado» → email). */
async function submitting(form, action, { fieldsFor = () => [] } = {}) {
  const button = form.querySelector("button[type=submit]");
  markInvalid(form, [], MESSAGE_ID);
  button.disabled = true;
  setMessage("Conectando con el servidor…", "info");
  // El servidor gratuito se duerme sin uso y tarda hasta un minuto en despertar
  const slow = setTimeout(
    () => setMessage("El servidor se está despertando: la primera vez puede tardar hasta un minuto. No cierres esta ventana.", "info"),
    SLOW_MS,
  );
  let invalid = [];
  try {
    await action(new FormData(form));
  } catch (error) {
    setMessage(error.message);
    invalid = errorFields(error, fieldsFor(error));
  } finally {
    clearTimeout(slow);
    button.disabled = false;
  }
  markInvalid(form, invalid, MESSAGE_ID); // después de reactivar el botón, para poder llevar el foco al campo
}

/** Cierra la sesión y borra de este navegador los datos personales (equipos compartidos).
    Con `keep`, el alumno ha elegido conservar en este navegador lo que no se pudo subir (SYNC-01).
    Se recarga la página para que tampoco quede nada en memoria; el aviso se muestra al volver. */
async function leave(message, { keep = false } = {}) {
  // La cookie de sesión es HttpOnly: solo la API puede borrarla
  await request("POST", "/api/auth/logout", { auth: false }).catch(() => {});
  endSession();
  if (!keep) clearLocalData();
  const after = keep
    ? "Tu progreso sigue en este navegador y se subirá a tu cuenta la próxima vez que entres."
    : "Tus datos se han borrado de este navegador.";
  try {
    sessionStorage.setItem(FLASH_KEY, `${message} ${after}`);
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

/** La API deja la sesión en una cookie HttpOnly. Si el navegador no la guarda
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
    setMessage("Confirma que has leído la política de privacidad para continuar con Google.");
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

// El servidor dice en /api/health si tiene GOOGLE_CLIENT_ID; sin él, el botón solo daría un error
let serverHasGoogle = true;
const googleAvailable = () => Boolean(window.PLD_CONFIG?.googleClientId) && serverHasGoogle;

async function checkServerGoogle() {
  const info = await serverInfo;
  if (info?.google !== false) return;
  serverHasGoogle = false;
  dialog().querySelector("[data-google-login]").hidden = true;
  dialog().querySelector("[data-google-delete]").hidden = true;
}

/** El script de Google se descarga aquí, al mostrar un botón de Google, no al abrir la web. */
function showGoogleButton(target, action) {
  renderGoogleButton(target, async (credential) => {
    if (!credential) {
      setMessage("Google no ha devuelto una credencial válida.");
      return;
    }
    try {
      await action(credential);
    } catch (error) {
      setMessage(error.message);
    }
  }).catch((error) => setMessage(error.message));
}

/** Cuentas creadas con Google: su contraseña es aleatoria, así que el borrado se confirma volviendo
    a elegir la misma cuenta de Google. */
async function deleteWithGoogle(credential) {
  if (!state.user || !dialog().querySelector("[data-view=profile] .account__danger").open) return; // solo desde su botón
  await request("POST", "/api/users/me/delete", { json: { google_credential: credential } });
  await leave("Tu cuenta y todos sus datos se han borrado.");
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

let leavingEverywhere = false;

/** Sube ya todo lo pendiente. Devuelve si la cuenta lo tiene todo. */
async function flushAll() {
  const results = await Promise.all([
    flushLessonsSync(),
    flushPcapSync(),
    flushCourseSync(),
    flushLearnSync(),
    flushGameSync(),
  ]);
  return results.every(Boolean) && unsavedStores().length === 0;
}

async function finishLogout({ keep = false } = {}) {
  if (leavingEverywhere) await request("POST", "/api/auth/logout-all").catch(() => {});
  await leave(leavingEverywhere ? "Sesión cerrada en todos tus dispositivos." : "Sesión cerrada.", { keep });
}

/** Cierra la sesión (desde el diálogo de la cuenta o desde el panel del alumno).
    Antes sube lo pendiente. Si algo no llega a la cuenta, no se borra nada de este navegador:
    se explica qué falta y el alumno elige (SYNC-01). Devuelve false si la sesión sigue abierta. */
export async function logout({ everywhere = false } = {}) {
  leavingEverywhere = everywhere;
  if (await flushAll()) {
    await finishLogout();
    return true;
  }
  showUnsaved();
  return false;
}

function showUnsaved() {
  openAccount("unsaved");
  $("#unsaved-list").textContent = listText(unsavedStores());
}

const listText = (items) =>
  items.length <= 1 ? (items[0] ?? "") : `${items.slice(0, -1).join(", ")} y ${items.at(-1)}`;

/** Aviso discreto cuando una subida falla: el alumno sabe que su cuenta aún no lo tiene (SYNC-04). */
function renderSyncStatus() {
  const box = $("#sync-status");
  if (!box) return;
  const failed = state.user ? failedStores() : [];
  box.textContent = failed.length
    ? `No se ha podido guardar en tu cuenta ${listText(failed)}. Se reintentará; mientras, sigue en este navegador.`
    : "";
}

export function initAccount({ toast }) {
  showToast = toast;
  renderAccountButton();
  setupPasswordRecovery();
  checkServerGoogle();
  subscribe((change) => {
    if (change.type === "profile") renderAccountButton(); // nombre cambiado en «Mi cuenta»
    if (change.type !== "user") return;
    renderAccountButton();
    renderSyncStatus();
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
    }, {
      // 409: el email ya existe; 422 sin campos: contraseña demasiado común o con tus datos
      fieldsFor: (error) => (error.status === 409 ? ["email"] : error.status === 422 && !error.fields?.length ? ["password"] : []),
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
        throw Object.assign(new Error("Las dos contraseñas no coinciden."), { fields: ["confirm_password"] });
      }
      await request("POST", "/api/auth/password-reset/confirm", {
        auth: false,
        json: { token: data.get("token"), new_password: data.get("new_password") },
      });
      event.target.reset();
      endSession();
      showView("login");
      setMessage("Tu contraseña se ha actualizado correctamente. Ya puedes iniciar sesión.", "success");
    }, {
      fieldsFor: (error) => (error.status === 422 && !error.fields?.length ? ["new_password"] : []),
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

  // Cerrar sesión con cambios sin subir (SYNC-01)
  $("#unsaved-retry").addEventListener("click", async (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    setMessage("Guardando en tu cuenta…", "info");
    try {
      if (await flushAll()) {
        await finishLogout();
        return;
      }
      $("#unsaved-list").textContent = listText(unsavedStores());
      setMessage("Todavía no se ha podido guardar. Comprueba tu conexión e inténtalo de nuevo.");
    } finally {
      button.disabled = false;
    }
  });
  $("#unsaved-keep").addEventListener("click", () => finishLogout({ keep: true }));
  $("#unsaved-discard").addEventListener("click", () => finishLogout());
  $("#unsaved-cancel").addEventListener("click", () => showView("profile"));

  onSyncStateChange(renderSyncStatus);

  const danger = dialog().querySelector("[data-view=profile] .account__danger");
  const googleDelete = dialog().querySelector("[data-google-delete]");
  danger.addEventListener("toggle", () => {
    googleDelete.hidden = !googleAvailable();
    if (danger.open && !googleDelete.hidden) showGoogleButton($("#google-delete"), deleteWithGoogle);
  });

  $("#delete-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitting(event.target, async (data) => {
      await request("POST", "/api/users/me/delete", { json: { password: data.get("password") } });
      await leave("Tu cuenta y todos sus datos se han borrado.");
    });
  });
}
