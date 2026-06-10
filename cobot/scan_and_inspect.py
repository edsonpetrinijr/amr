"""Orquestrador: varre rotacionando a camera, encontra a peca na posicao certa,
captura a imagem e roda a analise.

Uso:
    python scan_and_inspect.py            # robo + webcam reais
    python scan_and_inspect.py --simulate # 100% simulado (sem hardware)
"""
from __future__ import annotations
import argparse
import json
import os
import time
from datetime import datetime

import cv2

from vision.config import ScanConfig
from vision.camera import OpenCVCamera, MockCamera
from vision.detector import ArucoPartDetector
from vision.robot_scan import FairinoRobot, MockRobot, generate_scan_poses
from vision.analyzer import analyze_image


def build_components(cfg: ScanConfig, simulate: bool):
    detector = ArucoPartDetector(
        target_marker_id=cfg.target_marker_id,
        aruco_dict_name=cfg.aruco_dict,
        center_tol_px=cfg.center_tol_px,
        min_marker_size_px=cfg.min_marker_size_px,
    )
    if simulate:
        robot = MockRobot()
        # No simulado, a peca esta "na posicao certa" no alvo abaixo (offset 20 graus).
        base = robot.get_joints()
        target_joint_deg = base[cfg.scan_joint] + 20.0
        camera = MockCamera(robot, cfg.scan_joint, target_joint_deg,
                            aruco_dict_name=cfg.aruco_dict, marker_id=cfg.target_marker_id,
                            width=cfg.frame_width, height=cfg.frame_height)
    else:
        robot = FairinoRobot(cfg.robot_ip)
        camera = OpenCVCamera(cfg.camera_index, cfg.frame_width, cfg.frame_height,
                              cfg.flush_frames)
    return robot, camera, detector


def run(cfg: ScanConfig, simulate: bool = False) -> dict:
    robot, camera, detector = build_components(cfg, simulate)

    print("[1/4] Conectando ao robo...")
    robot.connect()
    robot.enable()

    base_joints = robot.get_joints()
    print(f"      Pose base (graus): {[round(j, 1) for j in base_joints]}")

    poses = generate_scan_poses(base_joints, cfg.scan_joint,
                                cfg.scan_start_deg, cfg.scan_end_deg, cfg.scan_step_deg)
    print(f"[2/4] Varredura: {len(poses)} poses na junta j{cfg.scan_joint + 1}")

    found_frame = None
    found_detection = None
    found_pose = None

    with camera:
        for i, pose in enumerate(poses):
            robot.move_joints(pose, cfg.move_vel, cfg.tool, cfg.user)
            time.sleep(cfg.settle_time_s)  # estabiliza antes de capturar
            frame = camera.read()
            det = detector.detect(frame)
            ang = round(pose[cfg.scan_joint], 1)
            print(f"      [{i + 1:02d}/{len(poses)}] j{cfg.scan_joint + 1}={ang:>6}  {det.message}")
            if det.in_position:
                found_frame = frame
                found_detection = det
                found_pose = pose
                break

    if found_frame is None:
        print("[3/4] Peca NAO encontrada na posicao certa durante a varredura.")
        robot.disconnect()
        return {"encontrado": False}

    print("[3/4] Peca encontrada na posicao certa! Capturando e analisando...")
    os.makedirs(cfg.output_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_path = os.path.join(cfg.output_dir, f"peca_{stamp}.png")
    cv2.imwrite(img_path, found_frame)

    analysis = analyze_image(found_frame, found_detection)
    analysis["pose_robo_graus"] = [round(j, 2) for j in found_pose]
    analysis["imagem"] = img_path

    json_path = os.path.join(cfg.output_dir, f"peca_{stamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"[4/4] Salvo: {img_path}")
    print(f"      Analise: {json_path}")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    robot.disconnect()
    return {"encontrado": True, "analise": analysis, "imagem": img_path}


def main():
    parser = argparse.ArgumentParser(description="Varredura eye-in-hand Fairino + visao")
    parser.add_argument("--simulate", action="store_true", help="Roda sem hardware (mock)")
    parser.add_argument("--ip", default=None, help="IP do robo")
    parser.add_argument("--camera", type=int, default=None, help="Indice da webcam USB")
    parser.add_argument("--marker-id", type=int, default=None, help="ID do marcador ArUco alvo")
    args = parser.parse_args()

    cfg = ScanConfig()
    if args.ip is not None:
        cfg.robot_ip = args.ip
    if args.camera is not None:
        cfg.camera_index = args.camera
    if args.marker_id is not None:
        cfg.target_marker_id = args.marker_id

    run(cfg, simulate=args.simulate)


if __name__ == "__main__":
    main()
