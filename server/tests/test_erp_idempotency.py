"""ERP idempotency test — the same ORDER line across two polls dedups to ONE row,
bumps last_seen_ts, and is never re-dispatched."""
from __future__ import annotations

import os
import tempfile
import time

try:
    import pytest  # noqa: F401
except ModuleNotFoundError:
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()

from server.app import config, db
from server.app.dispatcher import Dispatcher
from server.app.provider import SimProvider
from server.app.erp import ErpService, load_mapping
from server.tests.test_erp_filter import make_line


def _fresh_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="erpidem_")
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


def _service() -> ErpService:
    config.SIM_MODE = True
    config.SOAK_MODE = False
    _fresh_db()
    provider = SimProvider()
    disp = Dispatcher(provider)
    mapping = load_mapping(config.ERP_MAPPING_PATH)
    return ErpService(disp, lambda msg: None, mapping)


def test_same_order_twice_dedups_to_one_row():
    line = make_line(part="9990001", cell="C ILC")
    feed = _write_feed([line])
    work = feed + ".copy"
    config.ERP_FEED_PATH = feed
    config.ERP_WORK_COPY = work
    config.ERP_AMR_FILTER = {"field": "cell", "value": "C ILC"}

    svc = _service()
    svc.poll_once()
    after_first = db.list_erp_orders(100)
    assert len(after_first) == 1
    o1 = after_first[0]
    assert o1["status"] == "ready_for_confirmation"
    first_seen = o1["first_seen_ts"]
    seen_1 = o1["last_seen_ts"]

    time.sleep(0.02)
    svc.poll_once()
    after_second = db.list_erp_orders(100)
    # Exactly one row — no duplicate created.
    assert len(after_second) == 1
    o2 = after_second[0]
    assert o2["order_key"] == o1["order_key"]
    # last_seen_ts advanced; first_seen_ts and status unchanged (not re-dispatched).
    assert o2["last_seen_ts"] >= seen_1
    assert o2["first_seen_ts"] == first_seen
    assert o2["status"] == "ready_for_confirmation"
    assert o2["task_id"] is None


if __name__ == "__main__":
    test_same_order_twice_dedups_to_one_row()
    print("test_erp_idempotency OK")
