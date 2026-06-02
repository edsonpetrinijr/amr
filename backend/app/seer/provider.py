"""
SeerProvider — real hardware implementation of the Provider interface.

Wraps one RobotConn per robot. The dispatcher calls:
  goto(robot_id, x, y, station)  → maps to goto_target(seer_lm)
  stop(robot_id)                  → send zero velocity
  arrived(robot_id)               → check RobotConn.arrived()
  tick(dt)                        → copy RobotConn.state → Robot domain object

Station-to-landmark mapping is taken from config.STATIONS[*].seer_lm.
If seer_lm is None the robot is sent to the nearest map coordinate instead
(fallback for APs without a landmark binding — not yet implemented).
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from .. import config
from ..models import (
    Robot,
    IDLE, ENROUTE_PICKUP, ENROUTE_DROP, CHARGING, ERROR, OFFLINE,
)
from .robot_conn import RobotConn, TASK_FAILED, TASK_FINISHED

log = logging.getLogger(__name__)


class SeerProvider:
    """Real robots via SEER Robokit TCP API."""

    def __init__(self) -> None:
        # Build station_id → seer_lm lookup
        self._lm: dict[str, str] = {
            s['id']: s['seer_lm']
            for s in config.STATIONS
            if s.get('seer_lm')
        }

        # One RobotConn per robot
        self._conns: dict[str, RobotConn] = {}
        base = next((s for s in config.STATIONS if s['type'] == 'base'), None)
        bx, by = (base['x'], base['y']) if base else (0.0, 0.0)

        self.robots: dict[str, Robot] = {}

        for r in config.ROBOTS:
            rid = r['id']
            conn = RobotConn(rid, r['ip'])
            conn.start()
            self._conns[rid] = conn
            self.robots[rid] = Robot(
                id=rid, name=r['name'], ip=r.get('ip', ''),
                x=bx, y=by, status=OFFLINE,
            )

        log.info("SeerProvider: %d robots started", len(self.robots))

    # ── Provider interface ────────────────────────────────────────────────────

    def goto(self, robot_id: str, x: float, y: float, station: Optional[str]) -> None:
        """Send robot to a station. Uses the station's seer_lm if available."""
        conn = self._conns.get(robot_id)
        if conn is None:
            return
        lm = self._lm.get(station, '') if station else ''
        if not lm:
            log.warning("[%s] no landmark for station=%s — skipping goto", robot_id, station)
            return
        r = self.robots[robot_id]
        r.goal_x, r.goal_y, r.goal_station = x, y, station
        r.nav = 'moving'
        r.paused = False
        conn.goto_target(lm)

    def stop(self, robot_id: str) -> None:
        conn = self._conns.get(robot_id)
        if conn is None:
            return
        conn.stop()
        r = self.robots[robot_id]
        r.goal_x = r.goal_y = r.goal_station = None
        r.nav = 'idle'

    def send_velocity(self, robot_id: str, vx: float, vy: float, w: float) -> bool:
        """Open-loop manual velocity (operator jog) → SEER ctrl port 19205.
        Clears any nav goal so tick() doesn't fight the operator."""
        conn = self._conns.get(robot_id)
        if conn is None:
            return False
        r = self.robots.get(robot_id)
        if r is not None:
            r.goal_x = r.goal_y = r.goal_station = None
            r.nav = 'idle'
        return conn.send_velocity(vx, vy, w)

    def arrived(self, robot_id: str) -> bool:
        conn = self._conns.get(robot_id)
        if conn is None:
            return False
        return conn.arrived()

    def tick(self, dt: float) -> None:
        """Sync Robot domain objects from live RobotConn state snapshots."""
        for rid, r in self.robots.items():
            conn = self._conns.get(rid)
            if conn is None:
                continue
            s = conn.state.snapshot()

            r.x     = s.get('x',       r.x)
            r.y     = s.get('y',       r.y)
            r.theta = s.get('theta',   r.theta)
            r.battery = s.get('battery', r.battery)
            r.last_seen = s.get('last_seen', r.last_seen)

            connected = s.get('connected', False)
            ts = s.get('task_status', 0)
            nav = r.nav

            if not connected:
                r.status = OFFLINE
                r.nav    = 'idle'
            elif ts in (TASK_FINISHED, TASK_FAILED):
                # Robot finished its motion — mark idle
                if ts == TASK_FAILED and r.status not in (IDLE, CHARGING):
                    r.status = ERROR
                r.nav = 'idle'
                # Don't change goal here — dispatcher reads arrived() and advances state
            elif nav == 'moving':
                # Maintain high-level status while moving (set by dispatcher)
                pass
            else:
                if r.status not in (ERROR, CHARGING):
                    r.status = IDLE

    # ── Extra commands (used by Calibration page / RoboShop bridge) ───────────

    def relocalize(self, robot_id: str, x: float, y: float, theta: float) -> bool:
        conn = self._conns.get(robot_id)
        if conn is None:
            return False
        return conn.relocalize(x, y, theta)

    def set_do(self, robot_id: str, do_id: int, status: bool) -> bool:
        conn = self._conns.get(robot_id)
        if conn is None:
            return False
        return conn.set_do(do_id, status)

    def laser(self, robot_id: str) -> dict:
        """World-frame laser scan pulled by the poll thread (~2 Hz). Served via
        GET /robots/<id>/laser. Beams are [x, y] metres in the MAP frame per the
        protocol PDF (p.24) — drawn directly by the frontend with no transform."""
        conn = self._conns.get(robot_id)
        if conn is None:
            return {"beams": [], "ts": 0.0}
        s = conn.state.snapshot()
        return {"beams": s.get("laser_beams", []), "ts": s.get("laser_ts", 0.0)}

    def raw_state(self, robot_id: str) -> dict:
        """Rich per-tick fields straight from the RobotConn poll thread snapshot.
        confidence / blocked / lift DI/DO are opportunistic — they are only
        populated if the SEER replies actually carry them (see robot_conn)."""
        conn = self._conns.get(robot_id)
        if conn is None:
            return {}
        s = conn.state.snapshot()
        return {
            "connected": s.get("connected", False),
            "task_status": s.get("task_status", 0),
            "target_id": s.get("target_id", ""),
            "vx": s.get("vx"), "vy": s.get("vy"), "w": s.get("w"),
            "confidence": s.get("confidence"),
            "blocked": s.get("blocked", False),
            "last_seen": s.get("last_seen", time.time()),
        }

    # ── Recovery signals (real HW) ────────────────────────────────────────
    def nav_failed(self, robot_id: str) -> bool:
        return self.raw_state(robot_id).get("task_status") == TASK_FAILED

    def healthy(self, robot_id: str) -> bool:
        rs = self.raw_state(robot_id)
        return bool(rs.get("connected")) and \
            (time.time() - rs.get("last_seen", 0.0)) < config.ROBOT_STALE_S
