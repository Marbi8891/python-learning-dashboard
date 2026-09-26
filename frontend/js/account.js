/* Diálogo de cuenta: login, registro, recuperación, perfil, exportación y borrado. */

import { apiEnabled, request } from "./api.js";
import { endSession, startSession, state, subscribe } from "./store.js";

const $ = (selector) => document.querySelector(selector);
let showToast = () => {};

const dialog = () => $("#account-dialog");

function showView(name) {
  for (const view of dialog().querySelectorAll("[data-view]")) {
    view.hidden = view.dataset.view !== name;
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

async function submitting(form, action) {
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  setMessage("Conectando con el servidor…", "info");
  try {
    await action(new FormData(form));
  } catch (error) {
    setMessage(error.message);
  } finally {
    button.disabled = false;
  }
}

async function login(email, password) {
  const { access_token: token } = await request("POST", "/api/auth/login", {
    form: { username: email, password },
    auth: false,
  });
  await startSession(token);
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

/** Enlace del email de recuperación: #/restablecer?token=... */
export function openPasswordReset(token) {
  openAccount("reset");
  $("#reset-token").value = token;
}

export function initAccount({ toast }) {
  showToast = toast;
  renderAccountButton();
  subscribe((change) => {
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
      await request("POST", "/api/auth/password-reset/confirm", {
        auth: false,
        json: { token: data.get("token"), new_password: data.get("new_password") },
      });
      endSession();
      showView("login");
      setMessage("Contraseña cambiada. Ya puedes iniciar sesión.", "success");
    });
  });

  $("#export-button").addEventListener("click", async () => {
    try {
      downloadJson(await request("GET", "/api/users/me/export"), "mis-datos-python-learning.json");
    } catch (error) {
      setMessage(error.message);
    }
  });

  $("#logout-button").addEventListener("click", () => {
    endSession();
    dialog().close();
    showToast("Sesión cerrada. Tu progreso sigue guardado en este navegador.");
  });

  $("#delete-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitting(event.target, async (data) => {
      await request("POST", "/api/users/me/delete", { json: { password: data.get("password") } });
      endSession();
      dialog().close();
      showToast("Tu cuenta y todos sus datos se han borrado.");
    });
  });
}
