@echo off
REM Inicia um servidor HTTP local e abre a simulacao 3D do FR5 no navegador.
REM Necessario porque os arquivos .dae/.urdf nao carregam via file:// (CORS).
cd /d "%~dp0"
echo Servindo a simulacao em http://localhost:8000/
start "" http://localhost:8000/
python -m http.server 8000
