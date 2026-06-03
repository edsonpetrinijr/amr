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
T_RECOVERING = "recovering"

# ── Robot physical footprint (real-world, metres) ──────────────────────────────
# Top-down rectangle: length is along +theta (forward), width is perpendicular.
# Rendered to scale on the 2D map (frontend MapCanvas) using map px/m.
#
# PLACEHOLDER — needs founder confirmation. The CAD at repo root (AMR.step,
# AP242 from Onshape) parses cleanly (units = METRE, single shared origin) but
# its global bounding box is only ~0.065 x 0.215 x 0.025 m — a thin sub-component
# / bracket, NOT the full chassis. Those numbers are implausible as a robot
# footprint, so we use a documented compact-AMR default below until the real
# chassis dimensions are confirmed. Keep this the single source of truth; the
# frontend mirrors it in api/types.ts (DEFAULT_FOOTPRINT).
DEFAULT_FOOTPRINT_LENGTH_M = 0.70
DEFAULT_FOOTPRINT_WIDTH_M = 0.50


def default_footprint() -> dict:
    """Fresh dict so each Robot gets its own footprint (no shared mutable default)."""
    return {"length": DEFAULT_FOOTPRINT_LENGTH_M, "width": DEFAULT_FOOTPRINT_WIDTH_M}


# Callbutton states
CB_IDLE   = "idle"
CB_READY  = "ready"    # este lado apertou, aguardando o par
CB_CALLED = "called"   # ambos prontos, AMR despachado
CB_SERVED = "served"   # tarefa concluída


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
    # Real-world footprint in metres {"length", "width"} — rendered to scale on
    # the 2D map. Defaults to the shared compact-AMR placeholder (see above).
    footprint: dict = field(default_factory=default_footprint)

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
    cb_state: str = CB_IDLE
    cb_dir: Optional[str] = None   # "fwd" | "ret" | None

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
    facility_id: str = "piracicaba"
    created_at: float = field(default_factory=time.time)
    assigned_at: Optional[float] = None
    done_at: Optional[float] = None
    # ── Failure-recovery bookkeeping ──────────────────────────────────────
    retries: int = 0
    last_robot: Optional[str] = None          # robot that last failed this task (cooldown key)
    last_progress_at: Optional[float] = None   # wall time of last measured progress
    last_x: Optional[float] = None             # robot pose at last progress check
    last_y: Optional[float] = None
    fail_reason: Optional[str] = None          # nav_failed | robot_offline | stuck | battery

    @staticmethod
    def new(pickup: str, dropoff: str, facility_id: str = "piracicaba") -> "Task":
        return Task(id=f"T{next(_task_counter):04d}", pickup=pickup, dropoff=dropoff, facility_id=facility_id)

    def to_dict(self) -> dict:
        return asdict(self)


# ── WebSocket message types ────────────────────────────────────────────────────
# Server → client

def world_snapshot(robots: list[Robot], stations: list[Station], tasks_active: list[Task]) -> dict:
    return {
        "type": "world",
        "ts": time.time(),
        "robots": [r.to_dict() for r in robots],
        "stations": [s.to_dict() for s in stations],
        "tasks_active": [t.to_dict() for t in tasks_active if t.state not in (T_DONE, T_CANCELLED, T_FAILED)],
    }


def task_update_msg(task: Task, event: str) -> dict:
    return {"type": "task_update", "event": event, "task": task.to_dict()}


def callbutton_msg(station: Station) -> dict:
    return {"type": "callbutton", "station": station.to_dict()}


def alarm_msg(level: str, message: str, robot_id: Optional[str] = None,
              payload: Optional[dict] = None) -> dict:
    """SSE alarm. `payload` carries optional structured data (e.g. recovery
    relocalization assist) and is omitted entirely when None so existing
    consumers that only read level/message/robot_id keep working unchanged."""
    msg = {"type": "alarm", "level": level, "message": message, "robot_id": robot_id, "ts": time.time()}
    if payload is not None:
        msg["payload"] = payload
    return msg
