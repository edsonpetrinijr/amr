@echo off
REM Inicia a ponte ao vivo (robo real + camera) e abre a simulacao 3D do FR5.
cd /d "%~dp0"
echo Iniciando ponte ao vivo do FR5 em http://localhost:8000/
start "" http://localhost:8000/
python bridge.py %*
