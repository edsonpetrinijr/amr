"""Unit tests for _laser_reply_to_world_beams (real-HW 1009 decode).

Covers: (1) pass-through of world-frame laser_beams, (2) polar
angle_min/angle_increment/ranges → world transform, (3) garbage → [].

Also runnable standalone: `python -m server.tests.test_laser_decode`.
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

from server.app.seer.robot_conn import _laser_reply_to_world_beams


def test_passthrough_world_beams():
    reply = {"laser_beams": [[1.0, 2.0], [3.0, 4.0]]}
    out = _laser_reply_to_world_beams(reply, 99.0, 99.0, 1.23)
    assert out == [[1.0, 2.0], [3.0, 4.0]]  # ignores pose, passes through


def test_polar_scan_transform():
    # Robot at (10, 5, theta=0); one beam straight ahead (angle 0), distance 2.
    reply = {"angle_min": 0.0, "angle_increment": math.pi / 2, "ranges": [2.0]}
    out = _laser_reply_to_world_beams(reply, 10.0, 5.0, 0.0)
    assert len(out) == 1
    wx, wy = out[0]
    assert abs(wx - 12.0) < 1e-6, out
    assert abs(wy - 5.0) < 1e-6, out


def test_polar_scan_skips_bad_ranges():
    # inf / NaN / 0 / over-range get dropped; second beam (angle pi/2, d=3) kept.
    reply = {
        "angle_min": 0.0,
        "angle_increment": math.pi / 2,
        "distance": [float("inf"), 3.0, 0.0, 1e9],
    }
    out = _laser_reply_to_world_beams(reply, 0.0, 0.0, 0.0)
    assert len(out) == 1
    wx, wy = out[0]
    assert abs(wx - 0.0) < 1e-6 and abs(wy - 3.0) < 1e-6, out


def test_garbage_returns_empty():
    assert _laser_reply_to_world_beams({}, 0, 0, 0) == []
    assert _laser_reply_to_world_beams({"foo": "bar"}, 0, 0, 0) == []
    assert _laser_reply_to_world_beams(None, 0, 0, 0) == []  # type: ignore


if __name__ == "__main__":
    test_passthrough_world_beams()
    test_polar_scan_transform()
    test_polar_scan_skips_bad_ranges()
    test_garbage_returns_empty()
    print("ok")
