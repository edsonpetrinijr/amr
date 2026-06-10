"""Ponte ao vivo: robo real Fairino FR5 -> simulacao 3D no navegador.

Serve os arquivos estaticos da simulacao (index.html, urdf, meshes) e expoe:

    GET /api/joints        -> JSON {ok, joints:[j1..j6] graus, tcp:[...], ts, source}
    GET /api/camera.mjpg   -> stream MJPEG da camera eye-in-hand (flange)
    GET /api/snapshot.jpg  -> ultimo frame da camera (JPEG unico)

Uma thread de fundo le as juntas do robo via SDK (XML-RPC) e mantem o ultimo
valor em cache; o navegador faz polling de /api/joints (~15 Hz) e move o modelo.
Outra thread captura frames da webcam montada na ponta do robo.

Uso:
    python bridge.py                       # robo real 192.168.58.2 + webcam 0
    python bridge.py --ip 192.168.58.2     # escolher IP
    python bridge.py --camera 1            # escolher indice da webcam
    python bridge.py --no-camera           # sem camera
    python bridge.py --simulate            # sem hardware (robo e camera virtuais)

Seguranca: a leitura de juntas e sempre passiva. Comandos de movimento
(/api/move, /api/wave, /api/orbit-run) so executam fora do modo --simulate,
com o robo conectado, e a orbita real reusa as gates de seguranca do
run_orbit.py (limites URDF + chao + esfera da peca + MoveJ bloqueante).
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import math
from urllib.parse import urlsplit

# Permite importar os pacotes 'fairino' e 'vision' que ficam na pasta pai.
SIM_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SIM_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

HOME_JOINTS = [0.0, -20.0, -90.0, -70.0, 90.0, 0.0]


# --------------------------------------------------------------------------- #
# Estado compartilhado entre as threads de fundo e o servidor HTTP
# --------------------------------------------------------------------------- #
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.joints = list(HOME_JOINTS)
        self.tcp = None                 # [x,y,z,rx,ry,rz] em mm/graus, ou None
        self.ts = 0.0                   # timestamp da ultima leitura boa
        self.connected = False
        self.source = "starting"        # "robot" | "simulate" | "starting"
        self.error = ""
        # Movimento (botao "mover robo")
        self.ip = "192.168.58.2"
        self.simulate = False
        self.moving = False             # True enquanto o robo real esta se movendo
        self.move_msg = ""              # texto de status do movimento
        # Camera
        self.frame_jpeg = None          # bytes do ultimo JPEG
        self.frame_ts = 0.0
        self.cam_ok = False
        # Plano de orbita simulado (para o HTML desenhar guias fiéis ao movimento).
        self.orbit_plan = None
        # Runtime da orbita: parametros atuais + sequencia que o poller TOCA.
        # A versao incrementa a cada troca para o poller reiniciar o playback
        # de forma atomica (sem misturar duas sequencias).
        self.orbit_params = None        # OrbitParams atual
        self.orbit_sequence = None      # motion_deg atual (lista de poses, graus)
        self.orbit_seq_version = 0
        # Estado do job de recalculo ASSINCRONO da orbita.
        # status: "idle" | "calculando" | "pronto" | "erro"
        self.orbit_status = "idle"
        self.orbit_error = ""           # ultima mensagem de erro (status=="erro")
        self.orbit_metrics = None       # metricas da ultima solucao pronta
        self.sim_speed = 1.0            # multiplicador da velocidade no --simulate
        self.sim_base_pps = 5.0         # pontos/seg base do playback simulado
        # Soft limits do controlador (preenchido no startup, modo real).
        # Quando presente, toda orbita gerada e validada contra ele ANTES de
        # virar status='pronto'. Assim nenhuma trajetoria invalida chega ao
        # botao de executar.
        self.soft_limits_deg = None     # [(neg1,pos1), ...] em graus, ou None

    def set_joints(self, joints, tcp=None, source="robot"):
        with self.lock:
            self.joints = list(joints)
            if tcp is not None:
                self.tcp = list(tcp)
            self.ts = time.time()
            self.connected = True
            self.source = source
            self.error = ""

    def set_error(self, msg):
        with self.lock:
            self.connected = False
            self.error = str(msg)

    def snapshot(self):
        with self.lock:
            return {
                "ok": self.connected,
                "joints": list(self.joints),
                "tcp": list(self.tcp) if self.tcp else None,
                "ts": self.ts,
                "age_ms": int((time.time() - self.ts) * 1000) if self.ts else None,
                "source": self.source,
                "error": self.error,
                "camera": self.cam_ok,
                "moving": self.moving,
                "move_msg": self.move_msg,
            }

    def set_frame(self, jpeg_bytes):
        with self.lock:
            self.frame_jpeg = jpeg_bytes
            self.frame_ts = time.time()
            self.cam_ok = True

    def get_frame(self):
        with self.lock:
            return self.frame_jpeg

    def set_orbit_plan(self, plan_dict):
        with self.lock:
            self.orbit_plan = dict(plan_dict)

    def get_orbit_plan(self):
        with self.lock:
            return self.orbit_plan

    def set_orbit_runtime(self, params, sequence):
        """Troca atomica dos params + da sequencia tocada pelo poller.

        Incrementa a versao para o poller perceber a troca e reiniciar o
        indice de reproducao do zero (sem misturar a sequencia antiga e a nova).
        """
        with self.lock:
            self.orbit_params = params
            self.orbit_sequence = list(sequence)
            self.orbit_seq_version += 1

    def get_orbit_sequence(self):
        with self.lock:
            seq = list(self.orbit_sequence) if self.orbit_sequence else None
            return seq, self.orbit_seq_version

    def get_orbit_params(self):
        with self.lock:
            return self.orbit_params

    def set_orbit_status(self, status, metrics=None, error=""):
        """Atualiza o estado do job assincrono de recalculo da orbita."""
        with self.lock:
            self.orbit_status = status
            if status == "calculando":
                self.orbit_error = ""        # comecou de novo: limpa erro antigo
            if status == "erro":
                self.orbit_error = str(error)
            if metrics is not None:
                self.orbit_metrics = metrics

    def get_orbit_status(self):
        with self.lock:
            return {
                "status": self.orbit_status,
                "error": self.orbit_error,
                "metrics": self.orbit_metrics,
                "version": self.orbit_seq_version,
                "sim_speed": self.sim_speed,
            }

    def set_sim_speed(self, speed: float):
        with self.lock:
            self.sim_speed = float(speed)

    def get_sim_speed(self) -> float:
        with self.lock:
            return float(self.sim_speed)

    def set_sim_base_pps(self, pps: float):
        with self.lock:
            self.sim_base_pps = float(pps)

    def set_soft_limits(self, pairs):
        with self.lock:
            self.soft_limits_deg = (
                [(float(lo), float(hi)) for (lo, hi) in pairs] if pairs else None)

    def get_soft_limits(self):
        with self.lock:
            return list(self.soft_limits_deg) if self.soft_limits_deg else None

    def get_sim_runtime(self):
        """Snapshot do estado de playback simulado (sequencia + velocidade)."""
        with self.lock:
            seq = list(self.orbit_sequence) if self.orbit_sequence else None
            return {
                "sequence": seq,
                "version": self.orbit_seq_version,
                "base_points_per_sec": float(self.sim_base_pps),
                "sim_speed": float(self.sim_speed),
            }


STATE = SharedState()
MOVE_LOCK = threading.Lock()
# Serializa recalculos de orbita (IK pesado, ~1-2s). NAO segura STATE.lock
# durante o calculo, entao GET /api/joints continua respondendo em paralelo.
ORBIT_LOCK = threading.Lock()

# --- Recalculo ASSINCRONO da orbita -----------------------------------------
# Um unico worker de fundo serializa os recalculos. O POST /api/orbit-config
# NAO bloqueia: valida, enfileira os params e responde na hora. Se chegarem
# varios POSTs durante um calculo, so o MAIS RECENTE roda em seguida
# (coalescing) -- os intermediarios sao descartados.
_ORBIT_CV = threading.Condition()
_orbit_pending = None        # OrbitParams a calcular a seguir (ou None)
_orbit_worker = None         # thread unica do worker
_optimize_thread = None      # thread unica da busca automatica do centro

# Cache simples de payloads IK por parametros exatos (LRU curto), para evitar
# recomputar quando o usuario reaplica a mesma configuracao.
_ORBIT_CACHE_LOCK = threading.Lock()
_ORBIT_CACHE = {}            # key -> payload dict
_ORBIT_CACHE_ORDER = []      # ordem de uso (mais antigo na frente)
_ORBIT_CACHE_MAX = 16

# Warmup do ProcessPool (spawn/import no Windows) para reduzir latencia do
# PRIMEIRO recalculo real de orbita.
_ORBIT_WARMUP_STARTED = False
_ORBIT_WARMUP_LOCK = threading.Lock()

# Faixas sanas aceitas pelo endpoint /api/orbit-config.
ORBIT_RANGES = {
    "levels": (1, 12),
    "points_per_level": (6, 48),
    "radius_bottom": (0.10, 0.40),
    "radius_top": (0.10, 0.40),
    "z_floor": (0.0, 0.30),
    "r_safe": (0.0, 0.40),
}


def _orbit_plan_dict(plan, params=None):
    """Serializa um OrbitPlan no formato consumido por /api/orbit-plan."""
    out = {
        "levels": plan.levels,
        "points_per_level": plan.points_per_level,
        "poses": plan.poses_deg,          # keypoints resolvidos (IK)
        "points": plan.points,            # alvos cartesianos (m, frame base)
        "approaches": plan.approaches,    # direcao look-at por keypoint
        "center": plan.center,            # C no frame base (m)
        "point_errs_deg": plan.point_errs_deg,
        "pos_errs_m": plan.pos_errs_m,
        "metrics": plan.metrics(),
    }
    if params is not None:
        out.update({
            "radius_bottom": float(params.radius_bottom),
            "radius_top": float(params.radius_top),
            "z_bottom": float(params.z_bottom),
            "z_top": float(params.z_top),
            "z_floor": float(params.z_floor),
            "r_safe": float(params.r_safe),
        })
    return out


# --- Recalculo da orbita em OUTRO PROCESSO ----------------------------------
# O IK (plan_orbit) e' CPU-bound em Python puro: segura o GIL ~2s e congelaria
# o ThreadingHTTPServer inteiro (ate' o GET /api/joints). Por isso o calculo
# pesado roda num ProcessPoolExecutor de 1 worker, reutilizado. O processo
# filho SO calcula e devolve um dict picklavel; quem toca o STATE e' sempre o
# processo PRINCIPAL.
_ORBIT_EXECUTOR = None
_ORBIT_EXECUTOR_LOCK = threading.Lock()


def _orbit_cache_key(params):
    """Chave hashavel para cache de payload IK por OrbitParams."""
    c = tuple(round(float(v), 5) for v in params.center)
    return (
        round(float(params.radius_bottom), 5),
        round(float(params.radius_top), 5),
        round(float(params.z_bottom), 5),
        round(float(params.z_top), 5),
        int(params.levels),
        int(params.points_per_level),
        round(float(params.z_floor), 5),
        round(float(params.r_safe), 5),
        c,
    )


def _orbit_cache_get(params):
    """Busca payload no cache e atualiza ordem LRU."""
    key = _orbit_cache_key(params)
    with _ORBIT_CACHE_LOCK:
        payload = _ORBIT_CACHE.get(key)
        if payload is None:
            return None
        try:
            _ORBIT_CACHE_ORDER.remove(key)
        except ValueError:
            pass
        _ORBIT_CACHE_ORDER.append(key)
        return payload


def _orbit_cache_put(params, payload):
    """Grava payload no cache com eviccao LRU curta."""
    key = _orbit_cache_key(params)
    with _ORBIT_CACHE_LOCK:
        _ORBIT_CACHE[key] = payload
        try:
            _ORBIT_CACHE_ORDER.remove(key)
        except ValueError:
            pass
        _ORBIT_CACHE_ORDER.append(key)
        while len(_ORBIT_CACHE_ORDER) > _ORBIT_CACHE_MAX:
            old = _ORBIT_CACHE_ORDER.pop(0)
            _ORBIT_CACHE.pop(old, None)


def _orbit_worker_warmup_noop():
    """Trabalho minimo para forcar spawn/import do worker de processo."""
    return True


def _compute_orbit_payload(params):
    """Trabalho pesado de IK, rodado no PROCESSO FILHO (CPU-bound).

    Module-level e picklavel (Windows usa spawn -> re-importa este modulo).
    NAO toca o STATE (ele so existe no processo principal): apenas resolve a
    orbita, valida limites e devolve um dict puro com tudo que o pai precisa.
    """
    import os as _os
    import sys as _sys
    sim_dir = _os.path.dirname(_os.path.abspath(__file__))
    root_dir = _os.path.dirname(sim_dir)
    if root_dir not in _sys.path:
        _sys.path.insert(0, root_dir)
    from sim.orbit_ik import (plan_orbit, urdf_joint_limits_deg,
                              validate_sequence_limits, validate_sequence_safety)
    plan = plan_orbit(params=params)
    # Safety igual ao caminho do robo real: nenhuma pose fora dos limites.
    validate_sequence_limits(plan.motion_deg, urdf_joint_limits_deg())
    # Safety GEOMETRICA: nenhuma pose fura o chao ou invade a esfera da peca.
    if not plan.motion_deg:
        raise ValueError("plano sem poses seguras (todas removidas por seguranca)")
    validate_sequence_safety(plan.motion_deg, params.center,
                             z_floor=params.z_floor, r_safe=params.r_safe)
    return {
        "plan_dict": _orbit_plan_dict(plan, params),   # para STATE.set_orbit_plan
        "params": params,                       # para STATE.set_orbit_runtime
        "sequence": plan.motion_deg,            # idem (poses que o poller toca)
        "metrics": plan.metrics(),
    }


def _compute_optimized_center(params):
    """Rodado no processo filho: sugere centro (XYZ) melhor para a órbita."""
    import os as _os
    import sys as _sys
    sim_dir = _os.path.dirname(_os.path.abspath(__file__))
    root_dir = _os.path.dirname(sim_dir)
    if root_dir not in _sys.path:
        _sys.path.insert(0, root_dir)
    from sim.orbit_ik import optimize_orbit_center
    return optimize_orbit_center(params)


def _get_orbit_executor():
    """Cria (lazy) o ProcessPoolExecutor de 1 worker reutilizado.

    LAZY de proposito: no Windows o spawn re-importa bridge.py; criar o
    executor no import do modulo causaria recursao/fork-bomb. So criamos
    quando o primeiro recalculo realmente acontece, em runtime.
    """
    global _ORBIT_EXECUTOR
    with _ORBIT_EXECUTOR_LOCK:
        if _ORBIT_EXECUTOR is None:
            _ORBIT_EXECUTOR = ProcessPoolExecutor(max_workers=1)
            atexit.register(_shutdown_orbit_executor)
        return _ORBIT_EXECUTOR


def _shutdown_orbit_executor():
    """Encerra o executor (idempotente). Chamado no atexit e no finally do main."""
    global _ORBIT_EXECUTOR
    with _ORBIT_EXECUTOR_LOCK:
        ex = _ORBIT_EXECUTOR
        _ORBIT_EXECUTOR = None
    if ex is not None:
        ex.shutdown(wait=False, cancel_futures=True)


def _warmup_orbit_executor_async():
    """Dispara warmup em background (idempotente, nao bloqueante)."""
    global _ORBIT_WARMUP_STARTED
    with _ORBIT_WARMUP_LOCK:
        if _ORBIT_WARMUP_STARTED:
            return
        _ORBIT_WARMUP_STARTED = True

    def _run():
        try:
            ex = _get_orbit_executor()
            ex.submit(_orbit_worker_warmup_noop).result(timeout=15)
            print("[bridge] orbit worker warmup pronto")
        except Exception as e:
            # Warmup e best-effort: nao deve derrubar a ponte.
            print(f"[bridge] warmup do orbit worker falhou: {e}")

    threading.Thread(target=_run, daemon=True).start()


def _publish_orbit(params):
    """Resolve a orbita p/ `params`, valida e publica de forma atomica.

    SINGLE SOURCE OF TRUTH: usa plan_orbit/validate de orbit_ik.py (as MESMAS
    funcoes do robo real em run_orbit.py). So toca o STATE depois que o plano
    foi resolvido e validado -> em caso de erro o estado anterior fica intacto.
    Retorna o dict de metricas da nova solucao.
    """
    from sim.orbit_ik import (plan_orbit, urdf_joint_limits_deg,
                              validate_sequence_limits, validate_sequence_safety)
    with ORBIT_LOCK:
        plan = plan_orbit(params=params)
        # Safety igual ao caminho do robo real: nenhuma pose fora dos limites.
        validate_sequence_limits(plan.motion_deg, urdf_joint_limits_deg())
        # Safety GEOMETRICA: chao + esfera da peca.
        if not plan.motion_deg:
            raise ValueError("plano sem poses seguras (todas removidas por seguranca)")
        validate_sequence_safety(plan.motion_deg, params.center,
                                 z_floor=params.z_floor, r_safe=params.r_safe)
        # Soft limits do controlador (se ja lidos do robo real): garante que
        # NENHUMA pose violadora chegue ao painel/playback.
        _validate_sequence_soft_limits(plan.motion_deg)
        STATE.set_orbit_plan(_orbit_plan_dict(plan, params))
        STATE.set_orbit_runtime(params, plan.motion_deg)
        return plan.metrics()


def _validate_sequence_soft_limits(seq):
    """Valida `seq` contra os soft limits cacheados em STATE (se disponiveis).

    No-op quando soft limits ainda nao foram lidos (modo simulate, ou antes
    do fetch no startup). Mensagem orientada ao usuario: diz qual junta e
    qual a margem, para ele ajustar o slider correspondente.
    """
    pairs = STATE.get_soft_limits()
    if not pairs:
        return
    for p_idx, pose in enumerate(seq):
        for j, (val, (lo, hi)) in enumerate(zip(pose, pairs)):
            if not (lo - 1e-3 <= val <= hi + 1e-3):
                raise ValueError(
                    f"orbita atinge j{j + 1}={val:.1f}° (limite [{lo:.1f}, "
                    f"{hi:.1f}]) na pose #{p_idx}. Ajuste raios/altura/centro "
                    f"da peca para reduzir o alcance."
                )


def _fetch_soft_limits_async(ip: str):
    """Le os soft limits do controlador uma vez, em background, no startup.

    Abre uma conexao curta (mesmo padrao do FairinoRobot) so para ler
    GetJointSoftLimitDeg, popula STATE.soft_limits_deg e desconecta. A partir
    dai, toda nova orbita e validada contra esses limites no worker.
    """
    def _run():
        try:
            from vision.robot_scan import FairinoRobot
            r = FairinoRobot(ip=ip)
            r.connect()
            try:
                res = r.robot.GetJointSoftLimitDeg(1)
            finally:
                r.disconnect()
            if not (isinstance(res, tuple) and res[0] == 0 and len(res) >= 2):
                print(f"[bridge] aviso: soft limits indisponiveis ({res!r})")
                return
            flat = [float(x) for x in res[1]]
            if len(flat) < 12:
                print(f"[bridge] aviso: soft limits incompletos ({len(flat)} valores)")
                return
            pairs = [(flat[i * 2], flat[i * 2 + 1]) for i in range(6)]
            STATE.set_soft_limits(pairs)
            print(f"[bridge] soft limits lidos: "
                  + ", ".join(f"j{i+1}=[{lo:.0f},{hi:.0f}]"
                              for i, (lo, hi) in enumerate(pairs)))
            # Recalcula a orbita atual contra os limites recem-lidos para que
            # qualquer violacao apareca imediatamente no painel.
            params = STATE.get_orbit_params()
            if params is not None:
                submit_orbit(params)
        except Exception as e:  # noqa: BLE001
            print(f"[bridge] aviso: nao foi possivel ler soft limits: {e}")
    threading.Thread(target=_run, daemon=True).start()


def _validate_orbit_overrides(overrides):
    """Converte/valida os campos opcionais do POST. Levanta ValueError claro."""
    from sim.orbit_ik import OrbitParams
    allowed = ("radius_bottom", "radius_top", "z_bottom", "z_top",
               "levels", "points_per_level", "center", "z_floor", "r_safe")
    unknown = [k for k in overrides if k not in allowed]
    if unknown:
        raise ValueError(f"campos desconhecidos: {', '.join(unknown)}")
    clean = {}
    for key, val in overrides.items():
        if val is None:
            continue
        if key in ("levels", "points_per_level"):
            try:
                val = int(val)
            except (TypeError, ValueError):
                raise ValueError(f"{key} deve ser inteiro")
        elif key == "center":
            if not (isinstance(val, (list, tuple)) and len(val) == 3):
                raise ValueError("center deve ser [x, y, z]")
            val = tuple(float(v) for v in val)
        else:
            try:
                val = float(val)
            except (TypeError, ValueError):
                raise ValueError(f"{key} deve ser numero")
        rng = ORBIT_RANGES.get(key)
        if rng is not None:
            lo, hi = rng
            if not (lo <= val <= hi):
                raise ValueError(
                    f"{key}={val} fora da faixa permitida [{lo}, {hi}]")
        clean[key] = val
    return clean


def recompute_orbit(overrides):
    """Aplica overrides validados sobre os params atuais e re-resolve a orbita.

    Merge com os params correntes => updates parciais (so levels, so radius...).
    Retorna o dict de metricas. Levanta ValueError em entrada fora de faixa.
    """
    from dataclasses import replace
    from sim.orbit_ik import OrbitParams
    clean = _validate_orbit_overrides(overrides)
    base = STATE.get_orbit_params() or OrbitParams()
    params = replace(base, **clean)
    return _publish_orbit(params)


def _merge_orbit_params(overrides):
    """Valida overrides e mescla com os params atuais -> OrbitParams.

    Roda na thread do handler (rapido) para que erros de faixa virem 400 na
    hora. Levanta ValueError em entrada fora de faixa.
    """
    from dataclasses import replace
    from sim.orbit_ik import OrbitParams
    clean = _validate_orbit_overrides(overrides)
    base = STATE.get_orbit_params() or OrbitParams()
    return replace(base, **clean)


def _orbit_worker_loop():
    """Worker unico: recalcula a orbita em background, com coalescing.

    Espera por params pendentes; ao terminar um calculo, se chegou um pedido
    mais recente durante o caminho, roda so o ultimo (descarta intermediarios).
    """
    global _orbit_pending
    while True:
        with _ORBIT_CV:
            while _orbit_pending is None:
                _ORBIT_CV.wait()
            params = _orbit_pending
            _orbit_pending = None
        STATE.set_orbit_status("calculando")
        try:
            t0 = time.perf_counter()
            cache_hit = False
            payload = _orbit_cache_get(params)
            if payload is None:
                # O trabalho pesado (IK, ~2s, CPU-bound) roda em OUTRO PROCESSO:
                # nao segura o GIL do servidor -> GET /api/joints continua em ms.
                # Esperamos o future AQUI (no worker thread), nunca no handler.
                executor = _get_orbit_executor()
                payload = executor.submit(_compute_orbit_payload, params).result()
                _orbit_cache_put(params, payload)
            else:
                cache_hit = True
            # Soft limits do controlador: barreira final ANTES de publicar.
            # Cobre tambem cache hits (caso os limites tenham sido lidos
            # depois que a entrada foi cacheada).
            _validate_sequence_soft_limits(payload["sequence"])
            # De volta no PROCESSO PRINCIPAL: aplica no STATE atomicamente.
            with ORBIT_LOCK:
                STATE.set_orbit_plan(payload["plan_dict"])
                STATE.set_orbit_runtime(payload["params"], payload["sequence"])
            metrics = dict(payload["metrics"] or {})
            metrics["calc_ms"] = int((time.perf_counter() - t0) * 1000)
            metrics["cache_hit"] = cache_hit
            STATE.set_orbit_status("pronto", metrics=metrics)
        except Exception as e:  # noqa: BLE001
            STATE.set_orbit_status("erro", error=e)
            print(f"[bridge] erro ao recalcular orbita: {e}")


def submit_orbit(params):
    """Enfileira params (ja validados/mesclados) para recalculo assincrono.

    NAO bloqueia: marca status 'calculando', guarda o pedido mais recente
    (coalescing) e garante que o worker esteja rodando. O POST responde na hora.
    """
    global _orbit_pending, _orbit_worker
    STATE.set_orbit_status("calculando")
    with _ORBIT_CV:
        _orbit_pending = params          # coalescing: so o mais recente roda
        if _orbit_worker is None or not _orbit_worker.is_alive():
            _orbit_worker = threading.Thread(
                target=_orbit_worker_loop, daemon=True)
            _orbit_worker.start()
        _ORBIT_CV.notify()


def _optimize_center_loop(base_params):
    """Busca centro melhor em background e enfileira recálculo da órbita."""
    global _optimize_thread
    try:
        STATE.set_orbit_status("calculando")
        executor = _get_orbit_executor()
        res = executor.submit(_compute_optimized_center, base_params).result()
        if not isinstance(res, dict) or not res.get("ok"):
            msg = (res or {}).get("msg", "falha na otimizacao do centro")
            STATE.set_orbit_status("erro", error=msg)
            return

        from dataclasses import replace
        center = tuple(float(v) for v in res.get("best_center", base_params.center))
        params = replace(base_params, center=center)
        submit_orbit(params)
    except Exception as e:  # noqa: BLE001
        STATE.set_orbit_status("erro", error=f"falha ao otimizar centro: {e}")
    finally:
        _optimize_thread = None


def submit_orbit_center_optimization():
    """Dispara otimização de centro sem bloquear o request HTTP."""
    global _optimize_thread
    from sim.orbit_ik import OrbitParams
    base = STATE.get_orbit_params() or OrbitParams()
    if _optimize_thread is not None and _optimize_thread.is_alive():
        return False
    _optimize_thread = threading.Thread(
        target=_optimize_center_loop, args=(base,), daemon=True)
    _optimize_thread.start()
    return True



# --------------------------------------------------------------------------- #
# Movimento do robo REAL
# Usa uma conexao SEPARADA para nao competir com a thread que le as juntas,
# assim o modelo 3D continua atualizando ao vivo durante o movimento.
# --------------------------------------------------------------------------- #
def _run_moves(build_seq):
    """Roda uma sequencia de waypoints. build_seq(p0) -> [(label, pose, vel), ...]."""
    if not MOVE_LOCK.acquire(blocking=False):
        return  # ja tem um movimento em andamento
    mover = None  # GAP-5: declared here so finally can always reference it safely
    try:
        STATE.moving = True
        STATE.move_msg = "conectando..."
        from vision.robot_scan import FairinoRobot
        mover = FairinoRobot(ip=STATE.ip)
        mover.connect()
        STATE.move_msg = "habilitando..."
        mover.enable()

        # Pose atual: todos os waypoints sao RELATIVOS a ela e voltam ao fim.
        p0 = mover.get_joints()
        for label, pose, vel in build_seq(p0):
            STATE.move_msg = label
            mover.move_joints(pose, vel=vel, tool=0, user=0)  # bloqueante
        STATE.move_msg = "concluido"
    except Exception as e:  # noqa: BLE001
        STATE.move_msg = f"erro: {e}"
        print(f"[bridge] erro no movimento: {e}")
    finally:
        STATE.moving = False
        # GAP-5 fix: release the mover connection so we don't leak TCP connections.
        if mover is not None:
            try:
                mover.disconnect()
            except Exception:
                pass
        try:
            MOVE_LOCK.release()
        except Exception:
            pass


def _seq_demo(p0):
    """Balanca a base (J1) e gira o punho (J6), depois volta."""
    def wp(dj1, dj6):
        p = list(p0)
        p[0] += dj1
        p[5] += dj6
        return p
    return [
        ("balancando base ->", wp(25.0, 60.0), 20),
        ("balancando base <-", wp(-25.0, -60.0), 20),
        ("voltando ao inicio", list(p0), 20),
    ]


def _seq_wave(p0):
    """Tchau: levanta a mao (J5) e balanca o punho (J6) de um lado pro outro."""
    raised = list(p0)
    raised[4] += 45.0   # J5 levanta a "mao"

    def wave(dj6):
        p = list(raised)
        p[5] += dj6
        return p

    seq = [("levantando a mao", list(raised), 25)]
    for i in range(3):
        seq.append((f"tchau! {i + 1}", wave(-45.0), 45))
        seq.append((f"tchau! {i + 1}", wave(45.0), 45))
    seq.append(("abaixando", list(p0), 25))
    return seq


def run_demo_move():
    _run_moves(_seq_demo)


def run_wave_move():
    _run_moves(_seq_wave)


# --------------------------------------------------------------------------- #
# Executa a ORBITA DE INSPECAO no robo real
# Reusa a fonte unica da verdade (orbit_joint_sequence) — exatamente o que o
# viewer mostra — e as MESMAS gates de seguranca do run_orbit.py:
#   1) limites de junta do URDF; 2) chao + esfera da peca.
# So roda se a ultima orbita gerada esta em status "pronto".
# --------------------------------------------------------------------------- #
def run_orbit_on_real_robot(vel: float):
    """Executa a orbita atual no robo real (bloqueante, em thread)."""
    if not MOVE_LOCK.acquire(blocking=False):
        STATE.move_msg = "ja em movimento"
        return
    mover = None
    try:
        from sim.orbit_ik import (
            OrbitParams,
            orbit_joint_sequence,
            urdf_joint_limits_deg,
            validate_sequence_limits,
            validate_sequence_safety,
        )
        from vision.robot_scan import FairinoRobot

        STATE.moving = True
        STATE.move_msg = "gerando orbita..."
        params = STATE.get_orbit_params() or OrbitParams()
        seq = orbit_joint_sequence(params)
        if not seq:
            raise RuntimeError("orbita vazia; ajuste parametros e tente de novo")

        STATE.move_msg = f"validando {len(seq)} poses..."
        validate_sequence_limits(seq, urdf_joint_limits_deg())
        validate_sequence_safety(seq, params.center,
                                 z_floor=params.z_floor, r_safe=params.r_safe)

        STATE.move_msg = "conectando..."
        mover = FairinoRobot(ip=STATE.ip)
        mover.connect()
        STATE.move_msg = "habilitando..."
        mover.enable()
        mover.validate_scan_poses(seq)  # soft limits do controlador

        total = len(seq)
        # Trajetoria FLUIDA: enfileira tudo com blendT>0 (nao-bloqueante) e
        # deixa o CONTROLADOR misturar os cantos. Esperar entre poses anularia
        # o blend (o robo chegaria, pararia, e so dai a proxima entraria).
        blend_ms = 200.0
        pacing_s = 0.03  # ~33 poses/s no XML-RPC; evita estourar o buffer
        for i, pose in enumerate(seq):
            STATE.move_msg = f"enfileirando {i + 1}/{total} (vel {vel:.0f}%)"
            if i < total - 1:
                mover.move_joints_blend(pose, vel=vel, tool=0, user=0,
                                         blend_ms=blend_ms)
                time.sleep(pacing_s)
            else:
                # Ultimo waypoint: aguarda fila esvaziar e faz parada limpa.
                STATE.move_msg = "finalizando orbita..."
                mover.move_joints_blend(pose, vel=vel, tool=0, user=0,
                                         blend_ms=0.0)
                mover.wait_motion_done(timeout_s=60.0)
        STATE.move_msg = "orbita concluida"
    except Exception as e:  # noqa: BLE001
        STATE.move_msg = f"erro: {e}"
        print(f"[bridge] erro na orbita real: {e}")
    finally:
        STATE.moving = False
        if mover is not None:
            try:
                mover.disconnect()
            except Exception:
                pass
        try:
            MOVE_LOCK.release()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# Thread: leitura das juntas do robo
# --------------------------------------------------------------------------- #
def robot_poller(ip: str, simulate: bool, hz: float):
    interval = 1.0 / max(1.0, hz)

    if simulate:
        # Robo virtual: orbita REAL de inspecao (cartesiano + IK numerico).
        # A ponta (flange/wrist3) percorre circulos ao redor da peca, de baixo
        # para cima, com a camera (+Z local) sempre apontando para o centro C.
        # A sequencia tocada vive no STATE e pode ser TROCADA ao vivo via
        # POST /api/orbit-config (o poller percebe pela versao e reinicia).
        try:
            from sim.orbit_ik import OrbitParams

            metrics = _publish_orbit(OrbitParams())
            print("[bridge] orbita IK: "
                  f"{metrics['n']} pts, {metrics['frac_within_3deg']*100:.0f}% <=3deg, "
                  f"erro pos medio {metrics['mean_pos_err_mm']:.1f}mm")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[bridge] falha ao montar orbita IK ({e}); usando animacao simples")
            STATE.set_orbit_plan({"levels": 0, "points_per_level": 0, "poses": []})

        phase = 0.0
        last_version = -1
        # Playback continuo em tempo: elimina o efeito "step por step".
        # Publicamos juntas em alta frequencia (60 Hz) e amostramos a sequencia
        # com indice fracionario (lerp entre pose i e i+1).
        render_hz = 60.0
        dt = 1.0 / render_hz
        # Mantem velocidade aproximada do comportamento antigo (hz/3 pontos/s)
        # sem depender de substeps discretos.
        base_points_per_sec = max(1.0, hz / 3.0)
        STATE.set_sim_base_pps(base_points_per_sec)
        t0 = time.time()
        def _catmull_rom(p0, p1, p2, p3, t):
            """Interpolacao Catmull-Rom (C1) para reduzir trancos em waypoints."""
            t2 = t * t
            t3 = t2 * t
            return 0.5 * (
                (2.0 * p1)
                + (-p0 + p2) * t
                + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
                + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
            )

        while True:
            seq, version = STATE.get_orbit_sequence()
            if not seq:
                # fallback defensivo: orbita nao resolveu, anima algo suave.
                t = time.time() - t0
                j = list(HOME_JOINTS)
                j[0] = 35.0 * math.sin(t * 0.7)
                j[5] = 55.0 * math.sin(t * 1.1)
                j[4] = 90.0 + 25.0 * math.sin(t * 0.4)
                STATE.set_joints(j, source="simulate")
                time.sleep(dt)
                continue
            if version != last_version:
                phase = 0.0              # sequencia trocou: reinicia o playback
                last_version = version
            n = len(seq)
            i1 = int(phase) % n
            i2 = (i1 + 1) % n
            i0 = (i1 - 1) % n
            i3 = (i1 + 2) % n
            alpha = phase - math.floor(phase)
            p0 = seq[i0]
            p1 = seq[i1]
            p2 = seq[i2]
            p3 = seq[i3]
            j = [_catmull_rom(p0[k], p1[k], p2[k], p3[k], alpha) for k in range(6)]
            STATE.set_joints(j, source="simulate")

            speed = STATE.get_sim_speed()
            points_per_sec = base_points_per_sec * max(0.1, min(10.0, speed))
            phase = (phase + points_per_sec * dt) % n
            time.sleep(dt)
        return

    # --- robo real ---
    from vision.robot_scan import FairinoRobot
    robot = FairinoRobot(ip=ip)
    while True:
        try:
            robot.connect()
            STATE.source = "robot"
            print(f"[bridge] conectado ao robo {ip}")
            break
        except Exception as e:
            STATE.set_error(f"conectando... ({e})")
            print(f"[bridge] falha ao conectar ({e}); tentando de novo em 2s")
            time.sleep(2.0)

    while True:
        try:
            joints = robot.get_joints()
            tcp = None
            try:
                res = robot.robot.GetActualTCPPose(1)
                if isinstance(res, tuple) and res[0] == 0:
                    tcp = list(res[1])
            except Exception:
                pass
            STATE.set_joints(joints, tcp=tcp, source="robot")
        except Exception as e:
            STATE.set_error(e)
            print(f"[bridge] erro lendo juntas: {e}")
            time.sleep(0.5)
        time.sleep(interval)


# --------------------------------------------------------------------------- #
# Thread: captura da camera eye-in-hand
# --------------------------------------------------------------------------- #
def camera_grabber(index: int, simulate: bool):
    try:
        import cv2
        import numpy as np
    except Exception as e:
        print(f"[bridge] OpenCV indisponivel, camera desligada ({e})")
        return

    cap = None
    if not simulate:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not cap.isOpened():
            print(f"[bridge] webcam {index} nao abriu; usando imagem sintetica")
            cap.release()
            cap = None

    enc = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
    t0 = time.time()
    while True:
        frame = None
        if cap is not None:
            ok, f = cap.read()
            if ok and f is not None:
                frame = f
        if frame is None:
            # Frame sintetico (modo simulate ou webcam ausente).
            t = time.time() - t0
            frame = np.full((480, 640, 3), 30, np.uint8)
            cx = int(320 + 180 * np.sin(t * 0.8))
            cv2.circle(frame, (cx, 240), 40, (80, 200, 90), -1)
            cv2.putText(frame, "camera eye-in-hand (sintetica)", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            time.sleep(1 / 30)
        ok, buf = cv2.imencode(".jpg", frame, enc)
        if ok:
            STATE.set_frame(buf.tobytes())


# --------------------------------------------------------------------------- #
# Servidor HTTP
# --------------------------------------------------------------------------- #
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SIM_DIR, **kw)

    def log_message(self, *a):
        pass  # silencia o log por request

    def end_headers(self):
        # Impede o navegador de servir um index.html/JS antigo do cache. Sem
        # isso, depois de editar a simulacao o usuario continua vendo a versao
        # velha (sintoma: "o modelo 3d nao atualiza"). Forca recarga sempre.
        if not getattr(self, "_nocache_sent", False):
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self._nocache_sent = True
        super().end_headers()

    def do_GET(self):
        self._nocache_sent = False
        path = urlsplit(self.path).path
        if path.startswith("/api/joints"):
            return self._send_json(STATE.snapshot())
        if path.startswith("/api/orbit-plan"):
            plan = STATE.get_orbit_plan() or {"levels": 0, "points_per_level": 0, "poses": []}
            return self._send_json({"ok": True, "simulate": STATE.simulate, **plan})
        if path.startswith("/api/orbit-status"):
            return self._send_json({"ok": True, **STATE.get_orbit_status()})
        if path.startswith("/api/orbit-runtime"):
            return self._send_json({"ok": True, "simulate": STATE.simulate,
                                    **STATE.get_sim_runtime()})
        if path.startswith("/api/sim-speed"):
            return self._send_json({"ok": True, "simulate": STATE.simulate,
                                    "sim_speed": STATE.get_sim_speed()})
        if path.startswith("/api/camera.mjpg"):
            return self._stream_mjpeg()
        if path.startswith("/api/snapshot.jpg"):
            return self._send_jpeg(STATE.get_frame())
        return super().do_GET()

    def do_POST(self):
        self._nocache_sent = False
        path = urlsplit(self.path).path
        if path.startswith("/api/orbit-config"):
            return self._orbit_config()
        if path.startswith("/api/orbit-optimize"):
            return self._orbit_optimize()
        if path.startswith("/api/sim-speed"):
            return self._set_sim_speed()
        if path.startswith("/api/move"):
            return self._start_move(run_demo_move)
        if path.startswith("/api/wave"):
            return self._start_move(run_wave_move)
        if path.startswith("/api/orbit-run"):
            return self._start_orbit_run()
        self.send_error(404, "nao encontrado")

    def _orbit_config(self):
        """Recalcula a orbita ao vivo com novos parametros (sem reiniciar).

        Vale em ambos os modos: simulate (anima o resultado) e real (gera
        o plano para visualizar/executar). E so calculo IK em background.
        """
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length > 0 else b"{}"
            overrides = json.loads(raw or b"{}")
            if not isinstance(overrides, dict):
                raise ValueError("corpo deve ser um objeto JSON")
        except (ValueError, json.JSONDecodeError) as e:
            return self._send_json(
                {"ok": False, "msg": f"JSON invalido: {e}"}, status=400)
        try:
            params = _merge_orbit_params(overrides)
        except ValueError as e:
            # Entrada fora de faixa / invalida: estado anterior preservado.
            return self._send_json({"ok": False, "msg": str(e)}, status=400)
        # Recalculo pesado roda em background: responde NA HORA (nao bloqueia).
        submit_orbit(params)
        return self._send_json(
            {"ok": True, "status": "calculando", "msg": "recalculando orbita"},
            status=202)

    def _orbit_optimize(self):
        """Dispara busca automatica de centro da peça (XYZ) para órbita melhor.

        Roda em ambos os modos: e busca puramente offline.
        """
        if not submit_orbit_center_optimization():
            return self._send_json(
                {"ok": True, "status": "calculando", "msg": "otimizacao ja em andamento"},
                status=202)
        return self._send_json(
            {"ok": True, "status": "calculando", "msg": "otimizando centro da peca"},
            status=202)

    def _start_move(self, runner):
        if STATE.simulate:
            return self._send_json({
                "ok": True, "started": False,
                "msg": "modo simulado ja anima sozinho"})
        if not STATE.connected:
            return self._send_json({
                "ok": False, "started": False, "msg": "robo nao conectado"})
        if STATE.moving:
            return self._send_json({
                "ok": True, "started": False, "msg": "ja em movimento"})
        threading.Thread(target=runner, daemon=True).start()
        return self._send_json({
            "ok": True, "started": True, "msg": "movimento iniciado"})

    def _start_orbit_run(self):
        """Dispara a orbita ATUAL no robo real (mesma sequencia do viewer)."""
        if STATE.simulate:
            return self._send_json({
                "ok": False, "started": False,
                "msg": "execucao real indisponivel em --simulate"}, status=400)
        if not STATE.connected:
            return self._send_json({
                "ok": False, "started": False, "msg": "robo nao conectado"}, status=409)
        if STATE.moving:
            return self._send_json({
                "ok": True, "started": False, "msg": "ja em movimento"})
        status = STATE.get_orbit_status().get("status")
        if status != "pronto":
            return self._send_json({
                "ok": False, "started": False,
                "msg": f"orbita nao esta pronta (status={status})"}, status=409)
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length > 0 else b"{}"
            data = json.loads(raw or b"{}") if length > 0 else {}
            vel = float(data.get("vel", 15.0))
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return self._send_json(
                {"ok": False, "started": False, "msg": f"JSON invalido: {e}"},
                status=400)
        # Limite conservador para primeiro deploy: 5..25%
        if not (5.0 <= vel <= 25.0):
            return self._send_json({
                "ok": False, "started": False,
                "msg": "vel fora da faixa segura [5, 25]"}, status=400)
        threading.Thread(target=run_orbit_on_real_robot, args=(vel,),
                         daemon=True).start()
        return self._send_json({
            "ok": True, "started": True,
            "msg": f"orbita iniciada a {vel:.0f}%"})

    def _set_sim_speed(self):
        """Ajusta velocidade da animacao no modo --simulate em tempo real."""
        if not STATE.simulate:
            return self._send_json(
                {"ok": False, "msg": "sim-speed so disponivel no modo --simulate"},
                status=400)
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length > 0 else b"{}"
            data = json.loads(raw or b"{}")
            if not isinstance(data, dict):
                raise ValueError("corpo deve ser um objeto JSON")
            speed = float(data.get("sim_speed", 1.0))
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return self._send_json({"ok": False, "msg": f"JSON invalido: {e}"}, status=400)

        if not (0.1 <= speed <= 10.0):
            return self._send_json(
                {"ok": False, "msg": "sim_speed fora da faixa [0.1, 10.0]"},
                status=400)
        STATE.set_sim_speed(speed)
        return self._send_json({"ok": True, "sim_speed": speed})

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_jpeg(self, data):
        if not data:
            self.send_error(503, "sem frame")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _stream_mjpeg(self):
        self.send_response(200)
        self.send_header("Content-Type",
                         "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            while True:
                data = STATE.get_frame()
                if data:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(
                        f"Content-Length: {len(data)}\r\n\r\n".encode())
                    self.wfile.write(data)
                    self.wfile.write(b"\r\n")
                time.sleep(1 / 25)
        except (BrokenPipeError, ConnectionResetError):
            pass  # navegador fechou a aba/stream


def main():
    ap = argparse.ArgumentParser(description="Ponte ao vivo FR5 -> simulacao 3D")
    ap.add_argument("--ip", default="192.168.58.2", help="IP do robo")
    ap.add_argument("--camera", type=int, default=0, help="indice da webcam USB")
    ap.add_argument("--no-camera", action="store_true", help="nao usar camera")
    ap.add_argument("--simulate", action="store_true",
                    help="sem hardware (robo e camera virtuais)")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--hz", type=float, default=15.0, help="taxa de leitura das juntas")
    args = ap.parse_args()

    STATE.ip = args.ip
    STATE.simulate = args.simulate

    # Spawn/import do worker de processo em background para reduzir a latencia
    # percebida no primeiro recálculo de orbita.
    _warmup_orbit_executor_async()

    # Pre-computa uma orbita inicial em AMBOS os modos para o usuario
    # ver/editar o plano no painel desde o primeiro segundo. No simulate o
    # poller faz isso sozinho; no real fazemos aqui.
    if not args.simulate:
        try:
            from sim.orbit_ik import OrbitParams
            submit_orbit(OrbitParams())
        except Exception as e:  # noqa: BLE001
            print(f"[bridge] aviso: nao foi possivel pre-computar orbita: {e}")
        # Le os soft limits do controlador em background. Quando chegarem, a
        # orbita corrente e revalidada -> qualquer violacao aparece no painel
        # ANTES do usuario apertar Executar.
        _fetch_soft_limits_async(args.ip)

    threading.Thread(target=robot_poller,
                     args=(args.ip, args.simulate, args.hz),
                     daemon=True).start()
    if not args.no_camera:
        threading.Thread(target=camera_grabber,
                         args=(args.camera, args.simulate),
                         daemon=True).start()

    srv = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    mode = "SIMULADO" if args.simulate else f"robo {args.ip}"
    print(f"[bridge] {mode}")
    print(f"[bridge] abra  http://localhost:{args.port}/")
    print("[bridge] Ctrl+C para parar")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[bridge] encerrando")
    finally:
        _shutdown_orbit_executor()


if __name__ == "__main__":
    main()
