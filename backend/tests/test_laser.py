"""SimProvider synthetic laser tests.

Deterministic checks that SimProvider.laser():
  - returns WORLD-frame [x, y] beams cast from est_pose,
  - respects the LASER_MAX_RANGE_M clamp,
  - is non-empty when a wall is within range.

Also runnable standalone: `python -m backend.tests.test_laser`.
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

from backend.app import provider as provider_mod
from backend.app.provider import SimProvider


def _make(rid_est=(0.0, 0.0), walls=None):
    """Build a SimProvider, pin the first robot's est_pose, load walls."""
    p = SimProvider()
    rid = next(iter(p.robots))
    loc = p._loc[rid]
    loc.est_x, loc.est_y = rid_est
    p.set_walls(walls or [])
    return p, rid


def test_beams_world_frame_and_nonempty_near_wall():
    # Vertical wall at x=5 spanning y∈[-5,5]; robot est at origin.
    p, rid = _make((0.0, 0.0), [((5.0, -5.0), (5.0, 5.0))])
    scan = p.laser(rid)
    beams = scan["beams"]
    assert beams, "expected non-empty scan with a wall in range"
    # The ray pointing +x (angle 0) must land on the wall at ~ (5, 0) in WORLD frame.
    near = min(beams, key=lambda b: abs(b[1]))  # beam closest to y=0
    assert abs(near[0] - 5.0) < 0.1, near
    assert abs(near[1] - 0.0) < 0.1, near


def test_respects_max_range():
    # Same wall but pushed beyond the clamp → no returns.
    far = provider_mod.LASER_MAX_RANGE_M + 5.0
    p, rid = _make((0.0, 0.0), [((far, -5.0), (far, 5.0))])
    assert p.laser(rid)["beams"] == []

    # Box of walls around the robot, all within range → every beam within clamp.
    p2, rid2 = _make((0.0, 0.0), [
        ((-4.0, -4.0), (4.0, -4.0)),
        ((4.0, -4.0), (4.0, 4.0)),
        ((4.0, 4.0), (-4.0, 4.0)),
        ((-4.0, 4.0), (-4.0, -4.0)),
    ])
    beams = p2.laser(rid2)["beams"]
    assert beams
    for bx, by in beams:
        d = math.hypot(bx - 0.0, by - 0.0)
        assert d <= provider_mod.LASER_MAX_RANGE_M + 0.1, (bx, by, d)


def test_empty_when_no_walls():
    p, rid = _make((0.0, 0.0), [])
    assert p.laser(rid)["beams"] == []


if __name__ == "__main__":
    test_beams_world_frame_and_nonempty_near_wall()
    test_respects_max_range()
    test_empty_when_no_walls()
    print("ok")
