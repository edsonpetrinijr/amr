"""Nearest-landmarks relocalization-suggestions API tests.

Covers MapModel.nearest_landmarks (distance ordering, stable tie-break, k +
max clamp) and GET /api/relocalize/suggestions (robot_id path, explicit x/y
path, and the negative cases: no map, unknown robot, missing params).

Drives the real Flask app via its test client in SIM_MODE, mirroring the
harness in test_operator_endpoints.py. Offline-friendly: runnable with plain
`python -m server.tests.test_relocalize_api` or under pytest.
"""
from __future__ import annotations

import os
import tempfile

try:
    import pytest
except ModuleNotFoundError:  # offline sandbox — minimal shim
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()

from server.app import config, db
from server.app import main as appmod
from server.app.dispatcher import Dispatcher
from server.app.provider import SimProvider
from server.app.smap import Landmark, MapModel, Pos2D


# ── Harness ───────────────────────────────────────────────────────────────────

def _fresh_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="reloctest_")
    os.close(fd)
    config.DB_PATH = path
    db._conn = None
    db.init()
    return path


def _demo_map() -> MapModel:
    """Landmarks at known distances from the origin. LM_A and LM_DUP are placed
    at the exact same distance from (0,0) to exercise the tie-break."""
    return MapModel(
        name="test", map_type="2D-Map", version="1", resolution=0.02,
        min_pos=Pos2D(-100, -100), max_pos=Pos2D(100, 100),
        landmarks=[
            Landmark(id="LM3", x=3.0, y=0.0),      # dist 3
            Landmark(id="LM1", x=1.0, y=0.0),      # dist 1
            Landmark(id="LM_DUP", x=0.0, y=2.0),   # dist 2 (tie)
            Landmark(id="LM_A", x=2.0, y=0.0),     # dist 2 (tie)
            Landmark(id="LM5", x=0.0, y=5.0),      # dist 5
            Landmark(id="LM4", x=0.0, y=-4.0),     # dist 4
        ],
    )


def make_app(map_model: MapModel | None):
    config.SIM_MODE = True
    config.SOAK_MODE = False
    _fresh_db()
    provider = SimProvider()
    disp = Dispatcher(provider)
    appmod._dispatcher = disp
    appmod._map_model = map_model
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client(), disp


# ── MapModel.nearest_landmarks (unit) ─────────────────────────────────────────

def test_nearest_landmarks_distance_ordering_and_tiebreak():
    m = _demo_map()
    res = m.nearest_landmarks(0.0, 0.0, k=5)
    ids = [e["lm_id"] for e in res]
    # Ascending distance; the two dist-2 landmarks tie-break by lm_id (A < DUP).
    assert ids == ["LM1", "LM_A", "LM_DUP", "LM3", "LM4"]
    assert [round(e["dist_m"], 3) for e in res] == [1.0, 2.0, 2.0, 3.0, 4.0]
    for e in res:
        assert set(e.keys()) == {"lm_id", "name", "x", "y", "theta", "dist_m"}
        assert e["name"] == e["lm_id"]
        assert e["theta"] is None


def test_nearest_landmarks_default_k_and_clamp():
    m = _demo_map()
    assert len(m.nearest_landmarks(0.0, 0.0)) == 5            # default k=5
    assert len(m.nearest_landmarks(0.0, 0.0, k=2)) == 2
    assert len(m.nearest_landmarks(0.0, 0.0, k=100)) == 6     # only 6 landmarks


def test_nearest_landmarks_max_dist_filter():
    m = _demo_map()
    res = m.nearest_landmarks(0.0, 0.0, k=10, max_dist_m=2.5)
    assert [e["lm_id"] for e in res] == ["LM1", "LM_A", "LM_DUP"]


# ── GET /api/relocalize/suggestions ───────────────────────────────────────────

def test_suggestions_explicit_pose():
    client, _ = make_app(_demo_map())
    r = client.get("/api/relocalize/suggestions?x=0&y=0&k=3")
    assert r.status_code == 200, r.get_json()
    body = r.get_json()
    assert body["frame"] == "smap_meters"
    assert body["source"] == "explicit_pose"
    assert body["pose_used"] == {"x": 0.0, "y": 0.0, "theta": None, "confidence": None}
    assert [s["lm_id"] for s in body["suggestions"]] == ["LM1", "LM_A", "LM_DUP"]


def test_suggestions_k_clamped_to_max():
    client, _ = make_app(_demo_map())
    r = client.get("/api/relocalize/suggestions?x=0&y=0&k=999")
    assert r.status_code == 200
    # Only 6 landmarks exist; k is clamped to 20 internally so all 6 return.
    assert len(r.get_json()["suggestions"]) == 6


def test_suggestions_robot_id_uses_provider_pose():
    client, disp = make_app(_demo_map())
    rid = next(iter(disp.provider.robots))
    rs = disp.provider.raw_state(rid)
    r = client.get(f"/api/relocalize/suggestions?robot_id={rid}")
    assert r.status_code == 200, r.get_json()
    body = r.get_json()
    assert body["source"] == "robot_state"
    assert body["pose_used"]["x"] == rs["x"]
    assert body["pose_used"]["y"] == rs["y"]
    assert body["pose_used"]["confidence"] == rs["confidence"]
    # Suggestions are ordered by distance from the reported pose.
    dists = [s["dist_m"] for s in body["suggestions"]]
    assert dists == sorted(dists)


def test_suggestions_no_map_returns_409():
    client, _ = make_app(None)
    r = client.get("/api/relocalize/suggestions?x=0&y=0")
    assert r.status_code == 409
    assert r.get_json()["error"] == "MAP_NOT_LOADED"


def test_suggestions_unknown_robot_returns_404():
    client, _ = make_app(_demo_map())
    r = client.get("/api/relocalize/suggestions?robot_id=NOPE")
    assert r.status_code == 404
    assert r.get_json()["error"] == "POSE_UNAVAILABLE"


def test_suggestions_missing_params_returns_400():
    client, _ = make_app(_demo_map())
    r = client.get("/api/relocalize/suggestions")
    assert r.status_code == 400


# ── Standalone runner (offline sandbox; no pytest) ────────────────────────────

if __name__ == "__main__":
    import sys

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in tests:
        try:
            fn()
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
