"""Roda a pipeline densa do COLMAP com poses CONHECIDAS.

Pre-requisito: pasta gerada por to_colmap.py contem:
  colmap/images/*.png
  colmap/sparse/0/{cameras.txt, images.txt, points3D.txt}

Pipeline COLMAP known-pose (CLI):
  1. feature_extractor       (detecta SIFT)
  2. exhaustive_matcher      (casa features entre TODOS os pares)
  3. point_triangulator      (NAO roda SfM -- so' triangula com poses dadas)
  4. image_undistorter       (rectifica)
  5. patch_match_stereo      (mapas de profundidade densos -- CARO em CPU!)
  6. stereo_fusion           (junta depth maps -> nuvem densa)
  7. poisson_mesher          (nuvem -> mesh texturizado)

Saidas:
  <run>/colmap/dense/fused.ply        <- nuvem densa
  <run>/colmap/dense/meshed-poisson.ply <- mesh

Esqueleto: assume `colmap` no PATH. patch_match_stereo precisa CUDA p/ rodar
em tempo decente -- em CPU pode levar HORAS por dezenas de imagens. Comece
com poucos frames (~30) para ter um sanity check.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys


def run(cmd):
    print(">>", " ".join(cmd))
    r = subprocess.run(cmd, shell=False)
    if r.returncode != 0:
        raise SystemExit(f"falhou: {' '.join(cmd)} (rc={r.returncode})")


def have_colmap() -> bool:
    return shutil.which("colmap") is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="pasta do run")
    ap.add_argument("--backend", choices=["colmap"], default="colmap")
    ap.add_argument("--skip-dense", action="store_true",
                    help="para apos triangulacao (rapido) -- so' nuvem esparsa")
    args = ap.parse_args()

    if not have_colmap():
        print("[reconstruct] ERRO: `colmap` nao esta no PATH.")
        print("  Windows: https://github.com/colmap/colmap/releases")
        print("  Depois adicione a pasta com colmap.exe ao PATH e reinicie o shell.")
        sys.exit(2)

    colmap_root = os.path.join(args.inp, "colmap")
    if not os.path.isdir(colmap_root):
        raise SystemExit(f"sem pasta {colmap_root} -- rode to_colmap.py antes")

    db = os.path.join(colmap_root, "database.db")
    images = os.path.join(colmap_root, "images")
    sparse_in = os.path.join(colmap_root, "sparse", "0")
    sparse_out = os.path.join(colmap_root, "sparse", "triangulated")
    dense = os.path.join(colmap_root, "dense")
    os.makedirs(sparse_out, exist_ok=True)
    os.makedirs(dense, exist_ok=True)

    # 1. feature extraction
    run(["colmap", "feature_extractor",
         "--database_path", db,
         "--image_path", images,
         "--ImageReader.single_camera", "1",
         "--ImageReader.camera_model", "PINHOLE"])

    # 2. matching
    run(["colmap", "exhaustive_matcher",
         "--database_path", db])

    # 3. triangulate (NAO mapper -- usamos poses conhecidas)
    run(["colmap", "point_triangulator",
         "--database_path", db,
         "--image_path", images,
         "--input_path", sparse_in,
         "--output_path", sparse_out])

    if args.skip_dense:
        print(f"[reconstruct] OK (esparso) em {sparse_out}")
        return

    # 4. undistort
    run(["colmap", "image_undistorter",
         "--image_path", images,
         "--input_path", sparse_out,
         "--output_path", dense,
         "--output_type", "COLMAP"])

    # 5. patch match stereo (CARO -- CUDA recomendado)
    run(["colmap", "patch_match_stereo",
         "--workspace_path", dense,
         "--workspace_format", "COLMAP",
         "--PatchMatchStereo.geom_consistency", "true"])

    # 6. fusion
    run(["colmap", "stereo_fusion",
         "--workspace_path", dense,
         "--workspace_format", "COLMAP",
         "--input_type", "geometric",
         "--output_path", os.path.join(dense, "fused.ply")])

    # 7. mesh
    run(["colmap", "poisson_mesher",
         "--input_path", os.path.join(dense, "fused.ply"),
         "--output_path", os.path.join(dense, "meshed-poisson.ply")])

    print(f"[reconstruct] DONE")
    print(f"  nuvem densa: {os.path.join(dense, 'fused.ply')}")
    print(f"  mesh:        {os.path.join(dense, 'meshed-poisson.ply')}")


if __name__ == "__main__":
    main()
