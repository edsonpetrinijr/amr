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
    MoveWait = 0
    Rot1st4LeftArc = 1
    GoLeftArc = 2
    Rot2nd4GoForward = 3
    GoForward2Origin = 4
    Rot3rd4RightArc = 5
    GoRightArc = 6
    Rot4th4GoBackward = 7
    GoBackward2Origin = 8
    ActionEnd = 9

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.Rot1st4LeftArc
        self.move_dist = 2
        self.speed_x = 0.3
        self.speed_w = math.pi/4

    def run(self, r: SimModule, args:json):
        # 初始化
        if self.init:
            r.resetOdoMove()
            self.init = False
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.Rot1st4LeftArc
            if type(args) is dict and "L" in args:
                self.move_dist = float(args["L"])
            else:
                self.move_dist = 2.0
            if type(args) is dict and "V" in args:
                self.speed_x = float(args["V"])
            else:
                self.speed_x = 0.3
            if type(args) is dict and "W" in args:
                self.speed_w = float(args["W"]) * math.pi / 180
            else:
                self.speed_w = 45*math.pi/180

        # 实时运行
        if self.move_action == MoveAction.Rot1st4LeftArc:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":self.speed_w, "action_name":"Rot1st4LeftArc"})
        elif self.move_action == MoveAction.GoLeftArc:
            self.status = r.runOdoMove({"rot_degree":180.0,
                                                                      "rot_radius":-0.5*self.move_dist,
                                                                      "rot_speed":self.speed_x,
                                                                      "action_name":"GoLeftArc"})
        elif self.move_action == MoveAction.Rot2nd4GoForward:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":-self.speed_w, "action_name":"Rot2nd4GoForward"})
        elif self.move_action == MoveAction.GoForward2Origin:
            self.status = r.runOdoMove({"move_dist":self.move_dist, "speed_x":self.speed_x,  "action_name":"GoForward2Origin"})
        elif self.move_action == MoveAction.Rot3rd4RightArc:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":self.speed_w, "action_name":"Rot3rd4RightArc"})
        elif self.move_action == MoveAction.GoRightArc:
            self.status = r.runOdoMove({"rot_degree":180.0,
                                                                      "rot_radius":0.5*self.move_dist,
                                                                      "rot_speed":self.speed_x,
                                                                      "action_name":"GoRightArc"})
        elif self.move_action == MoveAction.Rot4th4GoBackward:
            self.status = r.runOdoMove({"move_angle": math.pi/2,  "speed_w":-self.speed_w, "action_name":"Rot4th4GoBackward"})
        elif self.move_action == MoveAction.GoBackward2Origin:
            self.status = r.runOdoMove({"move_dist":self.move_dist, "speed_x":-self.speed_x,  "action_name":"GoForward2Origin"})

        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["status"] = self.status
        info["move_dist"] = self.move_dist
        info["move_action"] = self.move_action
        info["speed_x"] = self.speed_x
        info["speed_w"] = self.speed_w

        r.setInfo(json.dumps(info))
        r.logDebug("LaserOdomCalib][{}|{}|{}|{}|{}|{}|".format(
                    self.move_action,
                    self.status,
                    self.move_dist,
                    self.move_action,
                    self.speed_x,
                    self.speed_w))

        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            self.move_action = self.move_action + 1
            if self.move_action != MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    print(m.run(r, data))