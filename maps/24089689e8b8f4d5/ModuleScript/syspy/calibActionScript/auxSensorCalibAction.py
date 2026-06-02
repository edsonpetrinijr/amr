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
        "value": 0.2,
        "tips": "长度",
        "type": "double",
        "unit":"m",
        "maxValue":10.0,
        "minValue":0.01
    },
    "V": {
        "value": 0.1,
        "tips": "速度",
        "type": "double",
        "unit":"m/s",
        "maxValue":2.0,
        "minValue":0.01
    }
}
####END DEFAULT ARGS####
"""

class MoveAction(IntEnum):
    Back1 = 1
    Back2 = 2
    Straight = 3
    NullAction = 4
    ActionEnd = 5

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.Back1
        self.move_dist = 0.2
        self.speed_x = 0.1

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            r.resetOdoMove()
            self.init = False
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.Back1
            if type(args) is dict and "L" in args:
                self.move_dist = float(args["L"])
            else:
                self.move_dist = 0.2
            if type(args) is dict and "V" in args:
                self.speed_x = float(args["V"])
            else:
                self.speed_x = 0.1
            if type(args) is dict and "calibType" in args:
                self.calibType = args["calibType"]
            else:
                self.calibType = ""

            self.deviceId = ""
            if type(args) is dict and "deviceId" in args:
                if self.calibType == "CameraMid360RPZExtrinsicCalib" or self.calibType == "CameraLocMid360RPZExtrinsicCalib":
                    self.deviceId = args["deviceId"]
                    r.addDisableDepthId(self.deviceId)
                

        # 实时运行
        if self.move_action == MoveAction.Back1:
            self.status = r.runOdoMove({"move_dist": self.move_dist*0.5,  "speed_x":-self.speed_x, "action_name":""})
        elif self.move_action == MoveAction.Back2:
            self.status = r.runOdoMove({"move_dist": self.move_dist*0.5,  "speed_x":-self.speed_x, "action_name":""})
        elif self.move_action == MoveAction.Straight:
            self.status = r.runOdoMove({"move_dist": self.move_dist,  "speed_x":self.speed_x, "action_name":""})
        elif self.move_action == MoveAction.NullAction:
            self.status = MoveStatus.FINISHED

        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["status"] = self.status
        info["speed_x"] = self.speed_x
        info["calibType"] = self.calibType
        info["deviceId"] = self.deviceId

        r.setInfo(json.dumps(info))
        r.logDebug("auxSensorCalibAction][{}|{}|{}|{}|{}".format(
                    self.move_action,
                    self.status,
                    self.speed_x,
                    self.calibType,
                    self.deviceId))

        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            record_status =  r.calibRecordService()
            if not record_status:
                return MoveStatus.RUNNING
            self.move_action = self.move_action + 1
            if self.move_action != MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING
        if self.status == MoveStatus.FINISHED and self.deviceId != "":
            r.clearDisableDepthId()

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    print(m.run(r, data))