"""Robot providers — the interface dispatcher/WS use, independent of real vs sim.

`SimProvider` moves fake robots toward goals (Fase 0).
`SeerProvider` (Fase 1) will implement the same interface over the Robokit
TCP API (ports 19204 state / 19205 ctrl / 19206 task gotarget).
"""
from __future__ import annotations
import math
import time
from typing import Optional

from . import config
from .models import Robot


class Provider:
    robots: dict[str, Robot]

    def goto(self, robot_id: str, x: float, y: float, station: Optional[str]) -> None: ...
    def stop(self, robot_id: str) -> None: ...
    def tick(self, dt: float) -> None: ...
    def arrived(self, robot_id: str) -> bool: ...


class SimProvider(Provider):
    """Fake robots. Each moves straight toward its goal at ROBOT_SPEED."""

    def __init__(self) -> None:
        base = next((s for s in config.STATIONS if s["type"] == "base"), None)
        bx, by = (base["x"], base["y"]) if base else (50.0, 92.0)
        self.robots = {
            r["id"]: Robot(id=r["id"], name=r["name"], ip=r.get("ip", ""), x=bx, y=by)
            for r in config.ROBOTS
        }

    def goto(self, robot_id: str, x: float, y: float, station: Optional[str]) -> None:
        r = self.robots[robot_id]
        r.goal_x, r.goal_y, r.goal_station = x, y, station
        r.nav = "moving"
        r.paused = False

    def stop(self, robot_id: str) -> None:
        r = self.robots[robot_id]
        r.goal_x = r.goal_y = r.goal_station = None
        r.nav = "idle"

    def arrived(self, robot_id: str) -> bool:
        return self.robots[robot_id].nav == "idle"

    def tick(self, dt: float) -> None:
        step = config.ROBOT_SPEED * dt
        for r in self.robots.values():
            r.last_seen = time.time()
            if r.nav != "moving" or r.paused or r.goal_x is None:
                # idle drain is negligible; trickle-charge near base handled by dispatcher
                continue
            dx = r.goal_x - r.x
            dy = r.goal_y - r.y
            dist = math.hypot(dx, dy)
            if dist <= max(config.ARRIVE_EPS, step):
                r.x, r.y = r.goal_x, r.goal_y
                r.nav = "idle"
                r.goal_x = r.goal_y = None
            else:
                r.x += dx / dist * step
                r.y += dy / dist * step
                r.theta = math.atan2(dy, dx)
                r.battery = max(0.0, r.battery - 0.05 * dt * config.ROBOT_SPEED)
