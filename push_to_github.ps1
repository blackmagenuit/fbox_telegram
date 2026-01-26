# Script para subir cambios a GitHub
Set-Location "c:\Users\cabja\OneDrive\Documents\fbox_telegram_repo"

# Configurar editor simple
git config core.editor "echo"

# Limpiar cualquier estado de rebase
if (Test-Path ".git\rebase-merge") {
    Remove-Item -Recurse -Force ".git\rebase-merge" -ErrorAction SilentlyContinue
}
if (Test-Path ".git\rebase-apply") {
    Remove-Item -Recurse -Force ".git\rebase-apply" -ErrorAction SilentlyContinue
}

# Agregar todos los cambios
git add .

# Hacer commit
$commitMsg = "Actualización del script de monitoreo FBOX - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git commit -m $commitMsg

# Intentar push directo
Write-Host "Intentando push directo..." -ForegroundColor Cyan
$pushResult = git push origin main 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Push directo falló. Intentando force push..." -ForegroundColor Yellow
    git push origin main --force
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Force push exitoso!" -ForegroundColor Green
    } else {
        Write-Host "❌ Force push falló. Estado:" -ForegroundColor Red
        git status
    }
} else {
    Write-Host "✅ Push exitoso!" -ForegroundColor Green
}

Write-Host "`nEstado final:" -ForegroundColor Cyan
git status
