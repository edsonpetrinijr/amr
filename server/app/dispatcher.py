"""
Fleet dispatcher — single asyncio task; the conflict-prevention core.

Guarantees:
  - One task per pickup station at a time (station lock).
  - One task per robot at a time (Robot.current_task exclusive).
  - Best-idle-robot assignment by Euclidean distance + battery penalty.
  - Auto-route low-battery idle robots to the nearest base/charger.
  - Callbutton press events are coalesced: duplicate press while station is
    already being served is silently dropped.

The dispatcher speaks only to the Provider interface — it never touches
sockets directly. Swap SimProvider for SeerProvider (Phase 3) with no
changes here.
"""
from __future__ import annotations

import asyncio
import logging
import math
import threading
import time
import uuid
from typing import Optional, Callable, Awaitable

from . import config
from . import db
from .config import BATTERY_LOW_THRESHOLD
from .models import (
    Robot, Station, Task,
    IDLE, ENROUTE_PICKUP, AT_PICKUP, ENROUTE_DROP, RETURNING, CHARGING, ERROR, OFFLINE,
    T_PENDING, T_ASSIGNED, T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP, T_DONE,
    T_CANCELLED, T_FAILED, T_RECOVERING,
    CB_IDLE, CB_READY, CB_CALLED, CB_SERVED,
    task_update_msg, callbutton_msg, alarm_msg,
)
from .provider import Provider

log = logging.getLogger(__name__)

TICK_INTERVAL = 1.0 / config.TICK_HZ


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class Dispatcher:
    def __init__(self, provider: Provider) -> None:
        self.provider = provider
        self.stations: dict[str, Station] = self._load_stations()

        # Active tasks: task_id → Task
        self._tasks: dict[str, Task] = {}
        # Station lock: station_id → task_id currently being served
        self._station_lock: dict[str, str] = {}

        # Recovery state: robot_id → monotonic-wall time until which the robot
        # must not be reassigned to the task it just failed.
        self._cooldown: dict[str, float] = {}
        # Robots we've already raised an offline alarm for (one per transition).
        self._offline_alarmed: set[str] = set()
        # Localization-recovery incident latch: robot_id → active incident_id.
        # While a robot stays in one localization incident we emit the actionable
        # relocalize-assist alarm exactly once; the latch clears when the robot
        # returns to a healthy, confident, OK-localization state.
        self._loc_incidents: dict[str, str] = {}

        # Optional soak-run telemetry state machine (owns cycle_id/step).
        self.soak = None
        if config.SOAK_MODE:
            from .soak import SoakRunner
            self.soak = SoakRunner(provider, self.stations)
            log.info("dispatcher: SOAK_MODE on — soak robot=%s", self.soak.robot_id)

        # Broadcast callback set by the WS layer
        self._broadcast: Optional[Callable[[dict], Awaitable[None]]] = None

        # Software STOP-ALL gate. When True, _assign_pending early-returns so no
        # new auto-assignment happens until resume(). This is a SOFTWARE stop,
        # NOT a substitute for a hardware E-stop.
        self._halted = False

        self._running = False

        # ── Continuous jog (WASD streaming) ───────────────────────────────────
        # robot_id → (vx, vy, w, expiry_monotonic). A background thread resends
        # each target to the robot at JOG_RESEND_INTERVAL_S (the SEER velocity
        # watchdog needs continuous commands) and auto-stops once expiry passes.
        self._jog_targets: dict[str, tuple[float, float, float, float]] = {}
        self._jog_lock = threading.Lock()
        self._jog_thread: Optional[threading.Thread] = None
        self._jog_thread_stop = threading.Event()

        # ── Callbutton 2-press transport ──────────────────────────────────────
        # First press records an origin; the next press on a DIFFERENT callbutton
        # is the destination → a transport task is created. None when idle.
        self._pending_origin: Optional[str] = None
        self._pending_origin_ts: float = 0.0

        # Event loop reference — set when run() starts so cross-thread callers
        # (Flask request handlers) can schedule emits safely via
        # asyncio.run_coroutine_threadsafe instead of asyncio.ensure_future.
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _load_stations(self) -> dict[str, Station]:
        stations = {}
        for s in config.STATIONS:
            stations[s["id"]] = Station(
                id=s["id"],
                type=s["type"],
                label=s["label"],
                x=s["x"],
                y=s["y"],
                seer_lm=s.get("seer_lm"),
                ap_id=s.get("ap_id"),
                opcua_node=s.get("opcua_node"),
                opcua_ret=s.get("opcua_ret"),
            )
        return stations

    def reload_stations(self) -> None:
        """Rebuild self.stations from config.STATIONS after a config edit,
        PRESERVING per-station runtime callbutton state (cb_state, cb_dir) for
        stations that still exist. Tasks/locks are untouched."""
        rebuilt = self._load_stations()
        for sid, st in rebuilt.items():
            prev = self.stations.get(sid)
            if prev is not None:
                st.cb_state = prev.cb_state
                st.cb_dir = prev.cb_dir
        self.stations = rebuilt

    def set_broadcast(self, fn: Callable[[dict], Awaitable[None]]) -> None:
        self._broadcast = fn

    # ── Public API ────────────────────────────────────────────────────────────

    def create_task(self, pickup: str, dropoff: str) -> Task | None:
        """Create and queue a task. Returns None if pickup is already locked."""
        if pickup not in self.stations or dropoff not in self.stations:
            log.warning("create_task: unknown station pickup=%s dropoff=%s", pickup, dropoff)
            return None
        if pickup in self._station_lock:
            log.info("create_task: station %s already locked — ignoring duplicate", pickup)
            return None
        task = Task.new(pickup=pickup, dropoff=dropoff)
        self._tasks[task.id] = task
        self._station_lock[pickup] = task.id
        db.log_task_event(task, "created")
        log.info("task created: %s %s→%s", task.id, pickup, dropoff)
        return task

    def button_pressed(self, station_id: str, direction: str = "fwd") -> Task | None:
        """Callbutton pressed (physical or simulated). 2-press transport model:
        the FIRST press records an origin (pickup); the next press on a DIFFERENT
        callbutton is the destination (dropoff) → a transport task is created and
        a robot is dispatched (origin LM → destination LM). Action Points were
        removed; `direction` is accepted for OPC-UA compatibility but ignored.
        Returns the created Task on the second press, else None."""
        station = self.stations.get(station_id)
        if not station or station.type != "callbutton":
            return None

        now = time.time()

        # Drop a stale origin so it never lingers forever.
        if self._pending_origin and (now - self._pending_origin_ts) > config.CALLBUTTON_ORIGIN_TIMEOUT_S:
            self._clear_pending_origin()

        # Pressing the SAME button that is the pending origin → cancel (toggle).
        if self._pending_origin == station_id:
            self._clear_pending_origin()
            log.info("button_pressed: origem %s cancelada", station_id)
            return None

        # No pending origin → this press IS the origin (await destination).
        if not self._pending_origin:
            self._pending_origin = station_id
            self._pending_origin_ts = now
            station.cb_state = CB_READY
            station.cb_dir = None
            self._schedule_emit(callbutton_msg(station))
            log.info("button_pressed: origem=%s (aguardando destino)", station_id)
            return None

        # Have an origin + a different destination → create the transport.
        origin_id = self._pending_origin
        self._clear_pending_origin(emit=False)
        task = self.create_task(pickup=origin_id, dropoff=station_id)
        if task:
            for sid in (origin_id, station_id):
                st = self.stations.get(sid)
                if st:
                    st.cb_state = CB_CALLED
                    st.cb_dir = None
                    self._schedule_emit(callbutton_msg(st))
            log.info("button_pressed: transporte %s→%s — task %s",
                     origin_id, station_id, task.id)
        else:
            # Origin locked/invalid — reset both so the operator can retry.
            for sid in (origin_id, station_id):
                st = self.stations.get(sid)
                if st:
                    st.cb_state = CB_IDLE
                    st.cb_dir = None
                    self._schedule_emit(callbutton_msg(st))
            log.info("button_pressed: transporte %s→%s recusado (origem ocupada?)",
                     origin_id, station_id)
        return task

    @property
    def pending_origin(self) -> Optional[str]:
        """Station id of a callbutton press awaiting its destination, or None."""
        return self._pending_origin

    def _clear_pending_origin(self, emit: bool = True) -> None:
        """Reset the pending origin station to idle (best-effort emit)."""
        sid = self._pending_origin
        self._pending_origin = None
        self._pending_origin_ts = 0.0
        if sid:
            st = self.stations.get(sid)
            if st and st.cb_state == CB_READY:
                st.cb_state = CB_IDLE
                st.cb_dir = None
                if emit:
                    self._schedule_emit(callbutton_msg(st))

    def reset_pair(self, station_id: str) -> bool:
        """Clear any pending origin and cancel an active transport touching this
        station. (No more supplier/consumer pairs — kept for the /reset route.)"""
        self._clear_pending_origin()
        cancelled = False
        for task in list(self._tasks.values()):
            if task.state in (T_DONE, T_CANCELLED, T_FAILED):
                continue
            if station_id in (task.pickup, task.dropoff):
                self.cancel_task(task.id)
                st = self.stations.get(station_id)
                if st:
                    st.cb_state = CB_IDLE
                    st.cb_dir = None
                    self._schedule_emit(callbutton_msg(st))
                cancelled = True
        log.info("reset_pair: %s resetado (cancelled=%s)", station_id, cancelled)
        return True

    def callbutton_pressed(self, station_id: str) -> Task | None:
        """Simulate/forward a callbutton press (used by POST /callbutton/<id>)."""
        return self.button_pressed(station_id)

    def cancel_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.state in (T_DONE, T_CANCELLED, T_FAILED):
            return False
        if task.robot:
            self.provider.stop(task.robot)
            robot = self.provider.robots.get(task.robot)
            if robot:
                robot.status = IDLE
                robot.current_task = None
        self._release_task(task, T_CANCELLED)
        return True

    def all_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    def active_tasks(self) -> list[Task]:
        done = (T_DONE, T_CANCELLED, T_FAILED)
        return [t for t in self._tasks.values() if t.state not in done]

    # ── Operator controls (manual jog / software STOP-ALL) ────────────────────

    @property
    def halted(self) -> bool:
        return self._halted

    def jog(self, robot_id: str, vx: float, vy: float, w: float,
            duration: Optional[float] = None) -> tuple[int, dict]:
        """Manual operator jog (continuous/WASD). Returns (http_status, payload).

        SAFETY gates (fail closed):
          • unknown robot                → 404
          • robot has an active task     → 409 (operator must cancel first)
          • robot unhealthy/offline      → 409 (reuse recovery healthy() check)
        vx/vy/w are clamped to the JOG_MAX_* envelope. The SEER robot has a
        velocity watchdog, so a single command barely moves it — instead this
        registers a CONTINUOUS target that a background thread resends every
        JOG_RESEND_INTERVAL_S. The target auto-expires (and the robot stops)
        JOG_KEEPALIVE_S after the last refresh, or after `duration` seconds if
        given. The frontend re-POSTs while a WASD key is held. Zero velocity
        clears the target (immediate stop). Allowed even while STOP-ALL is
        engaged so an operator can recover the fleet.
        """
        robot = self.provider.robots.get(robot_id)
        if robot is None:
            return 404, {"error": f"unknown robot '{robot_id}'"}
        if robot.current_task:
            return 409, {"error": "robot has an active task — cancel it before manual jog",
                         "robot_id": robot_id, "current_task": robot.current_task}
        if not self._robot_healthy(robot):
            return 409, {"error": "robot unhealthy/offline — refusing manual jog",
                         "robot_id": robot_id}

        cvx = _clamp(vx, -config.JOG_MAX_VX, config.JOG_MAX_VX)
        cvy = _clamp(vy, -config.JOG_MAX_VY, config.JOG_MAX_VY)
        cw  = _clamp(w,  -config.JOG_MAX_W,  config.JOG_MAX_W)
        dur = _clamp(duration, 0.0, config.JOG_MAX_DURATION_S) if duration is not None else None

        moving = bool(cvx or cvy or cw)
        if not moving:
            # Zero velocity == stop: clear the streaming target and halt now.
            self._jog_stop(robot_id)
            return 200, {
                "ok": True, "robot_id": robot_id,
                "vx": 0.0, "vy": 0.0, "w": 0.0, "duration": dur,
                "clamped": (cvx != vx or cvy != vy or cw != w),
                "halted": self._halted,
            }

        window = dur if (dur and dur > 0) else config.JOG_KEEPALIVE_S
        expiry = time.monotonic() + window
        with self._jog_lock:
            self._jog_targets[robot_id] = (cvx, cvy, cw, expiry)
        self._ensure_jog_thread()

        # Fire one immediately so motion starts without waiting for the resend tick.
        ok = False
        send = getattr(self.provider, "send_velocity", None)
        if callable(send):
            ok = bool(send(robot_id, cvx, cvy, cw))

        return 200, {
            "ok": ok, "robot_id": robot_id,
            "vx": cvx, "vy": cvy, "w": cw, "duration": dur,
            "clamped": (cvx != vx or cvy != vy or cw != w),
            "halted": self._halted,
        }

    def jog_stop(self, robot_id: str) -> tuple[int, dict]:
        """Stop a continuous jog immediately (POST /jog/stop)."""
        if robot_id not in self.provider.robots:
            return 404, {"error": f"unknown robot '{robot_id}'"}
        self._jog_stop(robot_id)
        return 200, {"ok": True, "robot_id": robot_id}

    def _ensure_jog_thread(self) -> None:
        """Lazily start the background velocity-resend loop (idempotent)."""
        if self._jog_thread is not None and self._jog_thread.is_alive():
            return
        self._jog_thread_stop.clear()
        self._jog_thread = threading.Thread(
            target=self._jog_resend_loop, daemon=True, name="jog-resend")
        self._jog_thread.start()

    def _jog_resend_loop(self) -> None:
        """Resend active jog targets to the robot continuously (SEER watchdog),
        and auto-stop any target that has expired. Exits when no targets remain."""
        while not self._jog_thread_stop.is_set():
            now = time.monotonic()
            expired: list[str] = []
            active: list[tuple[str, float, float, float]] = []
            with self._jog_lock:
                if not self._jog_targets:
                    return  # nothing to do — let the thread die; restarted on next jog
                for rid, (vx, vy, w, exp) in list(self._jog_targets.items()):
                    if now >= exp:
                        expired.append(rid)
                    else:
                        active.append((rid, vx, vy, w))
                for rid in expired:
                    self._jog_targets.pop(rid, None)
            for rid in expired:
                self._jog_stop(rid)
            send = getattr(self.provider, "send_velocity", None)
            if callable(send):
                for rid, vx, vy, w in active:
                    try:
                        send(rid, vx, vy, w)
                    except Exception as exc:  # noqa: BLE001 — keep streaming others
                        log.warning("jog resend failed for %s: %s", rid, exc)
            time.sleep(config.JOG_RESEND_INTERVAL_S)

    def _jog_stop(self, robot_id: str) -> None:
        with self._jog_lock:
            self._jog_targets.pop(robot_id, None)
        try:
            self.provider.stop(robot_id)
        except Exception as exc:  # noqa: BLE001 — a failed auto-stop must not crash the thread
            log.warning("jog stop failed for %s: %s", robot_id, exc)

    def jack(self, robot_id: str, action: str) -> tuple[int, dict]:
        """Raise/lower the jack by PULSING a Digital Output (set true → wait
        JACK_PULSE_S → set false), matching controle_completo_robo.py. The pulse
        runs in a background thread so the HTTP call returns immediately. Returns
        (http_status, payload). No-op (still 200) when the provider has no set_do
        (sim mode)."""
        if action not in ("up", "down"):
            return 400, {"error": "action must be 'up' or 'down'"}
        if robot_id not in self.provider.robots:
            return 404, {"error": f"unknown robot '{robot_id}'"}
        do_id = config.JACK_UP_DO_ID if action == "up" else config.JACK_DOWN_DO_ID
        set_do = getattr(self.provider, "set_do", None)
        if not callable(set_do):
            return 200, {"ok": True, "robot_id": robot_id, "action": action,
                         "note": "no set_do on provider (sim)"}

        def _pulse() -> None:
            try:
                set_do(robot_id, do_id, True)
                time.sleep(config.JACK_PULSE_S)
                set_do(robot_id, do_id, False)
                log.info("jack %s pulse complete (robot=%s do=%d)", action, robot_id, do_id)
            except Exception as exc:  # noqa: BLE001 — pulse runs detached
                log.warning("jack %s failed for %s: %s", action, robot_id, exc)

        threading.Thread(target=_pulse, daemon=True, name=f"jack-{robot_id}").start()
        return 200, {"ok": True, "robot_id": robot_id, "action": action,
                     "do_id": do_id, "pulse_s": config.JACK_PULSE_S}

    def stop_all(self) -> list[Task]:
        """Emergency SOFTWARE stop. NOT a substitute for a hardware E-stop.

        Commands every robot to stop, cancels all active tasks (releasing their
        station locks and setting robots idle), and engages the halted flag so
        auto-assignment is blocked until resume(). Returns the cancelled tasks
        so the caller can broadcast task_update messages.
        """
        self._halted = True
        for robot in self.provider.robots.values():
            try:
                self.provider.stop(robot.id)
            except Exception as exc:  # noqa: BLE001 — stop the rest even if one fails
                log.warning("stop_all: stop failed for %s: %s", robot.id, exc)

        cancelled: list[Task] = []
        for task in self.active_tasks():
            if task.robot:
                robot = self.provider.robots.get(task.robot)
                if robot:
                    robot.status = IDLE
                    robot.current_task = None
            self._release_task(task, T_CANCELLED)
            cancelled.append(task)

        # Any robot left mid-motion (no task) is also parked idle.
        for robot in self.provider.robots.values():
            if robot.status not in (CHARGING, OFFLINE):
                robot.status = IDLE
                robot.current_task = None
        log.critical("STOP-ALL engaged — %d task(s) cancelled (SOFTWARE stop, not E-stop)",
                     len(cancelled))
        return cancelled

    def resume(self) -> None:
        """Clear the STOP-ALL halt so auto-assignment can run again."""
        self._halted = False
        log.info("STOP-ALL cleared — auto-dispatch resumed")

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def run(self) -> None:
        self._loop = asyncio.get_event_loop()
        self._running = True
        log.info("dispatcher started (sim_mode=%s, tick_hz=%s)", config.SIM_MODE, config.TICK_HZ)
        last = time.monotonic()
        while self._running:
            now = time.monotonic()
            dt = now - last
            last = now

            self.provider.tick(dt)
            if self.soak is not None:
                self.soak.tick(dt)
            self._settle_returning()
            self._assign_pending()
            self._advance_active(dt)
            self._check_recovery(dt)
            self._check_battery()

            await asyncio.sleep(TICK_INTERVAL)

    def stop(self) -> None:
        self._running = False

    # ── Assignment ────────────────────────────────────────────────────────────

    def _assign_pending(self) -> None:
        if self._halted:
            return  # STOP-ALL engaged — no new auto-assignment until resume()
        for task in list(self._tasks.values()):
            if task.state != T_PENDING:
                continue
            robot = self._best_robot(task)
            if robot is None:
                continue
            # Assign
            task.state = T_ASSIGNED
            task.robot = robot.id
            task.assigned_at = time.time()
            robot.current_task = task.id
            robot.status = ENROUTE_PICKUP
            pickup = self.stations[task.pickup]
            self.provider.goto(robot.id, pickup.x, pickup.y, task.pickup)
            task.state = T_ENROUTE_PICKUP
            # Initialize stuck-detection progress trackers from the robot's pose.
            task.last_x, task.last_y = robot.x, robot.y
            task.last_progress_at = time.time()
            db.log_task_event(task, "assigned")
            log.info("assigned %s → robot %s pickup=%s drop=%s", task.id, robot.id, task.pickup, task.dropoff)
            self._schedule_emit(task_update_msg(task, "assigned"))

    def _best_robot(self, task: Task) -> Optional[Robot]:
        pickup = self.stations.get(task.pickup)
        if not pickup:
            return None
        best: Optional[Robot] = None
        best_cost = float("inf")
        for robot in self.provider.robots.values():
            if robot.status not in (IDLE,):
                continue
            if robot.current_task:
                continue
            if self.soak is not None and robot.id == self.soak.robot_id:
                continue  # reserved for the soak loop — never hand it a task
            if robot.battery < BATTERY_LOW_THRESHOLD:
                continue  # reserve for charging, handled separately
            # Recovery filters: don't bounce the task back to the robot that just
            # failed it (cooldown), and never assign to an unhealthy robot.
            if robot.id == task.last_robot and time.time() < self._cooldown.get(robot.id, 0.0):
                continue
            if not self._robot_healthy(robot):
                continue
            dist = math.hypot(robot.x - pickup.x, robot.y - pickup.y)
            cost = dist + max(0.0, 80.0 - robot.battery) * 0.5
            if cost < best_cost:
                best_cost = cost
                best = robot
        return best

    # ── Advance active tasks ───────────────────────────────────────────────────

    def _advance_active(self, dt: float) -> None:
        for task in list(self._tasks.values()):
            if task.state not in (T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP):
                continue
            robot = self.provider.robots.get(task.robot or "")
            if not robot:
                continue

            # A failed nav must NOT be read as an arrival. Recover first.
            if self.provider.nav_failed(robot.id):
                self._enter_recovery(task, robot, "nav_failed")
                continue

            if task.state == T_ENROUTE_PICKUP:
                if self.provider.arrived(robot.id):
                    task.state = T_AT_PICKUP
                    robot.status = AT_PICKUP
                    log.info("%s at pickup %s", task.id, task.pickup)
                    self._schedule_emit(task_update_msg(task, "at_pickup"))
                    # Immediately head to dropoff
                    dropoff = self.stations[task.dropoff]
                    self.provider.goto(robot.id, dropoff.x, dropoff.y, task.dropoff)
                    task.state = T_ENROUTE_DROP
                    robot.status = ENROUTE_DROP
                    self._schedule_emit(task_update_msg(task, "enroute_drop"))

            elif task.state == T_ENROUTE_DROP:
                if self.provider.arrived(robot.id):
                    task.state = T_DONE
                    task.done_at = time.time()
                    robot.status = IDLE
                    robot.current_task = None
                    log.info("%s done", task.id)
                    self._schedule_emit(task_update_msg(task, "done"))
                    self._release_task(task, T_DONE)
                    self._reset_pair_stations(task.pickup, task.dropoff)
                    # Return robot to base
                    self._return_to_base(robot)

    def _reset_pair_stations(self, pickup_id: str, dropoff_id: str) -> None:
        for sid in (pickup_id, dropoff_id):
            st = self.stations.get(sid)
            if st:
                st.cb_state = CB_IDLE
                st.cb_dir = None
                self._schedule_emit(callbutton_msg(st))

    def _return_to_base(self, robot: Robot) -> None:
        base = next((s for s in self.stations.values() if s.type == "base"), None)
        if base:
            robot.status = RETURNING
            self.provider.goto(robot.id, base.x, base.y, base.id)

    def _settle_returning(self) -> None:
        """A robot that has finished returning to base becomes available again.
        Without this a RETURNING robot never flips back to IDLE, so it would
        accept no further tasks after its first delivery."""
        for robot in self.provider.robots.values():
            if robot.status == RETURNING and not robot.current_task \
                    and self.provider.arrived(robot.id):
                robot.status = IDLE

    # ── Failure recovery ──────────────────────────────────────────────────────

    def _robot_healthy(self, robot: Robot) -> bool:
        try:
            return bool(self.provider.healthy(robot.id))
        except Exception:
            return True  # provider can't tell → assume healthy, don't block dispatch

    _RECOVERABLE = (T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP)

    def _check_recovery(self, dt: float) -> None:
        """Evaluate failure signals on every in-flight task's assigned robot and
        trigger recovery on the first one that fires."""
        now = time.time()

        # Bring offline robots back into service once they're healthy again
        # (real HW: SeerProvider.tick also restores status; this covers sim).
        for robot in self.provider.robots.values():
            if robot.status == OFFLINE and not robot.current_task and self._robot_healthy(robot):
                robot.status = IDLE
                self._offline_alarmed.discard(robot.id)
            # Clear the localization-incident latch once the robot recovers, so a
            # future loss fires a fresh alarm with a new incident_id.
            if robot.id in self._loc_incidents and self._loc_recovered(robot.id):
                self._loc_incidents.pop(robot.id, None)

        for task in list(self._tasks.values()):
            if task.state not in self._RECOVERABLE:
                continue
            robot = self.provider.robots.get(task.robot or "")
            if not robot:
                continue

            # 1) Robot unhealthy / disconnected.
            if not self._robot_healthy(robot):
                if robot.id not in self._offline_alarmed:
                    self._offline_alarmed.add(robot.id)
                    self._schedule_emit(
                        alarm_msg("warn", f"robot {robot.id} offline", robot.id))
                self._enter_recovery(task, robot, "robot_offline")
                continue

            # Robot is healthy again → allow future offline alarms.
            self._offline_alarmed.discard(robot.id)

            # 2) Navigation failed.
            if self.provider.nav_failed(robot.id):
                self._enter_recovery(task, robot, "nav_failed")
                continue

            # 3) Stuck — no progress for too long (skip if it just arrived).
            if not self.provider.arrived(robot.id):
                moved = math.hypot(robot.x - (task.last_x or robot.x),
                                   robot.y - (task.last_y or robot.y))
                if moved >= config.PROGRESS_EPS:
                    task.last_x, task.last_y = robot.x, robot.y
                    task.last_progress_at = now
                elif task.last_progress_at is not None and \
                        (now - task.last_progress_at) > config.STUCK_TIMEOUT_S:
                    self._enter_recovery(task, robot, "stuck")
                    continue

            # 4) Battery critical.
            if robot.battery < config.BATTERY_CRITICAL:
                self._enter_recovery(task, robot, "battery")
                continue

    def _enter_recovery(self, task: Task, robot: Robot, reason: str) -> None:
        """Abort the task on this robot and either re-queue it or fail it."""
        # NEVER command an offline robot — but a stop on a healthy one is safe.
        if reason != "robot_offline":
            self.provider.stop(robot.id)
        robot.current_task = None
        robot.status = OFFLINE if reason == "robot_offline" else IDLE
        self._cooldown[robot.id] = time.time() + config.ROBOT_COOLDOWN_S
        task.fail_reason = reason

        self._schedule_emit(task_update_msg(task, "recovering"))
        self._schedule_emit(
            alarm_msg("warn", f"{task.id} recovering: {reason}", robot.id))
        self._emit_loc_incident_alarm(task, robot, reason)
        log.warning("recovery: %s on robot %s — reason=%s", task.id, robot.id, reason)

        if task.retries < config.MAX_TASK_RETRIES:
            task.retries += 1
            task.last_robot = robot.id
            # Re-queue. Station lock is keyed on pickup and stays held until a
            # terminal state, so the task keeps its slot.
            task.robot = None
            task.assigned_at = None
            task.last_x = task.last_y = None
            task.last_progress_at = None
            task.state = T_PENDING
            self._schedule_emit(task_update_msg(task, "reassigning"))
            log.info("recovery: %s re-queued (retry %d/%d)",
                     task.id, task.retries, config.MAX_TASK_RETRIES)
        else:
            self._release_task(task, T_FAILED)
            self._schedule_emit(task_update_msg(task, "failed"))
            self._schedule_emit(
                alarm_msg("critical",
                          f"{task.id} failed after {task.retries} retries: {reason}",
                          robot.id))
            log.error("recovery: %s FAILED after %d retries — reason=%s",
                      task.id, task.retries, reason)

    # ── Localization-recovery alarm (actionable, latched per incident) ─────────

    # Recovery reasons that are localization-related and warrant a relocalize
    # assist alarm. robot_offline / battery are deliberately excluded.
    _LOC_ALARM_REASONS = {"nav_failed": "NAV_FAILED", "stuck": "STUCK"}

    def _raw_state_safe(self, robot_id: str) -> dict:
        get_raw = getattr(self.provider, "raw_state", None)
        if get_raw is None:
            return {}
        try:
            return get_raw(robot_id) or {}
        except Exception:
            return {}

    def _loc_recovered(self, robot_id: str) -> bool:
        """True when the robot is back to a healthy, OK-localization, confident
        navigating state — the signal to clear its incident latch."""
        rs = self._raw_state_safe(robot_id)
        if not rs.get("connected", True):
            return False
        if rs.get("loc_mode") not in (None, "ok"):
            return False
        conf = rs.get("confidence")
        if conf is not None and conf < config.LOC_LOST_CONFIDENCE_THRESHOLD:
            return False
        if rs.get("task_status") == 4:        # still nav-failed
            return False
        return True

    def _emit_loc_incident_alarm(self, task: Task, robot: Robot, reason: str) -> None:
        """Emit ONE structured, actionable alarm when a robot enters recovery for
        a localization-related reason. Latched per incident: while the robot stays
        in the same incident we do not re-emit; the latch clears in _check_recovery
        once the robot recovers (then a future loss gets a NEW incident_id)."""
        enum_reason = self._LOC_ALARM_REASONS.get(reason)
        if enum_reason is None:
            return                            # not a localization recovery
        if robot.id in self._loc_incidents:
            return                            # already alarmed this incident

        rs = self._raw_state_safe(robot.id)
        conf = rs.get("confidence")
        # A stuck robot that is also low-confidence/lost is best surfaced as a
        # localization confidence problem rather than a generic stall.
        if reason == "stuck" and (
            (conf is not None and conf < config.LOC_LOST_CONFIDENCE_THRESHOLD)
            or rs.get("loc_mode") in ("lost", "mislocalized")
        ):
            enum_reason = "LOW_CONFIDENCE"

        incident_id = f"loc-{uuid.uuid4().hex[:12]}"
        self._loc_incidents[robot.id] = incident_id
        payload = {
            "robot_id": robot.id,
            "task_id": task.id,
            "reason": enum_reason,
            "last_pose": {
                "x": rs.get("x"),
                "y": rs.get("y"),
                "theta": rs.get("theta"),
                "confidence": conf,
            },
            "action": "RELOCALIZE_ASSIST_V1",
            "suggestions_url": f"/api/relocalize/suggestions?robot_id={robot.id}",
            "timestamp": time.time(),
            "incident_id": incident_id,
        }
        self._schedule_emit(alarm_msg(
            "warn",
            f"{robot.id} needs relocalization ({enum_reason}) — task {task.id}",
            robot.id,
            payload=payload,
        ))
        log.warning("loc incident %s: robot=%s task=%s reason=%s",
                    incident_id, robot.id, task.id, enum_reason)

    # ── Battery management ────────────────────────────────────────────────────

    def _check_battery(self) -> None:
        for robot in self.provider.robots.values():
            if robot.status != IDLE:
                continue
            if robot.battery < BATTERY_LOW_THRESHOLD and not robot.current_task:
                base = next((s for s in self.stations.values() if s.type == "base"), None)
                if base and not (robot.x == base.x and robot.y == base.y):
                    robot.status = CHARGING
                    self.provider.goto(robot.id, base.x, base.y, base.id)
                    log.info("robot %s low battery (%.0f%%) → routing to base", robot.id, robot.battery)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _release_task(self, task: Task, final_state: str) -> None:
        task.state = final_state
        # Release station lock if this task held it
        held = self._station_lock.get(task.pickup)
        if held == task.id:
            del self._station_lock[task.pickup]
        db.log_task_event(task, final_state)

    def _schedule_emit(self, msg: dict) -> None:
        """Thread-safe emit: works whether called from inside or outside the
        dispatcher's asyncio event loop.

        - Inside the loop  (dispatcher tick thread): asyncio.ensure_future
        - Outside the loop (Flask request threads):  run_coroutine_threadsafe
        """
        loop = self._loop
        if loop is None or not loop.is_running():
            # Test harnesses and early startup paths may call dispatcher logic
            # before the background loop is running; emit sync when possible.
            if self._broadcast and not asyncio.iscoroutinefunction(self._broadcast):
                try:
                    self._broadcast(msg)
                except Exception as exc:
                    log.warning("broadcast error: %s", exc)
            return
        try:
            running = asyncio.get_event_loop()
            same_loop = running is loop and loop.is_running()
        except RuntimeError:
            same_loop = False
        if same_loop:
            asyncio.ensure_future(self._emit(msg), loop=loop)
        else:
            asyncio.run_coroutine_threadsafe(self._emit(msg), loop)

    async def _emit(self, msg: dict) -> None:
        if self._broadcast:
            try:
                import asyncio
                if asyncio.iscoroutinefunction(self._broadcast):
                    await self._broadcast(msg)
                else:
                    self._broadcast(msg)
            except Exception as exc:
                log.warning("broadcast error: %s", exc)
