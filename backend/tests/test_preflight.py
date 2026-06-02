"""Preflight readiness validation tests.

Pure unit tests over `preflight.validate` — no async, no I/O. Also runnable as a
plain module in the offline sandbox (`python -m backend.tests.test_preflight`).
"""
from __future__ import annotations

try:
    import pytest  # noqa: F401
except ModuleNotFoundError:  # offline sandbox — minimal shim
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()  # type: ignore

from backend.app import config, preflight


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stations(extra=None, drop=None):
    base = [
        {"id": "AP1", "type": "ap", "label": "Almox", "x": 18, "y": 58, "seer_lm": "LM20"},
        {"id": "CB1", "type": "callbutton", "label": "Posto 1", "x": 12, "y": 18, "seer_lm": "LM10"},
        {"id": "BASE", "type": "base", "label": "Base", "x": 50, "y": 92, "seer_lm": "LM1"},
    ]
    if drop:
        base = [s for s in base if s["id"] not in drop]
    if extra:
        base = base + list(extra)
    return base


PAIRS = [{"supplier": "AP1", "consumer": "CB1"}]


class _FakeLandmark:
    def __init__(self, lm_id):
        self.id = lm_id


class _FakeMap:
    def __init__(self, lm_ids):
        self.landmarks = [_FakeLandmark(i) for i in lm_ids]


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_valid_config_is_ready():
    res = preflight.validate(_stations(), PAIRS, sim_mode=True)
    assert res.ok
    assert res.readiness == "ok"
    assert res.issues == []


def test_duplicate_station_id_blocks():
    dup = {"id": "CB1", "type": "callbutton", "label": "dup", "x": 1, "y": 1, "seer_lm": "LM10"}
    res = preflight.validate(_stations(extra=[dup]), PAIRS, sim_mode=True)
    assert not res.ok
    assert res.readiness == "blocked"
    assert any("Duplicate station id 'CB1'" in i for i in res.issues)


def test_missing_paired_station_blocks():
    res = preflight.validate(_stations(drop=["CB1"]), PAIRS, sim_mode=True)
    assert not res.ok
    assert any("consumer 'CB1' not found" in i for i in res.issues)


def test_missing_seer_lm_blocks_in_real_mode_only():
    stations = _stations(drop=["CB1"]) + [
        {"id": "CB1", "type": "callbutton", "label": "Posto 1", "x": 12, "y": 18, "seer_lm": ""}
    ]
    # Sim mode tolerates a missing landmark binding.
    assert preflight.validate(stations, PAIRS, sim_mode=True).ok
    # Real mode blocks on it.
    res = preflight.validate(stations, PAIRS, sim_mode=False)
    assert not res.ok
    assert any("no seer_lm landmark binding" in i for i in res.issues)


def test_missing_map_landmark_blocks():
    good_map = _FakeMap(["LM20", "LM10", "LM1"])
    assert preflight.validate(_stations(), PAIRS, sim_mode=True, map_model=good_map).ok

    bad_map = _FakeMap(["LM20"])  # CB1's LM10 absent
    res = preflight.validate(_stations(), PAIRS, sim_mode=True, map_model=bad_map)
    assert not res.ok
    assert any("LM10' not found in loaded map" in i for i in res.issues)


def test_real_repo_config_is_ready_in_sim_mode():
    """Guards against re-introducing the duplicate CB1 station id."""
    res = preflight.validate(config.STATIONS, config.PAIRS, sim_mode=True)
    assert res.ok, res.issues


# ── Standalone runner (offline sandbox; no pytest) ─────────────────────────────
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
