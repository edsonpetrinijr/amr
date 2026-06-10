"""Orbita de inspecao baseada em geometria cartesiana + IK numerico.

Gera uma orbita REAL: a ponta (flange / wrist3_Link) do FR5 percorre circulos
empilhados ao redor da peca, de baixo para cima, com a camera (eixo +Z local da
flange) sempre apontando para o centro C da peca.

Pipeline:
  FASE 1 - geometria: pontos cartesianos em aneis ao redor de C (frame BASE,
           metros) + orientacao look-at desejada (eixo de aproximacao -> C).
  FASE 2 - FK a partir do URDF + IK numerico por DLS (damped least squares)
           com Jacobiano por diferencas finitas. Respeita limites de junta.
  FASE 3 - sequencia de baixo para cima, com seed = solucao anterior
           (continuidade) e rejeicao de saltos grandes de junta.

Sem heuristicas seno/cosseno em juntas. Sem libs externas alem de numpy.
"""
from __future__ import annotations

import math
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
URDF_PATH = os.path.join(SIM_DIR, "fr5.urdf")

# Cadeia cinematica usada na FK: base_link -> ... -> wrist3_Link (a "ponta"
# que o viewer desenha). Cada item e o nome do <joint> revoluto.
CHAIN_JOINTS = ["j1", "j2", "j3", "j4", "j5", "j6"]

# Eixo de aproximacao da ferramenta no frame local da flange (camera olha +Z).
TOOL_APPROACH_LOCAL = np.array([0.0, 0.0, 1.0])


# --------------------------------------------------------------------------- #
# Parse do URDF
# --------------------------------------------------------------------------- #
@dataclass
class JointDef:
    name: str
    xyz: np.ndarray          # origin translation (m)
    rpy: np.ndarray          # origin rotation (roll, pitch, yaw) rad
    axis: np.ndarray         # eixo de rotacao (unit) no frame do joint
    lower: float             # limite inferior (rad)
    upper: float             # limite superior (rad)
    R0: np.ndarray = field(default=None)  # rotacao fixa do origin (cache)


def _rpy_to_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """Convencao URDF: R = Rz(yaw) @ Ry(pitch) @ Rx(roll) (eixos fixos)."""
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def _axis_angle_matrix(axis: np.ndarray, theta: float) -> np.ndarray:
    """Rodrigues: rotacao de 'theta' rad em torno de 'axis' (unit)."""
    a = axis / (np.linalg.norm(axis) + 1e-12)
    x, y, z = a
    c, s = math.cos(theta), math.sin(theta)
    C = 1.0 - c
    return np.array([
        [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, c + z * z * C],
    ])


def parse_urdf_chain(urdf_path: str = URDF_PATH) -> List[JointDef]:
    """Le origins (xyz/rpy), axis e limits dos joints j1..j6 do URDF."""
    tree = ET.parse(urdf_path)
    root = tree.getroot()
    by_name = {}
    for j in root.findall("joint"):
        name = j.get("name")
        if name not in CHAIN_JOINTS:
            continue
        origin = j.find("origin")
        xyz = np.array([float(v) for v in (origin.get("xyz", "0 0 0")).split()])
        rpy = np.array([float(v) for v in (origin.get("rpy", "0 0 0")).split()])
        axis_el = j.find("axis")
        axis = np.array([float(v) for v in (axis_el.get("xyz", "0 0 1")).split()])
        lim = j.find("limit")
        lower = float(lim.get("lower")) if lim is not None else -math.pi
        upper = float(lim.get("upper")) if lim is not None else math.pi
        jd = JointDef(name=name, xyz=xyz, rpy=rpy, axis=axis,
                      lower=lower, upper=upper)
        jd.R0 = _rpy_to_matrix(*rpy)
        by_name[name] = jd
    return [by_name[n] for n in CHAIN_JOINTS]


# --------------------------------------------------------------------------- #
# FASE 2a - Cinematica direta (FK)
# --------------------------------------------------------------------------- #
def fk(chain: List[JointDef], q: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """FK base_link -> wrist3_Link. Retorna (posicao 3, rotacao 3x3)."""
    R = np.eye(3)
    p = np.zeros(3)
    for i, jd in enumerate(chain):
        # T_i = Origin(xyz, rpy) * Rot(axis, q_i)
        p = p + R @ jd.xyz
        R = R @ jd.R0
        R = R @ _axis_angle_matrix(jd.axis, q[i])
    return p, R


def tip_pose(chain: List[JointDef], q: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Posicao da ponta e eixo de aproximacao (mundo)."""
    p, R = fk(chain, q)
    approach = R @ TOOL_APPROACH_LOCAL
    return p, approach / (np.linalg.norm(approach) + 1e-12)


# --------------------------------------------------------------------------- #
# FASE 1 - Geometria da orbita (pontos cartesianos + look-at)
# --------------------------------------------------------------------------- #
@dataclass
class OrbitParams:
    # --- PARAMETROS FACILMENTE AJUSTAVEIS DA ORBITA ---
    # Raio maior = camera mais afastada da peca = movimento mais folgado/suave
    # para o robo real. Mantenha todos os pontos dentro do alcance (~0.9 m da
    # base) e dos limites de junta do URDF (validar com `python sim/orbit_ik.py`).
    center: Tuple[float, float, float] = (0.40, 0.40, 0.18)  # C no frame BASE (m)
    levels: int = 6
    points_per_level: int = 24
    radius_bottom: float = 0.28     # raio grande embaixo (m) -- camera afastada
    radius_top: float = 0.18        # raio menor no topo (m)
    z_bottom: float = 0.10          # altura do anel mais baixo (m, frame base)
    z_top: float = 0.40             # altura do anel mais alto (m)
    start_angle: float = 0.0        # angulo inicial de cada anel (rad)


def generate_orbit_points(p: OrbitParams):
    """Aneis empilhados ao redor de C, de baixo para cima.

    Retorna lista de (P, d, level, k) onde:
      P  = posicao 3D alvo da ponta (frame base, m)
      d  = direcao de aproximacao desejada (unit), de P para C (look-at)
    """
    C = np.array(p.center, dtype=float)
    out = []
    for lvl in range(p.levels):
        t = (lvl / (p.levels - 1)) if p.levels > 1 else 0.0
        radius = p.radius_bottom + (p.radius_top - p.radius_bottom) * t
        z = p.z_bottom + (p.z_top - p.z_bottom) * t
        for k in range(p.points_per_level):
            ang = p.start_angle + 2.0 * math.pi * k / p.points_per_level
            P = np.array([C[0] + radius * math.cos(ang),
                          C[1] + radius * math.sin(ang),
                          z])
            d = C - P
            d = d / (np.linalg.norm(d) + 1e-12)
            out.append((P, d, lvl, k))
    return out


# --------------------------------------------------------------------------- #
# FASE 2b - IK numerico (DLS + Jacobiano por diferencas finitas)
# --------------------------------------------------------------------------- #
def _orientation_error(a, d_target):
    """Vetor erro de apontamento (axis * angle) que gira 'a' ate 'd_target'.

    Usa axis-angle (nao apenas o produto vetorial) para nao perder magnitude
    perto de 180 graus, onde cross(a,d) -> 0 (singularidade que prende o IK).
    """
    cos_ang = float(np.clip(np.dot(a, d_target), -1.0, 1.0))
    ang = math.acos(cos_ang)
    axis = np.cross(a, d_target)
    n = np.linalg.norm(axis)
    if n < 1e-9:
        if cos_ang > 0.0:
            return np.zeros(3)            # ja alinhado
        # quase antiparalelo: escolhe um eixo perpendicular qualquer
        perp = np.array([1.0, 0.0, 0.0])
        if abs(a[0]) > 0.9:
            perp = np.array([0.0, 1.0, 0.0])
        axis = np.cross(a, perp)
        axis /= (np.linalg.norm(axis) + 1e-12)
        return axis * ang
    return (axis / n) * ang


def _residual(chain, q, P_target, d_target):
    """Erro de 6 componentes: [pos(3), apontamento(3)]."""
    p, a = tip_pose(chain, q)
    e_pos = p - P_target
    e_rot = _orientation_error(a, d_target)
    return np.concatenate([e_pos, e_rot])


def _numeric_jacobian(chain, q, P_target, d_target, eps=1e-6):
    J = np.zeros((6, 6))
    e0 = _residual(chain, q, P_target, d_target)
    for i in range(6):
        dq = q.copy()
        dq[i] += eps
        ei = _residual(chain, dq, P_target, d_target)
        J[:, i] = (ei - e0) / eps
    return J, e0


def solve_ik(chain: List[JointDef],
             P_target: np.ndarray,
             d_target: np.ndarray,
             seed: np.ndarray,
             pos_tol: float = 0.005,      # 5 mm
             point_tol_deg: float = 3.0,  # 3 graus
             max_iter: int = 120,
             lam: float = 0.06,
             null_gain: float = 0.04):
    """IK por DLS com bias de nullspace. Retorna (q, ok, pos_err_m, point_err_deg).

    O bias de nullspace puxa as juntas redundantes (roll da ferramenta, cotovelo)
    de volta para o 'seed', mantendo continuidade entre pontos consecutivos sem
    afetar o alvo (posicao + apontamento). Isso evita saltos/branch switches.
    """
    q = seed.astype(float).copy()
    q_ref = seed.astype(float).copy()
    lower = np.array([jd.lower for jd in chain])
    upper = np.array([jd.upper for jd in chain])
    point_tol = math.radians(point_tol_deg)
    I6 = np.eye(6)

    best_q = q.copy()
    best_score = float("inf")

    for _ in range(max_iter):
        J, e = _numeric_jacobian(chain, q, P_target, d_target)
        # DLS: dq = -J^T (J J^T + lam^2 I)^-1 e
        JJt = J @ J.T + (lam ** 2) * I6
        Jpinv = J.T @ np.linalg.inv(JJt)
        dq = -Jpinv @ e

        # tarefa secundaria no nullspace: puxa juntas redundantes p/ o seed
        N = I6 - Jpinv @ J
        dq += N @ (null_gain * (q_ref - q))

        # passo limitado para estabilidade (evita pular de basin/branch)
        step = np.linalg.norm(dq)
        max_step = 0.2
        if step > max_step:
            dq *= max_step / step

        q = np.clip(q + dq, lower, upper)

        p, a = tip_pose(chain, q)
        pos_err = float(np.linalg.norm(p - P_target))
        cos_ang = float(np.clip(np.dot(a, d_target), -1.0, 1.0))
        point_err = math.acos(cos_ang)

        score = pos_err + 0.05 * point_err
        if score < best_score:
            best_score = score
            best_q = q.copy()

        if pos_err <= pos_tol and point_err <= point_tol:
            return q, True, pos_err, math.degrees(point_err)

    # nao convergiu: devolve melhor tentativa
    p, a = tip_pose(chain, best_q)
    pos_err = float(np.linalg.norm(p - P_target))
    cos_ang = float(np.clip(np.dot(a, d_target), -1.0, 1.0))
    point_err = math.degrees(math.acos(cos_ang))
    ok = pos_err <= pos_tol and math.radians(point_err) <= point_tol
    return best_q, ok, pos_err, point_err


# --------------------------------------------------------------------------- #
# FASE 3 - Sequencia + suavizacao
# --------------------------------------------------------------------------- #
@dataclass
class OrbitPlan:
    poses_deg: List[List[float]]          # KEYPOINTS resolvidos (alvos da orbita)
    motion_deg: List[List[float]]         # sequencia densificada p/ playback suave
    points: List[List[float]]             # pontos cartesianos alvo (m)
    approaches: List[List[float]]         # direcao look-at desejada por keypoint
    center: List[float]                   # C no frame base
    point_errs_deg: List[float]           # erro de apontamento por keypoint resolvido
    pos_errs_m: List[float]               # erro de posicao por keypoint resolvido
    converged: List[bool]
    levels: int
    points_per_level: int

    def metrics(self):
        n = len(self.poses_deg)
        if n == 0:
            return {"n": 0}
        good = sum(1 for e in self.point_errs_deg if e <= 3.0)
        return {
            "n": n,
            "frac_within_3deg": good / n,
            "mean_point_err_deg": float(np.mean(self.point_errs_deg)),
            "max_point_err_deg": float(np.max(self.point_errs_deg)),
            "mean_pos_err_mm": float(np.mean(self.pos_errs_m)) * 1000.0,
            "max_pos_err_mm": float(np.max(self.pos_errs_m)) * 1000.0,
            "converged": sum(1 for c in self.converged if c),
        }


def _solve_with_restarts(chain, P, d, seed):
    """Tenta resolver a partir de varios seeds de j1 (anti local-minima).

    O ponto inicial e critico: um seed cujo braco aponta para longe da peca
    prende o IK. Varremos j1 ao redor do azimute da peca e ficamos com a
    melhor solucao convergida (ou a de menor erro).
    """
    best = None
    j1_candidates = list(np.radians(range(-175, 176, 30)))
    # tambem inclui o seed dado primeiro (continuidade)
    trials = [seed] + [
        np.array([j1, *seed[1:]]) for j1 in j1_candidates
    ]
    for s in trials:
        q, ok, pos_err, point_err = solve_ik(chain, P, d, s)
        score = pos_err + 0.02 * math.radians(point_err)
        if best is None or score < best[0]:
            best = (score, q, ok, pos_err, point_err)
        if ok:
            return q, ok, pos_err, point_err
    return best[1], best[2], best[3], best[4]


def densify_joint_path(poses_deg: List[List[float]],
                       max_step_deg: float = 6.0,
                       close_loop: bool = True) -> List[List[float]]:
    """Insere waypoints interpolados em juntas para nao haver salto brusco.

    Entre keypoints consecutivos (e do ultimo de volta ao primeiro, fechando o
    loop), se algum joint variar mais que 'max_step_deg', subdivide o segmento
    linearmente em juntas. Reconfiguracoes de punho (flips) viram varreduras
    suaves do punho em vez de saltos.
    """
    if len(poses_deg) < 2:
        return [list(p) for p in poses_deg]
    arr = [np.array(p, dtype=float) for p in poses_deg]
    seq = []
    pairs = list(zip(arr, arr[1:]))
    if close_loop:
        pairs.append((arr[-1], arr[0]))
    for a, b in pairs:
        seq.append([float(v) for v in a])
        max_delta = float(np.max(np.abs(b - a)))
        n = int(math.ceil(max_delta / max_step_deg))
        for s in range(1, n):
            alpha = s / n
            seq.append([float(v) for v in (a + (b - a) * alpha)])
    return seq


def plan_orbit(params: Optional[OrbitParams] = None,
               seed_deg: Optional[List[float]] = None,
               max_joint_jump_deg: float = 160.0,
               smooth_step_deg: float = 6.0,
               urdf_path: str = URDF_PATH) -> OrbitPlan:
    """Resolve a orbita completa em poses de junta (graus)."""
    params = params or OrbitParams()
    chain = parse_urdf_chain(urdf_path)
    targets = generate_orbit_points(params)

    if seed_deg is None:
        seed_deg = [0.0, -20.0, -90.0, -70.0, 90.0, 0.0]
    seed = np.radians(seed_deg)

    poses_deg, points, approaches = [], [], []
    point_errs, pos_errs, converged = [], [], []
    last_q = seed.copy()
    first = True

    for (P, d, lvl, k) in targets:
        if first:
            q, ok, pos_err, point_err = _solve_with_restarts(chain, P, d, last_q)
            first = False
        else:
            q, ok, pos_err, point_err = solve_ik(chain, P, d, last_q, null_gain=0.2)
            if not ok:
                # tenta multi-start antes de desistir do ponto
                q, ok, pos_err, point_err = _solve_with_restarts(chain, P, d, last_q)

        # FASE 3: rejeita saltos bruscos de junta (mantem continuidade).
        jump_deg = float(np.max(np.abs(np.degrees(q - last_q))))
        if poses_deg and jump_deg > max_joint_jump_deg and not ok:
            # ponto problematico: pula, mantem o anel continuo com a ultima pose
            continue

        poses_deg.append([float(v) for v in np.degrees(q)])
        points.append([float(v) for v in P])
        approaches.append([float(v) for v in d])
        point_errs.append(float(point_err))
        pos_errs.append(float(pos_err))
        converged.append(bool(ok))
        last_q = q  # seed do proximo ponto (continuidade)

    # FASE 3: sequencia densificada (fonte da verdade do movimento) sem saltos.
    motion_deg = densify_joint_path(poses_deg, max_step_deg=smooth_step_deg)

    return OrbitPlan(
        poses_deg=poses_deg,
        motion_deg=motion_deg,
        points=points,
        approaches=approaches,
        center=list(params.center),
        point_errs_deg=point_errs,
        pos_errs_m=pos_errs,
        converged=converged,
        levels=params.levels,
        points_per_level=params.points_per_level,
    )


# --------------------------------------------------------------------------- #
# SINGLE SOURCE OF TRUTH para o robo real
# --------------------------------------------------------------------------- #
def orbit_joint_sequence(params: Optional[OrbitParams] = None,
                         seed_deg: Optional[List[float]] = None,
                         urdf_path: str = URDF_PATH) -> List[List[float]]:
    """Sequencia de poses de junta (graus) da orbita de inspecao.

    Esta e' a MESMA sequencia que o viewer/sim reproduz (plan.motion_deg): a
    versao densificada (passos <= ~6 deg entre poses), segura para enviar ao
    FR5 real via MoveJ sem saltos bruscos. Usar esta funcao garante que sim e
    robo real partem da mesma fonte da verdade.
    """
    plan = plan_orbit(params=params, seed_deg=seed_deg, urdf_path=urdf_path)
    return plan.motion_deg


def urdf_joint_limits_deg(urdf_path: str = URDF_PATH) -> List[Tuple[float, float]]:
    """Limites (lower, upper) de cada junta j1..j6 em GRAUS, lidos do URDF."""
    chain = parse_urdf_chain(urdf_path)
    return [(math.degrees(jd.lower), math.degrees(jd.upper)) for jd in chain]


def validate_sequence_limits(seq: List[List[float]],
                             limits: List[Tuple[float, float]],
                             margin_deg: float = 0.001) -> None:
    """Levanta ValueError se qualquer pose viola os limites de junta do URDF."""
    for i, pose in enumerate(seq):
        for j, (val, (lo, hi)) in enumerate(zip(pose, limits)):
            if not (lo - margin_deg <= val <= hi + margin_deg):
                raise ValueError(
                    f"Pose #{i}: j{j + 1}={val:.2f} fora dos limites do URDF "
                    f"[{lo:.2f}, {hi:.2f}]")


# --------------------------------------------------------------------------- #
# CLI de validacao
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    plan = plan_orbit()
    m = plan.metrics()
    print("=== Orbita IK ===")
    print(f"pontos resolvidos : {m['n']}")
    print(f"convergidos       : {m['converged']}")
    print(f"<= 3 graus        : {m['frac_within_3deg'] * 100:.1f}%")
    print(f"erro apont medio  : {m['mean_point_err_deg']:.2f} deg (max {m['max_point_err_deg']:.2f})")
    print(f"erro pos medio    : {m['mean_pos_err_mm']:.2f} mm (max {m['max_pos_err_mm']:.2f})")
    # checa saltos de junta nos keypoints e na sequencia de movimento
    def max_jump(seq):
        mj = 0.0
        for a, b in zip(seq, seq[1:]):
            mj = max(mj, max(abs(x - y) for x, y in zip(a, b)))
        return mj
    print(f"salto keypoints   : {max_jump(plan.poses_deg):.2f} deg")
    print(f"motion (densif.)  : {len(plan.motion_deg)} poses, "
          f"maior salto {max_jump(plan.motion_deg):.2f} deg")
