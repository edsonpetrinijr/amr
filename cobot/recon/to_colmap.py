"""Converte uma captura (raw/*.png + raw/*.json + calib) para formato COLMAP.

COLMAP com poses CONHECIDAS dispensa o passo SfM caro. Geramos:
  <out>/sparse/0/cameras.txt   -- intrinsics (PINHOLE)
  <out>/sparse/0/images.txt    -- pose de cada imagem (qw qx qy qz tx ty tz)
  <out>/sparse/0/points3D.txt  -- vazio (COLMAP densifica depois)
  <out>/images/*.png           -- imagens renomeadas

Convencao COLMAP: T_world_camera (camera no frame world). Aqui world = BASE do
robo. Calculamos para cada frame:
    T_base_camera = T_base_flange * T_flange_camera

Esqueleto: assume intrinsics e hand-eye ja calibrados.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil

import cv2
import numpy as np


def _T_from_flange_pose(pose):
    """[x,y,z mm, rx,ry,rz deg] -> T 4x4 (metros)."""
    x, y, z, rx, ry, rz = pose
    R, _ = cv2.Rodrigues(np.deg2rad([rx, ry, rz]).reshape(3, 1))
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = [x/1000, y/1000, z/1000]
    return T


def _R_to_quat(R: np.ndarray):
    """Matriz rotacao -> quaternion (qw, qx, qy, qz). Convencao COLMAP."""
    tr = R[0, 0] + R[1, 1] + R[2, 2]
    if tr > 0:
        S = np.sqrt(tr + 1.0) * 2
        qw = 0.25 * S
        qx = (R[2, 1] - R[1, 2]) / S
        qy = (R[0, 2] - R[2, 0]) / S
        qz = (R[1, 0] - R[0, 1]) / S
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        S = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
        qw = (R[2, 1] - R[1, 2]) / S
        qx = 0.25 * S
        qy = (R[0, 1] + R[1, 0]) / S
        qz = (R[0, 2] + R[2, 0]) / S
    elif R[1, 1] > R[2, 2]:
        S = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
        qw = (R[0, 2] - R[2, 0]) / S
        qx = (R[0, 1] + R[1, 0]) / S
        qy = 0.25 * S
        qz = (R[1, 2] + R[2, 1]) / S
    else:
        S = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
        qw = (R[1, 0] - R[0, 1]) / S
        qx = (R[0, 2] + R[2, 0]) / S
        qy = (R[1, 2] + R[2, 1]) / S
        qz = 0.25 * S
    return qw, qx, qy, qz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True,
                    help="pasta do run (contem raw/ e run.json)")
    ap.add_argument("--out", default=None,
                    help="pasta de saida COLMAP (default: <in>/colmap)")
    args = ap.parse_args()

    in_dir = args.inp
    out_dir = args.out or os.path.join(in_dir, "colmap")
    raw_dir = os.path.join(in_dir, "raw")
    img_out = os.path.join(out_dir, "images")
    sparse_out = os.path.join(out_dir, "sparse", "0")
    os.makedirs(img_out, exist_ok=True)
    os.makedirs(sparse_out, exist_ok=True)

    with open(os.path.join(in_dir, "run.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)
    intr = meta.get("intrinsics")
    he = meta.get("hand_eye")
    if not intr or not he:
        raise RuntimeError("run.json sem intrinsics ou hand_eye -- calibre antes")
    K = np.array(intr["K"], dtype=np.float64)
    T_fc = np.array(he["T_flange_camera"], dtype=np.float64)
    w, h = intr["image_width"], intr["image_height"]

    # cameras.txt -- 1 camera PINHOLE (intrinsics fixos).
    with open(os.path.join(sparse_out, "cameras.txt"), "w", encoding="utf-8") as f:
        f.write("# camera_id model width height fx fy cx cy\n")
        f.write(f"1 PINHOLE {w} {h} {K[0,0]} {K[1,1]} {K[0,2]} {K[1,2]}\n")

    # images.txt -- pose por imagem.
    lines = ["# image_id qw qx qy qz tx ty tz camera_id name\n"]
    pose_files = sorted(glob.glob(os.path.join(raw_dir, "*.json")))
    for i, pj in enumerate(pose_files, start=1):
        with open(pj, "r", encoding="utf-8") as f:
            d = json.load(f)
        if not d.get("flange_pose_base"):
            print(f"  [skip] {pj}: sem flange_pose_base"); continue
        T_bf = _T_from_flange_pose(d["flange_pose_base"])
        T_bc = T_bf @ T_fc          # camera no frame base (=world)
        # COLMAP guarda T_world_camera INVERTIDA: pose = camera<-world.
        T_cw = np.linalg.inv(T_bc)
        R = T_cw[:3, :3]; t = T_cw[:3, 3]
        qw, qx, qy, qz = _R_to_quat(R)
        name = os.path.basename(pj).replace(".json", ".png")
        # copia imagem.
        src = os.path.join(raw_dir, name)
        if not os.path.exists(src):
            print(f"  [warn] sem imagem {src}; pulando"); continue
        shutil.copy2(src, os.path.join(img_out, name))
        lines.append(f"{i} {qw} {qx} {qy} {qz} {t[0]} {t[1]} {t[2]} 1 {name}\n")
        # linha vazia (sem keypoints conhecidos -- COLMAP encontra).
        lines.append("\n")
    with open(os.path.join(sparse_out, "images.txt"), "w", encoding="utf-8") as f:
        f.writelines(lines)
    # points3D.txt vazio (COLMAP preenche depois).
    open(os.path.join(sparse_out, "points3D.txt"), "w", encoding="utf-8").close()

    print(f"[to_colmap] escrito em {out_dir}")
    print(f"           {len(pose_files)} poses -> {(len(lines)-1)//2} imagens")
    print("Proximo passo: rodar `python recon/reconstruct.py --in <run> --backend colmap`")


if __name__ == "__main__":
    main()
