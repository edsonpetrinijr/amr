"""Deteccao da peca e decisao de "posicao certa" (o diferencial do sistema).

Usa marcadores ArUco por padrao, pois fornecem posicao e orientacao precisas.
Para trocar a estrategia (ex: deteccao por modelo treinado / cor / contorno),
basta implementar a interface PartDetector.
"""
from __future__ import annotations
import abc
from dataclasses import dataclass, field
from typing import Optional, List
import numpy as np
import cv2


@dataclass
class DetectionResult:
    found: bool = False                 # a peca/marcador apareceu no frame?
    in_position: bool = False           # esta na "posicao certa"?
    center: Optional[tuple] = None      # (x, y) do centro do marcador em px
    size_px: float = 0.0                # tamanho aparente (lado medio) em px
    offset_px: float = 0.0              # distancia do centro da imagem em px
    angle_deg: float = 0.0              # rotacao no plano da imagem (graus)
    corners: Optional[np.ndarray] = None
    message: str = ""


class PartDetector(abc.ABC):
    @abc.abstractmethod
    def detect(self, frame: np.ndarray) -> DetectionResult:
        ...


class ArucoPartDetector(PartDetector):
    """Detecta um marcador ArUco alvo e decide se esta na posicao correta.

    Criterio de "posicao certa":
      1. o marcador alvo esta visivel, E
      2. seu centro esta a no maximo `center_tol_px` do centro da imagem, E
      3. seu tamanho aparente >= `min_marker_size_px` (peca perto o suficiente).
    """

    def __init__(self, target_marker_id: int = 0, aruco_dict_name: str = "DICT_4X4_50",
                 center_tol_px: int = 60, min_marker_size_px: float = 40.0):
        self.target_id = target_marker_id
        self.center_tol_px = center_tol_px
        self.min_marker_size_px = min_marker_size_px
        self._dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, aruco_dict_name))
        self._params = cv2.aruco.DetectorParameters()
        self._detector = cv2.aruco.ArucoDetector(self._dict, self._params)

    def detect(self, frame: np.ndarray) -> DetectionResult:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self._detector.detectMarkers(gray)

        if ids is None:
            return DetectionResult(found=False, message="Nenhum marcador detectado")

        ids = ids.flatten().tolist()
        if self.target_id not in ids:
            return DetectionResult(
                found=False,
                message=f"Marcadores {ids} vistos, mas alvo {self.target_id} ausente")

        c = corners[ids.index(self.target_id)][0]  # 4 cantos (x, y)
        center = (float(c[:, 0].mean()), float(c[:, 1].mean()))

        # Tamanho aparente = media dos comprimentos dos lados.
        sides = [np.linalg.norm(c[i] - c[(i + 1) % 4]) for i in range(4)]
        size_px = float(np.mean(sides))

        # Angulo no plano da imagem (canto0 -> canto1).
        edge = c[1] - c[0]
        angle_deg = float(np.degrees(np.arctan2(edge[1], edge[0])))

        h, w = gray.shape[:2]
        img_center = (w / 2.0, h / 2.0)
        offset_px = float(np.hypot(center[0] - img_center[0], center[1] - img_center[1]))

        centered = offset_px <= self.center_tol_px
        close_enough = size_px >= self.min_marker_size_px
        in_position = centered and close_enough

        if in_position:
            msg = "Peca na posicao certa"
        elif not centered:
            msg = f"Peca vista, fora de centro (offset {offset_px:.0f}px)"
        else:
            msg = f"Peca vista, longe demais (tamanho {size_px:.0f}px)"

        return DetectionResult(
            found=True, in_position=in_position, center=center, size_px=size_px,
            offset_px=offset_px, angle_deg=angle_deg, corners=c, message=msg)
