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
    # Modo de varredura:
    # - "single": varia uma junta (comportamento legado)
    # - "orbit": varredura 2D (pan + tilt) aproximando uma meia-esfera
    scan_mode: str = "orbit"

    # Parametros do modo "single"
    # Junta usada para girar a camera durante a busca (0=j1 ... 5=j6).
    # j6 (indice 5) gira o flange/camera no proprio eixo; j1 (indice 0) varre a base.
    scan_joint: int = 5
    scan_start_deg: float = -60.0   # offset inicial em relacao a pose base
    scan_end_deg: float = 60.0      # offset final
    scan_step_deg: float = 10.0     # passo angular entre capturas

    # Parametros do modo "orbit" (aneis empilhados: grande embaixo -> menor no topo)
    orbit_pan_joint: int = 0
    orbit_tilt_joint: int = 1
    orbit_levels: int = 6                 # quantas subidas/aneis ate o topo
    orbit_points_per_level: int = 24      # quantos pontos por circulo
    orbit_radius_bottom_deg: float = 45.0 # raio angular no nivel mais baixo
    orbit_radius_top_deg: float = 8.0     # raio angular no topo
    orbit_tilt_bottom_deg: float = -28.0  # offset tilt no nivel da base
    orbit_tilt_top_deg: float = 22.0      # offset tilt no topo
    orbit_serpentine: bool = True         # alterna sentido entre aneis

    # Compensacao opcional para manter camera apontando para o centro no pan.
    # Ex.: com lookat_gain=1.0, ao girar +20 em pan aplica -20 no lookat_joint.
    orbit_lookat_joint: int = 5
    orbit_lookat_gain: float = 1.0
    orbit_enable_lookat_comp: bool = False

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

    # --- Simulacao (turbo para desenvolvimento) ---
    sim_turbo: bool = True               # sem delays desnecessarios na simulacao
    sim_settle_time_s: float = 0.0       # tempo de espera apos mover no modo turbo
    sim_motion_sleep: bool = False       # MockRobot move instantaneo no modo turbo
    sim_noise_sigma: float = 2.0         # ruido menor para render mais rapido
    sim_motion_blur: bool = False        # blur desligado para reduzir custo por frame
