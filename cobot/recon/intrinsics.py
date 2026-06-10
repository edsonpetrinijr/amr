"""Calibracao da intrinsics da webcam (fx, fy, cx, cy, distortion).

Mostra a webcam ao vivo e detecta um padrao de tabuleiro (chessboard). A cada
deteccao boa, salva os pontos. Quando juntar N frames, calibra com
cv2.calibrateCamera e salva em recon/calib/intrinsics.json.

Uso:
  python recon/intrinsics.py --chessboard 9x6 --square-mm 25 --frames 20

Dicas:
  - Imprima o padrao em A4 sem escala, cole numa superficie RIGIDA (livro/chapa).
  - Cubra angulos e distancias variados; encha o frame ate as bordas (a borda
    e' onde a distorcao mais aparece).
  - Boa iluminacao difusa, sem reflexo no padrao.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--chessboard", default="9x6",
                    help="cantos INTERIORES, ex: 9x6 = 10x7 quadrados")
    ap.add_argument("--square-mm", type=float, default=25.0)
    ap.add_argument("--frames", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(HERE, "calib", "intrinsics.json"))
    args = ap.parse_args()

    cols, rows = (int(x) for x in args.chessboard.split("x"))
    pattern = (cols, rows)
    sq = args.square_mm / 1000.0  # metros

    objp = np.zeros((cols * rows, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2) * sq

    cam = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cam.isOpened():
        raise RuntimeError(f"webcam {args.camera} nao abriu")

    obj_points = []
    img_points = []
    last_save = 0.0
    print("[intrinsics] aperte ESPACO para capturar quando ver o padrao com cantos verdes")
    print("[intrinsics] aperte ESC para cancelar")
    while True:
        ok, frame = cam.read()
        if not ok:
            time.sleep(0.05); continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray, pattern,
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE)
        vis = frame.copy()
        if found:
            corners = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1),
                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01))
            cv2.drawChessboardCorners(vis, pattern, corners, found)
        cv2.putText(vis, f"{len(img_points)}/{args.frames}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("intrinsics", vis)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            print("[intrinsics] cancelado"); return
        # auto: pega 1 frame por segundo se padrao visivel; espaco forca.
        now = time.time()
        take = (k == 32) or (found and now - last_save > 1.0)
        if take and found:
            obj_points.append(objp.copy())
            img_points.append(corners.copy())
            last_save = now
            print(f"  capturado {len(img_points)}/{args.frames}")
            if len(img_points) >= args.frames:
                break

    cam.release()
    cv2.destroyAllWindows()
    if len(img_points) < 6:
        raise RuntimeError(f"poucos frames ({len(img_points)}); abortando")

    h, w = gray.shape
    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, (w, h), None, None)
    print(f"[intrinsics] RMS reproj err = {ret:.3f} pixel")
    out = {
        "image_width": w,
        "image_height": h,
        "fx": float(K[0, 0]), "fy": float(K[1, 1]),
        "cx": float(K[0, 2]), "cy": float(K[1, 2]),
        "distortion": [float(x) for x in dist.ravel()],
        "K": K.tolist(),
        "rms_reproj_px": float(ret),
        "n_frames": len(img_points),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[intrinsics] salvo em {args.out}")


if __name__ == "__main__":
    main()
