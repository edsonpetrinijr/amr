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
from vision.robot_scan import FairinoRobot, MockRobot, generate_scan_poses, generate_orbit_poses
from vision.analyzer import analyze_image


def build_components(cfg: ScanConfig, simulate: bool, target_offset: float = 20.0):
    detector = ArucoPartDetector(
        target_marker_id=cfg.target_marker_id,
        aruco_dict_name=cfg.aruco_dict,
        center_tol_px=cfg.center_tol_px,
        min_marker_size_px=cfg.min_marker_size_px,
    )
    if simulate:
        robot = MockRobot(motion_sleep=(cfg.sim_motion_sleep if not cfg.sim_turbo else False))
        base = robot.get_joints()
        if cfg.scan_mode == "orbit":
            target_pan_deg = base[cfg.orbit_pan_joint] + target_offset
            target_tilt_deg = base[cfg.orbit_tilt_joint]
            camera = MockCamera(
                robot,
                cfg.orbit_pan_joint,
                target_pan_deg,
                secondary_joint=cfg.orbit_tilt_joint,
                secondary_target_joint_deg=target_tilt_deg,
                aruco_dict_name=cfg.aruco_dict,
                marker_id=cfg.target_marker_id,
                width=cfg.frame_width,
                height=cfg.frame_height,
                noise_sigma=cfg.sim_noise_sigma,
                motion_blur=cfg.sim_motion_blur,
            )
        else:
            # GAP-8 fix: target offset is now a parameter so "not found" paths are testable.
            target_joint_deg = base[cfg.scan_joint] + target_offset
            camera = MockCamera(robot, cfg.scan_joint, target_joint_deg,
                            aruco_dict_name=cfg.aruco_dict, marker_id=cfg.target_marker_id,
                            width=cfg.frame_width, height=cfg.frame_height,
                            noise_sigma=cfg.sim_noise_sigma,
                            motion_blur=cfg.sim_motion_blur)
    else:
        robot = FairinoRobot(cfg.robot_ip)
        camera = OpenCVCamera(cfg.camera_index, cfg.frame_width, cfg.frame_height,
                              cfg.flush_frames)
    return robot, camera, detector


def run(cfg: ScanConfig, simulate: bool = False, target_offset: float = 20.0) -> dict:
    robot, camera, detector = build_components(cfg, simulate, target_offset)

    print("[1/4] Conectando ao robo...")
    robot.connect()
    robot.enable()

    try:
        base_joints = robot.get_joints()
        print(f"      Pose base (graus): {[round(j, 1) for j in base_joints]}")

        if cfg.scan_mode == "orbit":
            poses = generate_orbit_poses(
                base_joints,
                cfg.orbit_pan_joint,
                cfg.orbit_tilt_joint,
                cfg.orbit_levels,
                cfg.orbit_points_per_level,
                cfg.orbit_radius_bottom_deg,
                cfg.orbit_radius_top_deg,
                cfg.orbit_tilt_bottom_deg,
                cfg.orbit_tilt_top_deg,
                cfg.orbit_serpentine,
                cfg.orbit_lookat_joint,
                cfg.orbit_lookat_gain,
                cfg.orbit_enable_lookat_comp,
            )
            print(
                "[2/4] Orbita meia-esfera: "
                f"{len(poses)} poses "
                f"({cfg.orbit_levels} niveis x {cfg.orbit_points_per_level} pontos) "
                f"[pan j{cfg.orbit_pan_joint + 1}, tilt j{cfg.orbit_tilt_joint + 1}]"
            )
        else:
            poses = generate_scan_poses(
                base_joints,
                cfg.scan_joint,
                cfg.scan_start_deg,
                cfg.scan_end_deg,
                cfg.scan_step_deg,
            )
            print(f"[2/4] Varredura: {len(poses)} poses na junta j{cfg.scan_joint + 1}")

        # GAP-3 fix: validate all poses against soft limits BEFORE moving anything.
        robot.validate_scan_poses(poses)

        found_frame = None
        found_detection = None
        found_pose = None

        with camera:
            for i, pose in enumerate(poses):
                robot.move_joints(pose, cfg.move_vel, cfg.tool, cfg.user)
                dwell = cfg.sim_settle_time_s if (simulate and cfg.sim_turbo) else cfg.settle_time_s
                if dwell > 0:
                    time.sleep(dwell)
                frame = camera.read()
                det = detector.detect(frame)
                if cfg.scan_mode == "orbit":
                    level_idx = (i // cfg.orbit_points_per_level) + 1
                    ring_idx = (i % cfg.orbit_points_per_level) + 1
                    pan = round(pose[cfg.orbit_pan_joint], 1)
                    tilt = round(pose[cfg.orbit_tilt_joint], 1)
                    print(
                        f"      [{i + 1:02d}/{len(poses)}] "
                        f"L{level_idx:02d} P{ring_idx:02d} "
                        f"j{cfg.orbit_pan_joint + 1}={pan:>6}  "
                        f"j{cfg.orbit_tilt_joint + 1}={tilt:>6}  {det.message}"
                    )
                else:
                    ang = round(pose[cfg.scan_joint], 1)
                    print(f"      [{i + 1:02d}/{len(poses)}] j{cfg.scan_joint + 1}={ang:>6}  {det.message}")
                if det.in_position:
                    found_frame = frame
                    found_detection = det
                    found_pose = pose
                    break

        if found_frame is None:
            print("[3/4] Peca NAO encontrada na posicao certa durante a varredura.")
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

        return {"encontrado": True, "analise": analysis, "imagem": img_path}

    finally:
        # GAP-1 fix: disconnect runs on every exit path — normal, exception, Ctrl+C.
        robot.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Varredura eye-in-hand Fairino + visao")
    parser.add_argument("--simulate", action="store_true", help="Roda sem hardware (mock)")
    parser.add_argument("--ip", default=None, help="IP do robo")
    parser.add_argument("--camera", type=int, default=None, help="Indice da webcam USB")
    parser.add_argument("--marker-id", type=int, default=None, help="ID do marcador ArUco alvo")
    parser.add_argument("--target-offset", type=float, default=20.0,
                        help="Offset em graus da peca simulada relativo a pose base "
                             "(use valor fora do range para testar 'nao encontrado')")
    parser.add_argument("--output-dir", default=None,
                        help="Diretorio de saida para imagens e JSON (default: captures)")
    parser.add_argument("--scan-mode", choices=["single", "orbit"], default=None,
                        help="Modo de varredura: single (1 junta) ou orbit (meia-esfera)")
    parser.add_argument("--sim-turbo", choices=["on", "off"], default=None,
                        help="No modo --simulate: on = max velocidade, off = mais realista")
    args = parser.parse_args()

    cfg = ScanConfig()
    if args.ip is not None:
        cfg.robot_ip = args.ip
    if args.camera is not None:
        cfg.camera_index = args.camera
    if args.marker_id is not None:
        cfg.target_marker_id = args.marker_id
    if args.output_dir is not None:
        cfg.output_dir = args.output_dir
    if args.scan_mode is not None:
        cfg.scan_mode = args.scan_mode
    if args.sim_turbo is not None:
        cfg.sim_turbo = (args.sim_turbo == "on")

    run(cfg, simulate=args.simulate, target_offset=args.target_offset)


if __name__ == "__main__":
    main()
