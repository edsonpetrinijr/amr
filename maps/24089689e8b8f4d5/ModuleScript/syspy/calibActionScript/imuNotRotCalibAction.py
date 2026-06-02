# coding=utf-8
import sys
import time
import math
from enum import Enum, IntEnum, auto
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
        "value": 0.5,
        "tips": "速度",
        "type": "double",
        "unit":"m/s",
        "maxValue":2.0,
        "minValue":0.1
    },
    "goStraightCnt": {
        "value": 3,
        "tips": "次数",
        "type": "int",
        "unit":"count",
        "maxValue":10,
        "minValue":1
    },
    "goRotCnt": {
        "value": 2,
        "tips": "次数",
        "type": "int",
        "unit":"count",
        "maxValue":10,
        "minValue":1
    }
}
####END DEFAULT ARGS####
"""

class MoveAction(IntEnum):
    GoStraightForWard = 0
    GoStraightBackWard = 1
    GoArcForWard = 2
    GoArcBackWard = 3
    ActionEnd = 4

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.GoStraightForWard

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            self.init = False
            r.resetOdoMove()
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.GoStraightForWard
            if type(args) is dict and "L" in args:
                self.move_dist = float(args["L"])
            else:
                self.move_dist = 2.0
            if type(args) is dict and "V" in args:
                self.speed_x = float(args["V"])
            else:
                self.speed_x = 0.5
            if type(args) is dict and "goStraightCnt" in args:
                self.goStraightCnt = int(args["goStraightCnt"])
            else:
                self.goStraightCnt = 3
            if type(args) is dict and "goRotCnt" in args:
                self.goRotCnt = int(args["goRotCnt"])
            else:
                self.goRotCnt = 2
            self.goCircleRadius = args.get("goCircleRadius")
            self.curGoStraightCnt = 0
            self.curGoRotCnt = 0

        # 实时运行
        if self.move_action == MoveAction.GoStraightForWard:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":self.speed_x, "action_name":"GoStraight"})
        elif self.move_action == MoveAction.GoStraightBackWard:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":-self.speed_x, "action_name":"GoStraight"})
        elif self.move_action == MoveAction.GoArcForWard:
            self.status = r.runOdoMove({"rot_degree":math.degrees(2*math.pi),
                                                                      "rot_radius":self.goCircleRadius,
                                                                      "rot_speed":self.speed_x,
                                                                      "action_name":"GoRot"})
        elif self.move_action == MoveAction.GoArcBackWard:
            self.status = r.runOdoMove({"rot_degree":math.degrees(2*math.pi),
                                                                      "rot_radius":self.goCircleRadius,
                                                                      "rot_speed":-self.speed_x,
                                                                      "action_name":"GoRot"})
    
        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            if self.move_action == MoveAction.GoStraightBackWard and self.curGoStraightCnt < self.goStraightCnt - 1:
                self.curGoStraightCnt = self.curGoStraightCnt + 1
                self.move_action = MoveAction.GoStraightForWard
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
            elif self.move_action == MoveAction.GoArcBackWard and self.curGoRotCnt < self.goRotCnt - 1:
                self.curGoRotCnt = self.curGoRotCnt + 1
                self.move_action = MoveAction.GoArcForWard
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
            else:
                self.move_action = self.move_action + 1
                if self.move_action !=  MoveAction.ActionEnd:
                    r.resetOdoMove()
                    self.status = MoveStatus.RUNNING
        
        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["speed_x"] = self.speed_x
        info["goStraightCnt"] = self.goStraightCnt
        info["goRotCnt"] = self.goRotCnt
        info["curGoStraightCnt"] = self.curGoStraightCnt
        info["curGoRotCnt"] = self.curGoRotCnt
        info["goCircleRadius"] = self.goCircleRadius

        r.setInfo(json.dumps(info))
        r.logDebug("GoRotCalib][{}|{}".format(
                    self.move_action,
                    self.status))

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    print(m.run(r, data))
