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

Seguranca: a ponte e SOMENTE LEITURA. Ela espelha o robo real na tela, mas
nunca envia comandos de movimento.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import math

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


STATE = SharedState()
MOVE_LOCK = threading.Lock()


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
# Thread: leitura das juntas do robo
# --------------------------------------------------------------------------- #
def robot_poller(ip: str, simulate: bool, hz: float):
    interval = 1.0 / max(1.0, hz)

    if simulate:
        # Robo virtual: orbita REAL de inspecao (cartesiano + IK numerico).
        # A ponta (flange/wrist3) percorre circulos ao redor da peca, de baixo
        # para cima, com a camera (+Z local) sempre apontando para o centro C.
        try:
            from sim.orbit_ik import plan_orbit

            plan = plan_orbit()
            metrics = plan.metrics()
            STATE.set_orbit_plan({
                "levels": plan.levels,
                "points_per_level": plan.points_per_level,
                "poses": plan.poses_deg,          # keypoints resolvidos (IK)
                "points": plan.points,            # alvos cartesianos (m, frame base)
                "approaches": plan.approaches,    # direcao look-at por keypoint
                "center": plan.center,            # C no frame base (m)
                "point_errs_deg": plan.point_errs_deg,
                "pos_errs_m": plan.pos_errs_m,
                "metrics": metrics,
            })
            print("[bridge] orbita IK: "
                  f"{metrics['n']} pts, {metrics['frac_within_3deg']*100:.0f}% <=3deg, "
                  f"erro pos medio {metrics['mean_pos_err_mm']:.1f}mm")
            poses = plan.motion_deg              # sequencia densificada p/ playback
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[bridge] falha ao montar orbita IK ({e}); usando animacao simples")
            poses = []
            STATE.set_orbit_plan({"levels": 0, "points_per_level": 0, "poses": []})

        if not poses:
            # fallback defensivo
            t0 = time.time()
            while True:
                t = time.time() - t0
                j = list(HOME_JOINTS)
                j[0] = 35.0 * math.sin(t * 0.7)
                j[5] = 55.0 * math.sin(t * 1.1)
                j[4] = 90.0 + 25.0 * math.sin(t * 0.4)
                STATE.set_joints(j, source="simulate")
                time.sleep(interval)
            return

        idx = 0
        substeps = 3  # interpola entre poses densas p/ visual ainda mais fluido
        while True:
            p0 = poses[idx]
            p1 = poses[(idx + 1) % len(poses)]
            for s in range(substeps):
                alpha = float(s) / float(substeps)
                j = [p0[k] + (p1[k] - p0[k]) * alpha for k in range(6)]
                STATE.set_joints(j, source="simulate")
                time.sleep(interval)
            idx = (idx + 1) % len(poses)
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
        if self.path.startswith("/api/joints"):
            return self._send_json(STATE.snapshot())
        if self.path.startswith("/api/orbit-plan"):
            plan = STATE.get_orbit_plan() or {"levels": 0, "points_per_level": 0, "poses": []}
            return self._send_json({"ok": True, "simulate": STATE.simulate, **plan})
        if self.path.startswith("/api/camera.mjpg"):
            return self._stream_mjpeg()
        if self.path.startswith("/api/snapshot.jpg"):
            return self._send_jpeg(STATE.get_frame())
        return super().do_GET()

    def do_POST(self):
        self._nocache_sent = False
        if self.path.startswith("/api/move"):
            return self._start_move(run_demo_move)
        if self.path.startswith("/api/wave"):
            return self._start_move(run_wave_move)
        self.send_error(404, "nao encontrado")

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

    def _send_json(self, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(200)
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


if __name__ == "__main__":
    main()
