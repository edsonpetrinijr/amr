"""Calibracao mao-olho (hand-eye): T_flange->camera.

Move o robo para N poses olhando um marcador ArUco fixo na bancada. Em cada
pose, registra (T_base_flange via robo) e (T_camera_marker via ArUco). Resolve
o classico AX = XB de Tsai/Park usando cv2.calibrateHandEye -> devolve a
transformacao Camera <- Flange (4x4) que precisa para colocar cada foto da
captura no frame do mundo.

Uso (semi-automatico, voce move o robo via UI ou jog manual):
  python recon/hand_eye.py --ip 192.168.58.2 --aruco-size-mm 50 --frames 15

Saida: recon/calib/hand_eye.json com T_flange_camera (4x4 em metros).

Esqueleto -- precisa ser refinado com poses bem distribuidas e visualizacao
do reproj error por pose antes de salvar.
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
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from vision.robot_scan import FairinoRobot


def _load_intrinsics(path: str):
    with open(path, "r", encoding="utf-8") as f:
        c = json.load(f)
    K = np.array(c["K"], dtype=np.float64)
    dist = np.array(c.get("distortion", []), dtype=np.float64)
    return K, dist


def _flange_to_T(pose):
    """Converte [x,y,z (mm), rx,ry,rz (graus)] -> T 4x4 (metros, frame base)."""
    x, y, z, rx, ry, rz = pose
    R, _ = cv2.Rodrigues(np.deg2rad([rx, ry, rz]).reshape(3, 1))
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = [x / 1000.0, y / 1000.0, z / 1000.0]
    return T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", default="192.168.58.2")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--frames", type=int, default=15)
    ap.add_argument("--aruco-size-mm", type=float, default=50.0)
    ap.add_argument("--aruco-dict", default="DICT_4X4_50")
    ap.add_argument("--intrinsics", default=os.path.join(HERE, "calib", "intrinsics.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "calib", "hand_eye.json"))
    args = ap.parse_args()

    K, dist = _load_intrinsics(args.intrinsics)
    aruco_size = args.aruco_size_mm / 1000.0

    aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, args.aruco_dict))
    detector = cv2.aruco.ArucoDetector(aruco_dict, cv2.aruco.DetectorParameters())

    robot = FairinoRobot(ip=args.ip)
    print(f"[hand_eye] conectando {args.ip}...")
    robot.connect(); robot.enable()

    cam = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cam.isOpened():
        raise RuntimeError(f"webcam {args.camera} nao abriu")
    cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    for _ in range(10): cam.read()

    R_base_flange, t_base_flange = [], []
    R_cam_target, t_cam_target = [], []
    print("[hand_eye] mova o robo (manualmente / jog / via UI) e aperte ESPACO em cada pose boa")
    print("[hand_eye] ESC quando tiver >=N frames com marcador estavel")

    try:
        while True:
            ok, frame = cam.read()
            if not ok: time.sleep(0.05); continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)
            vis = frame.copy()
            ok_marker = False
            if ids is not None and len(ids) > 0:
                cv2.aruco.drawDetectedMarkers(vis, corners, ids)
                # pose estimation para o PRIMEIRO marcador detectado.
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners, aruco_size, K, dist)
                cv2.drawFrameAxes(vis, K, dist, rvec[0], tvec[0], aruco_size)
                ok_marker = True
            cv2.putText(vis, f"{len(R_base_flange)}/{args.frames}  ESPACO=capturar  ESC=fim",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("hand_eye", vis)
            k = cv2.waitKey(1) & 0xFF
            if k == 27: break
            if k == 32 and ok_marker:
                res = robot.robot.GetActualToolFlangePose(1)
                if not (isinstance(res, tuple) and res[0] == 0):
                    print("  [warn] flange pose falhou; pulando")
                    continue
                T_bf = _flange_to_T(list(res[1]))
                R_bf = T_bf[:3, :3]
                t_bf = T_bf[:3, 3]
                R_ct, _ = cv2.Rodrigues(rvec[0].reshape(3, 1))
                t_ct = tvec[0].reshape(3)
                R_base_flange.append(R_bf); t_base_flange.append(t_bf)
                R_cam_target.append(R_ct); t_cam_target.append(t_ct)
                print(f"  capturado {len(R_base_flange)}/{args.frames}")
                if len(R_base_flange) >= args.frames: break
    finally:
        cam.release(); cv2.destroyAllWindows()
        try: robot.disconnect()
        except Exception: pass

    if len(R_base_flange) < 5:
        raise RuntimeError(f"poucas poses ({len(R_base_flange)}); abortando")

    R_fc, t_fc = cv2.calibrateHandEye(
        R_base_flange, t_base_flange,
        R_cam_target, t_cam_target,
        method=cv2.CALIB_HAND_EYE_PARK)
    T_fc = np.eye(4)
    T_fc[:3, :3] = R_fc; T_fc[:3, 3] = t_fc.ravel()
    print("[hand_eye] T_flange_camera =\n", T_fc)

    out = {
        "method": "PARK",
        "n_poses": len(R_base_flange),
        "T_flange_camera": T_fc.tolist(),
        "translation_m": t_fc.ravel().tolist(),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[hand_eye] salvo em {args.out}")


if __name__ == "__main__":
    main()
