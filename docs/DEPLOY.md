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

## 2. Backend en Render (Blueprint)

1. Crea una cuenta en [render.com](https://render.com) e inicia sesión con GitHub.
2. **New → Blueprint** → elige el repositorio. Render lee `render.yaml` y crea:
   - `pld-api`: el backend, construido con `backend/Dockerfile`.
   - `pld-db`: PostgreSQL. `DATABASE_URL` se conecta sola.
   - `JWT_SECRET`: Render lo genera automáticamente.
3. Espera al primer despliegue. Al arrancar, el contenedor migra la base de datos y carga las lecciones.
4. Comprueba `https://<tu-servicio>.onrender.com/api/health` → `{"status":"ok"}`.

> VERIFY: revisa las condiciones actuales del plan gratuito de Render. El servicio web gratuito se suspende tras un rato sin uso (la primera petición tarda cerca de un minuto) y la base de datos gratuita caduca pasado un tiempo. Para uso real, pasa la base de datos a un plan de pago o usa otro proveedor.

## 3. Conectar el frontend con el backend

Edita `frontend/config.js`:

```js
window.PLD_CONFIG = Object.assign({ apiUrl: "https://<tu-servicio>.onrender.com" }, window.PLD_CONFIG);
```

Publica de nuevo con `deploy.ps1`. Aparecerá el botón «Iniciar sesión».

Si cambias el dominio del frontend, actualiza en el backend `CORS_ORIGINS` y `FRONTEND_URL`.

## 4. Emails de recuperación de contraseña

Sin SMTP, el enlace de recuperación solo se escribe en los logs del servidor, así que en producción **hace falta configurarlo**. En Render → `pld-api` → Environment, rellena:

`SMTP_HOST`, `SMTP_PORT` (587), `SMTP_USER`, `SMTP_PASSWORD` y `SMTP_FROM`.

Sirve cualquier proveedor con SMTP y STARTTLS, por ejemplo el de tu dominio o un servicio de email transaccional.

## 5. Antes de abrirlo a usuarios reales (NEEDS_HUMAN)

- [ ] Completa en `frontend/privacidad.html` los campos marcados en amarillo: responsable, NIF, email de contacto, proveedor de alojamiento y de email.
- [ ] Si el alojamiento está fuera de la UE, revisa la base de la transferencia internacional.
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
