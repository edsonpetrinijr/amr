"""Controle do robo para a varredura + geracao de poses.

FairinoRobot: implementacao real (com o bypass is_connect do firmware sem CNDE).
MockRobot: simulacao para testes sem hardware.
"""
from __future__ import annotations
import abc
import time
from typing import List


class RobotScanner(abc.ABC):
    @abc.abstractmethod
    def connect(self) -> None:
        ...

    @abc.abstractmethod
    def enable(self) -> None:
        ...

    @abc.abstractmethod
    def get_joints(self) -> List[float]:
        """Posicao atual das juntas em graus [j1..j6]."""
        ...

    @abc.abstractmethod
    def move_joints(self, joints: List[float], vel: float, tool: int, user: int) -> int:
        ...

    def disconnect(self) -> None:
        pass


class FairinoRobot(RobotScanner):
    def __init__(self, ip: str = "192.168.58.2"):
        self.ip = ip
        self.robot = None

    def connect(self) -> None:
        from fairino import Robot
        self.robot = Robot.RPC(self.ip)
        # Firmware deste robo nao expoe as portas CNDE 20005 nem UDP 20007; os
        # comandos usam o XML-RPC (20003), que funciona. Liberamos o gate de
        # conexao (sem isso, todo comando retorna -4 sem enviar nada).
        Robot.RPC.is_connect = True
        # 20005/20007 ficam "filtradas" neste firmware. O SDK novo abre um cliente
        # UDP na 20007 e um auto-reconnect que tentam a 20005 em loop -- inuteis
        # aqui e fonte de ruido/travas. Desligamos os dois de forma defensiva.
        try:
            Robot.RPC._reconnect_enable = False
            self.robot.reconnect_flag = False
        except Exception:
            pass
        try:
            if getattr(self.robot, "_udp_client", None) is not None:
                self.robot._udp_client.stop_recv_thread()
        except Exception:
            pass

    def enable(self) -> None:
        ret = self.robot.RobotEnable(1)
        if ret not in (0, None):
            raise RuntimeError(f"RobotEnable falhou, codigo {ret}")

    def get_joints(self) -> List[float]:
        res = self.robot.GetActualJointPosDegree(1)
        # Sucesso: (0, [j1..j6]); falha: codigo de erro (int).
        if isinstance(res, tuple) and res[0] == 0:
            return list(res[1])
        raise RuntimeError(f"GetActualJointPosDegree falhou: {res}")

    def move_joints(self, joints: List[float], vel: float, tool: int, user: int) -> int:
        ret = self.robot.MoveJ(list(joints), tool=tool, user=user, vel=vel)
        if ret not in (0, None):
            raise RuntimeError(f"MoveJ falhou, codigo {ret}")
        return 0 if ret is None else ret

    @staticmethod
    def _ok(res):
        """Normaliza o retorno do SDK Fairino.

        Sucesso e' (0, valor) ou (0, v1, v2, ...). Falha e' um codigo int.
        Retorna o valor (ou lista de valores) em caso de sucesso, senao None.
        """
        if isinstance(res, tuple):
            if not res or res[0] != 0:
                return None
            if len(res) == 2:
                return res[1]
            return list(res[1:])
        return None

    def read_state(self) -> dict:
        """Puxa um retrato completo do robo.

        Os getters que passam pelo XML-RPC (20003) sao confiaveis neste firmware.
        Os marcados como 'stream' leem o pacote de status (porta UDP que este
        firmware nao expoe) e tendem a vir zerados sem o stream ativo.
        """
        r = self.robot

        def call(fn, *args):
            try:
                return self._ok(fn(*args))
            except Exception as exc:  # noqa: BLE001
                return f"<erro: {exc}>"

        return {
            # --- por junta (XML-RPC confiavel) ---
            "pos_deg": call(r.GetActualJointPosDegree, 1),
            "pos_rad": call(r.GetActualJointPosRadian, 1),
            "soft_limit_deg": call(r.GetJointSoftLimitDeg, 1),
            # --- por junta (stream de status; pode vir zerado) ---
            "vel_deg_s": call(r.GetActualJointSpeedsDegree, 1),
            "acc_deg_s2": call(r.GetActualJointAccDegree, 1),
            "torque": call(r.GetJointTorques, 1),
            "driver_torque": call(r.GetJointDriverTorque),
            "driver_temp_c": call(r.GetJointDriverTemperature),
            # --- cartesiano / geral ---
            "tcp_pose": call(r.GetActualTCPPose, 1),
            "flange_pose": call(r.GetActualToolFlangePose, 1),
            "joints_config": call(r.GetRobotCurJointsConfig),
            "tcp_num": call(r.GetActualTCPNum, 1),
            "install_angle": call(r.GetRobotInstallAngle),
            "error_code": call(r.GetRobotErrorCode),
            "system_clock_ms": call(r.GetSystemClock),
            "controller_ip": call(r.GetControllerIP),
            "sdk_version": call(r.GetSDKVersion),
        }


class MockRobot(RobotScanner):
    """Robo virtual: mantem estado das juntas em memoria."""

    def __init__(self, start_joints: List[float] = None):
        self._joints = list(start_joints) if start_joints else [0.0, -20.0, -90.0, -70.0, 90.0, 0.0]

    def connect(self) -> None:
        print("[MockRobot] conectado")

    def enable(self) -> None:
        print("[MockRobot] habilitado")

    def get_joints(self) -> List[float]:
        return list(self._joints)

    def move_joints(self, joints: List[float], vel: float, tool: int, user: int) -> int:
        self._joints = list(joints)
        return 0

    def read_state(self) -> dict:
        j = list(self._joints)
        import math
        return {
            "pos_deg": j,
            "pos_rad": [round(math.radians(x), 4) for x in j],
            "soft_limit_deg": None,
            "vel_deg_s": [0.0] * 6,
            "acc_deg_s2": [0.0] * 6,
            "torque": [0.0] * 6,
            "driver_torque": [0.0] * 6,
            "driver_temp_c": [0.0] * 6,
            "tcp_pose": None,
            "flange_pose": None,
            "joints_config": None,
            "tcp_num": 0,
            "install_angle": None,
            "error_code": [0, 0],
            "system_clock_ms": 0,
            "controller_ip": "mock",
            "sdk_version": ["SDK:mock", "Robot:mock"],
        }


def generate_scan_poses(base_joints: List[float], scan_joint: int,
                        start_deg: float, end_deg: float, step_deg: float) -> List[List[float]]:
    """Gera as poses da varredura variando UMA junta a partir da pose base."""
    if step_deg <= 0:
        raise ValueError("scan_step_deg deve ser > 0")
    poses = []
    base_val = base_joints[scan_joint]
    offset = start_deg
    while offset <= end_deg + 1e-6:
        pose = list(base_joints)
        pose[scan_joint] = base_val + offset
        poses.append(pose)
        offset += step_deg
    return poses
