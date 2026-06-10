# recon/ — POC de reconstrucao 3D a partir da camera eye-in-hand

Branch: `poc/3d-reconstruction`.

Objetivo: provar que da' para gerar um modelo 3D (nuvem de pontos ou mesh
texturizada) da peca usando APENAS a webcam ja montada na ponta do FR5, sem
hardware novo. Tudo isolado em `recon/` — nao toca em `sim/`.

## Por que isso e' viavel aqui (e nao no caso generico)

A pipeline classica de reconstrucao (COLMAP, NeRF, Gaussian Splatting) gasta
~80% do tempo descobrindo a pose das cameras (Structure-from-Motion). Aqui o
**robo ja sabe a pose** de cada foto via FK + calibracao mao-olho. Isso:

- pula o passo SfM completamente (modo COLMAP "known poses"),
- elimina deriva de pose e ambiguidade de escala,
- da cobertura controlada (a orbita ja e' uma captura ideal).

## Fases

- **F1 (este branch)**: capturar N imagens + poses durante a orbita, rodar
  COLMAP com poses conhecidas, gerar nuvem densa e mesh texturizada.
  Saida: `outputs/poc1/mesh.ply` + viewer 3D no navegador.
- **F2**: trocar COLMAP por Gaussian Splatting (3DGS) com poses conhecidas
  -> render fotorrealista, qualidade de estado-da-arte.
- **F3**: comparar reconstrucao vs CAD da peca -> deteccao de defeitos.

## Pipeline F1 (esta POC)

```
[bridge.py em modo real] --> orbita ja conhecida (sim/orbit_ik.py)
            |
            v
  capture.py   pega frame + pose (camera no frame BASE) a cada parada
            |
            v
  outputs/poc1/raw/{0001.png, 0001.json, ...}
            |
            v
  hand_eye.py  resolve T_flange->camera (ArUco; uma vez por setup)
            |
            v
  to_colmap.py converte raw/ + intrinsics + hand-eye -> cameras.txt + images.txt
            |
            v
  reconstruct.py  roda COLMAP (modo known-pose) + OpenMVS densificacao
            |
            v
  outputs/poc1/mesh.ply  <-- carregue em meshlab / blender / three.js
```

## Quick start

1. **Calibracao da intrinsics da webcam** (uma vez):
   - `python recon/intrinsics.py --chessboard 9x6 --square-mm 25 --frames 20`
   - Salva `recon/calib/intrinsics.json` (fx, fy, cx, cy, distortion).

2. **Calibracao mao-olho** (uma vez, com marcador ArUco fixo na bancada):
   - `python recon/hand_eye.py --ip 192.168.58.2 --aruco-size-mm 50`
   - Move o robo para ~15 poses olhando o marcador.
   - Salva `recon/calib/hand_eye.json` (T_flange->camera, 4x4).

3. **Captura sincronizada** (rodar uma orbita capturando):
   - Robo na home, peca colocada no centro definido na UI.
   - `python recon/capture.py --ip 192.168.58.2 --out outputs/poc1 --pause-ms 400`
   - Executa a orbita atual (mesma sequencia do botao "Executar"), pausa em
     cada keypoint, salva foto + pose JSON.

4. **Reconstrucao**:
   - `python recon/reconstruct.py --in outputs/poc1 --backend colmap`
   - Saida: `outputs/poc1/mesh.ply` + `points.ply`.

5. **Visualizar**:
   - Abre em meshlab, blender ou viewer web (TODO: integrar no `sim/index.html`).

## Dependencias novas (instalar antes)

Adicionadas em `requirements-recon.txt` (separado para nao poluir o main):

- `opencv-contrib-python` (ja temos; precisa do `aruco` que vem com `contrib`)
- `numpy` (ja temos)
- COLMAP CLI: instalar via https://colmap.github.io/install.html (Windows
  binarios: https://github.com/colmap/colmap/releases). Coloque no PATH.
- (opcional F2) `nerfstudio` ou impl. de Gaussian Splatting (depois).

## Criterio de matar (kill criteria)

- Se ate o fim da semana sair so' ruido (nuvem rala sem forma reconhecivel) e
  o problema for calibracao (intrinsics ruim, hand-eye errada, sincronizacao
  fora), entao o trabalho e' calibracao -- nao algoritmo. Investir nela
  ANTES de partir para 3DGS/NeRF.
- Se a calibracao estiver boa mas o mesh ainda for ruim, e' textura/luz: a
  peca metalica reflete demais e quebra feature matching. Solucao: spray
  revelador (white developer) ou padrao projetado.

## Status

- [ ] capture.py (esqueleto criado)
- [ ] intrinsics.py (esqueleto)
- [ ] hand_eye.py (esqueleto)
- [ ] to_colmap.py (esqueleto)
- [ ] reconstruct.py (esqueleto)
