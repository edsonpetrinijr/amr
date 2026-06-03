"""
Devices & callbuttons configuration + diagnostics endpoint tests.

Drives the real Flask app via its test client in SIM_MODE with a throwaway temp
sqlite DB AND a throwaway temp devices.json store, so robot CRUD / station OPC UA
edits and their persistence are exercised end-to-end with no real hardware.

Offline-friendly: runnable with plain `python server/tests/test_devices_api.py`
(same __main__ shim as test_operator_endpoints.py / test_opcua_driver.py) or
under pytest.
"""
from __future__ import annotations

import copy
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

from server.app import config, db, store
from server.app import main as appmod
from server.app.dispatcher import Dispatcher
from server.app.provider import SimProvider

# Pristine defaults so tests don't leak fleet/station mutations into each other.
_ORIG_ROBOTS = copy.deepcopy(config.ROBOTS)
_ORIG_STATIONS = copy.deepcopy(config.STATIONS)


# ── Harness ───────────────────────────────────────────────────────────────────

def _fresh_db() -> str:
    fd, path = tempfile.mkstemp(suffix=".db", prefix="devtest_")
    os.close(fd)
    config.DB_PATH = path
    db._conn = None
    db.init()
    return path


def _fresh_store() -> str:
    """Point the devices store at a brand-new temp path (file absent → seeded)."""
    fd, path = tempfile.mkstemp(suffix=".json", prefix="devices_")
    os.close(fd)
    os.unlink(path)                      # force first-run seed path
    config.DEVICES_STORE_PATH = path
    return path


def make_app():
    """Build a Flask test client backed by a real Dispatcher in SIM_MODE."""
    config.SIM_MODE = True
    config.SOAK_MODE = False
    # Restore pristine config so each test starts from the same fleet/stations.
    config.ROBOTS[:] = copy.deepcopy(_ORIG_ROBOTS)
    config.STATIONS[:] = copy.deepcopy(_ORIG_STATIONS)
    _fresh_db()
    _fresh_store()
    store.load_into_config()
    provider = SimProvider()
    disp = Dispatcher(provider)
    appmod._dispatcher = disp
    appmod._opcua_driver = None          # no real driver in tests
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client(), disp


# ── POST /robots ──────────────────────────────────────────────────────────────

def test_add_robot_by_ip():
    client, disp = make_app()
    r = client.post("/robots", json={"ip": "192.168.0.200"})
    assert r.status_code == 201, r.get_json()
    body = r.get_json()
    assert body["robot"]["ip"] == "192.168.0.200"
    assert body["connected"] is True
    assert "pulled" in body and body["pulled"]["model"] == "SIM-AMR"
    rid = body["robot"]["id"]
    # Appears in GET /robots.
    listing = client.get("/robots").get_json()
    assert any(x["id"] == rid for x in listing)


def test_add_robot_requires_ip():
    client, _ = make_app()
    r = client.post("/robots", json={"name": "no-ip"})
    assert r.status_code == 400


def test_update_robot_changes_ip():
    client, disp = make_app()
    rid = next(iter(disp.provider.robots))
    r = client.put(f"/robots/{rid}", json={"ip": "10.10.10.10"})
    assert r.status_code == 200, r.get_json()
    assert r.get_json()["robot"]["ip"] == "10.10.10.10"
    listing = {x["id"]: x for x in client.get("/robots").get_json()}
    assert listing[rid]["ip"] == "10.10.10.10"


def test_update_unknown_robot_404():
    client, _ = make_app()
    r = client.put("/robots/NOPE", json={"ip": "1.2.3.4"})
    assert r.status_code == 404


def test_probe_robot_connected():
    client, disp = make_app()
    rid = next(iter(disp.provider.robots))
    r = client.post(f"/robots/{rid}/probe")
    assert r.status_code == 200
    body = r.get_json()
    assert body["connected"] is True
    for k in ("name", "model", "battery", "x", "y", "theta"):
        assert k in body["pulled"]


def test_delete_robot_removes_it():
    client, disp = make_app()
    rid = next(iter(disp.provider.robots))
    r = client.delete(f"/robots/{rid}")
    assert r.status_code == 200
    assert r.get_json() == {"ok": True, "id": rid}
    listing = client.get("/robots").get_json()
    assert all(x["id"] != rid for x in listing)
    assert rid not in disp.provider.robots


def test_delete_unknown_robot_404():
    client, _ = make_app()
    r = client.delete("/robots/NOPE")
    assert r.status_code == 404


# ── Persistence (simulate restart) ────────────────────────────────────────────

def test_robot_crud_survives_restart():
    make_app()                            # fresh temp store
    added = store.add_robot({"ip": "172.16.0.5", "name": "PersistBot"})
    rid = added["id"]
    # Simulate a restart: wipe in-memory fleet back to defaults, reload from file.
    config.ROBOTS[:] = copy.deepcopy(_ORIG_ROBOTS)
    store.load_into_config()
    ids = {r["id"] for r in config.ROBOTS}
    assert rid in ids
    survivor = next(r for r in config.ROBOTS if r["id"] == rid)
    assert survivor["ip"] == "172.16.0.5"


def test_station_opcua_survives_restart():
    make_app()
    assert store.set_station_opcua("CB2", "ns=9;s=NEWNODE", None) is True
    config.STATIONS[:] = copy.deepcopy(_ORIG_STATIONS)
    store.load_into_config()
    cb2 = next(s for s in config.STATIONS if s["id"] == "CB2")
    assert cb2["opcua_node"] == "ns=9;s=NEWNODE"


# ── PUT /stations/<id> ────────────────────────────────────────────────────────

def test_update_station_opcua_and_preserve_cb_state():
    client, disp = make_app()
    # Dirty the runtime callbutton state so we can prove reload preserves it.
    disp.stations["CB2"].cb_state = "ready"
    disp.stations["CB2"].cb_dir = "fwd"
    r = client.put("/stations/CB2", json={"opcua_node": "ns=5;s=Changed"})
    assert r.status_code == 200, r.get_json()
    assert r.get_json()["station"]["opcua_node"] == "ns=5;s=Changed"
    # Reflected in GET /stations.
    stations = {s["id"]: s for s in client.get("/stations").get_json()}
    assert stations["CB2"]["opcua_node"] == "ns=5;s=Changed"
    # Runtime callbutton state preserved across reload.
    assert disp.stations["CB2"].cb_state == "ready"
    assert disp.stations["CB2"].cb_dir == "fwd"


def test_update_unknown_station_404():
    client, _ = make_app()
    r = client.put("/stations/NOPE", json={"opcua_node": "x"})
    assert r.status_code == 404


# ── POST /opcua/test ──────────────────────────────────────────────────────────

def test_opcua_test_passthrough_success():
    client, disp = make_app()
    captured = {}

    def _fake_probe(node_id, endpoint=None, timeout=3.0):
        captured["node"] = node_id
        return {"ok": True, "value": True, "error": None,
                "configured": True, "endpoint": "opc.tcp://x:4840"}

    orig = appmod.opcua.probe_node
    appmod.opcua.probe_node = _fake_probe
    try:
        r = client.post("/opcua/test", json={"node": "ns=2;s=Foo"})
    finally:
        appmod.opcua.probe_node = orig
    assert r.status_code == 200
    body = r.get_json()
    assert body["ok"] is True
    assert body["value"] is True
    assert body["configured"] is True
    assert body["node"] == "ns=2;s=Foo"
    assert captured["node"] == "ns=2;s=Foo"


def test_opcua_test_by_station_id():
    client, disp = make_app()

    def _fake_probe(node_id, endpoint=None, timeout=3.0):
        return {"ok": True, "value": False, "error": None,
                "configured": True, "endpoint": "opc.tcp://x"}

    orig = appmod.opcua.probe_node
    appmod.opcua.probe_node = _fake_probe
    try:
        r = client.post("/opcua/test", json={"station_id": "CB2"})
    finally:
        appmod.opcua.probe_node = orig
    assert r.status_code == 200
    assert r.get_json()["node"] == disp.stations["CB2"].opcua_node


def test_opcua_test_unset_endpoint_not_500():
    client, _ = make_app()

    def _fake_probe(node_id, endpoint=None, timeout=3.0):
        return {"ok": False, "value": None, "error": None,
                "configured": False, "endpoint": ""}

    orig = appmod.opcua.probe_node
    appmod.opcua.probe_node = _fake_probe
    try:
        r = client.post("/opcua/test", json={"node": "ns=2;s=Foo"})
    finally:
        appmod.opcua.probe_node = orig
    assert r.status_code == 200
    body = r.get_json()
    assert body["configured"] is False
    assert body["ok"] is False


def test_opcua_test_requires_node_or_station():
    client, _ = make_app()
    r = client.post("/opcua/test", json={})
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
