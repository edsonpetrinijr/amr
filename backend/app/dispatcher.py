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
            )
        return stations

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
        """Botão físico apertado. Só despacha quando AMBOS os lados confirmam a MESMA direção."""
        station = self.stations.get(station_id)
        if not station:
            return None

        pair = self._find_pair(station_id)
        if not pair:
            return None

        supplier = self.stations[pair["supplier"]]
        consumer = self.stations[pair["consumer"]]

        # Ignora se já tem task em andamento nesse par
        if supplier.cb_state == CB_CALLED or consumer.cb_state == CB_CALLED:
            log.info("button_pressed: task em andamento — ignorando %s", station_id)
            return None

        # Se estava pronto para outra direção, reseta
        if station.cb_state == CB_READY and station.cb_dir != direction:
            station.cb_state = CB_IDLE
            station.cb_dir = None

        station.cb_state = CB_READY
        station.cb_dir = direction
        asyncio.ensure_future(self._emit(callbutton_msg(station)))
        log.info("button_pressed: %s pronto dir=%s (aguardando par)", station_id, direction)

        partner = consumer if station_id == pair["supplier"] else supplier
        if partner.cb_state == CB_READY and partner.cb_dir == direction:
            supplier.cb_state = CB_CALLED
            supplier.cb_dir = direction
            consumer.cb_state = CB_CALLED
            consumer.cb_dir = direction
            asyncio.ensure_future(self._emit(callbutton_msg(supplier)))
            asyncio.ensure_future(self._emit(callbutton_msg(consumer)))
            # fwd: supplier→consumer / ret: consumer→supplier
            if direction == "fwd":
                task = self.create_task(pickup=pair["supplier"], dropoff=pair["consumer"])
            else:
                task = self.create_task(pickup=pair["consumer"], dropoff=pair["supplier"])
            log.info("button_pressed: ambos prontos dir=%s — task %s", direction, task.id if task else "None")
            return task

        return None

    def reset_pair(self, station_id: str) -> bool:
        """Reseta o par inteiro para idle e cancela task pendente."""
        pair = self._find_pair(station_id)
        if not pair:
            return False
        self._reset_pair_stations(pair["supplier"], pair["consumer"])
        # Cancela task ativa do par
        for task in list(self._tasks.values()):
            if task.state not in (T_DONE, T_CANCELLED, T_FAILED):
                if (task.pickup == pair["supplier"] and task.dropoff == pair["consumer"]) or \
                   (task.pickup == pair["consumer"] and task.dropoff == pair["supplier"]):
                    self.cancel_task(task.id)
        log.info("reset_pair: %s resetado", station_id)
        return True

    def _find_pair(self, station_id: str) -> dict | None:
        """Retorna o par (supplier, consumer) ao qual esta estação pertence."""
        for p in config.PAIRS:
            if station_id in (p["supplier"], p["consumer"]):
                return p
        return None

    def callbutton_pressed(self, station_id: str) -> Task | None:
        """Mantido para compatibilidade — usa o novo handshake."""
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
        """Manual operator jog. Returns (http_status, payload).

        SAFETY gates (fail closed):
          • unknown robot                → 404
          • robot has an active task     → 409 (operator must cancel first)
          • robot unhealthy/offline      → 409 (reuse recovery healthy() check)
        vx/vy/w are clamped to the JOG_MAX_* envelope before being sent. With a
        duration the robot auto-stops after that many seconds; without one the
        command is single-shot (operator must send zeros or call stop). Allowed
        even while STOP-ALL is engaged so an operator can recover the fleet.
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

        ok = False
        send = getattr(self.provider, "send_velocity", None)
        if callable(send):
            ok = bool(send(robot_id, cvx, cvy, cw))

        # Auto-stop after the requested window (only if actually moving).
        if dur and (cvx or cvy or cw):
            timer = threading.Timer(dur, self._jog_stop, args=(robot_id,))
            timer.daemon = True
            timer.start()

        return 200, {
            "ok": ok, "robot_id": robot_id,
            "vx": cvx, "vy": cvy, "w": cw, "duration": dur,
            "clamped": (cvx != vx or cvy != vy or cw != w),
            "halted": self._halted,
        }

    def _jog_stop(self, robot_id: str) -> None:
        try:
            self.provider.stop(robot_id)
        except Exception as exc:  # noqa: BLE001 — a failed auto-stop must not crash the timer thread
            log.warning("jog auto-stop failed for %s: %s", robot_id, exc)

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
            asyncio.ensure_future(self._emit(task_update_msg(task, "assigned")))

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
                    asyncio.ensure_future(self._emit(task_update_msg(task, "at_pickup")))
                    # Immediately head to dropoff
                    dropoff = self.stations[task.dropoff]
                    self.provider.goto(robot.id, dropoff.x, dropoff.y, task.dropoff)
                    task.state = T_ENROUTE_DROP
                    robot.status = ENROUTE_DROP
                    asyncio.ensure_future(self._emit(task_update_msg(task, "enroute_drop")))

            elif task.state == T_ENROUTE_DROP:
                if self.provider.arrived(robot.id):
                    task.state = T_DONE
                    task.done_at = time.time()
                    robot.status = IDLE
                    robot.current_task = None
                    log.info("%s done", task.id)
                    asyncio.ensure_future(self._emit(task_update_msg(task, "done")))
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
                asyncio.ensure_future(self._emit(callbutton_msg(st)))

    def _return_to_base(self, robot: Robot) -> None:
        base = next((s for s in self.stations.values() if s.type == "base"), None)
        if base:
            robot.status = RETURNING
            self.provider.goto(robot.id, base.x, base.y, base.id)

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
                    asyncio.ensure_future(self._emit(
                        alarm_msg("warn", f"robot {robot.id} offline", robot.id)))
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

        asyncio.ensure_future(self._emit(task_update_msg(task, "recovering")))
        asyncio.ensure_future(self._emit(
            alarm_msg("warn", f"{task.id} recovering: {reason}", robot.id)))
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
            asyncio.ensure_future(self._emit(task_update_msg(task, "reassigning")))
            log.info("recovery: %s re-queued (retry %d/%d)",
                     task.id, task.retries, config.MAX_TASK_RETRIES)
        else:
            self._release_task(task, T_FAILED)
            asyncio.ensure_future(self._emit(task_update_msg(task, "failed")))
            asyncio.ensure_future(self._emit(
                alarm_msg("critical",
                          f"{task.id} failed after {task.retries} retries: {reason}",
                          robot.id)))
            log.error("recovery: %s FAILED after %d retries — reason=%s",
                      task.id, task.retries, reason)

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
