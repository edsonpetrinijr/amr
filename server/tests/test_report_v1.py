"""Report v1 endpoint tests.

Covers basic and edge cases for:
- division by zero (no missions)
- missions with and without interventions
- MTBI calculation from failed events
"""
from __future__ import annotations

import os
import tempfile

from server.app import config, db
from server.app import main as appmod
from server.app.dispatcher import Dispatcher
from server.app.provider import SimProvider


# Keep deterministic timestamps for MTBI assertions.
_ORIG_TIME = appmod.time.time


def _fresh_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="reportv1_")
    os.close(fd)
    config.DB_PATH = path
    db._conn = None
    db.init()
    return path


def make_app():
    config.SIM_MODE = True
    config.SOAK_MODE = False
    _fresh_db()
    provider = SimProvider()
    disp = Dispatcher(provider)
    appmod._dispatcher = disp
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client()


class _Task:
    def __init__(self, tid: str, robot: str = "AMR-01", pickup: str = "CB-ALMOX", dropoff: str = "CB1"):
        self.id = tid
        self.robot = robot
        self.pickup = pickup
        self.dropoff = dropoff


def _seed_events(rows: list[tuple[str, float, str]]) -> None:
    """rows: [(task_id, ts, event), ...]"""
    seq = [ts for _, ts, _ in rows]
    idx = {"i": 0}

    def _fake_time():
        i = idx["i"]
        if i >= len(seq):
            return seq[-1] if seq else 0.0
        idx["i"] = i + 1
        return seq[i]

    appmod.time.time = _fake_time
    try:
        for task_id, _ts, event in rows:
            db.log_task_event(_Task(task_id), event)
    finally:
        appmod.time.time = _ORIG_TIME


def test_report_v1_empty_window_zero_rates():
    client = make_app()
    r = client.get("/report/v1/summary?from_ts=100&to_ts=200")
    assert r.status_code == 200
    body = r.get_json()

    assert body["period"] == {"from_ts": 100.0, "to_ts": 200.0}
    assert body["counts"] == {
        "missions_started": 0,
        "missions_finished": 0,
        "interventions_physical": 0,
    }
    assert body["mission_completion_rate_pct"] == 0.0
    assert body["intervention_physical_rate_pct"] == 0.0
    assert body["mtbi_seconds"] is None
    assert isinstance(body["notes"], list) and len(body["notes"]) >= 1


def test_report_v1_rates_and_mtbi():
    client = make_app()
    _seed_events([
        ("T1", 1000.0, "created"),
        ("T1", 1010.0, "done"),
        ("T2", 1020.0, "created"),
        ("T2", 1030.0, "failed"),
        ("T3", 1040.0, "created"),
        ("T3", 1055.0, "failed"),
    ])

    r = client.get("/report/v1/summary?from_ts=900&to_ts=1100")
    assert r.status_code == 200
    body = r.get_json()

    assert body["counts"] == {
        "missions_started": 3,
        "missions_finished": 1,
        "interventions_physical": 2,
    }
    assert body["mission_completion_rate_pct"] == 33.333
    assert body["intervention_physical_rate_pct"] == 66.667
    assert body["mtbi_seconds"] == 25.0


def test_report_v1_single_intervention_mtbi_null():
    client = make_app()
    _seed_events([
        ("T10", 2000.0, "created"),
        ("T10", 2020.0, "failed"),
    ])
    r = client.get("/report/v1/summary?from_ts=1900&to_ts=2100")
    assert r.status_code == 200
    body = r.get_json()
    assert body["counts"]["interventions_physical"] == 1
    assert body["mtbi_seconds"] is None


def test_report_v1_invalid_period_returns_400():
    client = make_app()
    r = client.get("/report/v1/summary?from_ts=300&to_ts=100")
    assert r.status_code == 400
    assert "from_ts" in r.get_json()["error"]
