# Cria branch + commit da POC de reconstrucao 3D.
# Uso: abra um terminal NOVO (nao o que esta rodando bridge.py) e rode:
#   powershell -ExecutionPolicy Bypass -File .\recon\setup_branch.ps1

$ErrorActionPreference = "Stop"
Set-Location -Path (Split-Path -Parent (Split-Path -Parent $PSCommandPath))

Write-Host "==> git status (antes)" -ForegroundColor Cyan
git status --short

Write-Host "`n==> commit da sessao atual em main (orbit UI + real-robot + drag)" -ForegroundColor Cyan
git add -A
$pending = git diff --cached --name-only
if ($pending) {
    git commit -m "feat: orbit live edit + real-robot run + part drag + fluid blendT"
} else {
    Write-Host "   (nada para commitar)" -ForegroundColor Yellow
}

Write-Host "`n==> criando branch poc/3d-reconstruction" -ForegroundColor Cyan
$exists = git branch --list "poc/3d-reconstruction"
if ($exists) {
    git checkout poc/3d-reconstruction
} else {
    git checkout -b poc/3d-reconstruction
}

Write-Host "`n==> instalando deps de reconstrucao" -ForegroundColor Cyan
pip install -r requirements-recon.txt

Write-Host "`n==> branch ativa:" -ForegroundColor Cyan
git branch --show-current

Write-Host "`nOK. Proximo: rodar 'python recon/intrinsics.py --chessboard 9x6 --square-mm 25 --frames 20'" -ForegroundColor Green
Write-Host "(precisa imprimir um chessboard antes -- ver recon/README.md)" -ForegroundColor Green
