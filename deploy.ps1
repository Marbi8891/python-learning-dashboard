<#
.SYNOPSIS
    Sube el proyecto a GitHub y activa GitHub Pages.

.DESCRIPTION
    Se puede ejecutar tantas veces como quieras:
      - 1.a vez: crea el repositorio público, activa Pages (vía GitHub Actions)
        y sube el código.
      - Siguientes: commit + push. El workflow pages.yml publica frontend/
        y ci.yml ejecuta lint + tests del backend.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\deploy.ps1
    powershell -ExecutionPolicy Bypass -File .\deploy.ps1 -Message "feat: panel de contenido"
#>
[CmdletBinding()]
param(
    [string]$RepoName = (Split-Path -Leaf $PSScriptRoot),
    [string]$Message  = "chore: actualizar dashboard",
    [string]$Branch   = "main"
)

Set-Location $PSScriptRoot

# ---------- Utilidades ----------
function Write-Step([string]$Text) { Write-Host "`n==> $Text" -ForegroundColor Cyan }
function Write-Ok([string]$Text)   { Write-Host "    $Text" -ForegroundColor Green }
function Stop-Deploy([string]$Text) { Write-Host "`nERROR: $Text" -ForegroundColor Red; exit 1 }

# PowerShell no se detiene solo cuando falla un programa externo (git, gh):
# comprobamos $LASTEXITCODE nosotros.
function Invoke-Native([string]$Command, [string[]]$Arguments) {
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { Stop-Deploy "Falló: $Command $($Arguments -join ' ')" }
}

# Ejecuta un comando en silencio y devuelve $true si terminó bien.
function Test-Native([string]$Command, [string[]]$Arguments) {
    & $Command @Arguments *> $null
    return ($LASTEXITCODE -eq 0)
}

# ---------- 1. Requisitos ----------
Write-Step "Comprobando requisitos"
$installIds = @{ git = "Git.Git"; gh = "GitHub.cli" }
foreach ($tool in $installIds.Keys) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Stop-Deploy "No se encuentra '$tool'. Instálalo con: winget install --id $($installIds[$tool]) y abre una terminal nueva."
    }
}
if (-not (Test-Path "frontend/index.html")) {
    Stop-Deploy "No hay frontend/index.html en $PSScriptRoot. El script debe estar en la raíz del proyecto."
}
if (-not (git config user.name) -or -not (git config user.email)) {
    Stop-Deploy ("Git no conoce tu identidad. Ejecuta:`n" +
        "  git config --global user.name  `"Tu Nombre`"`n" +
        "  git config --global user.email `"tu-email`"")
}
Write-Ok "git y gh disponibles"

# ---------- 2. Sesión en GitHub ----------
Write-Step "Comprobando sesión en GitHub"
if (-not (Test-Native gh @("auth", "status"))) {
    Invoke-Native gh @("auth", "login", "--hostname", "github.com", "--git-protocol", "https", "--web")
}
Invoke-Native gh @("auth", "setup-git")   # git usará las credenciales de gh al hacer push

$owner = gh api user --jq .login
if (-not $owner) { Stop-Deploy "No se pudo obtener tu usuario de GitHub." }
$fullName = "$owner/$RepoName"
Write-Ok "Usuario: $owner  |  Repositorio: $fullName"

# ---------- 3. Repositorio local y commit ----------
Write-Step "Preparando repositorio local"
if (-not (Test-Path ".git")) {
    Invoke-Native git @("init")
}
Invoke-Native git @("add", "-A")
if (git status --porcelain) {
    Invoke-Native git @("commit", "-m", $Message)
} else {
    Write-Ok "No hay cambios nuevos que commitear"
}
Invoke-Native git @("branch", "-M", $Branch)

# ---------- 4. Repositorio remoto y push ----------
Write-Step "Sincronizando con GitHub"
if (Test-Native gh @("repo", "view", $fullName)) {
    $visibility = gh repo view $fullName --json visibility --jq .visibility
    if ($visibility -ne "PUBLIC") {
        Write-Host "    AVISO: el repositorio es $visibility. Con la cuenta gratuita, Pages solo funciona en repos públicos." -ForegroundColor Yellow
    }
} else {
    Invoke-Native gh @("repo", "create", $fullName, "--public", "--description", "Python Learning Dashboard interactivo")
    Write-Ok "Repositorio creado"
}

# ---------- 5. GitHub Pages (publicado por GitHub Actions) ----------
# Se activa ANTES del push para que el primer workflow ya pueda desplegar.
Write-Step "Configurando GitHub Pages"
$pagesPending = $false
if (Test-Native gh @("api", "repos/$fullName/pages")) {
    $buildType = gh api "repos/$fullName/pages" --jq .build_type
    if ($buildType -ne "workflow") {
        Invoke-Native gh @("api", "--silent", "-X", "PUT", "repos/$fullName/pages", "-f", "build_type=workflow")
        Write-Ok "Pages cambiado a despliegue con GitHub Actions"
    } else {
        Write-Ok "Pages ya estaba activado"
    }
} elseif (Test-Native gh @("api", "-X", "POST", "repos/$fullName/pages", "-f", "build_type=workflow")) {
    Write-Ok "Pages activado (GitHub Actions)"
} else {
    $pagesPending = $true   # p. ej. repositorio aún vacío: se reintenta tras el push
}

# ---------- 6. Push ----------
Write-Step "Subiendo código"
$remoteUrl = "https://github.com/$fullName.git"
if ((git remote) -contains "origin") {
    Invoke-Native git @("remote", "set-url", "origin", $remoteUrl)
} else {
    Invoke-Native git @("remote", "add", "origin", $remoteUrl)
}
Invoke-Native git @("push", "-u", "origin", $Branch)
Write-Ok "Código subido"

if ($pagesPending) {
    Invoke-Native gh @("api", "--silent", "-X", "POST", "repos/$fullName/pages", "-f", "build_type=workflow")
    Write-Ok "Pages activado (GitHub Actions)"
    Invoke-Native gh @("workflow", "run", "pages.yml", "--ref", $Branch)
}
$siteUrl = gh api "repos/$fullName/pages" --jq .html_url

# ---------- 7. Esperar al despliegue de este commit ----------
Write-Step "Buscando el despliegue del frontend"
$headCommit = git rev-parse HEAD
$runId = $null
foreach ($i in 1..6) {
    Start-Sleep -Seconds 5
    $runId = gh run list --workflow pages.yml --commit $headCommit --limit 1 --json databaseId --jq '.[0].databaseId' 2>$null
    if ($runId) { break }
}

if (-not $runId) {
    Write-Ok "No hay despliegue nuevo (este commit no cambia frontend/)."
    Write-Host "Web: $siteUrl"
    exit 0
}

gh run watch $runId --exit-status
if ($LASTEXITCODE -ne 0) {
    Stop-Deploy "El despliegue falló. Revisa https://github.com/$fullName/actions/runs/$runId"
}
Write-Host "`nPublicado: $siteUrl" -ForegroundColor Green
Write-Host "(Si ves la versión anterior, recarga con Ctrl+F5)"
Start-Process $siteUrl
