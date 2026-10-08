# Guía de despliegue

La app tiene dos partes que se despliegan por separado (ver [ADR-0001](adr/0001-arquitectura.md)):

| Parte | Dónde | Coste |
|---|---|---|
| Frontend (`frontend/`) | GitHub Pages | Gratis |
| Backend (`backend/`) + PostgreSQL | Render (o cualquier servidor con Docker) | Gratis con límites, o de pago |

**El frontend funciona solo.** Sin backend, todo va igual (lecciones, consola, ejercicios y asistente), pero el progreso se guarda únicamente en el navegador y no aparece el botón «Iniciar sesión».

---

## 1. Frontend en GitHub Pages

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy.ps1 -Message "feat: versión 0.3.0"
```

El script crea el repositorio, activa Pages (vía GitHub Actions) y sube el código.

URL final: `https://marbi8891.github.io/python-learning-dashboard/`

## 2. Base de datos en Neon

La base de datos gratuita de Render caduca a los 30 días, así que se usa Neon: PostgreSQL con plan gratuito permanente (0,5 GB) y servidores en la UE (ver [ADR-0008](adr/0008-backend-render-neon.md)).

1. Crea una cuenta en [neon.com](https://neon.com) (puedes entrar con GitHub).
2. **New project** → nombre `pld`, **región AWS Europe Central 1 (Frankfurt)**, PostgreSQL 16 o superior.
3. En **Connect**, copia la cadena de conexión (`postgresql://...neon.tech/...?sslmode=require`). Es una contraseña: no la subas al repositorio.

## 3. Backend en Render (Blueprint)

1. Crea una cuenta en [render.com](https://render.com) e inicia sesión con GitHub.
2. **New → Blueprint** → elige el repositorio. Render lee `render.yaml` y te pide los valores secretos:
   - `DATABASE_URL`: pega la cadena de conexión de Neon.
   - `SMTP_*`: déjalos vacíos por ahora (ver el paso 5).
   - `JWT_SECRET` lo genera Render.
3. Espera al primer despliegue (unos minutos). Al arrancar, el contenedor crea las tablas en Neon y carga las lecciones.
4. Comprueba `https://<tu-servicio>.onrender.com/api/health` → `{"status":"ok"}`.

Plan gratuito de Render: el servicio se duerme tras 15 min sin tráfico y la primera petición tarda cerca de un minuto en despertarlo.

## 4. Conectar el frontend con el backend

Ya está hecho para `https://pld-api.onrender.com`. Si tu servicio tiene otra URL, edita `frontend/config.js`:

```js
window.PLD_CONFIG = Object.assign({ apiUrl: "https://<tu-servicio>.onrender.com" }, window.PLD_CONFIG);
```

Publica de nuevo con `deploy.ps1`. Aparecerá el botón «Iniciar sesión».

Si cambias el dominio del frontend, actualiza en el backend `CORS_ORIGINS` y `FRONTEND_URL`.

## 5. Emails de recuperación de contraseña

Sin SMTP no se envía el enlace de recuperación (tampoco se escribe en los logs: cualquiera con acceso a ellos podría usarlo) y la web muestra el email de contacto (`contactEmail` en `frontend/config.js`) en lugar del formulario. Cuando configuras el SMTP, `/api/health` devuelve `"email": true` y la web muestra el formulario sola: no hay que tocar el código.

> **Plan gratuito de Render:** desde 2025 bloquea la salida a los puertos SMTP (25, 465 y 587), así que con Gmail por SMTP `/api/health` dice `"email": true` pero el email **nunca sale** (en los logs: «No se pudo enviar el email», con *Network is unreachable* o un *timeout*). En el plan gratuito usa la opción A, que envía por HTTPS.

### Opción A: Brevo por HTTPS (gratis, funciona en el plan gratuito de Render)

1. Crea una cuenta gratuita en [brevo.com](https://www.brevo.com) (VERIFY: el plan gratuito permite unos 300 emails al día).
2. **Senders, domains & dedicated IPs → Senders → Add a sender**: tu dirección (por ejemplo, tu Gmail). Brevo te envía un email para verificarla.
3. **SMTP & API → API keys → Generate a new API key**. Cópiala: es un secreto, no la guardes en el repositorio.
4. En Render → `pld-api` → **Environment**:

| Variable | Valor |
|---|---|
| `BREVO_API_KEY` | la clave del paso 3 |
| `SMTP_FROM` | `Python Learning <la dirección verificada en el paso 2>` |

Las variables `SMTP_HOST`, `SMTP_USER` y `SMTP_PASSWORD` sobran: si `BREVO_API_KEY` existe, tiene prioridad.

5. **Save, rebuild and deploy**. Comprueba `https://pld-api.onrender.com/api/health` → `"email": true` y pide un enlace de recuperación desde la web. Si no llega, mira la carpeta de spam y los logs de Render (`No se pudo enviar el email`). Para ver el motivo exacto, ejecuta `python -m app.mailer tu-direccion@gmail.com` en la **Shell** de Render (si tu plan la incluye) o en local con las mismas variables en `backend/.env`.

### Opción B: Gmail por SMTP (servidor propio o plan de pago de Render)

1. En tu cuenta de Google activa la **verificación en dos pasos** (Seguridad → Verificación en dos pasos).
2. Crea una **contraseña de aplicación**: Seguridad → Contraseñas de aplicaciones → nombre «Python Learning». Google muestra 16 letras: cópialas (sin espacios). Es una contraseña: no la guardes en el repositorio.
3. En **Environment**:

| Variable | Valor |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | tu dirección de Gmail |
| `SMTP_PASSWORD` | la contraseña de aplicación |
| `SMTP_FROM` | `Python Learning <tu dirección de Gmail>` |

4. Para comprobar que el email llega de verdad: `python -m app.mailer tu-direccion@gmail.com` (en local con las variables en `backend/.env`, o en la **Shell** del servidor). Si falla, muestra el error del servidor SMTP.

VERIFY: Gmail limita los envíos diarios de una cuenta personal (del orden de cientos). Para un proyecto de clase sobra.

### Después de activarlo (RGPD)

Actualiza en `frontend/privacidad.html` la línea «Emails de recuperación de contraseña» con el proveedor elegido (Brevo, Google o el servicio que uses) y publica.

## 6. Antes de abrirlo a usuarios reales

- [x] Responsable, contacto y proveedores (Render y Neon, Frankfurt) en `frontend/privacidad.html`.
- [ ] Revisa y acepta los acuerdos de tratamiento de datos (DPA) de Render y Neon desde sus paneles o webs.
- [ ] Al activar el SMTP, añade el proveedor de email a la política (sección 5).
- [ ] Recomendado: que alguien con conocimientos de RGPD revise la política.

## Alternativa: servidor propio (por ejemplo, Oracle Cloud)

En cualquier máquina con Docker:

```bash
git clone https://github.com/Marbi8891/python-learning-dashboard.git
cd python-learning-dashboard
docker build -f backend/Dockerfile -t pld-api .
docker run -d --restart unless-stopped -p 8000:8000 \
  -e DATABASE_URL=postgresql://usuario:clave@host:5432/pld \
  -e JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))") \
  -e CORS_ORIGINS='["https://marbi8891.github.io"]' \
  -e FRONTEND_URL=https://marbi8891.github.io/python-learning-dashboard \
  pld-api
```

Ponle delante un proxy con HTTPS (Caddy o Nginx con Let's Encrypt). El contenedor ya arranca con `--proxy-headers`, así que el límite de intentos de login funcionará por IP real.

## Todo en local con Docker Compose

```bash
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))") docker compose up --build
```

Frontend en http://localhost:5500 y API en http://localhost:8000/docs.
