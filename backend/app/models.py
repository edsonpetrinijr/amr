"""Domain types shared by provider, dispatcher, and the WS layer."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import time
import itertools

# Robot status (high level, what the operator sees)
IDLE = "idle"
ENROUTE_PICKUP = "enroute_pickup"
AT_PICKUP = "at_pickup"
ENROUTE_DROP = "enroute_drop"
RETURNING = "returning"
CHARGING = "charging"
ERROR = "error"
OFFLINE = "offline"

# Task states
T_PENDING = "pending"
T_ASSIGNED = "assigned"
T_ENROUTE_PICKUP = "enroute_pickup"
T_AT_PICKUP = "at_pickup"
T_ENROUTE_DROP = "enroute_drop"
T_DONE = "done"
T_CANCELLED = "cancelled"
T_FAILED = "failed"

# Callbutton states
CB_IDLE = "idle"
CB_CALLED = "called"
CB_ACKED = "acknowledged"
CB_SERVED = "served"


@dataclass
class Robot:
    id: str
    name: str
    ip: str = ""
    x: float = 50.0
    y: float = 92.0
    theta: float = 0.0
    battery: float = 100.0
    status: str = IDLE
    nav: str = "idle"          # "moving" | "idle" — low-level motion state
    goal_x: Optional[float] = None
    goal_y: Optional[float] = None
    goal_station: Optional[str] = None
    current_task: Optional[str] = None
    paused: bool = False
    last_seen: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Station:
    id: str
    type: str
    label: str
    x: float
    y: float
    seer_lm: Optional[str] = None
    ap_id: Optional[str] = None
    opcua_node: Optional[str] = None
    cb_state: str = CB_IDLE     # only meaningful for type == "callbutton"

    def to_dict(self) -> dict:
        return asdict(self)


_task_counter = itertools.count(1)


@dataclass
class Task:
    id: str
    pickup: str                 # station id (where the part is / call origin)
    dropoff: str                # station id (destination)
    state: str = T_PENDING
    robot: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    assigned_at: Optional[float] = None
    done_at: Optional[float] = None

    @staticmethod
    def new(pickup: str, dropoff: str) -> "Task":
        return Task(id=f"T{next(_task_counter):04d}", pickup=pickup, dropoff=dropoff)

    def to_dict(self) -> dict:
        return asdict(self)
