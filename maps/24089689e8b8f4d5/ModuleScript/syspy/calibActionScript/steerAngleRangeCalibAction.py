# coding=utf-8
import sys
import time
import math
from enum import Enum, IntEnum
import json
sys.path.append("syspy")
from syspy.rbkSim import SimModule
from syspy.rbk import MoveStatus, BasicModule

class ActionType(Enum):
    NoAction = "NoAction"
    GoStraightForward = "GoStraightForward"
    GoStraightBackward = "GoStraightBackward"
    GoRotForward = "GoRotForward"
    GoRotBackward = "GoRotBackward"
    GoLeftArcForward = "GoLeftArcForward"
    GoLeftArcBackward = "GoLeftArcBackward"
    GoRightArcForward = "GoRightArcForward"
    GoRightArcBackward = "GoRightArcBackward"
    Capture = "Capture"
    SteerLeft = "SteerLeft"
    SteerRight = "SteerRight"

class SteerDir(IntEnum):
    MoveWait = 0
    CounterClockWise = 1
    ClockWise = 2
    MoveCenter = 3

class Module(BasicModule):

    def __init__(self, r: SimModule, args):

        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.steer_name = ""
        self.steer_dir = SteerDir.MoveWait
        self.last_send_angle = 0
        self.send_angle = 0
        self.steer_start_time = 0
        self.status = MoveStatus.RUNNING

    def get_motor_pos(self, r: SimModule, motor_name: str):
        """
        获取指定电机的当前位置
        :param r: SimModule类对象
        :param motor_name: 电机名称
        :return: 返回电机的当前位置，若电机不存在返回False
        """
        motors = r.odo().get("motor_info", [])
        motor_pos = False
        for m in motors:
            if m['motor_name'] == motor_name:
                motor_pos = m.get('position', False)
        return motor_pos

    def reachLimit(self, dt = 3.0):
        if abs(self.last_send_angle - self.send_angle) < 0.0001:
            if time.time() - self.steer_start_time > dt:
                return True
        else:
            self.steer_start_time = time.time()
        return False
    
    def run(self, r: SimModule, args):
        if self.init:
            self.init = False
            self.steer_name = args.get("name","")
            self.steer_start_time = time.time()
            self.steer_max_angle = args.get("max_angle")
            self.steer_min_angle = args.get("min_angle")
            self.steer_offset = args.get("offset")
            self.chassis_mode = args.get("chassis_mode")
            self.last_motor_angle = 0.0

        if self.steer_name == "":
            r.logInfo("steer name emtpy!")
            return MoveStatus.FINISHED
        cur_angle = self.get_motor_pos(r, self.steer_name)

        if self.steer_dir == SteerDir.MoveWait:
            self.send_angle = (self.steer_offset + 0.5*(self.steer_max_angle + self.steer_min_angle))*math.pi/180
            if self.reachLimit():
                r.logInfo("goto CounterClockWise")
                self.steer_dir = SteerDir.CounterClockWise

        if self.steer_dir == SteerDir.CounterClockWise:
            self.send_angle = cur_angle + 0.1  
            # if self.chassis_mode == "dualDiff":
            self.send_angle = min(self.send_angle, (self.steer_offset+150.0)*math.pi/180)
            if self.reachLimit():
                r.logInfo("goto ClockWise")
                self.steer_dir = SteerDir.ClockWise

        if self.steer_dir == SteerDir.ClockWise:
            self.send_angle = cur_angle - 0.1  
            # if self.chassis_mode == "dualDiff":
            self.send_angle = max(self.send_angle, (self.steer_offset-150.0)*math.pi/180)
            if self.reachLimit():
                r.logInfo("calib finished!")
                self.steer_dir = SteerDir.MoveCenter

        if self.steer_dir == SteerDir.MoveCenter:
                self.send_angle = (self.steer_offset + 0.5*(self.steer_max_angle + self.steer_min_angle))*math.pi/180
                if abs(self.last_motor_angle-cur_angle) < 0.001:
                    if self.reachLimit(3.0):
                        r.logInfo("go to MoveCenter")
                        self.status = MoveStatus.FINISHED
                else:
                    self.steer_start_time = time.time()

        if self.steer_dir == SteerDir.CounterClockWise:
            r.setSteerAngle(self.steer_name, self.send_angle,"SteerLeft")
        elif self.steer_dir == SteerDir.ClockWise:
            r.setSteerAngle(self.steer_name, self.send_angle,"SteerRight")
        else:
            r.setSteerAngle(self.steer_name, self.send_angle,"")

        dt =  time.time() - self.steer_start_time
        d_steer = self.last_motor_angle-cur_angle
        info = dict()
        info["steer_dir"] = self.steer_dir
        info["send_angle"] = self.send_angle
        info["last_send_angle"] = self.last_send_angle
        info["cur_angle"] = cur_angle
        info["da"] = abs(self.last_send_angle - self.send_angle)
        info["dt"] = dt
        info["reachLimit"] = self.reachLimit()
        info["steer_name"] = self.steer_name
        info["d_steer"] = d_steer
        r.setInfo(json.dumps(info))
        r.logDebug("SteerAngleRangeCalibAction][{}|{}|{}|{}|{}|{}|{}".format(
                    self.steer_name, 
                    self.send_angle,
                    self.last_send_angle,
                    cur_angle,
                    self.status,
                    self.steer_dir,
                    d_steer))
        self.last_send_angle = self.send_angle
        self.last_motor_angle = cur_angle
        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    data["name"] = "steer1"
    print(m.run(r, data))
