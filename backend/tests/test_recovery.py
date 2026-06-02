"""
Dispatcher failure-recovery tests.

Drive the REAL Dispatcher in SIM_MODE by calling its internal step functions
(_assign_pending / _advance_active / _check_recovery / _check_battery) directly
with a controlled dt — no real async loop spinning. SSE emits are captured by a
sync broadcast collector; the dispatcher schedules them via asyncio.ensure_future
so each step drains the loop once to flush them.

Recovery timers (STUCK_TIMEOUT_S, ROBOT_STALE_S, …) are env-overridable via
config; we shrink them here so runs are fast and deterministic.
"""
from __future__ import annotations

import asyncio

try:
    import pytest
except ModuleNotFoundError:  # offline sandbox — provide a minimal shim
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()

from backend.app import config
from backend.app.dispatcher import Dispatcher
from backend.app.models import (
    IDLE, OFFLINE, CHARGING,
    T_PENDING, T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP, T_FAILED,
)
from backend.app.provider import SimProvider


# ── Fixtures / helpers ────────────────────────────────────────────────────────

@pytest.fixture
def loop():
    lp = asyncio.new_event_loop()
    asyncio.set_event_loop(lp)
    yield lp
    lp.close()
    asyncio.set_event_loop(None)


@pytest.fixture
def fast_recovery(monkeypatch):
    """Shrink/normalize recovery knobs for fast, deterministic tests."""
    monkeypatch.setattr(config, "STUCK_TIMEOUT_S", 0.2)
    monkeypatch.setattr(config, "ROBOT_STALE_S", 6.0)
    monkeypatch.setattr(config, "PROGRESS_EPS", 1.0)
    monkeypatch.setattr(config, "BATTERY_CRITICAL", 15.0)
    monkeypatch.setattr(config, "ROBOT_COOLDOWN_S", 100.0)
    monkeypatch.setattr(config, "MAX_TASK_RETRIES", 2)
    monkeypatch.setattr(config, "SOAK_MODE", False)


def make_dispatcher():
    provider = SimProvider()
    disp = Dispatcher(provider)
    events: list[dict] = []
    disp.set_broadcast(lambda m: events.append(m))
    return disp, provider, events


def step(disp, provider, loop, dt=0.1):
    provider.tick(dt)
    disp._assign_pending()
    disp._advance_active(dt)
    disp._check_recovery(dt)
    disp._check_battery()
    loop.run_until_complete(asyncio.sleep(0))
    loop.run_until_complete(asyncio.sleep(0))


def events_for(events, event):
    return [e for e in events if e.get("type") == "task_update" and e.get("event") == event]


def alarms(events, level=None):
    out = [e for e in events if e.get("type") == "alarm"]
    return [e for e in out if level is None or e.get("level") == level]


IN_FLIGHT = (T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_nav_fail_reassigns_to_different_robot(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("AP1", "CB1")
    step(disp, provider, loop)                 # assign
    assert task.state in IN_FLIGHT
    first = task.robot
    assert first is not None

    provider.force_nav_fail(first)
    step(disp, provider, loop)                 # recover + requeue
    assert task.fail_reason == "nav_failed"
    assert first in disp._cooldown

    step(disp, provider, loop)                 # reassign to another robot
    assert task.state in IN_FLIGHT
    assert task.robot is not None and task.robot != first


def test_disconnect_marks_offline_and_reassigns(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("AP1", "CB1")
    step(disp, provider, loop)
    first = task.robot
    robot = provider.robots[first]

    provider.force_unhealthy(first, True)
    step(disp, provider, loop)                 # recover offline
    assert robot.status == OFFLINE
    assert robot.current_task is None
    assert task.fail_reason == "robot_offline"
    assert alarms(events, "warn")              # offline warn emitted

    step(disp, provider, loop)                 # reassign to a healthy robot
    assert task.robot is not None and task.robot != first


def test_stuck_enters_recovering_with_reason_stuck(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("AP1", "CB1")
    step(disp, provider, loop)
    first = task.robot
    robot = provider.robots[first]

    # Freeze the robot and backdate its last progress past STUCK_TIMEOUT_S.
    provider.force_stall(first)
    task.last_x, task.last_y = robot.x, robot.y
    task.last_progress_at = task.last_progress_at - 1000.0

    step(disp, provider, loop)
    assert task.fail_reason == "stuck"
    assert events_for(events, "recovering")


def test_max_retries_fails_task_and_releases_lock(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("AP1", "CB1")
    assert "AP1" in disp._station_lock

    # MAX_TASK_RETRIES=2 → fail 3 times (3 distinct robots) then T_FAILED.
    for _ in range(6):
        step(disp, provider, loop)
        if task.state == T_FAILED:
            break
        if task.robot:
            provider.force_nav_fail(task.robot)

    assert task.state == T_FAILED
    assert task.retries == config.MAX_TASK_RETRIES
    assert "AP1" not in disp._station_lock        # station lock released
    assert alarms(events, "critical")             # critical alarm emitted


def test_battery_critical_aborts_and_routes_to_base(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("AP1", "CB1")
    step(disp, provider, loop)
    first = task.robot
    robot = provider.robots[first]

    robot.battery = 10.0                         # below BATTERY_CRITICAL
    step(disp, provider, loop)                   # recover + route to charger
    assert task.fail_reason == "battery"
    assert robot.status == CHARGING              # _check_battery routed it to base

    step(disp, provider, loop)                   # reassign to a healthy robot
    assert task.robot is not None and task.robot != first


def test_single_robot_in_cooldown_waits_pending(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    # Keep exactly one robot.
    only = next(iter(provider.robots))
    provider.robots = {only: provider.robots[only]}

    task = disp.create_task("AP1", "CB1")
    step(disp, provider, loop)
    assert task.robot == only

    provider.force_nav_fail(only)
    step(disp, provider, loop)                   # recover → requeue, only robot cooling down
    assert task.state == T_PENDING
    assert only in disp._cooldown

    # No thrashing: task stays PENDING while the only robot is cooling down.
    for _ in range(10):
        step(disp, provider, loop)
        assert task.state == T_PENDING
        assert provider.robots[only].current_task is None


# ── Standalone runner ─────────────────────────────────────────────────────────
# This repo's sandbox is offline and pytest cannot be installed, so the file is
# also runnable with plain `python backend/tests/test_recovery.py`. The pytest
# API above is unchanged and runs identically under `python -m pytest` when the
# package is available.
if __name__ == "__main__":
    import sys

    class _MonkeyPatch:
        def __init__(self):
            self._undo = []

        def setattr(self, target, name, value):
            self._undo.append((target, name, getattr(target, name)))
            setattr(target, name, value)

        def undo(self):
            for target, name, old in reversed(self._undo):
                setattr(target, name, old)
            self._undo.clear()

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in tests:
        mp = _MonkeyPatch()
        # Apply the fast_recovery settings directly (mirror of the fixture).
        config.STUCK_TIMEOUT_S = 0.2
        config.ROBOT_STALE_S = 6.0
        config.PROGRESS_EPS = 1.0
        config.BATTERY_CRITICAL = 15.0
        config.ROBOT_COOLDOWN_S = 100.0
        config.MAX_TASK_RETRIES = 2
        config.SOAK_MODE = False
        lp = asyncio.new_event_loop()
        asyncio.set_event_loop(lp)
        try:
            fn(lp, None)
            print(f"PASS  {fn.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {fn.__name__}: {exc!r}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            import traceback
            print(f"ERROR {fn.__name__}: {exc!r}")
            traceback.print_exc()
        finally:
            lp.close()
            asyncio.set_event_loop(None)
            mp.undo()
    print(f"\n{len(tests) - failures} passed, {failures} failed")
    sys.exit(1 if failures else 0)
