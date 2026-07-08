# Сборка Windows-приложения Kinetix CRM
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> Kinetix Windows build" -ForegroundColor Cyan

# 1. Frontend
Write-Host "==> Building frontend..." -ForegroundColor Yellow
Push-Location (Join-Path $Root "frontend")
if (-not (Test-Path "node_modules")) { npm ci }
$env:VITE_BASE = "/"
$env:VITE_USE_LOCAL_API = "false"
$env:VITE_API_URL = "/api"
npm run build
if (-not (Test-Path "dist/index.html")) { throw "Frontend build failed" }
Pop-Location

# 2. Backend server (PyInstaller)
Write-Host "==> Building backend server..." -ForegroundColor Yellow
Push-Location (Join-Path $Root "backend")
python -m pip install -r requirements.txt pyinstaller --quiet
if (Test-Path "dist/kinetix-server") { Remove-Item -Recurse -Force "dist/kinetix-server" }
python -m PyInstaller kinetix-server.spec --noconfirm
if (-not (Test-Path "dist/kinetix-server/kinetix-server.exe")) { throw "Backend build failed" }
Pop-Location

# 3. Electron installer
Write-Host "==> Packaging Electron app..." -ForegroundColor Yellow
Push-Location (Join-Path $Root "desktop")
if (-not (Test-Path "node_modules")) { npm install }
npm run dist
Pop-Location

$installer = Get-ChildItem (Join-Path $Root "desktop/release") -Filter "*.exe" | Select-Object -First 1
if ($installer) {
  Write-Host ""
  Write-Host "Готово: $($installer.FullName)" -ForegroundColor Green
} else {
  Write-Host "Сборка завершена, проверьте desktop/release" -ForegroundColor Green
}
