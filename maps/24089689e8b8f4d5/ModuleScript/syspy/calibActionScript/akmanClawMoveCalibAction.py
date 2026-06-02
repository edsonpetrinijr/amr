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
    MoveWait = 0
    Straight = 1
    Back = 2
    RightArcStraight = 3
    RightArcBack = 4
    LeftArcStraight = 5
    LeftArcBack = 6
    ActionEnd = 7

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.Straight
        self.move_dist = 5.0
        self.speed_x = 0.3

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            r.resetOdoMove()
            self.init = False
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.Straight
            self.move_dist = args.get("move_dist")
            self.RotRadius = args.get("RotRadius") # R=L/sin(alpha)
            if type(args) is dict and "V" in args:
                self.speed_x = float(args["V"])
            else:
                self.speed_x = 0.5

        # 实时运行
        if self.move_action == MoveAction.Straight:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":self.speed_x, "action_name":"GoStraightForward"})
        elif self.move_action == MoveAction.Back:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":-self.speed_x, "action_name":"GoStraightBackward"})
        elif self.move_action == MoveAction.RightArcStraight:
            self.status = r.runOdoMove({"rot_degree":math.degrees(self.move_dist/self.RotRadius),
                                                                      "rot_radius":self.RotRadius,
                                                                      "rot_speed":self.speed_x,
                                                                      "action_name":"GoLeftArcForward"})
        elif self.move_action == MoveAction.RightArcBack:
            self.status = r.runOdoMove({"rot_degree":math.degrees(self.move_dist/self.RotRadius),
                                                                      "rot_radius":self.RotRadius,
                                                                      "rot_speed":-self.speed_x,
                                                                      "action_name":"GoLeftArcBackward"})
        elif self.move_action == MoveAction.LeftArcStraight:
            self.status = r.runOdoMove({"rot_degree":math.degrees(self.move_dist/self.RotRadius),
                                                                      "rot_radius":-self.RotRadius,
                                                                      "rot_speed":self.speed_x,
                                                                      "action_name":"GoRightArcForward"})
        elif self.move_action == MoveAction.LeftArcBack:
            self.status = r.runOdoMove({"rot_degree":math.degrees(self.move_dist/self.RotRadius),
                                                                      "rot_radius":-self.RotRadius,
                                                                      "rot_speed":-self.speed_x,
                                                                      "action_name":"GoRightArcBackward"})

        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["status"] = self.status
        info["speed_x"] = self.speed_x
        info["RotRadius"] = self.RotRadius

        r.setInfo(json.dumps(info))
        r.logDebug("CameraExtrinsicCalibBasedonOdom][{}|{}|{}|{}".format(
                    self.move_action,
                    self.status,
                    self.speed_x,
                    self.RotRadius))

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