# MCP: servidores, herramientas, permisos y riesgos

> Documento de la **Fase 1**. **Hoy el proyecto no usa ningún servidor MCP**: no existe `.mcp.json` ni
> `.claude/`. Aquí se documenta lo comprobado y qué MCP harían falta de verdad. Nada se instala hasta
> que se autorice la Fase 3.

## 1. Qué es MCP aquí

MCP (*Model Context Protocol*) conecta Claude Code con herramientas externas (GitHub, un navegador…).
Cada servidor añade herramientas con nombre `mcp__<servidor>__<herramienta>`. Más herramientas
significa más superficie de ataque y más contexto que leer, así que solo se añade un MCP si
resuelve algo que Claude Code **no** hace ya.

## 2. Herramientas que Claude Code ya trae (sin MCP)

| Necesidad | Herramienta integrada | Control de permisos |
|---|---|---|
| Leer y buscar archivos | `Read`, `Grep`, `Glob` | Reglas `Read(ruta)` |
| Editar archivos | `Edit`, `Write` | Reglas `Edit(ruta)` |
| Git, tests, auditorías | `Bash` (`git`, `pytest`, `npm`, `node`, `ruff`, `pip-audit`) | Reglas `Bash(git push *)`… |
| Documentación web | `WebFetch` | Reglas `WebFetch(domain:…)` |
| Subagentes | `Agent` | `tools: Agent(nombre)` |
| Revisión de seguridad del diff | `/security-review` (integrado) | — |

## 3. Análisis por prioridad

| Prioridad | MCP | ¿Hace falta? | Motivo |
|---|---|---|---|
| 1 | Filesystem | **No** | `Read`/`Edit` ya existen y respetan las reglas `Read(…)`/`Edit(…)` de `settings.json`. Un MCP de ficheros tendría sus propias herramientas, que **esas reglas no cubren**: empeoraría el control. |
| 2 | Git | **No** | `git` por `Bash` ya funciona y se controla con reglas (`deny` de `git reset --hard`, `git clean`, `git push --force`). Un MCP de Git saltaría esas reglas. |
| 3 | GitHub | **Opcional** | Para leer issues, PR y el estado de la CI. Si el autor ya tiene `gh` instalado y con sesión, basta `Bash(gh …)` con reglas. Si no, el servidor oficial de GitHub en **solo lectura**. |
| 4 | Documentación | **No** | `WebFetch` lee la documentación oficial (Python, MDN, FastAPI, Claude Code) con permiso por dominio. |
| 5 | Testing | **No** | `pytest`, `node --test`, Playwright y los `--check` se ejecutan con `Bash`. |
| 6 | Seguridad | **No** | `pip-audit`, `npm audit`, `ruff` y `/security-review` por `Bash`. |
| 7 | Navegador | **Opcional, más adelante** | Playwright MCP permitiría que los agentes **frontend** y **accessibility** abran la web local, naveguen con teclado y vean el resultado. Los tests e2e ya cubren lo automático; aporta valor en revisiones visuales. |
| 8 | Otros | **No** | No hay ninguna necesidad concreta. |

**Conclusión:** la primera implementación puede funcionar **sin `.mcp.json`**. Como mucho, GitHub en
solo lectura y, en una fase posterior, Playwright limitado a dos agentes.

## 4. Ficha de los MCP candidatos

### 4.1 GitHub (oficial) — opcional

| Campo | Valor |
|---|---|
| Nombre | `github` |
| Propósito | Leer issues, PR, comentarios de revisión y ejecuciones de la CI |
| Servidor | Remoto oficial: `https://api.githubcopilot.com/mcp/` (repositorio `github/github-mcp-server`) |
| Herramientas | Conjuntos `context`, `repos`, `issues`, `pull_requests`, `users` (por defecto) |
| Permisos propuestos | **Solo lectura**: cabecera `X-MCP-Readonly: true` |
| Lee | Código, issues, PR, comentarios y logs de Actions del repositorio |
| Modifica | Nada en modo solo lectura |
| Riesgos | El texto de issues y comentarios lo escribe cualquiera: puede contener instrucciones maliciosas (*prompt injection*). Un token con permisos de escritura permitiría hacer *merge* o publicar. |
| Agentes | orchestrator, release, security (lectura) |
| Alternativa | `gh` por `Bash` con `ask` para `gh pr create` y `deny` para `gh pr merge` y `gh release` |

Configuración que se usaría (sintaxis oficial de `.mcp.json`, el token **nunca** en el archivo):

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}",
        "X-MCP-Readonly": "true"
      }
    }
  }
}
```

### 4.2 Playwright — opcional, fase posterior

| Campo | Valor |
|---|---|
| Nombre | `playwright` |
| Propósito | Abrir la web local y comprobar navegación, teclado, foco y aspecto |
| Paquete | `@playwright/mcp` (Microsoft), por `npx` |
| Herramientas | Navegar, hacer clic, escribir, capturas y *snapshots* de accesibilidad, pestañas |
| Permisos propuestos | `--headless --isolated`, orígenes limitados a `http://localhost:5500`, `http://127.0.0.1:8000` y el CDN de Pyodide; sin las capacidades opcionales (`--caps`) |
| Lee | Lo que muestre la web local |
| Modifica | Nada del repositorio (perfil del navegador en memoria con `--isolated`) |
| Riesgos | Ejecuta un navegador y descarga un paquete npm: hay que **fijar la versión exacta** (nada de `@latest`). La lista de orígenes no es una barrera de seguridad completa. Las páginas pueden contener texto que intente manipular al agente. |
| Agentes | Solo **frontend** y **accessibility**, declarado **dentro de sus archivos de agente** (`mcpServers:`), no en `.mcp.json`, para que el resto no lo vea |

## 5. Capacidades detectadas

Comprobado en el entorno de esta auditoría el 5/10/2026:

| Comprobación | Resultado | Fuente |
|---|---|---|
| Versión de Claude Code | **2.1.289** en el entorno en la nube. **En el PC del autor hay que comprobarla** con `claude --version`. | `claude --version` |
| Agentes del proyecto | `.claude/agents/*.md` con `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`… | `code.claude.com/docs/en/sub-agents` |
| Límite de rutas por agente | **No** existe en `tools:`. Se hace con *hooks* `PreToolUse` o con reglas de `settings.json` | misma página |
| Comandos | `.claude/commands/<nombre>.md` **funcionan**; para lo nuevo se recomienda `.claude/skills/<nombre>/SKILL.md`. Admiten `description`, `argument-hint`, `allowed-tools`, `model`, `context: fork`, `agent` y `$ARGUMENTS` | `code.claude.com/docs/en/slash-commands` |
| `.mcp.json` | Soportado (ámbito *project*). Formato `{"mcpServers": {…}}`, `type: "http"` o `command`/`args`/`env`, variables `${VAR}` y `${VAR:-defecto}` | `claude mcp add --help`, `code.claude.com/docs/en/mcp` |
| Aprobación | Claude Code **pregunta** antes de usar un servidor de `.mcp.json` en sesiones interactivas. Ajustes: `enabledMcpjsonServers`, `disabledMcpjsonServers`, `enableAllProjectMcpServers` (no recomendado) | misma página |
| Permisos | `settings.json` → `permissions.allow/ask/deny`; se evalúan `deny` → `ask` → `allow`; `Edit(ruta)` y `Read(ruta)` | `code.claude.com/docs/en/permissions` |
| MCP existentes en el proyecto | **Ninguno** (`.mcp.json` no existe) | repositorio |
| MCP en el PC del autor | Desconocido: comprobar con `claude mcp list` antes de la Fase 3 para no duplicar | — |

Nota: el entorno en la nube donde se hizo esta auditoría tiene conectores propios (GitHub, documentos…).
Son de esa sesión, no del proyecto, y no se deben copiar a `.mcp.json`.

## 6. Riesgos generales de MCP y controles

| Riesgo | Control |
|---|---|
| Instrucciones maliciosas en datos externos (issues, web, comentarios) | Los agentes tratan esos datos como información, nunca como órdenes; las acciones irreversibles piden confirmación |
| Secretos en `.mcp.json` | Solo `${VARIABLE}`; el valor en el entorno del autor, nunca en el repositorio |
| Paquetes `npx` que cambian | Versión exacta fijada |
| Herramientas que saltan las reglas de permisos | No instalar MCP de ficheros ni de Git |
| Servidores nuevos sin revisar | Regla `ask` para `Edit(.mcp.json)`; aprobación por servidor |
| Demasiadas herramientas | Declarar MCP solo en los agentes que los usan (`mcpServers:` del agente) |
