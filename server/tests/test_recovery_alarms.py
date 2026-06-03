"""Dispatcher localization-recovery alarm tests (Feature 4).

Verify the latched, structured relocalization-assist alarm emitted when a task
enters recovery for a localization-related reason:
  - a forced localization loss while navigating emits exactly ONE alarm with all
    required keys,
  - staying in the same incident across many ticks does NOT re-emit,
  - after relocalize success + confidence recovery, a fresh loss emits a NEW
    alarm with a NEW incident_id.

Same harness style as test_recovery.py: drive the real Dispatcher step
functions directly with a controlled dt, capture SSE emits via a sync collector,
and drain the loop once per step. Offline-friendly standalone runner included.
"""
from __future__ import annotations

import asyncio

try:
    import pytest
except ModuleNotFoundError:  # offline sandbox — minimal shim
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()

from server.app import config
from server.app.dispatcher import Dispatcher
from server.app.models import T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP
from server.app.provider import LocMode, SimProvider


IN_FLIGHT = (T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP)


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
    monkeypatch.setattr(config, "STUCK_TIMEOUT_S", 0.2)
    monkeypatch.setattr(config, "ROBOT_STALE_S", 6.0)
    monkeypatch.setattr(config, "PROGRESS_EPS", 1.0)
    monkeypatch.setattr(config, "BATTERY_CRITICAL", 15.0)
    monkeypatch.setattr(config, "ROBOT_COOLDOWN_S", 100.0)
    monkeypatch.setattr(config, "MAX_TASK_RETRIES", 10)
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


def drain(loop):
    loop.run_until_complete(asyncio.sleep(0))
    loop.run_until_complete(asyncio.sleep(0))


def loc_alarms(events):
    """Structured relocalization-assist alarms only (carry a payload)."""
    return [e for e in events
            if e.get("type") == "alarm"
            and isinstance(e.get("payload"), dict)
            and e["payload"].get("action") == "RELOCALIZE_ASSIST_V1"]


REQUIRED_KEYS = {
    "robot_id", "task_id", "reason", "last_pose",
    "action", "suggestions_url", "timestamp", "incident_id",
}


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_loc_loss_emits_single_structured_alarm(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("CB-ALMOX", "CB1")
    step(disp, provider, loop)                 # assign + start navigating
    assert task.state in IN_FLIGHT
    rid = task.robot
    assert rid is not None

    # Lose localization while navigating, which fails the nav.
    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.0)
    provider.force_nav_fail(rid)
    step(disp, provider, loop)                 # _enter_recovery → one alarm

    al = loc_alarms(events)
    assert len(al) == 1
    p = al[0]["payload"]
    assert REQUIRED_KEYS.issubset(p.keys())
    assert p["robot_id"] == rid
    assert p["task_id"] == task.id
    assert p["reason"] == "NAV_FAILED"
    assert p["action"] == "RELOCALIZE_ASSIST_V1"
    assert p["suggestions_url"] == f"/api/relocalize/suggestions?robot_id={rid}"
    assert set(p["last_pose"].keys()) == {"x", "y", "theta", "confidence"}
    assert p["incident_id"]


def test_staying_in_incident_does_not_reemit(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("CB-ALMOX", "CB1")
    step(disp, provider, loop)
    rid = task.robot
    robot = provider.robots[rid]

    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.0)
    provider.force_nav_fail(rid)
    step(disp, provider, loop)
    assert len(loc_alarms(events)) == 1
    inc = loc_alarms(events)[0]["payload"]["incident_id"]

    # Re-enter recovery many times while the latch is held → still ONE alarm.
    for _ in range(10):
        provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.0)
        disp._enter_recovery(task, robot, "nav_failed")
        drain(loop)
    al = loc_alarms(events)
    assert len(al) == 1
    assert al[0]["payload"]["incident_id"] == inc


def test_relocalize_recovery_then_new_loss_new_incident(loop, fast_recovery):
    disp, provider, events = make_dispatcher()
    task = disp.create_task("CB-ALMOX", "CB1")
    step(disp, provider, loop)
    rid = task.robot
    robot = provider.robots[rid]

    # First incident.
    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.0)
    provider.force_nav_fail(rid)
    step(disp, provider, loop)
    al = loc_alarms(events)
    assert len(al) == 1
    inc1 = al[0]["payload"]["incident_id"]

    # Operator relocalizes onto the true pose → confidence recovers.
    assert provider.relocalize(rid, robot.x, robot.y, robot.theta) is True
    disp._check_recovery(0.1)                  # clearing pass drops the latch
    drain(loop)
    assert rid not in disp._loc_incidents

    # A fresh loss must raise a NEW alarm with a NEW incident_id.
    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.0)
    disp._enter_recovery(task, robot, "nav_failed")
    drain(loop)
    al = loc_alarms(events)
    assert len(al) == 2
    inc2 = al[1]["payload"]["incident_id"]
    assert inc2 != inc1


# ── Standalone runner ─────────────────────────────────────────────────────────

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
        # Mirror the fast_recovery fixture.
        config.STUCK_TIMEOUT_S = 0.2
        config.ROBOT_STALE_S = 6.0
        config.PROGRESS_EPS = 1.0
        config.BATTERY_CRITICAL = 15.0
        config.ROBOT_COOLDOWN_S = 100.0
        config.MAX_TASK_RETRIES = 10
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
    print(f"\n{len(tests) - failures} passed, {failures} failed")
    sys.exit(1 if failures else 0)
