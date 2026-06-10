"""Analise da imagem coletada quando a peca esta na posicao certa.

Placeholder extensivel: aqui voce pluga a sua analise real (medicao, classificacao,
OCR, modelo treinado, etc.). Por enquanto retorna metricas basicas de qualidade da
imagem + a pose do marcador detectado.
"""
from __future__ import annotations
from typing import Dict
import numpy as np
import cv2

from .detector import DetectionResult


def sharpness(frame: np.ndarray) -> float:
    """Nitidez via variancia do Laplaciano (maior = mais nitido)."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def analyze_image(frame: np.ndarray, detection: DetectionResult) -> Dict:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = {
        "brilho_medio": float(gray.mean()),
        "nitidez": sharpness(frame),
        "resolucao": [int(frame.shape[1]), int(frame.shape[0])],
        "marcador_centro_px": detection.center,
        "marcador_tamanho_px": detection.size_px,
        "marcador_angulo_deg": detection.angle_deg,
        "marcador_offset_centro_px": detection.offset_px,
        "veredito": "OK" if detection.in_position else "NAO_ALINHADO",
    }
    return result
