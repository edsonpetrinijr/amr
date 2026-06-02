# coding=utf-8
import sys
import math
from enum import IntEnum
import json
sys.path.append("syspy")
from syspy.rbkSim import SimModule
from syspy.rbk import MoveStatus, BasicModule

"""
####BEGIN DEFAULT ARGS####
{
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
    ActionStart = 0
    ActionEnd = 1

class Module(BasicModule):

    def __init__(self, r: SimModule, args):

        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.ActionStart
        self.move_angle = math.pi * 2
        self.speed_w=math.pi / 4

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            self.init = False
            r.resetOdoMove()
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.ActionStart
            self.move_angle = math.pi * 2
            if type(args) is dict and "W" in args:
                self.speed_w = float(args["W"]) * math.pi / 180
            else:
                self.speed_w = 45*math.pi/180

        # 实时运行
        if self.move_action == 0:
            self.status = r.runOdoMove({"move_angle":self.move_angle,  "speed_w":self.speed_w, "action_name":"GoRotForward", "spin":True})
        
        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            self.move_action = self.move_action + 1
            if self.move_action !=  MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
        
        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["move_angle"] = self.move_angle
        info["speed_w"] = self.speed_w
        r.setInfo(json.dumps(info))
        r.logDebug("spinRatio][{}|{}".format(
                    self.move_action,
                    self.status))
        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    data["name"] = "steer1"
    data["move_angle"] = math.pi * 6
    data["speed_w"] = math.pi / 3
    print(m.run(r, data))
