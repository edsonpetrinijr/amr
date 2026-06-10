"""Abstracao de camera. Implementacao real (OpenCV/webcam) e mock para testes."""
from __future__ import annotations
import abc
import numpy as np
import cv2


class Camera(abc.ABC):
    @abc.abstractmethod
    def open(self) -> None:
        ...

    @abc.abstractmethod
    def read(self) -> np.ndarray:
        """Retorna um frame BGR (np.ndarray HxWx3)."""
        ...

    @abc.abstractmethod
    def release(self) -> None:
        ...

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.release()


class OpenCVCamera(Camera):
    """Webcam USB comum via cv2.VideoCapture."""

    def __init__(self, index: int = 0, width: int = 1280, height: int = 720,
                 flush_frames: int = 5):
        self.index = index
        self.width = width
        self.height = height
        self.flush_frames = flush_frames
        self.cap = None

    def open(self) -> None:
        # CAP_DSHOW costuma abrir mais rapido e estavel no Windows.
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError(f"Nao foi possivel abrir a webcam no indice {self.index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def read(self) -> np.ndarray:
        if self.cap is None:
            raise RuntimeError("Camera nao aberta. Chame open() primeiro.")
        # Descarta frames velhos do buffer para pegar a imagem atual.
        for _ in range(max(0, self.flush_frames)):
            self.cap.grab()
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError("Falha ao capturar frame da webcam.")
        return frame

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class MockCamera(Camera):
    """Camera simulada para testes sem hardware.

    Renderiza um marcador ArUco cuja posicao depende do estado de uma junta do
    MockRobot, imitando uma camera eye-in-hand: conforme o robo varre, o marcador
    se aproxima do centro e fica grande (peca "na posicao certa") perto do angulo alvo.
    """

    def __init__(self, robot, scan_joint: int, target_joint_deg: float,
                 aruco_dict_name: str = "DICT_4X4_50", marker_id: int = 0,
                 width: int = 1280, height: int = 720):
        self.robot = robot
        self.scan_joint = scan_joint
        self.target_joint_deg = target_joint_deg
        self.width = width
        self.height = height
        self.marker_id = marker_id
        self._dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, aruco_dict_name))

    def open(self) -> None:
        pass

    def read(self) -> np.ndarray:
        frame = np.full((self.height, self.width, 3), 60, dtype=np.uint8)
        cur = self.robot.get_joints()[self.scan_joint]
        delta = cur - self.target_joint_deg  # graus de erro em relacao ao alvo

        # Fora de ~50 graus: peca nao aparece no campo de visao.
        if abs(delta) > 50:
            return frame

        # Tamanho do marcador cresce conforme aproxima do alvo (peca mais perto/alinhada).
        size = int(np.interp(abs(delta), [0, 50], [160, 40]))
        marker = cv2.aruco.generateImageMarker(self._dict, self.marker_id, size)
        marker = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)

        # Deslocamento horizontal proporcional ao erro angular (sai do centro).
        cx = int(self.width / 2 + delta * 12)
        cy = int(self.height / 2)
        x0 = cx - size // 2
        y0 = cy - size // 2
        if 0 <= x0 and x0 + size <= self.width and 0 <= y0 and y0 + size <= self.height:
            frame[y0:y0 + size, x0:x0 + size] = marker
        return frame

    def release(self) -> None:
        pass
