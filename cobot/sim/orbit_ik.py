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
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, replace
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
# Restricoes de SEGURANCA geometricas (frame BASE, metros). Invioláveis:
#   1) CHAO: nenhum ponto da cadeia pode ter z < Z_FLOOR (chao em z=0 + margem).
#   2) PECA: nenhum ponto da cadeia pode entrar na esfera de raio R_SAFE ao
#      redor do centro C da peca (R_SAFE um pouco MAIOR que a peca real).
# Valem para TODAS as juntas/links E para a ponta/flange. Sao defaults; podem
# ser sobrescritos por OrbitParams.z_floor / OrbitParams.r_safe.
Z_FLOOR = 0.02      # margem de seguranca acima do chao (m)
R_SAFE = 0.06       # raio de seguranca ao redor da peca (m)
# Amostras por segmento de link (interpolacao linear entre frames de junta
# consecutivos) para aproximar o CORPO do link, nao so as juntas.
LINK_SAMPLES = 4


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
    is_z: bool = False       # True se axis == +Z (rotacao = Rz trivial, rapida)


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


def _rotate_about_axis(R: np.ndarray, jd: "JointDef", theta: float) -> np.ndarray:
    """Retorna R @ Rot(jd.axis, theta).

    Caminho rapido para eixo +Z (caso do FR5: todos os joints giram em Z): a
    rotacao so mistura as colunas 0 e 1 de R, evitando montar a matriz de
    Rodrigues e o matmul 3x3 a cada junta/iteracao. Cai no caso geral se o
    eixo nao for +Z.
    """
    if jd.is_z:
        c, s = math.cos(theta), math.sin(theta)
        c0 = R[:, 0]
        c1 = R[:, 1]
        out = R.copy()
        out[:, 0] = c0 * c + c1 * s
        out[:, 1] = -c0 * s + c1 * c
        return out
    return R @ _axis_angle_matrix(jd.axis, theta)


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
        jd.is_z = bool(abs(axis[0]) < 1e-9 and abs(axis[1]) < 1e-9
                       and axis[2] > 0.0)
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
        R = _rotate_about_axis(R, jd, q[i])
    return p, R


def tip_pose(chain: List[JointDef], q: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Posicao da ponta e eixo de aproximacao (mundo)."""
    p, R = fk(chain, q)
    approach = R @ TOOL_APPROACH_LOCAL
    return p, approach / (np.linalg.norm(approach) + 1e-12)


def fk_axes(chain: List[JointDef], q: np.ndarray):
    """FK + dados para o Jacobiano analitico, numa unica passada.

    Retorna (p_tip, R_tip, axes) onde axes[i] = (z_i, o_i):
      z_i = eixo de rotacao da junta i no frame MUNDO (unit)
      o_i = posicao do ponto por onde passa o eixo da junta i (mundo)
    Com isso o Jacobiano de posicao e' z_i x (p_tip - o_i) e o de orientacao
    sai de da/dq_i = z_i x a -- tudo a partir de UMA FK, em vez de 7 FK por
    diferencas finitas.
    """
    R = np.eye(3)
    p = np.zeros(3)
    axes = []
    for i, jd in enumerate(chain):
        p = p + R @ jd.xyz
        R = R @ jd.R0
        # frame/posicao da junta i ANTES de aplicar sua propria rotacao
        z = R @ jd.axis
        axes.append((z, p.copy()))
        R = _rotate_about_axis(R, jd, q[i])
    return p, R, axes


# --------------------------------------------------------------------------- #
# FK de TODOS os pontos da cadeia (juntas + corpo dos links) + SEGURANCA
# --------------------------------------------------------------------------- #
def chain_link_points(chain: List[JointDef], q: np.ndarray,
                      link_samples: int = LINK_SAMPLES) -> np.ndarray:
    """Posicoes 3D (frame BASE) de TODOS os pontos da cadeia para uma config q.

    Reusa a MESMA composicao origin(rpy/xyz)*Rot(axis,theta) da FK e coleta a
    origem de cada frame acumulado (base -> j1 -> ... -> wrist3/ponta). Alem das
    juntas, amostra pontos intermediarios ao longo de cada link (interpolacao
    linear entre frames consecutivos) para aproximar o CORPO do link, nao so as
    juntas. Barato: sem libs novas, uma unica passada de FK.

    Retorna array (N, 3) com: base, amostras de cada segmento de link e a ponta
    (ultima amostra do ultimo segmento e' o frame wrist3).
    """
    R = np.eye(3)
    p = np.zeros(3)
    pts = [p.copy()]                         # base_link na origem
    n = max(1, int(link_samples))
    for i, jd in enumerate(chain):
        p_prev = p
        p = p + R @ jd.xyz                   # origem do frame da junta i
        for s in range(1, n + 1):            # amostras ao longo do link
            alpha = s / n
            pts.append(p_prev + (p - p_prev) * alpha)
        R = R @ jd.R0
        R = _rotate_about_axis(R, jd, q[i])
    return np.asarray(pts)


def check_pose_safety(chain: List[JointDef], q: np.ndarray, center,
                      z_floor: float = Z_FLOOR, r_safe: float = R_SAFE,
                      link_samples: int = LINK_SAMPLES) -> Tuple[bool, str]:
    """Checagem PURA das 2 regras invioláveis para uma config q (rad).

    Calcula todos os pontos da cadeia (juntas + amostras de link) e reprova se:
      - algum ponto tem z < z_floor (fura o chao), ou
      - algum ponto tem distancia a `center` < r_safe (invade a esfera da peca).
    Retorna (ok, reason). `reason` e' "ok" quando seguro.

    Obs.: a PONTA normalmente fica a `radius` (0.18-0.28 m) do centro, bem > do
    que r_safe (~0.06 m), entao a aproximacao normal NAO e' reprovada; o alvo e'
    pegar casos em que braco/cotovelo/ponta de fato furam o chao ou invadem a
    peca.

    O teste de CHAO ignora a montagem fixa da base: base_link e a origem de j1
    ficam em z=0 (o robo e' aparafusado na mesa em z=0), o que nao e' "furar o
    chao". Esses pontos nao dependem de q e sao os primeiros (1 + link_samples)
    da cadeia. O teste da PECA continua valendo para TODOS os pontos.
    """
    C = np.asarray(center, dtype=float)
    pts = chain_link_points(chain, q, link_samples)
    r2 = r_safe * r_safe
    floor_from = link_samples + 1   # pula base_link + segmento fixo base->j1
    for idx, pt in enumerate(pts):
        if idx >= floor_from and pt[2] < z_floor:
            return (False,
                    f"ponto {idx} da cadeia abaixo do chao: z={pt[2]:.3f} m "
                    f"< z_floor={z_floor:.3f} m")
        dx, dy, dz = pt[0] - C[0], pt[1] - C[1], pt[2] - C[2]
        d2 = dx * dx + dy * dy + dz * dz
        if d2 < r2:
            return (False,
                    f"ponto {idx} da cadeia entra na esfera da peca: "
                    f"d={math.sqrt(d2):.3f} m < r_safe={r_safe:.3f} m")
    return True, "ok"


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
    # --- RESTRICOES DE SEGURANCA (ver Z_FLOOR / R_SAFE acima) ---
    z_floor: float = Z_FLOOR        # nenhum ponto da cadeia abaixo disto (m)
    r_safe: float = R_SAFE          # esfera de exclusao ao redor de center (m)


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
    Cross/norm escritos a mao (3 floats) -> bem mais barato que np.cross em loop.
    """
    a0, a1, a2 = a[0], a[1], a[2]
    d0, d1, d2 = d_target[0], d_target[1], d_target[2]
    cos_ang = a0 * d0 + a1 * d1 + a2 * d2
    if cos_ang > 1.0:
        cos_ang = 1.0
    elif cos_ang < -1.0:
        cos_ang = -1.0
    ax = a1 * d2 - a2 * d1
    ay = a2 * d0 - a0 * d2
    az = a0 * d1 - a1 * d0
    n = math.sqrt(ax * ax + ay * ay + az * az)
    ang = math.acos(cos_ang)
    if n < 1e-9:
        if cos_ang > 0.0:
            return np.zeros(3)            # ja alinhado
        # quase antiparalelo: escolhe um eixo perpendicular qualquer
        perp = np.array([1.0, 0.0, 0.0])
        if abs(a0) > 0.9:
            perp = np.array([0.0, 1.0, 0.0])
        axis = np.cross(a, perp)
        axis /= (np.linalg.norm(axis) + 1e-12)
        return axis * ang
    s = ang / n
    return np.array([ax * s, ay * s, az * s])


def _analytic_jacobian(chain, q, P_target, d_target, eps=1e-6):
    """Jacobiano 6x6 do residuo [pos(3), apontamento(3)] em UMA passada de FK.

    Equivalente em 1a ordem ao Jacobiano por diferencas finitas (que custava 7
    FK por iteracao), mas ~7x mais barato:
      - posicao: linha i = z_i x (p_tip - o_i)            (geometrico, exato)
      - apontamento: d(e_rot)/dq = (de_rot/da) @ (da/dq), com da/dq_i = z_i x a
        e de_rot/da (3x3) por diferencas finitas BARATAS sobre o vetor 'a'
        (sem FK, so reavalia a funcao de erro de apontamento).
    Retorna (J, e, pos_err, point_err_rad). Os erros saem de graca de 'e'.
    """
    p, R, axes = fk_axes(chain, q)
    a = R @ TOOL_APPROACH_LOCAL
    a = a / (np.linalg.norm(a) + 1e-12)

    e_pos = p - P_target
    e_rot = _orientation_error(a, d_target)
    e = np.concatenate([e_pos, e_rot])

    J = np.zeros((6, 6))
    dadq = np.zeros((3, 6))
    ax, ay, az = a[0], a[1], a[2]
    px, py, pz = p[0], p[1], p[2]
    for i, (z, o) in enumerate(axes):
        z0, z1, z2 = z[0], z[1], z[2]
        rx, ry, rz = px - o[0], py - o[1], pz - o[2]
        # linhas de posicao: z x (p - o)
        J[0, i] = z1 * rz - z2 * ry
        J[1, i] = z2 * rx - z0 * rz
        J[2, i] = z0 * ry - z1 * rx
        # da/dq_i = z x a (tangente a esfera unitaria)
        dadq[0, i] = z1 * az - z2 * ay
        dadq[1, i] = z2 * ax - z0 * az
        dadq[2, i] = z0 * ay - z1 * ax

    # de_rot/da (3x3) por diferencas finitas no proprio 'a' (sem FK).
    M = np.zeros((3, 3))
    for k in range(3):
        ap = a.copy()
        ap[k] += eps
        ap /= np.linalg.norm(ap)
        M[:, k] = (_orientation_error(ap, d_target) - e_rot) / eps
    J[3:6, :] = M @ dadq

    pos_err = float(math.sqrt(e_pos[0] * e_pos[0] + e_pos[1] * e_pos[1] + e_pos[2] * e_pos[2]))
    point_err = float(math.sqrt(e_rot[0] * e_rot[0] + e_rot[1] * e_rot[1] + e_rot[2] * e_rot[2]))
    return J, e, pos_err, point_err


def solve_ik(chain: List[JointDef],
             P_target: np.ndarray,
             d_target: np.ndarray,
             seed: np.ndarray,
             pos_tol: float = 0.005,      # 5 mm
             point_tol_deg: float = 3.0,  # 3 graus
             max_iter: int = 80,
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
    best_pos = float("inf")
    best_point = float("inf")

    for _ in range(max_iter):
        J, e, pos_err, point_err = _analytic_jacobian(chain, q, P_target, d_target)

        score = pos_err + 0.05 * point_err
        if score < best_score:
            best_score = score
            best_q = q.copy()
            best_pos = pos_err
            best_point = point_err

        if pos_err <= pos_tol and point_err <= point_tol:
            return q, True, pos_err, math.degrees(point_err)

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

    # nao convergiu: devolve melhor tentativa (erros ja conhecidos)
    ok = best_pos <= pos_tol and best_point <= point_tol
    return best_q, ok, best_pos, math.degrees(best_point)


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
    # --- contabilidade de SEGURANCA ---
    skipped_floor: int = 0        # keypoints pulados por violarem o chao
    skipped_piece: int = 0        # keypoints pulados por invadirem a peca
    motion_removed_unsafe: int = 0  # poses densificadas removidas por seguranca
    reconfig_avoided: int = 0     # flips evitados re-resolvendo p/ ramo continuo
    safe: bool = True             # motion_deg 100% seguro e nao-vazio

    def metrics(self):
        n = len(self.poses_deg)
        skipped = self.skipped_floor + self.skipped_piece
        if n == 0:
            return {
                "n": 0,
                "skipped_safety": skipped,
                "skipped_floor": self.skipped_floor,
                "skipped_piece": self.skipped_piece,
                "motion_removed_unsafe": self.motion_removed_unsafe,
                "reconfig_avoided": self.reconfig_avoided,
                "safe": bool(self.safe),
            }
        good = sum(1 for e in self.point_errs_deg if e <= 3.0)
        return {
            "n": n,
            "frac_within_3deg": good / n,
            "mean_point_err_deg": float(np.mean(self.point_errs_deg)),
            "max_point_err_deg": float(np.max(self.point_errs_deg)),
            "mean_pos_err_mm": float(np.mean(self.pos_errs_m)) * 1000.0,
            "max_pos_err_mm": float(np.max(self.pos_errs_m)) * 1000.0,
            "converged": sum(1 for c in self.converged if c),
            "skipped_safety": skipped,
            "skipped_floor": self.skipped_floor,
            "skipped_piece": self.skipped_piece,
            "motion_removed_unsafe": self.motion_removed_unsafe,
            "reconfig_avoided": self.reconfig_avoided,
            "safe": bool(self.safe),
        }


# --------------------------------------------------------------------------- #
# CONTINUIDADE (anti-flip): criterios de selecao entre solucoes IK validas
# --------------------------------------------------------------------------- #
# Pesos do score de SELECAO. A regra: SEGURANCA e' gate duro (fora do score);
# entre solucoes convergidas e seguras, a CONTINUIDADE (proximidade em juntas a
# pose anterior) DESEMPATA -- nunca sacrificamos posicao/apontamento, que ja
# estao dentro da tolerancia quando ok=True.
_W_POINT = 0.02          # peso do apontamento (rad) no termo de erro
_CONT_ACCEPT_DEG = 30.0  # se a solucao do seed converge e o maior salto de
#                          junta vs anterior e' <= isto, aceita sem varrer mais.


def _max_joint_jump_deg(q, q_ref) -> float:
    """Maior salto (graus) de UMA junta entre duas configs (rad)."""
    return float(np.max(np.abs(np.degrees(q - q_ref))))


def _sel_key(ok: bool, pos_err: float, point_err_rad: float,
             q, q_ref) -> Tuple[int, float]:
    """Chave ordenavel (menor = melhor) para escolher entre solucoes IK.

    - Convergidas (ok) vem antes das nao-convergidas (tier 0 < 1).
    - Entre convergidas: a distancia em juntas ao anterior DOMINA (continuidade);
      o erro entra so como desempate fino (ja esta <= tolerancia).
    - Entre nao-convergidas: o erro DOMINA (queremos a de menor erro).
    """
    jdist = float(np.linalg.norm(q - q_ref))   # rad
    err = pos_err + _W_POINT * point_err_rad
    if ok:
        return (0, jdist + 0.25 * err)
    return (1, err + 0.05 * jdist)


def _solve_with_restarts(chain, P, d, seed):
    """Resolve preferindo a solucao convergida E mais proxima do anterior.

    O ponto inicial e critico: um seed cujo braco aponta para longe da peca
    prende o IK. Varremos j1 ao redor do azimute da peca, mas em vez de pegar a
    PRIMEIRA convergida (que pode estar num ramo/azimute arbitrario -> flip),
    escolhemos a convergida de MENOR salto de junta vs `seed` (continuidade).
    """
    # 1) tenta primeiro o seed dado (continuidade) com iteracoes cheias.
    q, ok, pos_err, point_err = solve_ik(chain, P, d, seed)
    best_q, best_ok, best_pe, best_pt = q, ok, pos_err, point_err
    best_key = _sel_key(ok, pos_err, math.radians(point_err), q, seed)
    # sai cedo se o seed ja converge E mal se move (ramo continuo garantido).
    if ok and _max_joint_jump_deg(q, seed) <= _CONT_ACCEPT_DEG:
        return q, ok, pos_err, point_err

    # 2) varre j1 ao redor do azimute (anti local-minima) e fica com a melhor
    #    por continuidade (gate de convergencia embutido no _sel_key).
    for j1 in np.radians(range(-180, 180, 45)):
        s = np.array([j1, *seed[1:]])
        q, ok, pos_err, point_err = solve_ik(chain, P, d, s, max_iter=80)
        key = _sel_key(ok, pos_err, math.radians(point_err), q, seed)
        if key < best_key:
            best_key = key
            best_q, best_ok, best_pe, best_pt = q, ok, pos_err, point_err
            # convergida e ja bem continua: bom o bastante, corta o custo.
            if best_ok and _max_joint_jump_deg(best_q, seed) <= _CONT_ACCEPT_DEG:
                break
    return best_q, best_ok, best_pe, best_pt


def _solve_safe(chain, P, d, seed, center, z_floor, r_safe):
    """Resolve IK buscando uma solucao SEGURA (chao + peca) E continua.

    Tenta primeiro o seed (continuidade). Se a solucao violar a seguranca, faz
    multi-start variando o azimute de j1 e o seed do cotovelo (j3), procurando
    uma config que satisfaca posicao+apontamento, passe em check_pose_safety E
    fique o mais proxima possivel da pose anterior (anti-flip). Seguranca e' gate
    duro; continuidade desempata entre as candidatas seguras.
    Retorna (q, ok, pos_err, point_err_deg, safe).
    """
    q, ok, pos_err, point_err = solve_ik(chain, P, d, seed, null_gain=0.2)
    safe, _ = check_pose_safety(chain, q, center, z_floor, r_safe)
    if ok and safe and _max_joint_jump_deg(q, seed) <= _CONT_ACCEPT_DEG:
        return q, ok, pos_err, point_err, True

    best = (q, ok, pos_err, point_err, safe)  # melhor tentativa (pode ser insegura)
    best_safe = None  # (key, q, ok, pos_err, point_err) -- so convergidas+seguras
    if ok and safe:
        best_safe = (_sel_key(ok, pos_err, math.radians(point_err), q, seed),
                     q, ok, pos_err, point_err)
    elbow = float(seed[2])
    elbow_seeds = [elbow, -abs(elbow), abs(elbow), elbow + math.radians(30),
                   elbow - math.radians(30)]
    for j1 in np.radians(range(-180, 180, 30)):
        for e in elbow_seeds:
            s = np.array([j1, seed[1], e, seed[3], seed[4], seed[5]])
            q, ok, pos_err, point_err = solve_ik(chain, P, d, s, max_iter=80)
            if not ok:
                continue
            safe, _ = check_pose_safety(chain, q, center, z_floor, r_safe)
            if not safe:
                continue
            key = _sel_key(ok, pos_err, math.radians(point_err), q, seed)
            if best_safe is None or key < best_safe[0]:
                best_safe = (key, q, ok, pos_err, point_err)
            # convergida, segura E continua: bom o bastante, corta o custo.
            if _max_joint_jump_deg(q, seed) <= _CONT_ACCEPT_DEG:
                return q, ok, pos_err, point_err, True
    if best_safe is not None:
        _, q, ok, pos_err, point_err = best_safe
        return q, ok, pos_err, point_err, True
    return best[0], best[1], best[2], best[3], best[4]


def _densify_safe(poses_deg, chain, center, z_floor, r_safe,
                  max_step_deg: float = 6.0):
    """Densifica a sequencia e GARANTE que cada pose resultante e' segura.

    A interpolacao linear em juntas entre dois keypoints SEGUROS pode passar por
    uma config insegura (o caminho no espaco de juntas nao e' reto no cartesiano).
    Aqui validamos CADA pose densificada com check_pose_safety e descartamos as
    inseguras (os keypoints sao seguros por construcao). Retorna (seq, removidos).
    """
    dense = densify_joint_path(poses_deg, max_step_deg=max_step_deg)
    seq = []
    removed = 0
    for pose in dense:
        ok, _ = check_pose_safety(chain, np.radians(pose), center, z_floor, r_safe)
        if ok:
            seq.append(pose)
        else:
            removed += 1
    return seq, removed


def unwrap_keypoints(poses_deg: List[List[float]],
                     limits: List[Tuple[float, float]]) -> List[List[float]]:
    """Escolhe o representante angular (+/- 360k) de cada junta que MINIMIZA o
    salto para a pose anterior, mantendo-se DENTRO dos limites do URDF.

    Corrige o wrap +/-360: 170 deg -> -170 deg (mesma orientacao fisica, mas
    diff numerico de 340 deg) vira 170 -> 190 (passo de 20 deg) SE o limite da
    junta permitir. Se nenhum representante alternativo couber nos limites,
    mantem o valor original (reconfiguracao real, tratada na sequenciacao).

    Nao altera a config FISICA (so soma multiplos de 360 em juntas revolutas),
    entao seguranca e apontamento ficam IDENTICOS; so encurta a interpolacao.
    """
    if len(poses_deg) < 2:
        return [list(p) for p in poses_deg]
    out = [list(poses_deg[0])]
    for pose in poses_deg[1:]:
        prev = out[-1]
        newp = []
        for j, (val, (lo, hi)) in enumerate(zip(pose, limits)):
            best = float(val)
            best_d = abs(best - prev[j])
            for k in range(-3, 4):
                if k == 0:
                    continue
                cand = float(val) + 360.0 * k
                if lo - 1e-6 <= cand <= hi + 1e-6:
                    dd = abs(cand - prev[j])
                    if dd < best_d:
                        best_d = dd
                        best = cand
            newp.append(best)
        out.append(newp)
    return out


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
               max_keypoint_jump_deg: float = 30.0,
               smooth_step_deg: float = 6.0,
               urdf_path: str = URDF_PATH) -> OrbitPlan:
    """Resolve a orbita completa em poses de junta (graus)."""
    params = params or OrbitParams()
    chain = parse_urdf_chain(urdf_path)
    targets = generate_orbit_points(params)
    center = np.array(params.center, dtype=float)
    z_floor = params.z_floor
    r_safe = params.r_safe
    limits_deg = [(math.degrees(jd.lower), math.degrees(jd.upper)) for jd in chain]

    if seed_deg is None:
        seed_deg = [0.0, -20.0, -90.0, -70.0, 90.0, 0.0]
    seed = np.radians(seed_deg)

    poses_deg, points, approaches = [], [], []
    point_errs, pos_errs, converged = [], [], []
    skipped_floor = 0
    skipped_piece = 0
    reconfig_avoided = 0
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

        # ANTI-FLIP: mesmo convergida, a solucao do seed pode cair num ramo
        # diferente (cotovelo/punho flipado) -> salto grande de junta. Se isso
        # acontecer, procura via restarts uma solucao convergida MAIS PROXIMA da
        # anterior (continuidade). So troca se for convergida, SEGURA e reduzir
        # o salto (nunca regride seguranca nem qualidade).
        if poses_deg:
            jump_now = _max_joint_jump_deg(q, last_q)
            if jump_now > max_keypoint_jump_deg:
                qc, okc, pec, ptc = _solve_with_restarts(chain, P, d, last_q)
                if okc and _max_joint_jump_deg(qc, last_q) < jump_now:
                    safe_c, _ = check_pose_safety(chain, qc, center, z_floor, r_safe)
                    if safe_c:
                        q, ok, pos_err, point_err = qc, okc, pec, ptc
                        reconfig_avoided += 1

        # SEGURANCA (planejamento): se a solucao furar o chao ou invadir a peca,
        # tenta recuperar com multi-start buscando uma solucao SEGURA. Se nao
        # houver, PULA o ponto (mantem a orbita continua) em vez de incluir uma
        # pose perigosa, e contabiliza o motivo.
        safe, reason = check_pose_safety(chain, q, center, z_floor, r_safe)
        if not safe:
            q2, ok2, pe2, pt2, safe2 = _solve_safe(
                chain, P, d, last_q, center, z_floor, r_safe)
            if safe2:
                q, ok, pos_err, point_err = q2, ok2, pe2, pt2
                safe = True
            else:
                if "chao" in reason:
                    skipped_floor += 1
                else:
                    skipped_piece += 1
                continue  # ponto inseguro irrecuperavel: descarta

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

    # UNWRAP ANGULAR: antes de densificar/sequenciar, escolhe o representante
    # +/-360k de cada junta revoluta que minimiza o salto vs a pose anterior
    # (sem sair dos limites do URDF). Corrige o wrap 170->-170 (340 deg) para
    # 170->190 (20 deg), encurtando a interpolacao linear. Aplicado aos
    # KEYPOINTS para que poses_deg, sim, viewer e robo real partam do mesmo dado.
    poses_deg = unwrap_keypoints(poses_deg, limits_deg)

    # FASE 3: sequencia densificada (fonte da verdade do movimento) sem saltos.
    # Densificacao SEGURA: a interpolacao entre dois keypoints seguros pode
    # passar por uma config insegura -> validamos e removemos essas poses.
    motion_deg, motion_removed = _densify_safe(
        poses_deg, chain, center, z_floor, r_safe, max_step_deg=smooth_step_deg)

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
        skipped_floor=skipped_floor,
        skipped_piece=skipped_piece,
        motion_removed_unsafe=motion_removed,
        reconfig_avoided=reconfig_avoided,
        safe=bool(len(motion_deg) > 0),
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


def _max_jump_deg(seq_deg: List[List[float]]) -> float:
    if len(seq_deg) < 2:
        return 0.0
    mj = 0.0
    for a, b in zip(seq_deg, seq_deg[1:]):
        mj = max(mj, max(abs(x - y) for x, y in zip(a, b)))
    return float(mj)


def _plan_quality_score(plan: OrbitPlan) -> float:
    """Score escalar para comparar centros da peça (maior = melhor)."""
    m = plan.metrics()
    n = float(m.get("n", 0))
    frac = float(m.get("frac_within_3deg", 0.0))
    pos_mm = float(m.get("mean_pos_err_mm", 1e6))
    jump = _max_jump_deg(plan.motion_deg)
    skipped = float(plan.skipped_floor + plan.skipped_piece + plan.motion_removed_unsafe)
    return (
        8.0 * frac
        + 0.01 * n
        - 0.03 * pos_mm
        - 0.03 * jump
        - 0.12 * skipped
        + (1.0 if plan.safe else -2.0)
    )


def optimize_orbit_center(params: OrbitParams) -> dict:
    """Sugere centro (X,Y,Z) que tende a produzir órbita mais estável/segura."""
    cx, cy, cz = params.center
    t0 = time.perf_counter()
    budget_s = 10.0

    coarse = replace(
        params,
        # Busca de centro precisa ser rapida: o plano completo roda depois,
        # quando o bridge chama submit_orbit() com o centro escolhido.
        levels=min(params.levels, 3),
        points_per_level=min(params.points_per_level, 8),
    )

    def clamp_center(x, y, z):
        return (
            float(min(0.65, max(0.15, x))),
            float(min(0.65, max(0.10, y))),
            float(min(0.50, max(0.05, z))),
        )

    best = None
    tested = 0
    for dx in (0.0, -0.04, 0.04):
        for dy in (0.0, -0.04, 0.04):
            for dz in (0.0, -0.02, 0.02):
                if (time.perf_counter() - t0) > budget_s:
                    break
                c = clamp_center(cx + dx, cy + dy, cz + dz)
                try:
                    p = replace(coarse, center=c)
                    plan = plan_orbit(p)
                    s = _plan_quality_score(plan)
                    tested += 1
                    if best is None or s > best[0]:
                        best = (s, c)
                except Exception:
                    continue
            if (time.perf_counter() - t0) > budget_s:
                break
        if (time.perf_counter() - t0) > budget_s:
            break

    if best is None:
        return {
            "ok": False,
            "msg": "nenhum centro viavel encontrado na busca",
            "tested": tested,
            "best_center": list(params.center),
        }

    bx, by, bz = best[1]
    refined = (best[0], best[1])
    for dx in (-0.02, 0.0, 0.02):
        for dy in (-0.02, 0.0, 0.02):
            for dz in (-0.015, 0.0, 0.015):
                if (time.perf_counter() - t0) > budget_s:
                    break
                c = clamp_center(bx + dx, by + dy, bz + dz)
                try:
                    p = replace(coarse, center=c)
                    plan = plan_orbit(p)
                    s = _plan_quality_score(plan)
                    tested += 1
                    if s > refined[0]:
                        refined = (s, c)
                except Exception:
                    continue
            if (time.perf_counter() - t0) > budget_s:
                break
        if (time.perf_counter() - t0) > budget_s:
            break

    return {
        "ok": True,
        "tested": tested,
        "best_center": [float(v) for v in refined[1]],
        "score": float(refined[0]),
        "elapsed_ms": int((time.perf_counter() - t0) * 1000),
    }


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


def validate_sequence_safety(seq_deg: List[List[float]],
                             center,
                             z_floor: float = Z_FLOOR,
                             r_safe: float = R_SAFE,
                             chain: Optional[List[JointDef]] = None,
                             urdf_path: str = URDF_PATH) -> None:
    """Gate de SEGURANCA: levanta ValueError se QUALQUER pose violar as regras.

    Analoga a validate_sequence_limits, mas geometrica: reprova qualquer pose
    cuja cadeia (juntas + corpo dos links) fure o chao (z < z_floor) ou invada a
    esfera de seguranca da peca (dist < r_safe). Usada como gate no robo real
    (run_orbit.py) e no recalculo ao vivo (sim/bridge.py).
    """
    if chain is None:
        chain = parse_urdf_chain(urdf_path)
    for i, pose in enumerate(seq_deg):
        ok, reason = check_pose_safety(
            chain, np.radians(pose), center, z_floor, r_safe)
        if not ok:
            raise ValueError(f"Pose #{i} INSEGURA: {reason}")


# --------------------------------------------------------------------------- #
# CLI de validacao
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import time as _time
    _t0 = _time.perf_counter()
    plan = plan_orbit()
    _dt = _time.perf_counter() - _t0
    m = plan.metrics()
    print("=== Orbita IK ===")
    print(f"tempo plan_orbit  : {_dt:.3f} s")
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

    # --- SEGURANCA -------------------------------------------------------- #
    _p = OrbitParams()
    print("=== Seguranca ===")
    print(f"z_floor / r_safe  : {_p.z_floor:.3f} m / {_p.r_safe:.3f} m")
    print(f"keypoints pulados : {m['skipped_safety']} "
          f"(chao={m['skipped_floor']}, peca={m['skipped_piece']})")
    print(f"motion removidas  : {m['motion_removed_unsafe']}")
    print(f"flag safe         : {m['safe']}")
    # confirma que NENHUMA pose de motion_deg viola (varre todas).
    _chain = parse_urdf_chain()
    _C = np.array(_p.center)
    _viol = 0
    _first_reason = ""
    for _pose in plan.motion_deg:
        _ok, _r = check_pose_safety(_chain, np.radians(_pose), _C,
                                    _p.z_floor, _p.r_safe)
        if not _ok:
            _viol += 1
            if not _first_reason:
                _first_reason = _r
    print(f"violacoes motion  : {_viol}" +
          (f"  ({_first_reason})" if _viol else "  (ZERO)"))

    # --- caso adverso: r_safe grande deve pular/rejeitar pontos ----------- #
    _adv = OrbitParams(r_safe=0.20)
    _plan_adv = plan_orbit(params=_adv)
    _ma = _plan_adv.metrics()
    _viol_adv = 0
    for _pose in _plan_adv.motion_deg:
        _ok, _ = check_pose_safety(_chain, np.radians(_pose),
                                   np.array(_adv.center), _adv.z_floor, _adv.r_safe)
        if not _ok:
            _viol_adv += 1
    print("=== Adverso (r_safe=0.20) ===")
    print(f"keypoints pulados : {_ma['skipped_safety']} "
          f"(chao={_ma['skipped_floor']}, peca={_ma['skipped_piece']})")
    print(f"motion removidas  : {_ma['motion_removed_unsafe']}")
    print(f"motion poses      : {len(_plan_adv.motion_deg)}, violacoes: {_viol_adv}")
