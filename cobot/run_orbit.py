"""Executa a orbita de inspecao IK no robo FR5 (real ou mock).

A sequencia de poses de junta vem de sim.orbit_ik.orbit_joint_sequence() — a
MESMA fonte da verdade que o viewer/sim reproduz (plan.motion_deg densificado,
passos <= ~6 deg, sem saltos bruscos). Assim, o que voce ve na simulacao e o
que o robo real executa sao identicos.

Seguranca:
  - valida TODAS as poses contra os limites do URDF e contra os soft limits do
    controlador ANTES de mover qualquer junta;
  - usa velocidade conservadora por padrao (--vel 15);
  - cada MoveJ e bloqueante e faz polling de conclusao + checagem de falha
    (FairinoRobot._wait_joints_reached); qualquer erro aborta a sequencia.

Uso:
    python run_orbit.py --simulate          # mock, sem hardware (valida tudo)
    python run_orbit.py --dry-run           # robo real, so valida (nao move)
    python run_orbit.py --ip 192.168.58.2   # robo real, EXECUTA a orbita
    python run_orbit.py --ip 192.168.58.2 --vel 10   # ainda mais devagar
"""
from __future__ import annotations

import argparse

from sim.orbit_ik import (
    OrbitParams,
    orbit_joint_sequence,
    urdf_joint_limits_deg,
    validate_sequence_limits,
    validate_sequence_safety,
)
from vision.robot_scan import FairinoRobot, MockRobot


def build_params(args) -> OrbitParams:
    p = OrbitParams()
    if args.radius_bottom is not None:
        p.radius_bottom = args.radius_bottom
    if args.radius_top is not None:
        p.radius_top = args.radius_top
    if args.levels is not None:
        p.levels = args.levels
    if args.points_per_level is not None:
        p.points_per_level = args.points_per_level
    if args.z_floor is not None:
        p.z_floor = args.z_floor
    if args.r_safe is not None:
        p.r_safe = args.r_safe
    return p


def main():
    ap = argparse.ArgumentParser(description="Executa a orbita de inspecao IK no FR5")
    ap.add_argument("--simulate", action="store_true",
                    help="Roda no MockRobot (sem hardware); valida geracao + limites")
    ap.add_argument("--dry-run", action="store_true",
                    help="Conecta no robo real mas SO valida (nao envia movimento)")
    ap.add_argument("--ip", default="192.168.58.2", help="IP do robo real")
    ap.add_argument("--vel", type=float, default=15.0,
                    help="Velocidade MoveJ em %% (conservador; default 15)")
    ap.add_argument("--radius-bottom", type=float, default=None)
    ap.add_argument("--radius-top", type=float, default=None)
    ap.add_argument("--levels", type=int, default=None)
    ap.add_argument("--points-per-level", type=int, default=None)
    ap.add_argument("--z-floor", type=float, default=None,
                    help="Margem de seguranca acima do chao (m); default 0.02")
    ap.add_argument("--r-safe", type=float, default=None,
                    help="Raio da esfera de seguranca da peca (m); default 0.06")
    ap.add_argument("--force-unsafe-test", action="store_true",
                    help="Auto-teste: injeta uma pose insegura para provar que "
                         "o gate de seguranca ABORTA sem mover (nao usar em prod)")
    args = ap.parse_args()

    # 1) Gera a sequencia (single source of truth, identica ao sim).
    params = build_params(args)
    print("[1/4] Gerando orbita IK (fonte da verdade do sim)...")
    seq = orbit_joint_sequence(params)
    print(f"      {len(seq)} poses de junta (densificadas, passos <= ~6 deg)")

    if args.force_unsafe_test:
        # Pose claramente insegura (cadeia estendida para baixo do chao) para
        # validar que o gate de seguranca a rejeita ANTES de qualquer movimento.
        seq = list(seq) + [[0.0, 80.0, 0.0, 0.0, 0.0, 0.0]]
        print("      [force-unsafe-test] pose insegura injetada no fim da seq")

    # 2) Valida contra os limites do URDF (vale em mock e real).
    print("[2/4] Validando poses contra os limites de junta do URDF...")
    limits = urdf_joint_limits_deg()
    validate_sequence_limits(seq, limits)
    print("      OK: todas as poses dentro dos limites do URDF")

    # 2b) GATE DE SEGURANCA geometrica: chao + esfera da peca. Aborta se
    #     QUALQUER pose furar o chao ou invadir a peca (mesma checagem do sim).
    print("[2b ] Validando SEGURANCA geometrica (chao + peca)...")
    validate_sequence_safety(seq, params.center,
                             z_floor=params.z_floor, r_safe=params.r_safe)
    print(f"      OK: todas as poses seguras "
          f"(z_floor={params.z_floor} m, r_safe={params.r_safe} m)")

    if not seq:
        print("      Nenhuma pose gerada; abortando.")
        return

    # 3) Conecta (mock ou real) e valida contra os soft limits do controlador.
    robot = MockRobot(motion_sleep=False) if args.simulate else FairinoRobot(ip=args.ip)
    mode = "MOCK" if args.simulate else f"REAL {args.ip}"
    print(f"[3/4] Conectando ao robo ({mode})...")
    robot.connect()
    robot.enable()
    try:
        robot.validate_scan_poses(seq)  # no-op no mock; soft limits no real
        print("      OK: validacao de soft limits concluida")

        if args.dry_run:
            print("[4/4] --dry-run: validacao OK, nenhum movimento enviado.")
            return

        # 4) Percorre a sequencia com velocidade conservadora; para em qualquer erro.
        print(f"[4/4] Executando {len(seq)} poses a vel={args.vel}%...")
        for i, pose in enumerate(seq):
            robot.move_joints(pose, vel=args.vel, tool=0, user=0)
            if (i + 1) % 20 == 0 or i == len(seq) - 1:
                print(f"      [{i + 1:03d}/{len(seq)}] "
                      f"j={[round(v, 1) for v in pose]}")
        print("      Orbita concluida.")
    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
