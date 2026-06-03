"""
End-to-end integration tests for the OPC UA callbutton driver.

Spins up a real (in-process) asyncua server (the mock), points the real
``OpcUaCallbuttonDriver`` at it over localhost TCP, and asserts the full path:
connect → subscribe → rising-edge press → debounce → reconnect/resubscribe.

The driver runs in its own background thread/loop (as in production); the mock
server runs in the test's asyncio loop. They talk real OPC UA over TCP.

This repo's sandbox has asyncua but NOT pytest, so the file is also runnable
standalone:  ``python -m backend.tests.test_opcua_driver``
The pytest API is unchanged and runs identically under ``python -m pytest``.
"""
from __future__ import annotations

import asyncio
import time

try:
    import pytest
except ModuleNotFoundError:  # offline sandbox — minimal shim
    class _PytestShim:
        @staticmethod
        def mark(*a, **k):
            return lambda f: f
    pytest = _PytestShim()  # type: ignore

from backend.app import config
from backend.app.opcua import OpcUaCallbuttonDriver
from backend.tests.opcua_mock_server import MockOpcUaServer

ENDPOINT = "opc.tcp://127.0.0.1:48400/fleet"
CB1 = "ns=2;s=CallButton.CB1"
CB2 = "ns=2;s=CallButton.CB2"
NODE_MAP = {CB1: ("CB1", "fwd"), CB2: ("CB2", "ret")}


class FakeDispatcher:
    """Records button_pressed calls in order (thread-safe enough for this test)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def button_pressed(self, station_id: str, direction: str = "fwd"):
        self.calls.append((station_id, direction))
        return None


def _apply_fast_config() -> None:
    """Point the driver at the mock and shrink every timer for a fast run."""
    config.OPCUA_ENDPOINT = ENDPOINT
    config.OPCUA_NODE_MAP = dict(NODE_MAP)
    config.OPCUA_DEBOUNCE_S = 0.3
    config.OPCUA_HEALTH_S = 0.2
    config.OPCUA_RECONNECT_MIN_S = 0.2
    config.OPCUA_RECONNECT_MAX_S = 1.0
    config.OPCUA_SUB_PERIOD_MS = 50


async def _wait_for(predicate, timeout: float = 6.0, interval: float = 0.05) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        await asyncio.sleep(interval)
    return False


def _count(disp: FakeDispatcher, station: str) -> int:
    return sum(1 for s, _ in disp.calls if s == station)


# ── Tests ─────────────────────────────────────────────────────────────────────

async def _test_connect_rising_edge_and_no_refire() -> None:
    """(a) connect+subscribe; (b) rising edge fires once, held True does not refire;
    (c) True→False does not fire; rising edge re-arms after the line goes low."""
    _apply_fast_config()
    server = MockOpcUaServer(ENDPOINT, {CB1: False, CB2: False})
    await server.start()
    disp = FakeDispatcher()
    driver = OpcUaCallbuttonDriver(disp)
    driver.start()
    try:
        # (b) False → True fires exactly one ("CB1","fwd")
        await asyncio.sleep(0.4)               # let it connect + subscribe
        await server.set(CB1, True)
        assert await _wait_for(lambda: ("CB1", "fwd") in disp.calls), "press not delivered"
        assert _count(disp, "CB1") == 1, f"expected 1 press, got {disp.calls}"

        # True → True (write same value): no new datachange, must not refire
        await server.set(CB1, True)
        await asyncio.sleep(0.4)
        assert _count(disp, "CB1") == 1, f"held True refired: {disp.calls}"

        # (c) True → False: falling edge must not fire
        await server.set(CB1, False)
        await asyncio.sleep(0.4)               # also clears the debounce window
        assert _count(disp, "CB1") == 1, f"falling edge fired: {disp.calls}"

        # Re-arm: a fresh rising edge fires again
        await server.set(CB1, True)
        assert await _wait_for(lambda: _count(disp, "CB1") == 2), "rising edge did not re-arm"
        assert _count(disp, "CB2") == 0, "unexpected CB2 press"
    finally:
        driver.stop()
        await server.stop()


async def _test_debounce_suppresses_chatter() -> None:
    """A burst of False→True→False→True within the debounce window fires once."""
    _apply_fast_config()
    config.OPCUA_DEBOUNCE_S = 1.5               # wide window so the burst is inside it
    server = MockOpcUaServer(ENDPOINT, {CB1: False, CB2: False})
    await server.start()
    disp = FakeDispatcher()
    driver = OpcUaCallbuttonDriver(disp)
    driver.start()
    try:
        await asyncio.sleep(0.4)
        # rapid chatter
        for _ in range(4):
            await server.set(CB2, True)
            await asyncio.sleep(0.05)
            await server.set(CB2, False)
            await asyncio.sleep(0.05)
        assert await _wait_for(lambda: _count(disp, "CB2") >= 1), "no press from chatter"
        await asyncio.sleep(0.3)
        assert _count(disp, "CB2") == 1, f"debounce failed, got {disp.calls}"
    finally:
        driver.stop()
        await server.stop()


async def _test_missing_node_does_not_break_others() -> None:
    """A configured node absent from the server is skipped; the rest still work."""
    _apply_fast_config()
    config.OPCUA_NODE_MAP = {
        "ns=2;s=DoesNotExist": ("GHOST", "fwd"),
        CB1: ("CB1", "fwd"),
    }
    server = MockOpcUaServer(ENDPOINT, {CB1: False})   # ghost node not created
    await server.start()
    disp = FakeDispatcher()
    driver = OpcUaCallbuttonDriver(disp)
    driver.start()
    try:
        await asyncio.sleep(0.5)
        await server.set(CB1, True)
        assert await _wait_for(lambda: ("CB1", "fwd") in disp.calls), "good node not delivered"
        assert _count(disp, "GHOST") == 0
    finally:
        driver.stop()
        await server.stop()


async def _test_reconnect_resubscribes() -> None:
    """(d) kill+restart the server; driver re-subscribes and still delivers presses."""
    _apply_fast_config()
    server = MockOpcUaServer(ENDPOINT, {CB1: False, CB2: False})
    await server.start()
    disp = FakeDispatcher()
    driver = OpcUaCallbuttonDriver(disp)
    driver.start()
    try:
        await asyncio.sleep(0.4)
        await server.set(CB1, True)
        assert await _wait_for(lambda: _count(disp, "CB1") == 1), "pre-drop press failed"

        # Drop the server.
        await server.stop()
        await asyncio.sleep(0.6)               # let the driver notice + enter backoff

        # Bring it back on the same endpoint (fresh nodes, default False).
        server = MockOpcUaServer(ENDPOINT, {CB1: False, CB2: False})
        await server.start()

        # After resubscribe a new press must be delivered.
        async def _press_until_seen() -> bool:
            await server.set(CB2, True)
            await asyncio.sleep(0.15)
            await server.set(CB2, False)
            await asyncio.sleep(0.15)
            return _count(disp, "CB2") >= 1

        ok = False
        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline and not ok:
            ok = await _press_until_seen()
        assert ok, f"driver did not re-subscribe after reconnect: {disp.calls}"
    finally:
        driver.stop()
        await server.stop()


# pytest entrypoints (async bodies driven by asyncio.run so no pytest-asyncio needed)
def test_connect_rising_edge_and_no_refire():
    asyncio.run(_test_connect_rising_edge_and_no_refire())


def test_debounce_suppresses_chatter():
    asyncio.run(_test_debounce_suppresses_chatter())


def test_missing_node_does_not_break_others():
    asyncio.run(_test_missing_node_does_not_break_others())


def test_reconnect_resubscribes():
    asyncio.run(_test_reconnect_resubscribes())


# ── probe_node diagnostics tests ──────────────────────────────────────────────

async def _test_probe_node_reads_seeded_value() -> None:
    """probe_node against the mock server returns ok=True with the seeded value."""
    from backend.app.opcua import probe_node
    _apply_fast_config()
    server = MockOpcUaServer(ENDPOINT, {CB1: False})
    await server.start()
    try:
        await server.set(CB1, True)
        loop = asyncio.get_event_loop()
        # probe_node is sync (spins its own loop) → run in an executor thread.
        res = await loop.run_in_executor(None, lambda: probe_node(CB1, ENDPOINT, 4.0))
        assert res["ok"] is True, f"probe failed: {res}"
        assert res["value"] is True, f"unexpected value: {res}"
        assert res["error"] is None
        assert res["configured"] is True
        assert res["endpoint"] == ENDPOINT
    finally:
        await server.stop()


def _test_probe_node_empty_endpoint() -> None:
    """probe_node with endpoint='' is configured=False, ok=False, no exception."""
    from backend.app.opcua import probe_node
    res = probe_node(CB1, "", 1.0)
    assert res["ok"] is False, res
    assert res["configured"] is False, res
    assert res["value"] is None
    assert res["endpoint"] is None
    assert res["error"]


def _test_probe_node_unreachable() -> None:
    """probe_node against a bogus port returns ok=False with an error string."""
    from backend.app.opcua import probe_node
    bogus = "opc.tcp://127.0.0.1:1/none"
    res = probe_node(CB1, bogus, 1.0)
    assert res["ok"] is False, res
    assert res["configured"] is True, res
    assert res["value"] is None
    assert isinstance(res["error"], str) and res["error"]


# pytest entrypoints
def test_probe_node_reads_seeded_value():
    asyncio.run(_test_probe_node_reads_seeded_value())


def test_probe_node_empty_endpoint():
    _test_probe_node_empty_endpoint()


def test_probe_node_unreachable():
    _test_probe_node_unreachable()


# ── Standalone runner (offline sandbox: no pytest) ─────────────────────────────
if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(level=logging.WARNING)
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
