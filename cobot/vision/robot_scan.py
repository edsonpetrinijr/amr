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

    def validate_scan_poses(self, poses: List[List[float]]) -> None:
        """No-op por padrao; FairinoRobot sobrescreve com a checagem real."""
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
        # MoveJ pode retornar antes do movimento concluir neste firmware:
        # poll ate a junta chegar perto do alvo (ou levantar erro/timeout).
        self._wait_joints_reached(joints)
        return 0 if ret is None else ret

    def move_joints_blend(self, joints: List[float], vel: float,
                          tool: int = 0, user: int = 0,
                          blend_ms: float = 200.0) -> int:
        """MoveJ NAO-BLOQUEANTE (blendT>0): so enfileira o waypoint.

        A fluidez vem de enfileirar o PROXIMO ponto enquanto o robo ainda esta
        executando o atual; o controlador faz a mistura. NAO espere chegar.
        Use wait_motion_done() apos a sequencia para garantir conclusao.
        """
        ret = self.robot.MoveJ(list(joints), tool=tool, user=user, vel=vel,
                               blendT=float(blend_ms))
        if ret not in (0, None):
            raise RuntimeError(f"MoveJ(blend) falhou, codigo {ret}")
        self._check_no_fault()
        return 0

    def wait_motion_done(self, timeout_s: float = 60.0,
                          poll_s: float = 0.05) -> None:
        """Espera o controlador esvaziar a fila de movimento."""
        deadline = time.time() + timeout_s
        # GetRobotMotionDone retorna (0, 1) quando parou.
        while time.time() < deadline:
            try:
                res = self.robot.GetRobotMotionDone()
                if isinstance(res, tuple) and res[0] == 0 and int(res[1]) == 1:
                    return
            except Exception:
                pass
            self._check_no_fault()
            time.sleep(poll_s)
        raise TimeoutError(f"motion nao concluiu em {timeout_s}s")

    # ---------------------------------------------------------------------- #
    # Conclusao de movimento + checagem de falha
    # ---------------------------------------------------------------------- #
    def _wait_joints_reached(self, target: List[float],
                              tol_deg: float = 0.5,
                              timeout_s: float = 15.0) -> None:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            res = self.robot.GetActualJointPosDegree(1)
            if isinstance(res, tuple) and res[0] == 0:
                cur = list(res[1])
                if all(abs(cur[i] - target[i]) <= tol_deg for i in range(len(target))):
                    return
            self._check_no_fault()
            time.sleep(0.05)
        raise TimeoutError(
            f"MoveJ nao concluiu em {timeout_s}s; alvo={[round(v, 1) for v in target]}")

    def _check_no_fault(self) -> None:
        try:
            res = self.robot.GetRobotErrorCode()
            if not (isinstance(res, tuple) and res[0] == 0):
                return
            codes = res[1] if hasattr(res[1], "__iter__") else [res[1]]
            if any(c != 0 for c in codes):
                raise RuntimeError(f"Falha do controlador durante movimento: codigos {list(codes)}")
        except RuntimeError:
            raise
        except Exception:
            pass

    # ---------------------------------------------------------------------- #
    # Validacao contra soft limits do controlador (defesa em profundidade).
    # ---------------------------------------------------------------------- #
    def validate_scan_poses(self, poses: List[List[float]]) -> None:
        """Levanta ValueError se qualquer pose viola os soft limits das juntas.

        GetJointSoftLimitDeg retorna lista plana de 12 valores:
        [neg1, pos1, neg2, pos2, ..., neg6, pos6].
        """
        try:
            res = self.robot.GetJointSoftLimitDeg(1)
        except Exception as exc:
            print(f"[warn] Nao foi possivel ler soft limits: {exc}")
            return
        if not (isinstance(res, tuple) and res[0] == 0 and len(res) >= 2):
            print(f"[warn] GetJointSoftLimitDeg retornou formato inesperado: {res!r}")
            return
        try:
            flat = [float(x) for x in res[1]]
            if len(flat) < 12:
                print(f"[warn] Soft limits incompletos ({len(flat)} valores); pulando")
                return
            lim_pairs = [(flat[i * 2], flat[i * 2 + 1]) for i in range(6)]
        except Exception as exc:
            print(f"[warn] Nao foi possivel parsear soft limits ({res[1]!r}): {exc}")
            return
        for p_idx, pose in enumerate(poses):
            for j, (val, (lo, hi)) in enumerate(zip(pose, lim_pairs)):
                if not (lo - 1e-3 <= val <= hi + 1e-3):
                    raise ValueError(
                        f"Pose #{p_idx}: j{j + 1}={val:.2f}° fora dos soft limits "
                        f"[{lo:.2f}, {hi:.2f}]. Ajuste raios/altura/centro da peca."
                    )

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
