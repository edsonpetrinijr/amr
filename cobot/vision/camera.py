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
        # GAP-10 fix: check grab() return value. Consecutive failures on the USB bus
        # (e.g., brief disconnect, buffer overrun) are surfaced instead of returning
        # a stale buffered frame silently.
        grab_failures = 0
        for _ in range(max(0, self.flush_frames)):
            if not self.cap.grab():
                grab_failures += 1
                if grab_failures >= 2:
                    break  # stop flushing; let cap.read() give the last good frame
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError(
                "Falha ao capturar frame da webcam"
                + (f" ({grab_failures} grab(s) falharam durante o flush)" if grab_failures else "")
            )
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

    GAP-7 fix: noise_sigma e motion_blur simulam condicoes reais de fabrica so que
    os limiares do detector sejam calibrados contra imagens realisticas.
    """

    def __init__(self, robot, scan_joint: int, target_joint_deg: float,
                 aruco_dict_name: str = "DICT_4X4_50", marker_id: int = 0,
                 width: int = 1280, height: int = 720,
                 noise_sigma: float = 8.0, motion_blur: bool = True,
                 secondary_joint: int | None = None,
                 secondary_target_joint_deg: float = 0.0):
        self.robot = robot
        self.scan_joint = scan_joint
        self.target_joint_deg = target_joint_deg
        self.secondary_joint = secondary_joint
        self.secondary_target_joint_deg = secondary_target_joint_deg
        self.width = width
        self.height = height
        self.marker_id = marker_id
        self.noise_sigma = noise_sigma
        self.motion_blur = motion_blur
        self._dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, aruco_dict_name))

    def open(self) -> None:
        pass

    def read(self) -> np.ndarray:
        frame = np.full((self.height, self.width, 3), 60, dtype=np.uint8)
        joints = self.robot.get_joints()
        cur = joints[self.scan_joint]
        delta = cur - self.target_joint_deg  # graus de erro em relacao ao alvo (pan)
        delta_secondary = 0.0
        if self.secondary_joint is not None:
            delta_secondary = joints[self.secondary_joint] - self.secondary_target_joint_deg

        # Fora de ~50 graus: peca nao aparece no campo de visao.
        if abs(delta) <= 50 and abs(delta_secondary) <= 35:
            # Tamanho do marcador cresce conforme aproxima do alvo (peca mais perto/alinhada).
            radial_err = float(np.hypot(delta, delta_secondary * 1.5))
            size = int(np.interp(min(radial_err, 55.0), [0, 55], [170, 38]))
            marker = cv2.aruco.generateImageMarker(self._dict, self.marker_id, size)
            marker = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)

            # Deslocamento proporcional ao erro angular pan/tilt.
            cx = int(self.width / 2 + delta * 12)
            cy = int(self.height / 2 + delta_secondary * 8)
            x0 = cx - size // 2
            y0 = cy - size // 2
            if 0 <= x0 and x0 + size <= self.width and 0 <= y0 and y0 + size <= self.height:
                frame[y0:y0 + size, x0:x0 + size] = marker

            # Motion blur proportional to angular error: simulates camera shake while
            # the arm is still settling. Fades to zero at delta=0 (arm at rest).
            blur_mag = max(abs(delta), abs(delta_secondary))
            if self.motion_blur and blur_mag > 2.0:
                k = int(np.interp(min(blur_mag, 30.0), [2, 30], [3, 15]))
                k = k if k % 2 == 1 else k + 1  # must be odd
                frame = cv2.GaussianBlur(frame, (k, k), 0)

        # Gaussian sensor noise — always present, represents real camera noise floor.
        if self.noise_sigma > 0:
            noise = np.random.normal(0, self.noise_sigma, frame.shape)
            frame = np.clip(frame.astype(np.int16) + noise.astype(np.int16), 0, 255).astype(np.uint8)

        return frame

    def release(self) -> None:
        pass
