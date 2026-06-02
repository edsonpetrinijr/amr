# -*- coding: utf-8 -*-
# @Date : 2025/09/20
# @Author : zhong
# @File :jack.py
# @Update :


import json
import sys
import os
import time
import math
from enum import IntEnum

sys.path.append(os.path.dirname(__file__) + "/syspy")
sys.path.append("../syspy")

from syspy.rbk import MoveStatus, BasicModule
from syspy.rbkSim import SimModule
from syspy.robot import ModuleTool as Utils

"""
####BEGIN DEFAULT ARGS####
{
    "operation": {
        "value": "jack",
        "type": "complex",
        "default_value": ["jack_lift", "rotate"],
        "tips": "操作类型"
    },
    "robot_rotate_angle": {
        "value": 0.0,
        "type": "float",
        "unit": "°",
        "tips": "车体旋转角度, 默认世界坐标系"
    },
    "lift_height": {
        "value": 0.0,
        "type": "float",
        "unit": "m",
        "tips": "顶升高度"
    },
    "shelf_rotate_angle": {
        "value": 0.0,
        "type": "float",
        "unit": "°",
        "tips": "货架旋转角度, 默认世界坐标系"
    },
    "robot_rotate_direction": {
        "value": 0,
        "type": "int",
        "tips": "车体旋转方向：-1 顺时针 0 就近 1 逆时针"
    },
    "shelf_rotate_direction": {
        "value": 0,
        "type": "int",
        "tips": "车体旋转方向：-1 顺时针 0 就近 1 逆时针"
    },
    "robot_rotate_coordinate": {
        "value": "world",
        "type": "complex",
        "default_value": ["robot", "world"],
        "tips": "车体旋转坐标系"
    },
    "shelf_rotate_coordinate": {
        "value": "world",
        "type": "complex",
        "default_value": ["robot", "world", "increase"],
        "tips": "货架旋转坐标系"
    },
    "spin": {
        "value": true,
        "type": "bool",
        "tips": "机器人转动时，是否随动"
    }
}
####END DEFAULT ARGS####
"""


class ConfigParams:
    """配置参数"""
    timeout = 120  # 脚本运行超时时间
    shelf_file = "shelf/s0001.shelf"  # 顶升货架模型文件
    lift_motor_name = "lift"
    spin_motor_name = "spin"


class Module(BasicModule):
    def __init__(self, r: SimModule, args):
        super(Module, self).__init__()
        self.init_args = False
        self.script_args = args
        self.script_status = MoveStatus.NONE
        self.spin = args.get("spin", False)
        self.robot_rotate_angle = args.get("robot_rotate_angle", None)
        self.shelf_rotate_angle = args.get("shelf_rotate_angle", None)
        self.robot_rotate_coordinate = args.get("robot_rotate_coordinate", Coordinate.WORLD)
        self.shelf_rotate_coordinate = args.get("shelf_rotate_coordinate", Coordinate.WORLD)
        self.robot_rotate_direction = args.get("robot_rotate_direction", RotateDirection.NEARBY)
        self.shelf_rotate_direction = args.get("shelf_rotate_direction", RotateDirection.NEARBY)
        self.lift_height = args.get("lift_height", 0)
        self.lift_speed = args.get("lift_speed", 0.03)
        self.lift_stop_di = -1
        self.operation = args.get("operation", None)
        self.report_info = dict()
        self.action_list = list()
        self.action_id = 0
        r.logInfo(f"init args: {args}")
        r.clearError(53000)
        r.clearWarning(55300)
        r.clearNotice(57300)

    def run(self, r: SimModule, args):
        self.script_status = MoveStatus.RUNNING
        self._init_args(r)
        self._execute_actions()

        if self.action_id < len(self.action_list):
            self.report_info["current_action"] = self.action_list[self.action_id].action_state
        self.report_info["action_list_name"] = list(map(lambda x: x.__class__.__name__, self.action_list))
        self.report_info["action_id"] = self.action_id
        self.report_info["date"] = Utils.get_now_date()
        self.report_info["current_robot_angle"] = r.loc().get("angle", 0.) / math.pi * 180
        self.report_info["jack_to_robot_angle"] = Utils.get_motor_pos(r, ConfigParams.spin_motor_name) / math.pi * 180
        self.report_info["current_lift"] = Utils.get_motor_pos(r, ConfigParams.lift_motor_name)
        self.report_info["script_args"] = args
        self.report_info["script_status"] = self.script_status
        r.setInfo(json.dumps(self.report_info))
        r.logInfo(json.dumps(self.report_info))
        return self.script_status

    def _init_args(self, r: SimModule):
        if not self.init_args:
            self.init_args = True
            if self.operation == "jack_lift":
                self.action_list.append(
                    Jack(r, ConfigParams.lift_motor_name, self.lift_height, self.lift_speed, self.lift_stop_di))
            elif self.robot_rotate_angle is not None and self.shelf_rotate_angle is not None:
                self.action_list.append(RobotRotateAndSpin(r, self.robot_rotate_angle, self.robot_rotate_coordinate,
                                                           self.spin, self.robot_rotate_direction,
                                                           self.shelf_rotate_angle,
                                                           self.shelf_rotate_coordinate, self.shelf_rotate_direction))
            elif self.robot_rotate_angle is not None:
                self.action_list.append(RobotRotate(r, self.robot_rotate_angle, self.robot_rotate_coordinate,
                                                    self.spin, self.robot_rotate_direction))
            elif self.shelf_rotate_angle is not None:
                self.action_list.append(Spin(r, self.shelf_rotate_angle, self.shelf_rotate_coordinate,
                                             self.shelf_rotate_direction))
            else:
                r.setError(f"script args error: {self.script_args}")

    def _execute_actions(self):
        if self.action_id < len(self.action_list):
            if self.action_list[self.action_id].action_status == ActionStatus.FINISHED:
                self.action_id += 1
            elif self.action_list[self.action_id].action_status == ActionStatus.FAILED:
                self.script_status = MoveStatus.FAILED
            else:
                self.action_list[self.action_id].run()
        else:
            self.script_status = MoveStatus.FINISHED


class BaseAction:
    """定义动作的基类"""

    def __init__(self, r: SimModule):
        self.action_args = locals()
        self.filter_args()
        self.rbk = r
        self.init = False
        self.start_time = time.time()
        self.action_status = ActionStatus.INIT
        self.action_state = dict()

    def run(self):
        """外部调用时，输出或打印实例对象的 action_state 字段 """
        self.action_state['action_name'] = self.__class__.__name__
        self.action_state["action_args"] = self.action_args
        self.action_state['action_status'] = self.action_status
        self.action_state["action_runtime"] = time.time() - self.start_time
        pass

    def reset(self):
        pass

    def filter_args(self):
        self.action_args.pop('r', None)
        self.action_args.pop('self', None)
        self.action_args.pop('__class__', None)

    def __str__(self):
        return json.dumps({json.dumps(self.action_state)})


class Jack(BaseAction):
    def __init__(self, r: SimModule, motor_name: str, height: float, speed=0., stop_di=-1):
        super().__init__(r)
        self.action_args = locals()
        self.filter_args()
        self.rbk = r
        self.motor_name = motor_name
        self.height = height
        self.speed = speed
        self.stop_di = stop_di

    def run(self):
        self.action_status = ActionStatus.RUNNING
        if not self.init:
            self.init = True
        self.rbk.setMotorPosition(self.motor_name, self.height, self.speed, self.stop_di)
        self.rbk.publishSpeed()
        if self.rbk.isMotorReached(self.motor_name) or Utils.check_DI(self.rbk, self.stop_di):
            if self.height > 0:
                self.rbk.setLocalShelfArea(ConfigParams.shelf_file)
            else:
                self.rbk.resetLocalShelfArea()
            self.action_status = ActionStatus.FINISHED

        self.action_state['action_name'] = self.__class__.__name__
        self.action_state["action_args"] = self.action_args
        self.action_state['action_status'] = self.action_status
        self.action_state["action_runtime"] = time.time() - self.start_time

    def reset(self):
        pass


class Spin(BaseAction):
    def __init__(self, r: SimModule, angle, coordinate, direction):
        super().__init__(r)
        self.rbk = r
        self.angle = angle
        self.coordinate = coordinate
        self.direction = direction
        self.init = False

    def run(self):
        self.action_status = ActionStatus.RUNNING

        if not self.init:
            self.init = True
            if self.coordinate == Coordinate.ROBOT:
                self.rbk.setRobotSpinAngle(self.angle / 180 * math.pi, self.direction)
            elif self.coordinate == Coordinate.WORLD:
                self.rbk.setGlobalSpinAngle(self.angle / 180 * math.pi, self.direction)
            elif self.coordinate == Coordinate.INCREASE:
                self.rbk.setIncreaseSpinAngle(self.angle / 180 * math.pi)

        self.rbk.publishSpeed()
        if self.rbk.spinRun():
            self.action_status = ActionStatus.FINISHED

        self.action_state['coordinate'] = self.coordinate
        self.action_state['angle'] = self.angle
        self.action_state['action_status'] = self.action_status
        self.action_state['direction'] = self.direction
        self.action_state['action_name'] = self.__class__.__name__


class RobotRotate(BaseAction):
    """实现车体旋转，包含货架随动的情况"""

    def __init__(self, r: SimModule, angle, coordinate, spin=False, direction=0):
        super().__init__(r)
        self.rbk = r
        self.angle = angle
        self.coordinate = coordinate
        self.spin = spin
        self.direction = direction
        self.speed = 0.5
        self.move_args = dict()
        self.move_args['spin'] = self.spin  # 是否随动
        self.move_args['speed_w'] = self.speed
        if self.coordinate == Coordinate.ROBOT:
            self.move_args['loc_mode'] = 0  # 基于里程定位
            self.move_args['move_angle'] = self.angle / 180 * math.pi
            if self.angle < 0:
                self.move_args['move_angle'] = -self.angle / 180 * math.pi
                self.move_args['speed_w'] = -self.speed
        elif self.coordinate == Coordinate.WORLD:
            self.move_args['loc_mode'] = 1  # 基于激光定位
            current_angle = self.rbk.loc().get('angle', 0)
            rotate_dist = (self.angle / 180 * math.pi) - current_angle
            rotate_dist = rotate_dist % (2 * math.pi)  # 需要转动的角度, 正数
            self.move_args['move_angle'] = rotate_dist
            if self.direction == RotateDirection.CLOCKWISE:  # 顺时针
                self.move_args['speed_w'] = -self.speed
                self.move_args['move_angle'] = 2 * math.pi - rotate_dist
            elif self.direction == RotateDirection.COUNTERCLOCKWISE:  # 逆时针
                self.move_args['speed_w'] = self.speed
            elif self.direction == RotateDirection.NEARBY:  # 就近
                if rotate_dist > math.pi:
                    self.move_args['speed_w'] = -self.speed
                    self.move_args['move_angle'] = 2 * math.pi - rotate_dist
        r.resetOdoMove()

    def run(self):
        self.action_status = ActionStatus.RUNNING

        if self.rbk.runOdoMove(self.move_args) == MoveStatus.FINISHED:
            self.action_status = ActionStatus.FINISHED
        self.action_state['coordinate'] = self.coordinate
        self.action_state['angle'] = self.angle
        self.action_state['spin'] = self.spin
        self.action_state['move_args'] = self.move_args
        self.action_state['action_status'] = self.action_status
        self.action_state['direction'] = self.direction
        self.action_state['action_name'] = self.__class__.__name__
        print("***", self.action_state, "***")


class RobotRotateAndSpin(BaseAction):
    """实现车体和货架都要旋转，且各自旋转角度不同的情况"""

    def __init__(self, r: SimModule, robot_angle, robot_coordinate, spin, robot_direction, spin_angle, spin_coordinate,
                 spin_direction):
        super().__init__(r)
        self.rbk = r
        self.robot_angle = robot_angle
        self.robot_coordinate = robot_coordinate
        self.robot_direction = robot_direction
        self.spin_direction = spin_direction
        self.spin = spin
        self.spin_angle = spin_angle
        self.spin_coordinate = spin_coordinate
        self.spin_rotate = Spin(r, spin_angle, spin_coordinate, spin_direction)
        self.robot_rotate = RobotRotate(r, robot_angle, robot_coordinate, spin=spin, direction=robot_direction)

    def run(self):
        self.action_status = ActionStatus.RUNNING
        if (self.spin_rotate.action_status == ActionStatus.FAILED or
                self.robot_rotate.action_status == ActionStatus.FAILED):
            self.action_status = ActionStatus.FAILED
            return self.action_status

        if self.robot_rotate.action_status != ActionStatus.FINISHED:
            self.robot_rotate.run()

        elif self.spin_rotate.action_status != ActionStatus.FINISHED:
            self.spin_rotate.run()

        if (self.spin_rotate.action_status == ActionStatus.FINISHED and
                self.robot_rotate.action_status == ActionStatus.FINISHED):
            self.action_status = ActionStatus.FINISHED

        self.action_state['shelf_coordinate'] = self.spin_coordinate
        self.action_state['shelf_angle'] = self.spin_angle
        self.action_state['shelf_direction'] = self.spin_direction
        self.action_state['robot_direction'] = self.robot_direction
        self.action_state['robot_coordinate'] = self.robot_coordinate
        self.action_state['robot_angle'] = self.robot_angle
        self.action_state['spin'] = self.spin
        self.action_state['action_status'] = self.action_status
        self.action_state['robot_action_status'] = self.robot_rotate.action_status
        self.action_state['shelf_action_status'] = self.spin_rotate.action_status
        self.action_state['action_name'] = self.__class__.__name__


class PgvAdjust(BaseAction):
    pass


class CheckGoodsId:
    pass


class Coordinate:
    ROBOT = "robot"
    WORLD = "world"
    INCREASE = "increase"


class ActionStatus(IntEnum):
    INIT = 0
    RUNNING = 1
    FINISHED = 3
    FAILED = 4
    SUSPENDED = 5


class RotateDirection(IntEnum):
    NEARBY = 0
    COUNTERCLOCKWISE = 1
    CLOCKWISE = -1


if __name__ == '__main__':
    r1 = SimModule()
    args1 = {
        "operation": "rotate",
        "robot_rotate_angle": 270,
        "robot_rotate_direction": 0,
        "shelf_rotate_angle": 270,
        "shelf_rotate_direction": 0,
        "spin": True
    }
    m = Module(r1, args1)
    run_counter = 0
    while m.status is not MoveStatus.FAILED and m.status is not MoveStatus.FINISHED:
        m.run(r1, args1)
        if run_counter > 20:
            break
        else:
            print("run次数：", run_counter)
            run_counter += 1
