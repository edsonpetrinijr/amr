# coding=utf-8
import sys
import time
import math
from enum import Enum, IntEnum
import json
sys.path.append("syspy")
from syspy.rbkSim import SimModule
from syspy.rbk import MoveStatus, BasicModule

"""
####BEGIN DEFAULT ARGS####
{
    "W": {
        "value": 25,
        "tips": "长度",
        "type": "double",
        "unit":"°/s",
        "maxValue":90,
        "minValue":10
    }
}
####END DEFAULT ARGS####
"""

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

# 为方便分离模态，每次运动的角速度方向要相异
class MoveAction(IntEnum):
    SteerPSpeedPSteer = 0
    SteerPSpeedP = 1
    SteerPSpeedNSteer = 2
    SteerPSpeedN = 3
    SteerNSpeedNSteer = 4
    SteerNSpeedN = 5
    SteerNSpeedPSteer = 6
    SteerNSpeedP = 7
    ActionEnd = 8

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.SteerPSpeedPSteer
        self.steer_name = ""

    def run(self, r: SimModule, args:json):
        # 初始化
        if self.init:
            self.init = False
            r.resetOdoMove()
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.SteerPSpeedPSteer
            self.steer_name = args.get("name")
            if type(args) is dict and "W" in args:
                self.speed_w = float(args["W"]) * math.pi / 180
            else:
                self.speed_w = 45*math.pi/180

        # 实时运行
        if self.move_action == 0:
            self.status = r.setSteerAngle(self.steer_name, math.pi/2,"NoAction")
            if self.status:
                self.status = MoveStatus.FINISHED
        elif self.move_action == 1:
            self.status = r.runOdoMove({"move_angle": math.pi,  "speed_w":self.speed_w, "action_name":"GoRotForward1"})
        elif self.move_action == 2:
            self.status = r.setSteerAngle(self.steer_name,math.pi/2,"NoAction")
            if self.status:
                self.status = MoveStatus.FINISHED
        elif self.move_action == 3:
            self.status = r.runOdoMove({"move_angle": math.pi,  "speed_w":-self.speed_w, "action_name":"GoRotBackward1"})
        elif self.move_action == 4:
            self.status = r.setSteerAngle(self.steer_name, -math.pi/2,"NoAction")
            if self.status:
                self.status = MoveStatus.FINISHED
        elif self.move_action == 5:
            self.status = r.runOdoMove({"move_angle": math.pi,  "speed_w":self.speed_w, "action_name":"GoRotForward2"})
        elif self.move_action == 6:
            self.status = r.setSteerAngle(self.steer_name, -math.pi/2,"NoAction")
            if self.status:
                self.status = MoveStatus.FINISHED
        elif self.move_action == 7:
            self.status = r.runOdoMove({"move_angle": math.pi,  "speed_w":-self.speed_w, "action_name":"GoRotBackward2"})
        
        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            self.move_action = self.move_action + 1
            if self.move_action !=  MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
        
        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["steer_name"] = self.steer_name
        info["speed_w"] = self.speed_w
        info["status"] = self.status
        info["goal status"] = MoveStatus.FINISHED
        r.setInfo(json.dumps(info))
        r.logDebug("GoRotCalib][{}|{}".format(
                    self.move_action,
                    self.status))

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    data["name"] = "steer1"
    data["speed_w"] = math.pi / 3
    print(m.run(r, data))
