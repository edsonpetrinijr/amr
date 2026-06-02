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
    def raw_state(self, robot_id: str) -> dict: ...

    # ── Recovery signals (thin views over raw_state) ──────────────────────
    def nav_failed(self, robot_id: str) -> bool:
        return self.raw_state(robot_id).get("task_status") == 4

    def healthy(self, robot_id: str) -> bool:
        rs = self.raw_state(robot_id)
        return bool(rs.get("connected")) and \
            (time.time() - rs.get("last_seen", 0.0)) < config.ROBOT_STALE_S


class SimProvider(Provider):
    """Fake robots. Each moves straight toward its goal at ROBOT_SPEED."""

    def __init__(self) -> None:
        base = next((s for s in config.STATIONS if s["type"] == "base"), None)
        bx, by = (base["x"], base["y"]) if base else (50.0, 92.0)
        self.robots = {
            r["id"]: Robot(id=r["id"], name=r["name"], ip=r.get("ip", ""), x=bx, y=by)
            for r in config.ROBOTS
        }
        # SIM-ONLY recovery test hooks (absent on SeerProvider).
        self._force_unhealthy: dict[str, bool] = {}
        self._force_nav_fail: set[str] = set()

    def goto(self, robot_id: str, x: float, y: float, station: Optional[str]) -> None:
        r = self.robots[robot_id]
        r.goal_x, r.goal_y, r.goal_station = x, y, station
        r.nav = "moving"
        r.paused = False

    def stop(self, robot_id: str) -> None:
        r = self.robots[robot_id]
        r.goal_x = r.goal_y = r.goal_station = None
        r.nav = "idle"
        self._force_nav_fail.discard(robot_id)  # nav failure acknowledged

    def arrived(self, robot_id: str) -> bool:
        return self.robots[robot_id].nav == "idle"

    def raw_state(self, robot_id: str) -> dict:
        """Rich per-tick fields for telemetry. The sim has no real localization
        confidence / obstacle sensing, so those are None/False (TODO real HW).
        task_status is synthesized as a RAW SEER int (1=running, 3=finished,
        4=failed when a sim test forces a nav failure)."""
        r = self.robots[robot_id]
        moving = r.nav == "moving" and not r.paused and r.goal_x is not None
        connected = not self._force_unhealthy.get(robot_id, False)
        if robot_id in self._force_nav_fail:
            task_status = 4
        else:
            task_status = 1 if moving else 3
        return {
            "connected": connected,
            "task_status": task_status,
            "target_id": r.goal_station or "",
            "vx": None, "vy": None, "w": None,   # sim tracks no velocity; sampler derives it
            "confidence": None,                  # TODO(real HW): SEER loc confidence
            "blocked": False,                    # TODO(real HW): SEER obstacle flag
            "last_seen": r.last_seen,
        }

    # ── Recovery signals ──────────────────────────────────────────────────
    def nav_failed(self, robot_id: str) -> bool:
        return robot_id in self._force_nav_fail

    def healthy(self, robot_id: str) -> bool:
        """Sim robots are always healthy unless a test forces them offline."""
        return not self._force_unhealthy.get(robot_id, False)

    # ── SIM-ONLY test hooks (no-op equivalents absent on SeerProvider) ─────
    def force_unhealthy(self, robot_id: str, value: bool = True) -> None:
        """Make healthy() False AND raw_state connected False."""
        self._force_unhealthy[robot_id] = bool(value)

    def force_nav_fail(self, robot_id: str) -> None:
        """Make the next raw_state report task_status == 4 (FAILED)."""
        self._force_nav_fail.add(robot_id)

    def clear_nav_fail(self, robot_id: str) -> None:
        self._force_nav_fail.discard(robot_id)

    def force_stall(self, robot_id: str) -> None:
        """Pause the robot so its position stops changing (reuses sim 'paused')."""
        r = self.robots.get(robot_id)
        if r is not None:
            r.paused = True

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
