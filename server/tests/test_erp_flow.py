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
    assert len(body["orders"]) == 3

    # ── confirm-delivery → FIFO oldest dispatched, Sim task created ──────────
    n_tasks_before = len(disp.all_tasks())
    r = client.post("/erp/confirm-delivery")
    assert r.status_code == 200
    res = r.get_json()
    assert res["ok"] is True
    order = res["order"]
    assert order["status"] == "dispatched"
    assert order["task_id"] is not None
    assert order["pickup_station"] == "BTLOG1"
    assert order["dropoff_station"] == _PN_ROUTE[order["part_number"]]
    assert len(disp.all_tasks()) == n_tasks_before + 1
    task = next(t for t in disp.all_tasks() if t.id == order["task_id"])
    assert task.pickup == "BTLOG1" and task.dropoff == order["dropoff_station"]

    # ── request-empty → pickup <POU> → dropoff BTLOG1 ────────────────────────
    r = client.post("/erp/request-empty")
    assert r.status_code == 200
    res = r.get_json()
    assert res["ok"] is True
    empty = res["order"]
    assert empty["record_type_class"] == "empty_return"
    assert empty["pickup_station"] in _PN_ROUTE.values()
    assert empty["dropoff_station"] == "BTLOG1"
    et = next(t for t in disp.all_tasks() if t.id == empty["task_id"])
    assert et.pickup == empty["pickup_station"] and et.dropoff == "BTLOG1"


def test_confirm_delivery_no_ready_returns_409():
    # Part number outside the PoC trigger set → no ready orders.
    client, disp, svc = make_app([make_line(part="2000001", cell="BT09TC")])
    svc.poll_once()  # nothing matches the part_number filter → no ready orders
    r = client.post("/erp/confirm-delivery")
    assert r.status_code == 409
    assert r.get_json()["error"] == "no_ready_order"


if __name__ == "__main__":
    test_end_to_end_flow()
    test_confirm_delivery_no_ready_returns_409()
    print("test_erp_flow OK")
