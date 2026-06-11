"""Risk A layer-0 localization detection tests.

Covers the observe-only detector in Dispatcher:
  - degraded after short low-confidence timeout,
  - lost after longer persistence,
  - recovered when confidence returns,
  - anti-spam (no repeated same-event per tick).
Also validates the minimal status endpoint.
"""
from __future__ import annotations

import copy

try:
    import pytest
except ModuleNotFoundError:  # offline sandbox — minimal shim
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()  # type: ignore

from server.app import config
from server.app.dispatcher import Dispatcher
from server.app.provider import SimProvider
from server.app import main as appmod

_ORIG_ROBOTS = copy.deepcopy(config.ROBOTS)


@pytest.fixture
def fast_risk_a(monkeypatch):
    monkeypatch.setattr(config, "RISK_A_ENABLED", True)
    monkeypatch.setattr(config, "SOAK_MODE", False)
    monkeypatch.setattr(config, "LOC_DEGRADED_TIMEOUT_S", 0.2)
    monkeypatch.setattr(config, "LOC_LOST_TIMEOUT_S", 0.5)
    monkeypatch.setattr(config, "LOC_MIN_CONFIDENCE", 0.6)
    monkeypatch.setattr(config, "LOC_CONFIDENCE_DECAY_RATE", 0.0)


def make_dispatcher():
    config.ROBOTS[:] = copy.deepcopy(_ORIG_ROBOTS)
    provider = SimProvider()
    disp = Dispatcher(provider)
    events: list[dict] = []
    disp.set_broadcast(lambda m: events.append(m))
    return disp, provider, events


def _loc_events(events: list[dict]) -> list[dict]:
    return [e for e in events if e.get("type") == "localization_event"]


def _set_confidence(provider: SimProvider, rid: str, value: float) -> None:
    provider._loc[rid].confidence = value


def _tick_risk(disp: Dispatcher, provider: SimProvider, dt: float = 0.1) -> None:
    provider.tick(dt)
    disp._check_localization_layer0()


def _age_low_window(disp: Dispatcher, rid: str, seconds: float) -> None:
    st = disp._risk_a_loc_state[rid]
    st["low_since_ts"] = float(st["low_since_ts"]) - seconds


def test_degraded_after_short_timeout(fast_risk_a):
    disp, provider, events = make_dispatcher()
    rid = next(iter(provider.robots))

    _set_confidence(provider, rid, 0.2)
    _tick_risk(disp, provider, 0.1)
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)

    loc = _loc_events(events)
    assert any(e["event"] == "LOCALIZATION_DEGRADED" and e["robot_id"] == rid for e in loc)
    st = [x for x in disp.localization_status() if x["robot_id"] == rid][0]
    assert st["state"] == "degraded"


def test_lost_after_longer_timeout(fast_risk_a):
    disp, provider, events = make_dispatcher()
    rid = next(iter(provider.robots))

    _set_confidence(provider, rid, 0.2)
    _tick_risk(disp, provider, 0.1)
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)  # degraded
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)  # lost

    loc = [e for e in _loc_events(events) if e["robot_id"] == rid]
    assert [e["event"] for e in loc].count("LOCALIZATION_DEGRADED") == 1
    assert [e["event"] for e in loc].count("LOCALIZATION_LOST") == 1
    st = [x for x in disp.localization_status() if x["robot_id"] == rid][0]
    assert st["state"] == "lost"


def test_recovered_when_confidence_returns(fast_risk_a):
    disp, provider, events = make_dispatcher()
    rid = next(iter(provider.robots))

    _set_confidence(provider, rid, 0.2)
    _tick_risk(disp, provider, 0.1)
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)

    _set_confidence(provider, rid, 0.95)
    _tick_risk(disp, provider, 0.1)

    loc = [e for e in _loc_events(events) if e["robot_id"] == rid]
    assert [e["event"] for e in loc].count("LOCALIZATION_RECOVERED") == 1
    st = [x for x in disp.localization_status() if x["robot_id"] == rid][0]
    assert st["state"] == "healthy"
    assert st["last_event"] == "LOCALIZATION_RECOVERED"


def test_anti_spam_no_repeat_same_event_per_tick(fast_risk_a):
    disp, provider, events = make_dispatcher()
    rid = next(iter(provider.robots))

    _set_confidence(provider, rid, 0.2)
    _tick_risk(disp, provider, 0.1)
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)
    for _ in range(10):
        _tick_risk(disp, provider, 0.1)

    per_robot = [e for e in _loc_events(events) if e["robot_id"] == rid]
    assert [e["event"] for e in per_robot].count("LOCALIZATION_DEGRADED") == 1
    assert [e["event"] for e in per_robot].count("LOCALIZATION_LOST") == 1


def test_status_endpoint_returns_state_per_robot(fast_risk_a):
    disp, provider, _ = make_dispatcher()
    appmod._dispatcher = disp
    appmod.app.config["TESTING"] = True
    rid = next(iter(provider.robots))

    _set_confidence(provider, rid, 0.2)
    _tick_risk(disp, provider, 0.1)
    _age_low_window(disp, rid, 1.0)
    _tick_risk(disp, provider, 0.1)

    client = appmod.app.test_client()
    resp = client.get("/risk-a/localization/status")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["enabled"] is True
    assert isinstance(body["robots"], list)
    row = [x for x in body["robots"] if x["robot_id"] == rid][0]
    assert set(row.keys()) == {"robot_id", "state", "since_ts", "confidence", "last_event"}


if __name__ == "__main__":
    import sys

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in tests:
        config.RISK_A_ENABLED = True
        config.SOAK_MODE = False
        config.LOC_DEGRADED_TIMEOUT_S = 0.2
        config.LOC_LOST_TIMEOUT_S = 0.5
        config.LOC_MIN_CONFIDENCE = 0.6
        config.LOC_CONFIDENCE_DECAY_RATE = 0.0
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
