"""SimProvider dual-pose localization model tests.

Enforce the dispatcher↔provider contract: est_pose reporting, confidence,
LOST/MISLOCALIZED → blocked → nav_failed timeouts, relocalize success/failure,
and that the existing force_* recovery hooks still behave. Deterministic — no
real clock dependency beyond monotonic timeouts we shrink via config.

Also runnable standalone: `python -m server.tests.test_localization`.
"""
from __future__ import annotations

import math

try:
    import pytest
except ModuleNotFoundError:  # offline sandbox — minimal shim
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()  # type: ignore

from server.app import config
from server.app.provider import SimProvider, LocMode


# ── Fixtures / helpers ────────────────────────────────────────────────────────

@pytest.fixture
def fast_loc(monkeypatch):
    monkeypatch.setattr(config, "NAV_FAIL_POSE_ERROR_THRESHOLD_M", 3.0)
    monkeypatch.setattr(config, "LOC_STUCK_TIMEOUT_S", 0.2)
    monkeypatch.setattr(config, "LOC_NAV_FAIL_TIMEOUT_S", 0.5)
    monkeypatch.setattr(config, "RELOCALIZE_SUCCESS_RADIUS_M", 1.0)
    monkeypatch.setattr(config, "RELOCALIZE_SUCCESS_THETA_DEG", 30.0)


def _apply_fast_loc():
    config.NAV_FAIL_POSE_ERROR_THRESHOLD_M = 3.0
    config.LOC_STUCK_TIMEOUT_S = 0.2
    config.LOC_NAV_FAIL_TIMEOUT_S = 0.5
    config.RELOCALIZE_SUCCESS_RADIUS_M = 1.0
    config.RELOCALIZE_SUCCESS_THETA_DEG = 30.0


def _first_robot(provider):
    rid = next(iter(provider.robots))
    return rid, provider.robots[rid]


def _backdate(provider, rid, seconds):
    """Push pose_error_since into the past to cross a timeout deterministically."""
    loc = provider._loc[rid]
    if loc.pose_error_since is not None:
        loc.pose_error_since -= seconds


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_lost_while_navigating_blocks_then_nav_fails(fast_loc):
    provider = SimProvider()
    rid, robot = _first_robot(provider)
    provider.goto(rid, robot.x + 40, robot.y, "CB1")   # active nav goal

    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.1)
    provider.set_pose_error(rid, dx=10.0, dy=0.0)       # error >> threshold

    # First tick registers the pose-error window; no timeout crossed yet.
    provider.tick(0.1)
    assert not provider.nav_failed(rid)
    assert provider.raw_state(rid)["confidence"] < config.LOC_LOST_CONFIDENCE_THRESHOLD

    # Cross the stuck timeout → blocked, but not yet nav_failed.
    _backdate(provider, rid, config.LOC_STUCK_TIMEOUT_S + 0.05)
    provider.tick(0.1)
    assert provider.raw_state(rid)["blocked"] is True
    assert not provider.nav_failed(rid)

    # Cross the nav-fail timeout → nav_failed (task_status 4).
    _backdate(provider, rid, config.LOC_NAV_FAIL_TIMEOUT_S + 0.05)
    provider.tick(0.1)
    assert provider.nav_failed(rid)
    assert provider.raw_state(rid)["task_status"] == 4


def test_no_teleport_true_pose_frozen_while_lost(fast_loc):
    provider = SimProvider()
    rid, robot = _first_robot(provider)
    gx = robot.x + 40
    provider.goto(rid, gx, robot.y, "CB1")
    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.1)
    provider.set_pose_error(rid, dx=10.0, dy=0.0)

    x_before = robot.x
    for _ in range(5):
        provider.tick(0.1)
    # Lost + large pose error → true pose must not advance toward the goal.
    assert robot.x == x_before
    assert not provider.arrived(rid)


def test_relocalize_near_true_pose_recovers(fast_loc):
    provider = SimProvider()
    rid, robot = _first_robot(provider)
    provider.goto(rid, robot.x + 40, robot.y, "CB1")
    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.1)
    provider.set_pose_error(rid, dx=10.0, dy=0.0)
    provider.tick(0.1)                       # establish the pose-error window
    _backdate(provider, rid, 1000.0)
    provider.tick(0.1)
    assert provider.raw_state(rid)["blocked"]

    ok = provider.relocalize(rid, robot.x + 0.5, robot.y - 0.2, robot.theta)
    assert ok is True
    rs = provider.raw_state(rid)
    assert rs["confidence"] >= 0.9
    assert rs["blocked"] is False
    assert rs["loc_mode"] == LocMode.OK.value
    # est snaps back onto true pose.
    assert math.hypot(rs["x"] - robot.x, rs["y"] - robot.y) < 0.01


def test_relocalize_far_stays_lost(fast_loc):
    provider = SimProvider()
    rid, robot = _first_robot(provider)
    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.1)

    ok = provider.relocalize(rid, robot.x + 25, robot.y + 25, robot.theta)
    assert ok is False
    rs = provider.raw_state(rid)
    assert rs["loc_mode"] == LocMode.LOST.value
    assert rs["confidence"] < config.LOC_LOST_CONFIDENCE_THRESHOLD


def test_raw_state_reports_est_pose_in_meters(fast_loc):
    provider = SimProvider()
    rid, robot = _first_robot(provider)
    # Healthy: est tracks true pose closely.
    provider.tick(0.1)
    rs = provider.raw_state(rid)
    assert isinstance(rs["x"], float) and isinstance(rs["y"], float)
    assert math.hypot(rs["x"] - robot.x, rs["y"] - robot.y) < 1.0

    # A forced pose error is reflected verbatim in est_pose.
    provider.set_pose_error(rid, dx=5.0, dy=-3.0, dtheta=0.1)
    rs = provider.raw_state(rid)
    assert abs(rs["x"] - (robot.x + 5.0)) < 1e-6
    assert abs(rs["y"] - (robot.y - 3.0)) < 1e-6


def test_existing_force_hooks_still_behave(fast_loc):
    provider = SimProvider()
    rid, robot = _first_robot(provider)

    # force_nav_fail → nav_failed + task_status 4; stop() clears it.
    provider.force_nav_fail(rid)
    assert provider.nav_failed(rid)
    assert provider.raw_state(rid)["task_status"] == 4
    provider.stop(rid)
    assert not provider.nav_failed(rid)

    # force_unhealthy → healthy() False + connected False, independent of loc.
    provider.force_unhealthy(rid, True)
    assert not provider.healthy(rid)
    assert provider.raw_state(rid)["connected"] is False
    provider.force_unhealthy(rid, False)
    assert provider.healthy(rid)

    # force_stall → true pose frozen (dispatcher stuck watchdog relies on this).
    provider.goto(rid, robot.x + 40, robot.y, "CB1")
    provider.force_stall(rid)
    x_before = robot.x
    for _ in range(5):
        provider.tick(0.1)
    assert robot.x == x_before


def test_healthy_independent_of_localization(fast_loc):
    provider = SimProvider()
    rid, _ = _first_robot(provider)
    provider.force_loc_loss(rid, LocMode.LOST, initial_confidence=0.0)
    # Lost but still connected → healthy.
    assert provider.healthy(rid)


# ── Standalone runner (offline sandbox; no pytest) ─────────────────────────────
if __name__ == "__main__":
    import sys

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in tests:
        _apply_fast_loc()
        try:
            fn(None)
            print(f"PASS  {fn.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {fn.__name__}: {exc!r}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            import traceback
            print(f"ERROR {fn.__name__}: {exc!r}")
            traceback.print_exc()
    print(f"\n{len(tests) - failures} passed, {failures} failed")
    sys.exit(1 if failures else 0)
