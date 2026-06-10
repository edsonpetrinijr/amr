"""ERP end-to-end flow test (SIM) — poll → ready rows → confirm-delivery →
request-empty, via the real Flask test client."""
from __future__ import annotations

import os
import tempfile

try:
    import pytest  # noqa: F401
except ModuleNotFoundError:
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()

from server.app import config, db
from server.app import main as appmod
from server.app.dispatcher import Dispatcher
from server.app.provider import SimProvider
from server.app.erp import ErpService, load_mapping
from server.app.models import ENROUTE_PICKUP
from server.tests.test_erp_filter import make_line


def _fresh_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="erpflow_")
    os.close(fd)
    config.DB_PATH = path
    db._conn = None
    db.init()
    return path


def _write_feed(lines) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="erpfeed_")
    os.close(fd)
    with open(path, "w", encoding="latin-1") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def make_app(feed_lines):
    config.SIM_MODE = True
    config.SOAK_MODE = False
    config.ERP_MAX_DISPATCH = 5
    config.ERP_AMR_FILTER = {"field": "part_number",
                             "values": ["3679579", "4175193", "3989602"]}
    _fresh_db()
    feed = _write_feed(feed_lines)
    config.ERP_FEED_PATH = feed
    config.ERP_WORK_COPY = feed + ".copy"
    provider = SimProvider()
    disp = Dispatcher(provider)
    mapping = load_mapping(config.ERP_MAPPING_PATH)
    svc = ErpService(disp, appmod._sync_broadcast, mapping)
    appmod._dispatcher = disp
    appmod._erp_service = svc
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client(), disp, svc


# PoC Conversor de Torque: PN → POU físico distinto (pickup único BTLOG1).
_PN_ROUTE = {
    "3679579": "FLBT10TC2",  # BT10TC
    "4175193": "FLBT10TC1",  # BT10TC
    "3989602": "FLBT10TC3",  # BT09TC
}


def test_end_to_end_flow():
    # 3 distinct torque-converter orders (< ERP_MAX_DISPATCH so the count is stable).
    lines = [
        make_line(part="3679579", cell="BT10TC", pou="FLBT10TC2"),
        make_line(part="4175193", cell="BT10TC", pou="FLBT10TC1"),
        make_line(part="3989602", cell="BT09TC", pou="FLBT10TC3"),
    ]
    client, disp, svc = make_app(lines)

    # ── one poll cycle → exactly min(N, cap) ready rows ──────────────────────
    svc.poll_once()
    ready = [o for o in db.list_erp_orders(100) if o["status"] == "ready_for_confirmation"]
    assert len(ready) == min(3, config.ERP_MAX_DISPATCH) == 3
    for o in ready:
        assert o["pickup_station"] == "BTLOG1"
        assert o["dropoff_station"] == _PN_ROUTE[o["part_number"]]
        assert o["amr_flagged"] is True

    # ── second poll → no duplicates ──────────────────────────────────────────
    svc.poll_once()
    assert len(db.list_erp_orders(100)) == 3

    # ── GET /erp/orders contract ─────────────────────────────────────────────
    r = client.get("/erp/orders")
    assert r.status_code == 200
    body = r.get_json()
    assert body["envio_station"] == "BTLOG1"
    assert body["amr_ready"] is True
    assert body["dispatch_mode"] == "dual"   # 4 robots idle → dual capable
    assert len(body["orders"]) == 3

    # ── confirm-delivery → dual dispatch: AMR-A (loaded) + AMR-B (empty) ─────
    n_tasks_before = len(disp.all_tasks())
    r = client.post("/erp/confirm-delivery")
    assert r.status_code == 200
    res = r.get_json()
    assert res["ok"] is True
    assert res["dispatch_mode"] == "dual"

    order = res["order"]
    assert order["status"] == "dispatched"
    assert order["task_id"] is not None
    assert order["pickup_station"] == "BTLOG1"
    assert order["dropoff_station"] == _PN_ROUTE[order["part_number"]]
    assert order["note"] is None  # no warning in dual mode

    # Two new tasks: AMR-A (loaded) + AMR-B (auto empty return)
    assert len(disp.all_tasks()) == n_tasks_before + 2
    task_a = next(t for t in disp.all_tasks() if t.id == order["task_id"])
    assert task_a.pickup == "BTLOG1" and task_a.dropoff == order["dropoff_station"]

    empty_order = res["empty_order"]
    assert empty_order is not None
    assert empty_order["record_type_class"] == "empty_return"
    assert empty_order["pickup_station"] == order["dropoff_station"]  # POU → BTLOG1
    assert empty_order["dropoff_station"] == "BTLOG1"
    task_b = next(t for t in disp.all_tasks() if t.id == empty_order["task_id"])
    assert task_b.pickup == empty_order["pickup_station"]
    assert task_b.dropoff == "BTLOG1"

    # ── request-empty still works as manual override ──────────────────────────
    # After dual dispatch, FLBT10TC2 is station-locked by AMR-B, so a second
    # request-empty targeting the same POU would be refused. Test the
    # manual fallback in isolation via test_single_amr_fallback.


def test_single_amr_fallback():
    """With only 1 idle robot, confirm-delivery dispatches AMR-A only.

    The loaded-rack task is created and the order note signals
    'single_amr_mode — empty return pending'. No empty_order in the response.
    POST /erp/request-empty remains the manual fallback.
    """
    lines = [make_line(part="3679579", cell="BT10TC", pou="FLBT10TC2")]
    client, disp, svc = make_app(lines)
    svc.poll_once()

    ready = [o for o in db.list_erp_orders(100) if o["status"] == "ready_for_confirmation"]
    assert len(ready) == 1

    # Simulate exactly 1 idle robot by directly marking the rest as busy.
    # (The async assign loop isn't running in test; we set robot state manually.)
    robots = list(disp.provider.robots.values())
    assert len(robots) >= 2, f"need ≥2 robots in config; got {len(robots)}"
    for r in robots[1:]:
        r.status = ENROUTE_PICKUP
        r.current_task = "dummy_busy"

    assert len(svc._idle_robots()) == 1

    # Confirm dispatch_mode reflects single before the call
    r = client.get("/erp/orders")
    assert r.get_json()["dispatch_mode"] == "single"

    n_tasks_before = len(disp.all_tasks())
    r = client.post("/erp/confirm-delivery")
    assert r.status_code == 200
    res = r.get_json()
    assert res["ok"] is True
    assert res["dispatch_mode"] == "single"
    assert res.get("empty_order") is None   # no auto AMR-B in single mode

    order = res["order"]
    assert order["status"] == "dispatched"
    assert order["task_id"] is not None
    assert "single_amr_mode" in (order["note"] or "")

    # Only 1 new task (AMR-A); AMR-B was NOT created
    assert len(disp.all_tasks()) == n_tasks_before + 1

    # The last robot is now also consumed → 0 idle
    robots[0].status = ENROUTE_PICKUP        # simulate dispatcher picking it up
    robots[0].current_task = order["task_id"]
    assert len(svc._idle_robots()) == 0

    # request-empty queues a T_PENDING task (ok=True) — the dispatcher assigns a
    # robot once one is free. 409 would only fire if the POU station were locked.
    r = client.post("/erp/request-empty")
    assert r.status_code == 200
    res = r.get_json()
    assert res["ok"] is True
    empty = res["order"]
    assert empty["record_type_class"] == "empty_return"
    assert empty["pickup_station"] == order["dropoff_station"]  # FLBT10TC2
    assert empty["dropoff_station"] == "BTLOG1"


def test_confirm_delivery_no_ready_returns_409():
    # Part number outside the PoC trigger set → no ready orders.
    client, disp, svc = make_app([make_line(part="2000001", cell="BT09TC")])
    svc.poll_once()  # nothing matches the part_number filter → no ready orders
    r = client.post("/erp/confirm-delivery")
    assert r.status_code == 409
    assert r.get_json()["error"] == "no_ready_order"


if __name__ == "__main__":
    test_end_to_end_flow()
    test_single_amr_fallback()
    test_confirm_delivery_no_ready_returns_409()
    print("test_erp_flow OK")
