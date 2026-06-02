"""
SoakRunner — the ONE authoritative state machine for a supervised soak run.

Owns the run's ``cycle_id`` (int, increments per loop) and ``step`` (enum), so
that EVERY per-tick telemetry snapshot and EVERY discrete event can be joined
to the exact cycle + phase. This is the single most important guarantee of the
capture system (per CTO): without it the run is just noise.

Loop:  GOTO_A → LIFT → GOTO_B → LOWER → (cycle_end) → IDLE → repeat.

DATA CAPTURE ONLY. No watchdog / SAFE-HOLD / alerting (out of scope). The runner
only commands the existing Provider (goto / arrived / set_do) and records what
happens — it never touches sockets and adds no control/recovery logic.
"""
from __future__ import annotations

import logging
import math
import statistics
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

from . import config, telemetry
from .provider import Provider
from .seer.protocol import TASK_FAILED

log = logging.getLogger(__name__)

# Step enum
GOTO_A = "GOTO_A"
LIFT   = "LIFT"
GOTO_B = "GOTO_B"
LOWER  = "LOWER"
IDLE   = "IDLE"


@dataclass
class _Cycle:
    """Per-cycle accumulator. Mutated by the dispatcher thread (FSM) and the
    sampler thread (observe); both go through SoakRunner's lock."""
    cycle_id: int
    t_start: float                       # monotonic
    t_start_wall: float
    battery_start: Optional[float] = None
    battery_end: Optional[float] = None
    # phase timestamps (monotonic)
    t_goto_a: Optional[float] = None
    t_arrive_a: Optional[float] = None
    t_depart_a: Optional[float] = None
    t_lift_start: Optional[float] = None
    t_lift_end: Optional[float] = None
    t_goto_b: Optional[float] = None
    t_arrive_b: Optional[float] = None
    t_depart_b: Optional[float] = None
    t_lower_start: Optional[float] = None
    t_lower_end: Optional[float] = None
    t_end: Optional[float] = None
    idle_wait_s: float = 0.0
    # aggregates from the sampler
    distance_m: float = 0.0
    max_pose_jump_m: float = 0.0
    obstacle_stops: int = 0
    nav_failures: int = 0
    relocalizations: int = 0
    conf_at_pick: Optional[float] = None   # min confidence seen during LIFT
    conf_at_drop: Optional[float] = None   # min confidence seen during LOWER
    _last_x: Optional[float] = None
    _last_y: Optional[float] = None
    # stop-position accuracy
    stop_err_a_xy: Optional[float] = None
    stop_err_a_theta: Optional[float] = None
    stop_err_b_xy: Optional[float] = None
    stop_err_b_theta: Optional[float] = None
    # lift verification
    load_present_before: Optional[bool] = None
    load_present_after: Optional[bool] = None
    lift_ok: Optional[bool] = None


def _ang_err(a: float, b: Optional[float]) -> Optional[float]:
    if b is None:
        return None
    d = (a - b + math.pi) % (2 * math.pi) - math.pi
    return abs(d)


class SoakRunner:
    def __init__(self, provider: Provider, stations: dict) -> None:
        self.provider = provider
        self.robot_id = config.SOAK_ROBOT
        self.run_id = config.RUN_ID
        self._a = stations.get(config.SOAK_A_STATION)
        self._b = stations.get(config.SOAK_B_STATION)
        if self._a is None or self._b is None:
            raise ValueError(
                f"SoakRunner: station(s) not found A={config.SOAK_A_STATION} "
                f"B={config.SOAK_B_STATION}"
            )

        self._lock = threading.RLock()
        self.cycle_id = 0
        self.step = IDLE
        self.lift_do = False          # commanded lift output (logical)
        self.lift_di = False          # load-present input (modeled in sim)
        self._cyc: Optional[_Cycle] = None
        self._goal_sent = False
        self._idle_until = 0.0
        self._idle_entered: Optional[float] = None
        self._durations: list[float] = []
        self._prev_duration: Optional[float] = None
        self._stopped = False
        self._started = False

    # ── lifecycle ──────────────────────────────────────────────────────────
    @property
    def running(self) -> bool:
        return self._started and not self._stopped

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._started = True
            telemetry.write_event(self.run_id, self.robot_id, 0, IDLE, "run_start",
                                  detail={"a": self._a.id, "b": self._b.id,
                                          "sample_hz": config.SAMPLE_HZ})
            log.info("soak: run_start robot=%s A=%s B=%s", self.robot_id, self._a.id, self._b.id)
            self._begin_cycle(now=time.monotonic())

    def stop(self) -> None:
        with self._lock:
            if self._stopped:
                return
            self._stopped = True
            telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, self.step,
                                  "run_end", detail={"completed_cycles": len(self._durations)})
            log.info("soak: run_end completed_cycles=%d", len(self._durations))

    # ── authoritative tag + observe (called by sampler thread) ─────────────
    def observe(self, x: float, y: float, battery: Optional[float],
                blocked: bool, confidence: Optional[float]) -> dict:
        """Atomically read the authoritative (cycle_id, step, lift state) AND
        fold this sample into the active cycle's aggregates. Returns the tag so
        the telemetry row and the accumulator can never disagree on cycle/phase."""
        with self._lock:
            cyc = self._cyc
            if cyc is not None:
                if cyc._last_x is not None:
                    jump = math.hypot(x - cyc._last_x, y - cyc._last_y)
                    cyc.distance_m += jump
                    if jump > cyc.max_pose_jump_m:
                        cyc.max_pose_jump_m = jump
                cyc._last_x, cyc._last_y = x, y
                if battery is not None:
                    if cyc.battery_start is None:
                        cyc.battery_start = battery
                    cyc.battery_end = battery
                if confidence is not None:
                    if self.step == LIFT:
                        cyc.conf_at_pick = (confidence if cyc.conf_at_pick is None
                                            else min(cyc.conf_at_pick, confidence))
                    elif self.step == LOWER:
                        cyc.conf_at_drop = (confidence if cyc.conf_at_drop is None
                                            else min(cyc.conf_at_drop, confidence))
            return {
                "cycle_id": self.cycle_id,
                "step": self.step,
                "lift_di": self.lift_di,
                "lift_do": self.lift_do,
            }

    def note_obstacle_stop(self) -> None:
        with self._lock:
            if self._cyc:
                self._cyc.obstacle_stops += 1

    def note_relocalization(self) -> None:
        with self._lock:
            if self._cyc:
                self._cyc.relocalizations += 1

    # ── FSM tick (called by dispatcher thread) ─────────────────────────────
    def tick(self, dt: float) -> None:
        if not self._started or self._stopped:
            return
        with self._lock:
            now = time.monotonic()
            step = self.step
            if step == IDLE:
                if now >= self._idle_until:
                    self._begin_cycle(now)
            elif step == GOTO_A:
                self._tick_goto(now, self._a, GOTO_A)
            elif step == LIFT:
                self._tick_lift(now)
            elif step == GOTO_B:
                self._tick_goto(now, self._b, GOTO_B)
            elif step == LOWER:
                self._tick_lower(now)

    # ── phase handlers ─────────────────────────────────────────────────────
    def _begin_cycle(self, now: float) -> None:
        if config.SOAK_MAX_CYCLES and len(self._durations) >= config.SOAK_MAX_CYCLES:
            self.stop()
            return
        self.cycle_id += 1
        self._cyc = _Cycle(cycle_id=self.cycle_id, t_start=now, t_start_wall=time.time())
        if self._idle_entered is not None:
            self._cyc.idle_wait_s = max(0.0, now - self._idle_entered)
        telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, GOTO_A, "cycle_start")
        # load check before move (mis-pick detection baseline)
        self._cyc.load_present_before = self.lift_di
        self._transition(GOTO_A, now)
        self._cyc.t_goto_a = now

    def _tick_goto(self, now: float, station, step: str) -> None:
        if not self._goal_sent:
            self.provider.goto(self.robot_id, station.x, station.y, station.id)
            self._goal_sent = True
            telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, step,
                                  "nav_goal_sent", target=station.id,
                                  detail={"x": station.x, "y": station.y})
            return
        # nav failure (real HW: task_status == FAILED). Sim never fails.
        raw = self._raw()
        if raw.get("task_status") == TASK_FAILED and self._cyc:
            self._cyc.nav_failures += 1
            telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, step,
                                  "nav_failed", target=station.id)
        if self.provider.arrived(self.robot_id):
            self._on_arrived(now, station, step)

    def _on_arrived(self, now: float, station, step: str) -> None:
        r = self.provider.robots.get(self.robot_id)
        xy_err = th_err = None
        if r is not None:
            xy_err = math.hypot(r.x - station.x, r.y - station.y)
            tgt_theta = config.SOAK_A_THETA if step == GOTO_A else config.SOAK_B_THETA
            th_err = _ang_err(r.theta, tgt_theta)
        telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, step,
                              "nav_arrived", target=station.id,
                              detail={"stop_err_xy": xy_err, "stop_err_theta": th_err})
        self._goal_sent = False
        if step == GOTO_A:
            self._cyc.t_arrive_a = now
            self._cyc.stop_err_a_xy = xy_err
            self._cyc.stop_err_a_theta = th_err
            self._begin_lift(now)
        else:
            self._cyc.t_arrive_b = now
            self._cyc.stop_err_b_xy = xy_err
            self._cyc.stop_err_b_theta = th_err
            self._begin_lower(now)

    def _begin_lift(self, now: float) -> None:
        self._transition(LIFT, now)
        self._cyc.t_lift_start = now
        self.lift_do = True
        self._set_do(True)
        telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, LIFT,
                              "lift_start", target=self._a.id)

    def _tick_lift(self, now: float) -> None:
        if now - self._cyc.t_lift_start >= config.SOAK_LIFT_S:
            # Modeled load-present input: in sim, lifting attaches the load.
            # TODO(real HW): replace with the actual SEER lift DI once wired.
            self.lift_di = True
            self._cyc.t_lift_end = now
            self._cyc.t_depart_a = now
            self._cyc.load_present_after = self.lift_di
            self._cyc.lift_ok = bool(self.lift_di)
            telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, LIFT,
                                  "lift_end", target=self._a.id,
                                  detail={"load_present": self.lift_di, "lift_ok": self._cyc.lift_ok})
            self._transition(GOTO_B, now)
            self._cyc.t_goto_b = now

    def _begin_lower(self, now: float) -> None:
        self._transition(LOWER, now)
        self._cyc.t_lower_start = now
        self.lift_do = False
        self._set_do(False)
        telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, LOWER,
                              "lower_start", target=self._b.id)

    def _tick_lower(self, now: float) -> None:
        if now - self._cyc.t_lower_start >= config.SOAK_LOWER_S:
            self.lift_di = False
            self._cyc.t_lower_end = now
            self._cyc.t_depart_b = now
            telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, LOWER,
                                  "lower_end", target=self._b.id)
            self._end_cycle(now)

    def _end_cycle(self, now: float) -> None:
        c = self._cyc
        c.t_end = now
        duration = now - c.t_start
        delta_prev = (duration - self._prev_duration) if self._prev_duration is not None else None
        self._durations.append(duration)
        mean = statistics.fmean(self._durations)
        stddev = statistics.pstdev(self._durations) if len(self._durations) > 1 else 0.0
        self._prev_duration = duration

        def span(a, b):
            return (b - a) if (a is not None and b is not None) else None

        row = {
            "run_id": self.run_id, "robot_id": self.robot_id, "cycle_id": c.cycle_id,
            "t_start": c.t_start_wall, "t_end": time.time(), "duration_s": duration,
            "goto_a_s": span(c.t_goto_a, c.t_arrive_a),
            "time_to_lift_s": span(c.t_lift_start, c.t_lift_end),
            "goto_b_s": span(c.t_goto_b, c.t_arrive_b),
            "time_to_lower_s": span(c.t_lower_start, c.t_lower_end),
            "dwell_a_s": span(c.t_arrive_a, c.t_depart_a),
            "dwell_b_s": span(c.t_arrive_b, c.t_depart_b),
            "idle_wait_s": c.idle_wait_s,
            "distance_m": c.distance_m,
            "obstacle_stops": c.obstacle_stops,
            "nav_failures": c.nav_failures,
            "relocalizations": c.relocalizations,
            "max_pose_jump_m": c.max_pose_jump_m,
            "battery_start": c.battery_start,
            "battery_end": c.battery_end,
            "battery_delta": (c.battery_end - c.battery_start)
                             if (c.battery_start is not None and c.battery_end is not None) else None,
            "stop_err_a_xy": c.stop_err_a_xy, "stop_err_a_theta": c.stop_err_a_theta,
            "stop_err_b_xy": c.stop_err_b_xy, "stop_err_b_theta": c.stop_err_b_theta,
            "conf_at_pick": c.conf_at_pick, "conf_at_drop": c.conf_at_drop,
            "lift_ok": (1 if c.lift_ok else 0) if c.lift_ok is not None else None,
            "cycle_time_delta_vs_prev_s": delta_prev,
            "duration_mean_s": mean, "duration_stddev_s": stddev,
        }
        telemetry.write_cycle(row)
        telemetry.write_event(self.run_id, self.robot_id, c.cycle_id, IDLE, "cycle_end",
                              detail={"duration_s": duration, "lift_ok": c.lift_ok,
                                      "distance_m": c.distance_m})
        log.info("soak: cycle %d done dur=%.2fs dist=%.2f lift_ok=%s",
                 c.cycle_id, duration, c.distance_m, c.lift_ok)

        # idle gap before next cycle, then loop
        self._idle_until = now + config.SOAK_IDLE_S
        self._idle_entered = now
        self._cyc = None
        self._transition(IDLE, now)
        if config.SOAK_MAX_CYCLES and len(self._durations) >= config.SOAK_MAX_CYCLES:
            self.stop()

    # ── helpers ────────────────────────────────────────────────────────────
    def _transition(self, new_step: str, now: float) -> None:
        old = self.step
        if old == new_step:
            return
        self.step = new_step
        telemetry.write_event(self.run_id, self.robot_id, self.cycle_id, new_step,
                              "state_transition", detail={"from": old, "to": new_step})

    def _set_do(self, status: bool) -> None:
        set_do = getattr(self.provider, "set_do", None)
        if callable(set_do):
            try:
                set_do(self.robot_id, config.SOAK_LIFT_DO, status)
            except Exception as exc:   # never let capture break the run
                log.debug("soak: set_do failed: %s", exc)

    def _raw(self) -> dict:
        raw = getattr(self.provider, "raw_state", None)
        return raw(self.robot_id) if callable(raw) else {}
