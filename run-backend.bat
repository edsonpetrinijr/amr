@echo off
echo Starting Caterpillar Inc. Fleet backend on http://localhost:8765 ...
cd /d "%~dp0"
python -m server.app.main
