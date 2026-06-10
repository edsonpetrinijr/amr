"""Configuracao do sistema de varredura + visao."""
from dataclasses import dataclass


@dataclass
class ScanConfig:
    # --- Robo ---
    robot_ip: str = "192.168.58.2"
    tool: int = 0
    user: int = 0
    move_vel: float = 20.0          # velocidade do MoveJ em % (0-100)

    # --- Varredura (rotacao da camera) ---
    # Junta usada para girar a camera durante a busca (0=j1 ... 5=j6).
    # j6 (indice 5) gira o flange/camera no proprio eixo; j1 (indice 0) varre a base.
    scan_joint: int = 5
    scan_start_deg: float = -60.0   # offset inicial em relacao a pose base
    scan_end_deg: float = 60.0      # offset final
    scan_step_deg: float = 10.0     # passo angular entre capturas
    settle_time_s: float = 0.5      # espera apos mover, antes de capturar (evita borrao)

    # --- Camera ---
    camera_index: int = 0           # indice da webcam USB
    frame_width: int = 1280
    frame_height: int = 720
    flush_frames: int = 5           # descarta N frames velhos do buffer antes de ler

    # --- Deteccao da peca (ArUco) ---
    aruco_dict: str = "DICT_4X4_50"
    target_marker_id: int = 0       # id do marcador que representa a peca

    # --- Criterio de "posicao certa" ---
    center_tol_px: int = 60         # marcador deve estar a no max N px do centro
    min_marker_size_px: float = 40  # tamanho minimo do marcador (peca perto o bastante)

    # --- Saida ---
    output_dir: str = "captures"
