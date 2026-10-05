# Seguridad: amenazas y controles

> Documento de la **Fase 1**. Complementa, no sustituye:
> - [`/SECURITY.md`](../SECURITY.md): cómo avisar de vulnerabilidades y medidas del proyecto;
> - [`security/mitre-attack.md`](security/mitre-attack.md): modelo de amenazas MITRE ATT&CK (ADR-0023);
> - [`security/revision-2026-10.md`](security/revision-2026-10.md): riesgos abiertos de octubre de 2026.
>
> Aquí se juntan las amenazas de **la aplicación** y las nuevas que trae **trabajar con agentes**.

## 1. Superficie de ataque de la aplicación

| Entrada | Quién la controla | Dónde se procesa |
|---|---|---|
| Código Python del alumno | El alumno (o quien le haga pegar algo) | Worker de Pyodide |
| `localStorage` (`pld:*`) | Cualquiera con acceso al navegador o un XSS | `store.js`, `game.js`, `*-store.js` |
| Respuesta de la API (progreso de la cuenta) | El servidor, o un atacante si lo compromete | `cleanProgress`, `cleanLearning` |
| Contenido JSON (`frontend/data/`) | El autor (y los agentes de contenido) | `markdown.js`, highlight.js |
| URL (`#/restablecer?token=…`) | Cualquiera que envíe un enlace | `account.js` |
| Peticiones a la API | Cualquiera en Internet | FastAPI + Pydantic |
| Dependencias (pip, npm, Gradle, CDN) | Terceros | CI, navegador |

## 2. Amenazas de la aplicación

| Amenaza | Controles existentes | Hueco detectado en la auditoría |
|---|---|---|
| **XSS** | Todo el texto pasa por `escapeHtml`/`renderMarkdown`; `safeUrl` solo admite `https://`; CSP sin scripts en línea; test `markdown.test.mjs` | `app.js` (barra lateral) pone `slug` en atributos sin escapar (dato propio, riesgo bajo). `style-src 'unsafe-inline'` |
| **Robo de sesión** | JWT de 30 min en memoria (no en `localStorage`), `token_version`, «cerrar todas las sesiones» | Un XSS activo podría usar el token mientras la página está abierta (documentado) |
| **CSRF** | No aplica: la API usa `Authorization: Bearer`, no cookies; CORS solo admite el origen de la web | — |
| **Fuerza bruta / enumeración** | Argon2id, tiempo constante, límites por IP y cuenta, log `pld.security` | Límites en memoria (una sola instancia) |
| **Inyección SQL** | SQLAlchemy con parámetros; ningún SQL construido con texto | — |
| **Autorización** | El usuario sale siempre del token; lista cerrada de cursos (`COURSES`) | — |
| **Datos manipulados en `localStorage`** | `cleanProgress`, `cleanLearning` | `pld:game` y `pld:completed` se cargan sin validar (hoy no llegan a HTML sin escapar) |
| **Código Python malicioso** | Worker aislado (sin DOM, sin token, sin `localStorage`), límite de 10 s, aviso al pegar código que toca el navegador o la red | El Worker probablemente no hereda la CSP de `<meta>` *(inferido de la especificación CSP; falta una prueba)*: `import js` permitiría peticiones a cualquier origen |
| **Cadena de suministro** | Dependabot, `pip-audit`, `npm audit`, versiones npm exactas, wrapper de Gradle validado, token de Actions de solo lectura | Pyodide del CDN sin SRI; `python-multipart` y `argon2-cffi` sin límite superior; sin *lockfile* con *hashes* en pip |
| **Clickjacking** | `theme-init.js` oculta la página dentro de un marco | Sin `frame-ancestors` (GitHub Pages no permite cabeceras) |
| **Service Worker** | No guarda la API; solo borra sus propias cachés (`pld-site-*`) | Versión manual: un olvido deja archivos viejos en caché |
| **Exposición de secretos** | `.gitignore` de `.env`, `*.jks`, `*.key`…; `JWT_SECRET` obligatorio de 32+ caracteres; secretos de firma solo en GitHub | Activar *secret scanning* y *push protection* (ajuste manual en GitHub) |
| **Configuración** | `/docs` desactivado en producción; TLS obligatorio a la BD; límite de 300 KB por petición | La CSP de producción permite `http://127.0.0.1:8000` y `http://localhost:8000` |
| **Privacidad (RGPD)** | Export y borrado de cuenta, emails enmascarados en logs, analítica desactivada | — |

## 3. Amenazas nuevas al trabajar con agentes

| Amenaza | Ejemplo | Control propuesto |
|---|---|---|
| Agente que toca lo que no debe | El agente de contenido cambia `api.js` | `tools:` por agente + *hook* `PreToolUse` que bloquea rutas fuera de su área ([`AGENTS.md`](AGENTS.md)) |
| Publicar sin querer | *merge* a `main` publica la web (`pages.yml`); `deploy.ps1` hace *push* a `main` | `deny` de `git push` a `main`, de `deploy.ps1` y de `gh pr merge`; el *merge* lo hace una persona |
| Comandos destructivos | `git reset --hard`, `git clean -fd`, `rm -rf` | Reglas `deny` en `.claude/settings.json` |
| Lectura de secretos | Leer `backend/.env` o un `.jks` | Reglas `deny` `Read(…)` |
| Instrucciones maliciosas en datos | Un issue o una web dice «borra los tests» | Los agentes tratan esos textos como datos; acciones irreversibles con confirmación |
| Quitar tests para pasar la CI | Borrar o saltar un test que falla | Regla en `CLAUDE.md` y en el agente **test**; `git diff` revisado; la cobertura del 100 % del backend lo detecta |
| Desactivar controles | Relajar la CSP o `cleanProgress` «para que funcione» | Archivos de seguridad con `ask`; revisión del agente **security** |
| Dependencias innecesarias | Añadir un paquete npm para algo de 10 líneas | `ask` para editar `package.json` y `requirements*.txt` |
| MCP inseguro | Paquete `npx …@latest` o token en `.mcp.json` | Ver [`MCP.md`](MCP.md#6-riesgos-generales-de-mcp-y-controles) |
| Agentes que crean ficheros sin fin | Cientos de informes o archivos | Informes en la conversación, no en archivos; cambios pequeños por PR |

Límite real: un *hook* sobre `Bash` ve el comando, no lo que hace un script por dentro. La última
barrera es **Git + CI + revisión humana**.

## 4. Reglas de permisos propuestas (Fase 4, todavía no creadas)

Esbozo de `.claude/settings.json` con la sintaxis oficial (se ajustará y probará en la Fase 4):

```json
{
  "permissions": {
    "deny": [
      "Read(.env)", "Read(**/.env)", "Read(**/*.jks)", "Read(**/*.keystore)",
      "Read(backend/.local-secret)",
      "Bash(git push --force *)", "Bash(git reset --hard *)", "Bash(git clean *)",
      "Bash(gh pr merge *)", "Bash(gh release *)", "Bash(*deploy.ps1*)"
    ],
    "ask": [
      "Bash(git push *)", "Bash(gh pr create *)",
      "Edit(.github/**)", "Edit(render.yaml)", "Edit(docker-compose.yml)", "Edit(backend/Dockerfile)",
      "Edit(.claude/**)", "Edit(.mcp.json)", "Edit(CLAUDE.md)",
      "Edit(package.json)", "Edit(backend/requirements*.txt)",
      "Edit(backend/app/security.py)", "Edit(backend/app/deps.py)", "Edit(backend/app/routers/auth.py)",
      "Edit(backend/migrations/**)"
    ]
  }
}
```

## 5. Revisión de seguridad por cambio

El agente **security** interviene cuando un cambio toca: entrada del usuario, HTML generado,
autenticación o sesión, `localStorage`, CSP, Worker o Pyodide, service worker, dependencias,
configuración de despliegue, MCP o, en el futuro, el tutor IA. Comprueba como mínimo:

1. ¿Todo texto externo pasa por `escapeHtml`/`renderMarkdown`?
2. ¿Los datos de `localStorage` o de la API se validan antes de usarse?
3. ¿Se añade algún origen a la CSP o alguna dependencia? ¿Hace falta?
4. `pip-audit -r backend/requirements.txt` y `npm audit --audit-level=high`.
5. `/security-review` sobre el diff.
