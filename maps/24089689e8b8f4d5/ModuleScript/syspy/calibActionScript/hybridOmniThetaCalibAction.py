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
    "L": {
        "value": 2.0,
        "tips": "长度",
        "type": "double",
        "unit":"m",
        "maxValue":5.0,
        "minValue":1.0
    },
    "V": {
        "value": 0.3,
        "tips": "速度",
        "type": "double",
        "unit":"m/s",
        "maxValue":2.0,
        "minValue":0.1
    },
    "W": {
        "value": 45,
        "tips": "角速度",
        "type": "double",
        "unit":"°/s",
        "maxValue":90,
        "minValue":10
    }
}
####END DEFAULT ARGS####
"""

class MoveAction(IntEnum):
    Forward = 0
    Backward = 1
    GoLeftArc = 2
    Rot2nd4GoForward = 3
    GoForward2Origin = 4
    Rot3rd4RightArc = 5
    GoRightArc = 6
    Rot4th4GoBackward = 7
    GoBackward2Origin = 8
    GoRot2Origin = 9
    ActionEnd = 10

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.Forward

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            self.init = False
            r.resetOdoMove()
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.Forward
            if type(args) is dict and "L" in args:
                self.move_dist = float(args["L"])
            else:
                self.move_dist = 2
            if type(args) is dict and "V" in args:
                self.speed = float(args["V"])
            else:
                self.speed = 0.3
            if type(args) is dict and "W" in args:
                self.speed_w = float(args["W"]) * math.pi / 180
            else:
                self.speed_w = 45*math.pi/180
            self.move_num = args.get("move_num")
            self.move_n = 0
            self.move_dir = self.move_n * math.pi / self.move_num
            self.speed_x = self.speed * math.cos(self.move_dir)
            self.speed_y = self.speed * math.sin(self.move_dir)

        # 实时运行
        if self.move_action == MoveAction.Forward:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":self.speed_x, "speed_y":self.speed_y, "action_name":"OmniMove"})
        elif self.move_action == MoveAction.Backward:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":-self.speed_x, "speed_y":-self.speed_y, "action_name":"OmniMove"})
        elif self.move_action == MoveAction.GoLeftArc:
            self.status = r.runOdoMove({"rot_degree":180.0,
                                                                      "rot_radius":0.5*self.move_dist,
                                                                      "rot_speed":self.speed,
                                                                      "action_name":"ThetaMove"})
        elif self.move_action == MoveAction.Rot2nd4GoForward:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":self.speed_w, "action_name":"ThetaMove"})
        elif self.move_action == MoveAction.GoForward2Origin:
            self.status = r.runOdoMove({"move_dist":self.move_dist, "speed_x":self.speed,  "action_name":"ThetaMove"})
        elif self.move_action == MoveAction.Rot3rd4RightArc:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":-self.speed_w, "action_name":"ThetaMove"})
        elif self.move_action == MoveAction.GoRightArc:
            self.status = r.runOdoMove({"rot_degree":180.0,
                                                                      "rot_radius":-0.5*self.move_dist,
                                                                      "rot_speed":self.speed,
                                                                      "action_name":"ThetaMove"})
        elif self.move_action == MoveAction.Rot4th4GoBackward:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":self.speed_w, "action_name":"ThetaMove"})
        elif self.move_action == MoveAction.GoBackward2Origin:
            self.status = r.runOdoMove({"move_dist":self.move_dist, "speed_x":-self.speed,  "action_name":"ThetaMove"})
        elif self.move_action == MoveAction.GoRot2Origin:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":-self.speed_w, "action_name":"ThetaMove"})

        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            self.move_action = self.move_action + 1
            if self.move_action != MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
            if self.move_action ==  MoveAction.GoLeftArc and self.move_n + 1 < self.move_num:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
                self.move_n = self.move_n + 1
                self.move_dir = self.move_n * math.pi / self.move_num
                self.speed_x = self.speed * math.cos(self.move_dir)
                self.speed_y = self.speed * math.sin(self.move_dir)
                self.move_action = MoveAction.Forward
        
        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["move_dist"] = self.move_dist
        info["speed_x"] = self.speed_x
        info["speed_y"] = self.speed_y
        info["move_n"] = self.move_n
        info["move_num"] = self.move_num
        r.setInfo(json.dumps(info))
        r.logDebug("GoLineCalibAction][{}|{}".format(
                    self.move_action,
                    self.status))

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    data["name"] = "steer1"
    print(m.run(r, data))