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
    "distanceBack": {
        "value": 0.1,
        "tips": "长度",
        "type": "double",
        "unit":"m",
        "maxValue":10.0,
        "minValue":0.01
    },
    "angleBack": {
        "value":30,
        "tips": "角度",
        "type": "double",
        "unit":"°",
        "maxValue":360.0,
        "minValue":1.0
    },
    "distanceForward": {
        "value": 1,
        "tips": "长度",
        "type": "double",
        "unit":"m",
        "maxValue":10.0,
        "minValue":0.01
    },
    "angleForward": {
        "value": 360,
        "tips": "角度",
        "type": "double",
        "unit":"°",
        "maxValue":3600.0,
        "minValue":1.0
    },
    "V": {
        "value": 0.1,
        "tips": "速度",
        "type": "double",
        "unit":"m/s",
        "maxValue":2.0,
        "minValue":0.01
    },
    "W": {
        "value": 30,
        "tips": "角速度",
        "type": "double",
        "unit":"°/s",
        "maxValue":360.0,
        "minValue":1.0
    }
}
####END DEFAULT ARGS####
"""

class MoveAction(IntEnum):
    InitcallGo2QRCenter = 0
    ShortBackward = 1
    Forward = 2
    Backward = 3
    callGo2QRCenter = 4
    ShortRotLeftInPlace = 5
    RotLeftInPlace = 6
    ActionEnd = 7

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.InitcallGo2QRCenter
        self.short_move_dist = 0.1
        self.short_rot_angle = math.pi/6
        self.move_dist = 1.0
        self.move_angle = 2 * math.pi
        self.speed_x = 0.1
        self.speed_w = math.pi/6

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            r.resetOdoMove()
            self.init = False
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.InitcallGo2QRCenter
            self.upside = args.get("up_side")
            if type(args) is dict and "distanceBack" in args:
                self.short_move_dist = float(args["distanceBack"])
            else:
                self.short_move_dist = 0.1
            if type(args) is dict and "angleBack" in args:
                self.short_rot_angle = float(args["angleBack"])*math.pi/180
            else:
                self.short_rot_angle = 30*math.pi/180
            if type(args) is dict and "distanceForward" in args:
                self.move_dist = float(args["distanceForward"])
            else:
                self.move_dist = 1.0
            if type(args) is dict and "angleForward" in args:
                self.move_angle = float(args["angleForward"])*math.pi/180
            else:
                self.move_angle = 360*math.pi/180
            if type(args) is dict and "V" in args:
                self.speed_x = float(args["V"])
            else:
                self.speed_x = 0.1
            if type(args) is dict and "W" in args:
                self.speed_w = float(args["W"])*math.pi/180
            else:
                self.speed_w = 30*math.pi/180
            r.resetGoPGV()

        # 实时运行
        if self.move_action == MoveAction.InitcallGo2QRCenter:
            self.status = r.goPGVRun({"use_down_pgv":not self.upside, "action_name":"callGo2QRCenter"})
        elif self.move_action == MoveAction.ShortBackward:
            self.status = r.runOdoMove({"move_dist": self.short_move_dist,  "speed_x":-self.speed_x, "action_name":"short_move_dist"})
        elif self.move_action == MoveAction.Forward:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":self.speed_x, "action_name":"Forward"})
        elif self.move_action == MoveAction.Backward:
            self.status = r.runOdoMove({"move_dist": self.move_dist - self.short_move_dist,  "speed_x":-self.speed_x, "action_name":"Backward"})
        elif self.move_action == MoveAction.callGo2QRCenter:
            self.status = r.goPGVRun({"use_down_pgv":not self.upside, "action_name":"callGo2QRCenter"})
        elif self.move_action == MoveAction.ShortRotLeftInPlace:
            self.status = r.runOdoMove({"move_angle": self.short_rot_angle,  "speed_w":-self.speed_w, "action_name":"ShortRotLeftInPlace"})
        elif self.move_action == MoveAction.RotLeftInPlace:
            self.status = r.runOdoMove({"move_angle": self.move_angle+self.short_rot_angle,  "speed_w":self.speed_w, "action_name":"RotLeftInPlace"})

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
            if self.move_action == MoveAction.callGo2QRCenter:
                r.resetGoPGV()
                self.status = MoveStatus.RUNNING
            if self.move_action != MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    print(m.run(r, data))