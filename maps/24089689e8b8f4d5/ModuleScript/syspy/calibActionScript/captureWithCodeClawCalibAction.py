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
        "value": 1.5,
        "tips": "长度",
        "type": "double",
        "unit":"m",
        "maxValue":5.0,
        "minValue":1.0
    },
    "angle": {
        "value": 30,
        "tips": "角度",
        "type": "double",
        "unit":"°",
        "maxValue":90,
        "minValue":10
    },
    "num": {
        "value": 8,
        "tips": "个数",
        "type": "int",
        "unit":"count",
        "maxValue":30,
        "minValue":1
    } ,
    "time": {
        "value": 1,
        "tips": "次数",
        "type": "int",
        "unit":"count",
        "maxValue":10,
        "minValue":1
    } ,
    "tagCols": {
        "value": 5,
        "tips": "二维码阵列一行有多少个二维码数",
        "type": "int",
        "unit":"count",
        "maxValue":100,
        "minValue":1
    } ,
    "tagRows": {
        "value": 2,
        "tips": "二维码阵列有多少行",
        "type": "int",
        "unit":"count",
        "maxValue":100,
        "minValue":1
    } ,
    "tagSize": {
        "value": 0.35,
        "tips": "每一个二维码的宽度",
        "type": "double",
        "unit":"",
        "maxValue":10.0,
        "minValue":0.0
    } ,
    "tagSpace": {
        "value":0.05,
        "tips": "与二维码相邻黑块的大小",
        "type": "double",
        "unit":"",
        "maxValue":10.0,
        "minValue":0.0
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
    TrunRight = 3
    RightArcStraight = 4
    RightArcBack = 5
    TrunLeft = 6
    LeftArcStraight = 7
    LeftArcBack = 8
    TurnToOrigin = 9
    ActionEnd = 10

class Module(BasicModule):

    def __init__(self, r: SimModule, args):
        super().__init__()
        self.reset()

    def reset(self):
        self.init = True
        self.status = MoveStatus.RUNNING
        self.move_action = MoveAction.Straight
        self.MoveMaxDist = 1.5
        self.MoveMaxAngle = math.pi / 4
        self.MoveSpeed = 0.3
        self.MoveAngleSpeed = math.pi / 6
        self.CapturePhotoNum = 15

    def run(self, r: SimModule, args):
        # 初始化
        if self.init:
            r.resetOdoMove()
            self.init = False
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.Straight
            if type(args) is dict and "L" in args:
                self.MoveMaxDist = float(args["L"])
            else:
                self.MoveMaxDist = 1.5
            if type(args) is dict and "angle" in args:
                self.MoveMaxAngle = float(args["angle"])* math.pi/180
            else:
                self.MoveMaxAngle = 30 * math.pi/180
            if type(args) is dict and "num" in args:
                self.CapturePhotoNum = int(args["num"])
            else:
                self.CapturePhotoNum = 8
            if type(args) is dict and "time" in args:
                self.time = int(args["time"])
            else:
                self.time = 1
            self.MoveSpeed = args.get("MoveSpeed")
            self.MoveAngleSpeed = args.get("MoveAngleSpeed")
            self.cur_num = 0
            self.fileName = args.get("fileName")
            self.filePath = args.get("filePath")
            self.cam_id = args.get("deviceId")
            self.cur_time = 1

        # 实时运行
        if self.move_action == MoveAction.Straight:
            self.status = r.runOdoMove({"move_dist": self.MoveMaxDist / self.CapturePhotoNum,  "speed_x":self.MoveSpeed, "action_name":"GoStraightForward"})
        elif self.move_action == MoveAction.Back:
            self.status = r.runOdoMove({"move_dist": self.MoveMaxDist,  "speed_x":-self.MoveSpeed, "action_name":"GoStraightBackward"})
        elif self.move_action == MoveAction.TrunRight:
            self.status = r.runOdoMove({"move_angle": self.MoveMaxAngle,  "speed_w":-self.MoveAngleSpeed, "action_name":"GoRotBackward"})
        elif self.move_action == MoveAction.RightArcStraight:
            self.status = r.runOdoMove({"rot_degree":2 * math.degrees(self.MoveMaxAngle) / self.CapturePhotoNum ,
                                                                      "rot_radius":(self.MoveMaxDist/2)/math.sin(self.MoveMaxAngle),
                                                                      "rot_speed":self.MoveSpeed/2,
                                                                      "maxAcc":0.05,
                                                                      "maxDec":0.05,
                                                                      "action_name":"GoLeftArcForward"})
        elif self.move_action == MoveAction.RightArcBack:
            self.status = r.runOdoMove({"rot_degree":2 * math.degrees(self.MoveMaxAngle)  ,
                                                            "rot_radius":(self.MoveMaxDist/2)/math.sin(self.MoveMaxAngle),
                                                            "rot_speed":-self.MoveSpeed/2,
                                                            "maxAcc":0.05,
                                                            "maxDec":0.05,
                                                            "action_name":"GoLeftArcBackward"})
        elif self.move_action == MoveAction.TrunLeft:
            self.status = r.runOdoMove({"move_angle": 2 * self.MoveMaxAngle,  "speed_w":self.MoveAngleSpeed, "action_name":"GoRotForward"})
        elif self.move_action == MoveAction.LeftArcStraight:
            self.status = r.runOdoMove({"rot_degree":2 * math.degrees(self.MoveMaxAngle) / self.CapturePhotoNum ,
                                                            "rot_radius":-(self.MoveMaxDist/2)/math.sin(self.MoveMaxAngle),
                                                            "rot_speed":self.MoveSpeed/2,
                                                            "maxAcc":0.05,
                                                            "maxDec":0.05,
                                                            "action_name":"GoRightArcForward"})
        elif self.move_action == MoveAction.LeftArcBack:
            self.status = r.runOdoMove({"rot_degree":2 * math.degrees(self.MoveMaxAngle),
                                                            "rot_radius":-(self.MoveMaxDist/2)/math.sin(self.MoveMaxAngle),
                                                            "rot_speed":-self.MoveSpeed/2,
                                                            "maxAcc":0.05,
                                                            "maxDec":0.05,
                                                            "action_name":"GoRightArcBackward"})
        elif self.move_action == MoveAction.TurnToOrigin:
            self.status = r.runOdoMove({"move_angle": self.MoveMaxAngle,  "speed_w":-self.MoveAngleSpeed, "action_name":"NoAction"})

        # 实时打印
        info = dict()
        info["move_action"] = self.move_action
        info["status"] = self.status
        info["MoveMaxDist"] = self.MoveMaxDist
        info["MoveMaxAngle"] = self.MoveMaxAngle
        info["MoveSpeed"] = self.MoveSpeed
        info["MoveAngleSpeed"] = self.MoveAngleSpeed
        info["CapturePhotoNum"] = self.CapturePhotoNum
        info["cur_num"] = self.cur_num
        info["fileName"] = self.fileName
        info["filePath"] = self.filePath
        info["cam_id"] = self.cam_id

        r.setInfo(json.dumps(info))
        r.logDebug("CameraExtrinsicCalibBasedonOdom][{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(
                    self.move_action,
                    self.status,
                    self.MoveMaxDist,
                    self.MoveMaxAngle,
                    self.MoveSpeed,
                    self.MoveAngleSpeed,
                    self.CapturePhotoNum,
                    self.cur_num,
                    self.fileName,
                    self.filePath,
                    self.cam_id))

        # 当前任务完成时改变状态
        if self.status == MoveStatus.FINISHED:
            if (self.move_action == MoveAction.Straight  or self.move_action == MoveAction.RightArcStraight or
                 self.move_action == MoveAction.LeftArcStraight ):

                captrue_status =  r.recordCapture(self.fileName,self.filePath,self.cam_id)
                #captrue_status = True
                if not captrue_status:
                    return MoveStatus.RUNNING
                
                self.cur_num = self.cur_num + 1
                
                if self.cur_num == self.CapturePhotoNum:
                    self.move_action = self.move_action + 1
                    self.cur_num = 0
            else:
                self.move_action = self.move_action + 1
                self.cur_num = 0
            if self.move_action != MoveAction.ActionEnd:
                r.resetOdoMove()
                self.status = MoveStatus.RUNNING

        if self.move_action == MoveAction.ActionEnd and self.cur_time < self.time:
            r.resetOdoMove()
            self.cur_time = self.cur_time + 1
            self.status = MoveStatus.RUNNING
            self.move_action = MoveAction.Straight

        return self.status

if __name__ == '__main__':
    r = SimModule()
    m = Module(r, None)
    data = dict()
    print(m.run(r, data))
