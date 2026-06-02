"""Robot providers — the interface dispatcher/WS use, independent of real vs sim.

`SimProvider` moves fake robots toward goals (Fase 0).
`SeerProvider` (Fase 1) will implement the same interface over the Robokit
TCP API (ports 19204 state / 19205 ctrl / 19206 task gotarget).
"""
from __future__ import annotations
import math
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from . import config
from .models import Robot


class LocMode(str, Enum):
    """Localization quality, mirroring how a SEER robot degrades on a real floor."""
    OK = "ok"
    DEGRADED = "degraded"
    LOST = "lost"
    MISLOCALIZED = "mislocalized"


@dataclass
class _LocState:
    """Per-robot localization model. `est_*` is what raw_state() reports; the
    robot's own x/y/theta remain ground truth used for motion physics."""
    mode: LocMode = LocMode.OK
    confidence: float = 1.0
    est_x: float = 0.0
    est_y: float = 0.0
    est_theta: float = 0.0
    blocked: bool = False
    nav_failed: bool = False
    drift_dir: float = 0.0                       # fixed heading drift travels along (rad)
    pose_error_since: Optional[float] = None     # when pose error first exceeded threshold while navigating


class Provider:
    robots: dict[str, Robot]

    def goto(self, robot_id: str, x: float, y: float, station: Optional[str]) -> None: ...
    def stop(self, robot_id: str) -> None: ...
    def send_velocity(self, robot_id: str, vx: float, vy: float, w: float) -> bool:
        """Open-loop manual velocity command (operator jog). Default no-op."""
        return False
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
        # Deterministic RNG so localization noise/drift is reproducible in tests.
        self._rng = random.Random(0xC0FFEE)
        # Per-robot localization state. est_pose starts pinned to true pose.
        self._loc: dict[str, _LocState] = {
            rid: _LocState(
                est_x=r.x, est_y=r.y, est_theta=r.theta,
                drift_dir=self._rng.uniform(0.0, 2 * math.pi),
            )
            for rid, r in self.robots.items()
        }
        # SIM-ONLY recovery test hook: connection loss is independent of
        # localization (a robot can be healthy but lost).
        self._force_unhealthy: dict[str, bool] = {}
        # Manual operator jog velocities (robot_id → (vx, vy, w)); integrated in
        # tick() until cleared by stop(). Lets the Calibration page actually move
        # the sim robot, mirroring SeerProvider.send_velocity on real HW.
        self._manual_vel: dict[str, tuple[float, float, float]] = {}

    def goto(self, robot_id: str, x: float, y: float, station: Optional[str]) -> None:
        r = self.robots[robot_id]
        r.goal_x, r.goal_y, r.goal_station = x, y, station
        r.nav = "moving"
        r.paused = False

    def stop(self, robot_id: str) -> None:
        r = self.robots[robot_id]
        r.goal_x = r.goal_y = r.goal_station = None
        r.nav = "idle"
        self._manual_vel.pop(robot_id, None)       # cancel any manual jog
        loc = self._loc.get(robot_id)
        if loc is not None:                        # nav failure acknowledged
            loc.nav_failed = False
            loc.blocked = False
            loc.pose_error_since = None

    def send_velocity(self, robot_id: str, vx: float, vy: float, w: float) -> bool:
        """Manual operator jog. Stores the velocity; tick() integrates it.
        Zero velocity is treated as a stop (clears the manual hold)."""
        r = self.robots.get(robot_id)
        if r is None:
            return False
        r.goal_x = r.goal_y = r.goal_station = None
        r.nav = "idle"
        if vx == 0 and vy == 0 and w == 0:
            self._manual_vel.pop(robot_id, None)
        else:
            self._manual_vel[robot_id] = (vx, vy, w)
        return True

    def arrived(self, robot_id: str) -> bool:
        return self.robots[robot_id].nav == "idle"

    def raw_state(self, robot_id: str) -> dict:
        """Rich per-tick fields for telemetry. Reports the ESTIMATED pose
        (est_pose) in the same metric frame as the smap — NOT ground truth — so
        the dispatcher/operator see exactly what a real SEER robot would publish.
        task_status is a RAW SEER int (1=running, 3=finished, 4=failed)."""
        r = self.robots[robot_id]
        loc = self._loc[robot_id]
        moving = r.nav == "moving" and not r.paused and r.goal_x is not None
        connected = not self._force_unhealthy.get(robot_id, False)
        task_status = 4 if loc.nav_failed else (1 if moving else 3)
        return {
            "connected": connected,
            "task_status": task_status,
            "target_id": r.goal_station or "",
            "x": loc.est_x, "y": loc.est_y, "theta": loc.est_theta,
            "vx": None, "vy": None, "w": None,   # sim tracks no velocity; sampler derives it
            "confidence": loc.confidence,        # simulated SEER loc confidence
            "loc_mode": loc.mode.value,
            "blocked": loc.blocked,              # simulated SEER stuck/obstacle flag
            "last_seen": r.last_seen,
        }

    # ── Recovery signals ──────────────────────────────────────────────────
    def nav_failed(self, robot_id: str) -> bool:
        return self._loc[robot_id].nav_failed

    def healthy(self, robot_id: str) -> bool:
        """Health (connection) is independent of localization: a sim robot can be
        healthy but lost. Only force_unhealthy() takes it offline."""
        return not self._force_unhealthy.get(robot_id, False)

    # ── SIM-ONLY test hooks (no-op equivalents absent on SeerProvider) ─────
    def force_unhealthy(self, robot_id: str, value: bool = True) -> None:
        """Make healthy() False AND raw_state connected False."""
        self._force_unhealthy[robot_id] = bool(value)

    def force_nav_fail(self, robot_id: str) -> None:
        """Make the next raw_state report task_status == 4 (FAILED)."""
        self._loc[robot_id].nav_failed = True

    def clear_nav_fail(self, robot_id: str) -> None:
        self._loc[robot_id].nav_failed = False

    def force_stall(self, robot_id: str) -> None:
        """Pause the robot so its (true) position stops changing (reuses sim
        'paused'). The dispatcher's progress watchdog then trips on the frozen
        pose, independent of localization."""
        r = self.robots.get(robot_id)
        if r is not None:
            r.paused = True

    # ── SIM-ONLY localization fault injection (deterministic tests) ────────
    def force_loc_loss(self, robot_id: str, mode: "LocMode | str" = LocMode.LOST,
                       initial_confidence: float = 0.0,
                       jump_to_landmark: Optional[tuple[float, float]] = None) -> None:
        """Force a localization fault. `mode` is LOST/DEGRADED/MISLOCALIZED.
        `jump_to_landmark` (x, y) snaps est_pose to a wrong landmark → mislocalized."""
        loc = self._loc[robot_id]
        loc.mode = LocMode(mode)
        loc.confidence = float(initial_confidence)
        loc.nav_failed = False
        loc.blocked = False
        loc.pose_error_since = None
        if jump_to_landmark is not None:
            loc.est_x, loc.est_y = float(jump_to_landmark[0]), float(jump_to_landmark[1])
            loc.mode = LocMode.MISLOCALIZED

    def set_pose_error(self, robot_id: str, dx: float, dy: float, dtheta: float = 0.0) -> None:
        """Offset est_pose from true pose by (dx, dy, dtheta) — forces a known
        pose error so timeout transitions can be tested deterministically."""
        r = self.robots[robot_id]
        loc = self._loc[robot_id]
        loc.est_x = r.x + dx
        loc.est_y = r.y + dy
        loc.est_theta = r.theta + dtheta

    def relocalize(self, robot_id: str, x: float, y: float, theta: float) -> bool:
        """Operator-seeded relocalization. Succeeds only when the seed is within
        RELOCALIZE_SUCCESS_RADIUS_M and heading tolerance of the TRUE pose; on
        success est_pose snaps back, confidence resets, and blocked/nav_failed
        for the current attempt clear. A bad seed leaves the robot lost."""
        r = self.robots.get(robot_id)
        loc = self._loc.get(robot_id)
        if r is None or loc is None:
            return False
        d = math.hypot(x - r.x, y - r.y)
        dtheta = abs((theta - r.theta + math.pi) % (2 * math.pi) - math.pi)
        if d <= config.RELOCALIZE_SUCCESS_RADIUS_M and \
                dtheta <= math.radians(config.RELOCALIZE_SUCCESS_THETA_DEG):
            loc.mode = LocMode.OK
            loc.confidence = 0.95
            loc.est_x, loc.est_y, loc.est_theta = r.x, r.y, r.theta
            loc.blocked = False
            loc.nav_failed = False
            loc.pose_error_since = None
            return True
        return False

    # ── Localization estimate update (confidence trend + est drift) ────────
    def _update_loc(self, r: Robot, loc: _LocState, dt: float) -> None:
        decay = config.LOC_CONFIDENCE_DECAY_RATE * dt
        if loc.mode == LocMode.OK:
            loc.confidence = min(1.0, loc.confidence + decay)
            n = config.LOC_DRIFT_RATE_OK * dt
            loc.est_x = r.x + (self._rng.uniform(-n, n) if n else 0.0)
            loc.est_y = r.y + (self._rng.uniform(-n, n) if n else 0.0)
            loc.est_theta = r.theta
        elif loc.mode == LocMode.DEGRADED:
            loc.confidence = max(config.LOC_LOST_CONFIDENCE_THRESHOLD, loc.confidence - decay)
            rate = config.LOC_DRIFT_RATE_DEGRADED * dt
            loc.est_x += math.cos(loc.drift_dir) * rate
            loc.est_y += math.sin(loc.drift_dir) * rate
        else:  # LOST or MISLOCALIZED — confidence collapses, est drifts fast
            loc.confidence = max(0.0, loc.confidence - decay)
            rate = config.LOC_DRIFT_RATE_LOST * dt
            loc.est_x += math.cos(loc.drift_dir) * rate
            loc.est_y += math.sin(loc.drift_dir) * rate

    def tick(self, dt: float) -> None:
        now = time.time()
        step = config.ROBOT_SPEED * dt
        for r in self.robots.values():
            r.last_seen = now
            loc = self._loc[r.id]

            navigating = r.nav == "moving" and not r.paused and r.goal_x is not None
            pose_err = math.hypot(loc.est_x - r.x, loc.est_y - r.y)
            lost_badly = loc.mode in (LocMode.LOST, LocMode.MISLOCALIZED) and \
                pose_err > config.NAV_FAIL_POSE_ERROR_THRESHOLD_M

            # Localization-induced stall: while navigating with a large pose
            # error the robot can't make progress. Freeze true motion, then trip
            # blocked → nav_failed on the configured timeouts (no teleport).
            if navigating and lost_badly:
                if loc.pose_error_since is None:
                    loc.pose_error_since = now
                elapsed = now - loc.pose_error_since
                if elapsed > config.LOC_STUCK_TIMEOUT_S:
                    loc.blocked = True
                if elapsed > config.LOC_NAV_FAIL_TIMEOUT_S:
                    loc.nav_failed = True
                self._update_loc(r, loc, dt)   # est keeps drifting; true pose frozen
                continue
            loc.pose_error_since = None

            # Manual operator jog takes priority over goal-following.
            mv = self._manual_vel.get(r.id)
            if mv is not None:
                vx, vy, w = mv
                r.x = max(0.0, min(100.0, r.x + vx * dt))
                r.y = max(0.0, min(100.0, r.y + vy * dt))
                r.theta += w * dt
                self._update_loc(r, loc, dt)
                continue
            if r.nav != "moving" or r.paused or r.goal_x is None:
                # idle drain is negligible; trickle-charge near base handled by dispatcher
                self._update_loc(r, loc, dt)
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
            self._update_loc(r, loc, dt)
