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
    "V": {
        "value": 0.5,
        "tips": "速度",
        "type": "double",
        "unit":"m/s",
        "maxValue":2.0,
        "minValue":0.1
    },
    "L": {
        "value": 2.0,
        "tips": "长度",
        "type": "double",
        "unit":"m",
        "maxValue":5.0,
        "minValue":1.0
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

class MoveAction(IntEnum):
    Forward = 0
    ActionEnd = 1

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
                self.move_dist = 2.0
            if type(args) is dict and "V" in args:
                self.speed_x = float(args["V"])
            else:
                self.speed_x = 0.5

        # 实时运行
        if self.move_action == 0:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":self.speed_x, "action_name":"GoStraightForward"})
        
        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            self.move_action = self.move_action + 1
            if self.move_action != MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
        
        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["move_dist"] = self.move_dist
        info["speed_x"] = self.speed_x
        r.setInfo(json.dumps(info))
        r.logDebug("GoLineCalibAction][{}|{}".format(
                    self.move_action,
                    self.status))

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    print(m.run(r, data))