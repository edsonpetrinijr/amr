@echo off
title BehaveX — Fleet
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════╗
echo  ║   BehaveX Fleet — Starting...   ║
echo  ╚══════════════════════════════════╝
echo.

:: Backend (Flask) numa janela separada
echo [1/2] Iniciando backend (porta 8765)...
start "Fleet Backend" cmd /k "cd /d "%~dp0" && python -m backend.app.main"

:: Aguarda o backend subir
timeout /t 3 /nobreak > nul

:: Frontend (Vite + Electron)
echo [2/2] Iniciando frontend (Electron)...
npm run dev

echo.
echo  Tudo encerrado.
pause
