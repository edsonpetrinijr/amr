"""
Operator-facing endpoint tests: manual jog, software STOP-ALL/resume, and the
read-only telemetry/analytics queries.

Drives the real Flask app via its test client in SIM_MODE. A throwaway temp
sqlite DB is wired in (config.DB_PATH) and seeded with a couple of telemetry /
task_event rows so the analytics endpoints have real data to fold.

Offline-friendly: runnable with plain `python server/tests/test_operator_endpoints.py`
(same __main__ shim as test_recovery.py / test_opcua_driver.py) or under pytest.
"""
from __future__ import annotations

import os
import tempfile
import time

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
from server.app.models import IDLE, ENROUTE_PICKUP, T_ENROUTE_PICKUP
from server.app.provider import SimProvider


# ── Harness ───────────────────────────────────────────────────────────────────

def _fresh_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="optest_")
    os.close(fd)
    config.DB_PATH = path
    # Reset the module-level connection so init() rebinds to the temp DB.
    db._conn = None
    db.init()
    return path


def make_app():
    """Build a Flask test client backed by a real Dispatcher in SIM_MODE."""
    config.SIM_MODE = True
    config.SOAK_MODE = False
    _fresh_db()
    provider = SimProvider()
    disp = Dispatcher(provider)
    appmod._dispatcher = disp
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client(), disp


def _seed_rows(disp: Dispatcher) -> None:
    robots = list(disp.provider.robots.values())
    db.log_telemetry(robots)                       # one telemetry row per robot
    # A completed + a failed task event pair so stats has something to count.
    class _T:
        def __init__(self, tid, robot, pickup, dropoff):
            self.id, self.robot, self.pickup, self.dropoff = tid, robot, pickup, dropoff
    rid = robots[0].id
    t1 = _T("T9001", rid, "CB-ALMOX", "CB1")
    db.log_task_event(t1, "created")
    time.sleep(0.01)
    db.log_task_event(t1, "done")
    t2 = _T("T9002", rid, "CB-ALMOX", "CB1")
    db.log_task_event(t2, "created")
    db.log_task_event(t2, "failed")


# ── /jog ──────────────────────────────────────────────────────────────────────

def test_jog_accepts_valid_command():
    client, disp = make_app()
    rid = next(iter(disp.provider.robots))
    r = client.post("/jog", json={"robot_id": rid, "vx": 0.1, "vy": 0.0, "w": 0.05})
    assert r.status_code == 200, r.get_json()
    body = r.get_json()
    assert body["ok"] is True
    assert body["robot_id"] == rid
    assert body["vx"] == 0.1


def test_jog_clamps_out_of_range():
    client, disp = make_app()
    rid = next(iter(disp.provider.robots))
    r = client.post("/jog", json={"robot_id": rid, "vx": 999.0, "vy": 0, "w": -999.0})
    assert r.status_code == 200
    body = r.get_json()
    assert body["vx"] == config.JOG_MAX_VX
    assert body["w"] == -config.JOG_MAX_W
    assert body["clamped"] is True


def test_jog_rejects_unknown_robot():
    client, _ = make_app()
    r = client.post("/jog", json={"robot_id": "NOPE", "vx": 0.1})
    assert r.status_code == 404


def test_jog_rejects_non_numeric():
    client, disp = make_app()
    rid = next(iter(disp.provider.robots))
    r = client.post("/jog", json={"robot_id": rid, "vx": "fast"})
    assert r.status_code == 400


def test_jog_rejected_with_active_task():
    client, disp = make_app()
    rid = next(iter(disp.provider.robots))
    robot = disp.provider.robots[rid]
    robot.current_task = "T0001"          # simulate an in-flight task
    robot.status = ENROUTE_PICKUP
    r = client.post("/jog", json={"robot_id": rid, "vx": 0.1})
    assert r.status_code == 409
    assert "active task" in r.get_json()["error"]


# ── /stop_all + /resume ───────────────────────────────────────────────────────

def test_stop_all_cancels_and_halts_then_resume():
    client, disp = make_app()
    # Create + assign a task so there is something to cancel.
    task = disp.create_task("CB-ALMOX", "CB1")
    assert task is not None
    disp._assign_pending()
    assert task.state == T_ENROUTE_PICKUP
    assert task.robot is not None

    r = client.post("/stop_all")
    assert r.status_code == 200
    body = r.get_json()
    assert body["halted"] is True
    assert task.id in body["cancelled"]
    assert disp.halted is True
    # Robot freed.
    assert disp.provider.robots[task.robot].current_task is None

    # While halted, a brand-new pending task must NOT be auto-assigned.
    t2 = disp.create_task("CB-ALMOX", "CB1")
    assert t2 is not None
    disp._assign_pending()
    assert t2.robot is None

    # Resume re-enables assignment.
    r = client.post("/resume")
    assert r.status_code == 200
    assert r.get_json()["halted"] is False
    assert disp.halted is False
    disp._assign_pending()
    assert t2.robot is not None


def test_jog_allowed_while_halted():
    client, disp = make_app()
    client.post("/stop_all")
    assert disp.halted is True
    rid = next(iter(disp.provider.robots))
    r = client.post("/jog", json={"robot_id": rid, "vx": 0.1})
    assert r.status_code == 200


# ── Telemetry / analytics queries ─────────────────────────────────────────────

def test_telemetry_query_shape():
    client, disp = make_app()
    _seed_rows(disp)
    rid = next(iter(disp.provider.robots))
    r = client.get(f"/telemetry/robots/{rid}?limit=10")
    assert r.status_code == 200
    body = r.get_json()
    assert body["robot_id"] == rid
    assert body["count"] >= 1
    row = body["rows"][0]
    for k in ("ts", "x", "y", "battery", "status"):
        assert k in row


def test_tasks_history_shape():
    client, disp = make_app()
    _seed_rows(disp)
    r = client.get("/tasks/history")
    assert r.status_code == 200
    body = r.get_json()
    assert body["count"] >= 2
    ids = {t["id"]: t for t in body["tasks"]}
    assert ids["T9001"]["state"] == "done"
    assert ids["T9001"]["duration_s"] is not None
    assert ids["T9002"]["state"] == "failed"
    for k in ("id", "pickup", "dropoff", "robot", "state", "created_ts"):
        assert k in ids["T9001"]


def test_stats_summary_shape():
    client, disp = make_app()
    _seed_rows(disp)
    r = client.get("/stats/summary")
    assert r.status_code == 200
    body = r.get_json()
    for k in ("tasks_completed_today", "tasks_failed_today", "avg_task_duration_s",
              "fleet_total", "fleet_active", "fleet_utilization", "avg_battery", "halted"):
        assert k in body
    assert body["tasks_completed_today"] >= 1
    assert body["tasks_failed_today"] >= 1
    assert body["fleet_total"] == len(disp.provider.robots)


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
