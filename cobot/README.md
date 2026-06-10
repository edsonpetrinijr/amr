# Fairino cobot — movimento + visão eye-in-hand

Projeto para o cobot Fairino (conectado em `192.168.58.2`).

## Conteúdo

| Arquivo | O que faz |
|---------|-----------|
| `move_robot.py` | Movimento simples (MoveJ entre duas poses). Bom para o "hello world". |
| `scan_and_inspect.py` | **Sistema principal**: gira a câmera, encontra a peça na posição certa, captura e analisa. |
| `make_marker.py` | Gera um marcador ArUco para imprimir e colar na peça. |
| `vision/` | Pacote modular (câmera, detector, robô, análise). |
| `fairino/` | SDK pure-Python da Fairino (já incluído — funciona no Python 3.13). |

## Setup

```powershell
cd c:\Users\junioeg\robotics\fairino_test
pip install -r requirements.txt
```

O SDK `fairino` já está na pasta — não precisa instalar.

## O sistema de visão (eye-in-hand)

Câmera USB montada na **ponta do robô**. O robô faz uma varredura angular da
câmera para encontrar a peça na **posição certa** (o diferencial). No modo atual
recomendado, a câmera faz uma órbita em **anéis empilhados**: começa embaixo
(nível da base) com círculo maior, sobe por níveis e reduz o círculo até o topo,
aproximando uma meia-esfera ao redor da peça. Quando encontra a posição certa,
captura a imagem final e roda a análise.

### Como a "posição certa" é detectada

Por padrão usamos **marcadores ArUco** colados na peça — eles dão posição **e**
orientação precisas. A peça é considerada "na posição certa" quando:

1. o marcador alvo está visível,
2. está **centralizado** (≤ `center_tol_px` do centro da imagem), e
3. está **grande o suficiente** (≥ `min_marker_size_px` → perto/alinhado).

Tudo é configurável em `vision/config.py`. Para trocar a estratégia (cor, contorno,
modelo treinado, YOLO, etc.), implemente a interface `PartDetector` em
`vision/detector.py` — o resto do pipeline não muda.

## Como usar

### 1. Testar a lógica sem hardware (recomendado primeiro)

```powershell
python scan_and_inspect.py --simulate
```

Roda 100% simulado (robô e câmera virtuais) e prova o fluxo: orbita, encontra,
captura e salva `captures/peca_*.png` + `.json`.

Para forçar o modo legado de varredura em 1 junta:

```powershell
python scan_and_inspect.py --simulate --scan-mode single
```

### 2. Preparar o marcador

```powershell
python make_marker.py --id 0 --size 600
```

Imprima `marker_DICT_4X4_50_id0.png` e cole na peça.

### 3. Rodar com o robô + webcam reais

```powershell
python scan_and_inspect.py
# opcoes: --ip 192.168.58.2 --camera 0 --marker-id 0 --scan-mode orbit
```

Saída: imagem + JSON de análise em `captures/`.

## Ajustes principais (`vision/config.py`)

- `scan_mode` — `orbit` (meia-esfera em 2 juntas) ou `single` (varredura legada).
- `orbit_pan_joint` / `orbit_tilt_joint` — juntas usadas na órbita (pan + tilt).
- `orbit_levels` — quantos níveis/subidas a órbita terá.
- `orbit_points_per_level` — quantos pontos por círculo em cada nível.
- `orbit_radius_bottom_deg` / `orbit_radius_top_deg` — círculo maior embaixo e menor no topo.
- `orbit_tilt_bottom_deg` / `orbit_tilt_top_deg` — altura angular do primeiro e último nível.
- `orbit_enable_lookat_comp` / `orbit_lookat_joint` / `orbit_lookat_gain` — compensação opcional para manter a câmera apontando ao centro durante pan.
- `scan_joint` e `scan_*` — parâmetros do modo legado (`single`).
- `settle_time_s` — espera após mover antes de capturar (evita borrão).
- `center_tol_px` / `min_marker_size_px` — rigor do critério de "posição certa".
- `target_marker_id` / `aruco_dict` — marcador alvo.

## Notas técnicas

- **Bypass de conexão:** este firmware não abre a porta CNDE `20005`, então o SDK
  marcaria `is_connect=False` e bloquearia todos os comandos. Forçamos
  `Robot.RPC.is_connect = True`; os comandos usam o XML-RPC (`20003`), que funciona.
- **SDK:** usamos a versão **pure-Python** (`windows\fairino\Robot.py`), pois o
  `libfairino` só tem binários para Python 3.10–3.12 (não 3.13).

## Segurança

- Área livre e botão de emergência à mão antes de mover o robô.
- Comece com `move_vel` baixo (20%) e amplitude de varredura pequena.
- Ajuste as poses para valores seguros do seu robô antes do primeiro teste real.

## Próximos passos sugeridos

- Trocar ArUco por detecção da peça real (cor/contorno/modelo).
- Refino fino: após "achar", centralizar com pequenos passos (visual servoing).
- Acionar garra/IO para coletar a peça depois da análise.
