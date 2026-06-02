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
    "rotCount": {
        "value": 3,
        "tips": "圈数",
        "type": "int",
        "unit":"圈",
        "maxValue":10,
        "minValue":1
    },
    "W": {
        "value": 30,
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
    ForkUnload1 = 1
    Rot1st = 2
    ForkLoad = 3
    Rot2nd = 4
    ForkUnload2 = 5
    ActionEnd = 6

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.ForkUnload1
        self.rotCount = 3
        self.speed_w = 45*math.pi/180

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            r.resetOdoMove()
            r.resetForkHeight()
            self.init = False
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.ForkUnload1
            if type(args) is dict and "rotCount" in args:
                self.rotCount = int(args["rotCount"])
            else:
                self.rotCount = 3
            if type(args) is dict and "W" in args:
                self.speed_w = float(args["W"])*math.pi/180
            else:
                self.speed_w = 45*math.pi/180
            r.resetGoPGV()

        # 实时运行
        if self.move_action == MoveAction.ForkUnload1:
            self.status = r.runForkHeight({"id":"SELF_POSITION",  "operation":"ForkUnload", "end_height":0.0})
        elif self.move_action == MoveAction.Rot1st:
            self.status = r.runOdoMove({"move_angle": self.rotCount * 2 * math.pi,  "speed_w":self.speed_w, "action_name":"Rot1st"})
        elif self.move_action == MoveAction.ForkLoad:
            self.status = r.runForkHeight({"id":"SELF_POSITION",  "operation":"ForkLoad", "end_height":1.0})
        elif self.move_action == MoveAction.Rot2nd:
            self.status = r.runOdoMove({"move_angle": self.rotCount * 2 * math.pi,  "speed_w":self.speed_w, "action_name":"Rot2nd"})
        elif self.move_action == MoveAction.ForkUnload2:
            self.status = r.runForkHeight({"id":"SELF_POSITION",  "operation":"ForkUnload", "end_height":0.0})

        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["status"] = self.status
        info["rotCount"] = self.rotCount
        info["move_action"] = self.move_action
        info["speed_w"] = self.speed_w

        r.setInfo(json.dumps(info))
        r.logDebug("LaserOdomCalib][{}|{}|{}|{}|{}|".format(
                    self.move_action,
                    self.status,
                    self.rotCount,
                    self.move_action,
                    self.speed_w))

        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            if self.move_action == MoveAction.ForkUnload1 or self.move_action == MoveAction.ForkUnload2:
                r.wheelBaseShift(False)
            if self.move_action == MoveAction.ForkLoad:
                r.wheelBaseShift(True)
            self.move_action = self.move_action + 1
            if self.move_action != MoveAction.ActionEnd:
                r.resetOdoMove()
                r.resetForkHeight()
                self.status = MoveStatus.RUNNING

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    print(m.run(r, data))