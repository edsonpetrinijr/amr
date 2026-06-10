"""Le e imprime as informacoes do robo Fairino (estado de cada junta + geral).

Uso:
    python robot_info.py                 # robo real (192.168.58.2)
    python robot_info.py --ip 192.168.58.2
    python robot_info.py --simulate      # sem hardware (mock)
    python robot_info.py --loop          # atualiza continuamente (Ctrl+C para sair)
    python robot_info.py --json          # imprime em JSON e sai

Observacao: getters de posicao/TCP/limites/versao usam o XML-RPC (porta 20003) e
sao confiaveis neste firmware. Velocidade, aceleracao, torque e temperatura vem do
pacote de status (porta UDP que este firmware nao expoe), entao tendem a vir zerados.
"""
from __future__ import annotations
import argparse
import json
import time

from vision.config import ScanConfig
from vision.robot_scan import FairinoRobot, MockRobot

JOINT_LABELS = ["j1", "j2", "j3", "j4", "j5", "j6"]


def _fmt(values, ndigits=2):
    if not isinstance(values, (list, tuple)):
        return str(values)
    out = []
    for v in values:
        try:
            out.append(f"{float(v):.{ndigits}f}")
        except (TypeError, ValueError):
            out.append(str(v))
    return out


def print_state(state: dict) -> None:
    print("=" * 64)
    print(" INFORMACOES DO ROBO")
    print("=" * 64)
    print(f" Controlador IP : {state.get('controller_ip')}")
    sdk = state.get("sdk_version")
    if isinstance(sdk, (list, tuple)):
        print(f" Versao         : {', '.join(str(s) for s in sdk)}")
    print(f" Relogio (ms)   : {state.get('system_clock_ms')}")
    print(f" Config juntas  : {state.get('joints_config')}")
    print(f" Num. TCP       : {state.get('tcp_num')}")
    print(f" Angulo instal. : {_fmt(state.get('install_angle'))}")
    err = state.get("error_code")
    if isinstance(err, (list, tuple)) and len(err) >= 2:
        status = "OK" if err[0] in (0, "0") else "ERRO"
        print(f" Codigo de erro : main={err[0]} sub={err[1]} ({status})")
    else:
        print(f" Codigo de erro : {err}")

    print("-" * 64)
    print(" POR JUNTA")
    print("-" * 64)
    header = f" {'junta':<6}{'pos(deg)':>11}{'pos(rad)':>11}{'vel(d/s)':>10}{'torque':>10}{'temp(C)':>9}"
    print(header)
    pos_d = _fmt(state.get("pos_deg"))
    pos_r = _fmt(state.get("pos_rad"), 4)
    vel = _fmt(state.get("vel_deg_s"))
    tor = _fmt(state.get("torque"))
    tmp = _fmt(state.get("driver_temp_c"), 1)

    def cell(seq, i):
        if isinstance(seq, list) and i < len(seq):
            return seq[i]
        return "-"

    for i, label in enumerate(JOINT_LABELS):
        print(f" {label:<6}{cell(pos_d, i):>11}{cell(pos_r, i):>11}"
              f"{cell(vel, i):>10}{cell(tor, i):>10}{cell(tmp, i):>9}")

    sl = state.get("soft_limit_deg")
    if isinstance(sl, list) and len(sl) >= 12:
        print("-" * 64)
        print(" LIMITES SOFT (deg) por junta")
        for i, label in enumerate(JOINT_LABELS):
            a, b = sl[2 * i], sl[2 * i + 1]
            print(f"   {label}: [{float(a):.2f}, {float(b):.2f}]")

    print("-" * 64)
    print(" CARTESIANO")
    print("-" * 64)
    print(f" TCP   [x,y,z,rx,ry,rz] : {_fmt(state.get('tcp_pose'))}")
    print(f" Flange[x,y,z,rx,ry,rz] : {_fmt(state.get('flange_pose'))}")
    print("=" * 64)


def main() -> None:
    parser = argparse.ArgumentParser(description="Le informacoes do robo Fairino")
    parser.add_argument("--simulate", action="store_true", help="Roda sem hardware (mock)")
    parser.add_argument("--ip", default=None, help="IP do robo")
    parser.add_argument("--loop", action="store_true", help="Atualiza continuamente")
    parser.add_argument("--interval", type=float, default=1.0, help="Intervalo do --loop (s)")
    parser.add_argument("--json", action="store_true", help="Imprime em JSON e sai")
    args = parser.parse_args()

    cfg = ScanConfig()
    if args.ip is not None:
        cfg.robot_ip = args.ip

    robot = MockRobot() if args.simulate else FairinoRobot(cfg.robot_ip)
    robot.connect()
    robot.enable()

    try:
        if args.loop:
            while True:
                state = robot.read_state()
                if args.json:
                    print(json.dumps(state, ensure_ascii=False))
                else:
                    print("\033[2J\033[H", end="")  # limpa a tela
                    print_state(state)
                time.sleep(max(0.05, args.interval))
        else:
            state = robot.read_state()
            if args.json:
                print(json.dumps(state, indent=2, ensure_ascii=False))
            else:
                print_state(state)
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
