"""Captura sincronizada: para cada keypoint da orbita, foto + pose do robo.

Saida:
  outputs/<run>/raw/0001.png       <- frame BGR da webcam
  outputs/<run>/raw/0001.json      <- pose do flange no frame BASE + timestamp
  outputs/<run>/run.json           <- meta do run (intrinsics, hand-eye, ts)

Pose no JSON:
  {
    "index": int,
    "joints_deg": [j1..j6],
    "flange_pose_base": [x, y, z, rx, ry, rz],   # mm + graus
    "T_base_flange":   [[...4x4...]],            # metros
    "ts": float
  }

Reusa a sequencia IK ja resolvida (orbit_ik.orbit_joint_sequence), as gates
de seguranca (limites URDF + chao + esfera) e o FairinoRobot. Em cada pose,
faz MoveJ BLOQUEANTE, espera estabilizar, captura.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime

import cv2

# Permite importar `sim`, `vision`, `fairino` (ficam na raiz do projeto).
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sim.orbit_ik import (
    OrbitParams,
    orbit_joint_sequence,
    urdf_joint_limits_deg,
    validate_sequence_limits,
    validate_sequence_safety,
)
from vision.robot_scan import FairinoRobot, MockRobot


def _ensure_dirs(out_dir: str) -> str:
    raw = os.path.join(out_dir, "raw")
    os.makedirs(raw, exist_ok=True)
    return raw


def _load_calib(path: str | None):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _grab_stable(cam: cv2.VideoCapture, settle_frames: int = 5):
    """Le N frames seguidos para o sensor estabilizar (AE/AF/AWB) e devolve o ultimo."""
    frame = None
    for _ in range(settle_frames):
        ok, frame = cam.read()
        if not ok:
            time.sleep(0.05)
    return frame


def main():
    ap = argparse.ArgumentParser(description="Captura orbita: imagem + pose")
    ap.add_argument("--ip", default="192.168.58.2")
    ap.add_argument("--simulate", action="store_true", help="MockRobot (sem hardware)")
    ap.add_argument("--camera", type=int, default=0, help="indice da webcam")
    ap.add_argument("--out", default="recon/outputs/poc1", help="pasta do run")
    ap.add_argument("--vel", type=float, default=15.0, help="vel MoveJ (%) entre poses")
    ap.add_argument("--pause-ms", type=int, default=400,
                    help="pausa apos chegar antes de capturar (estabilizacao)")
    ap.add_argument("--intrinsics", default="recon/calib/intrinsics.json")
    ap.add_argument("--hand-eye", default="recon/calib/hand_eye.json")
    # parametros da orbita (mesmos defaults do bridge)
    ap.add_argument("--radius-bottom", type=float, default=None)
    ap.add_argument("--radius-top", type=float, default=None)
    ap.add_argument("--levels", type=int, default=None)
    ap.add_argument("--points-per-level", type=int, default=None)
    args = ap.parse_args()

    # 1) Monta params da orbita.
    params = OrbitParams()
    if args.radius_bottom is not None: params.radius_bottom = args.radius_bottom
    if args.radius_top is not None:    params.radius_top = args.radius_top
    if args.levels is not None:        params.levels = args.levels
    if args.points_per_level is not None: params.points_per_level = args.points_per_level

    # 2) Gera + valida a sequencia (mesma source-of-truth do run_orbit.py).
    print("[capture] gerando sequencia IK...")
    seq = orbit_joint_sequence(params)
    print(f"[capture] {len(seq)} poses")
    validate_sequence_limits(seq, urdf_joint_limits_deg())
    validate_sequence_safety(seq, params.center,
                             z_floor=params.z_floor, r_safe=params.r_safe)
    print("[capture] OK: limites URDF + seguranca geometrica")

    # 3) Conecta robo + camera.
    robot = MockRobot() if args.simulate else FairinoRobot(ip=args.ip)
    print(f"[capture] conectando {'MOCK' if args.simulate else args.ip}...")
    robot.connect(); robot.enable()
    if not args.simulate:
        robot.validate_scan_poses(seq)

    cam = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cam.isOpened():
        raise RuntimeError(f"webcam {args.camera} nao abriu")
    # Desativa auto-exposure/AF/AWB se possivel (reconstrucao adora estabilidade).
    cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    # frame warmup (descarta lixo inicial do driver)
    for _ in range(10):
        cam.read()

    # 4) Roda a orbita: MoveJ bloqueante + pausa + captura.
    raw_dir = _ensure_dirs(args.out)
    run_meta = {
        "ts_iso": datetime.now().isoformat(timespec="seconds"),
        "ip": None if args.simulate else args.ip,
        "intrinsics": _load_calib(args.intrinsics),
        "hand_eye": _load_calib(args.hand_eye),
        "orbit_params": {
            "center": list(params.center),
            "radius_bottom": params.radius_bottom,
            "radius_top": params.radius_top,
            "z_bottom": params.z_bottom,
            "z_top": params.z_top,
            "levels": params.levels,
            "points_per_level": params.points_per_level,
        },
        "n_poses": len(seq),
        "vel_pct": args.vel,
    }
    with open(os.path.join(args.out, "run.json"), "w", encoding="utf-8") as f:
        json.dump(run_meta, f, indent=2)

    try:
        for i, pose in enumerate(seq):
            print(f"[capture] {i+1}/{len(seq)}  j={[round(v,1) for v in pose]}")
            robot.move_joints(pose, vel=args.vel, tool=0, user=0)
            time.sleep(args.pause_ms / 1000.0)
            frame = _grab_stable(cam, settle_frames=5)
            if frame is None:
                print(f"  [warn] sem frame na pose {i+1}; pulando")
                continue
            # pose real lida (nao a alvo) -- mais fiel.
            joints_real = robot.get_joints()
            flange = None
            if not args.simulate:
                try:
                    res = robot.robot.GetActualToolFlangePose(1)
                    if isinstance(res, tuple) and res[0] == 0:
                        flange = list(res[1])
                except Exception as e:  # noqa: BLE001
                    print(f"  [warn] flange pose falhou: {e}")
            img_path = os.path.join(raw_dir, f"{i+1:04d}.png")
            pose_path = os.path.join(raw_dir, f"{i+1:04d}.json")
            cv2.imwrite(img_path, frame)
            with open(pose_path, "w", encoding="utf-8") as f:
                json.dump({
                    "index": i + 1,
                    "joints_deg": joints_real,
                    "flange_pose_base": flange,
                    "ts": time.time(),
                }, f, indent=2)
        print(f"[capture] done -> {args.out}")
    finally:
        cam.release()
        try: robot.disconnect()
        except Exception: pass


if __name__ == "__main__":
    main()
