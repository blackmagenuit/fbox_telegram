@echo off
cd /d "c:\Users\cabja\OneDrive\Documents\fbox_telegram_repo"

echo Configurando git...
git config core.editor "echo"
git config --global core.editor "echo"

echo Limpiando estado de rebase...
if exist ".git\rebase-merge" rd /s /q ".git\rebase-merge"
if exist ".git\rebase-apply" rd /s /q ".git\rebase-apply"

echo Agregando archivos...
git add .

echo Haciendo commit...
git commit -m "Actualización del script de monitoreo FBOX"

echo Subiendo a GitHub (forzado)...
git push origin main --force

echo.
echo Estado final:
git status

pause
