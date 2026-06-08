"""
End-to-end integration tests for the OPC UA callbutton ACTION bindings.

Same harness as ``test_opcua_driver.py`` (real in-process asyncua mock server,
real ``OpcUaCallbuttonDriver`` over localhost TCP), but exercises the
``config.OPCUA_ACTION_MAP`` path: a configured node-id routes a debounced rising
edge to ``action_handler(action_name)`` instead of ``dispatcher.button_pressed``.

Runnable standalone (offline sandbox has asyncua but not pytest):
    python -m server.tests.test_opcua_action_bindings
"""
from __future__ import annotations

import asyncio
import time

try:
    import pytest
except ModuleNotFoundError:  # offline sandbox â€” minimal shim
    class _PytestShim:
        @staticmethod
        def mark(*a, **k):
            return lambda f: f
    pytest = _PytestShim()  # type: ignore

from server.app import config
from server.app.opcua import OpcUaCallbuttonDriver
from server.tests.opcua_mock_server import MockOpcUaServer

ENDPOINT = "opc.tcp://127.0.0.1:48401/fleet"
ACT_A = "ns=2;s=CallButton.ActA"   # â†’ confirm-delivery
ACT_B = "ns=2;s=CallButton.ActB"   # â†’ request-empty
CB1 = "ns=2;s=CallButton.CB1"      # normal station node
ACTION_MAP = {ACT_A: "confirm-delivery", ACT_B: "request-empty"}


class FakeDispatcher:
    """Records button_pressed calls in order (thread-safe enough for this test)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def button_pressed(self, station_id: str, direction: str = "fwd"):
        self.calls.append((station_id, direction))
        return None


class FakeActionHandler:
    """Records action_handler(action_name) calls in order."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, action: str) -> None:
        self.calls.append(action)


def _apply_fast_config(node_map: dict | None = None,
                       action_map: dict | None = None) -> None:
    """Point the driver at the mock and shrink every timer for a fast run."""
    config.OPCUA_ENDPOINT = ENDPOINT
    config.OPCUA_NODE_MAP = dict(node_map or {})
    config.OPCUA_ACTION_MAP = dict(action_map or {})
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


def _count(handler: FakeActionHandler, action: str) -> int:
    return sum(1 for a in handler.calls if a == action)


# â”€â”€ Tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async def _test_action_rising_edge_and_no_refire() -> None:
    """ACT_A: Falseâ†’True fires one confirm-delivery; held True / falling edge don't;
    rising edge re-arms after the line goes low."""
    _apply_fast_config(action_map=ACTION_MAP)
    server = MockOpcUaServer(ENDPOINT, {ACT_A: False, ACT_B: False})
    await server.start()
    disp = FakeDispatcher()
    actions = FakeActionHandler()
    driver = OpcUaCallbuttonDriver(disp, action_handler=actions)
    driver.start()
    try:
        await asyncio.sleep(0.4)               # connect + subscribe
        await server.set(ACT_A, True)
        assert await _wait_for(lambda: "confirm-delivery" in actions.calls), "action not delivered"
        assert _count(actions, "confirm-delivery") == 1, f"expected 1, got {actions.calls}"

        # Held True (same value re-written): no datachange, must not refire.
        await server.set(ACT_A, True)
        await asyncio.sleep(0.4)
        assert _count(actions, "confirm-delivery") == 1, f"held True refired: {actions.calls}"

        # True â†’ False: falling edge must not fire.
        await server.set(ACT_A, False)
        await asyncio.sleep(0.4)               # also clears debounce window
        assert _count(actions, "confirm-delivery") == 1, f"falling edge fired: {actions.calls}"

        # Re-arm: a fresh rising edge fires again.
        await server.set(ACT_A, True)
        assert await _wait_for(lambda: _count(actions, "confirm-delivery") == 2), "did not re-arm"

        # No spurious dispatcher calls â€” action nodes never hit the dispatcher.
        assert disp.calls == [], f"unexpected dispatcher calls: {disp.calls}"
    finally:
        driver.stop()
        await server.stop()
        config.OPCUA_ACTION_MAP = {}


async def _test_action_b_fires_request_empty() -> None:
    """ACT_B routes to action_handler('request-empty')."""
    _apply_fast_config(action_map=ACTION_MAP)
    server = MockOpcUaServer(ENDPOINT, {ACT_A: False, ACT_B: False})
    await server.start()
    disp = FakeDispatcher()
    actions = FakeActionHandler()
    driver = OpcUaCallbuttonDriver(disp, action_handler=actions)
    driver.start()
    try:
        await asyncio.sleep(0.4)
        await server.set(ACT_B, True)
        assert await _wait_for(lambda: "request-empty" in actions.calls), "request-empty not delivered"
        assert _count(actions, "request-empty") == 1, f"expected 1, got {actions.calls}"
        assert _count(actions, "confirm-delivery") == 0, "wrong action fired"
        assert disp.calls == [], f"unexpected dispatcher calls: {disp.calls}"
    finally:
        driver.stop()
        await server.stop()
        config.OPCUA_ACTION_MAP = {}


async def _test_mixed_map_station_vs_action() -> None:
    """A normal station node calls dispatcher.button_pressed and NOT the action
    handler; an action node calls the action handler and NOT the dispatcher."""
    _apply_fast_config(node_map={CB1: ("CB1", "fwd")}, action_map=ACTION_MAP)
    server = MockOpcUaServer(ENDPOINT, {CB1: False, ACT_A: False, ACT_B: False})
    await server.start()
    disp = FakeDispatcher()
    actions = FakeActionHandler()
    driver = OpcUaCallbuttonDriver(disp, action_handler=actions)
    driver.start()
    try:
        await asyncio.sleep(0.4)

        # Station node â†’ dispatcher only.
        await server.set(CB1, True)
        assert await _wait_for(lambda: ("CB1", "fwd") in disp.calls), "station press not delivered"
        assert actions.calls == [], f"station press leaked to action handler: {actions.calls}"

        # Action node â†’ action handler only.
        await server.set(ACT_A, True)
        assert await _wait_for(lambda: "confirm-delivery" in actions.calls), "action not delivered"
        assert disp.calls == [("CB1", "fwd")], f"action leaked to dispatcher: {disp.calls}"
    finally:
        driver.stop()
        await server.stop()
        config.OPCUA_ACTION_MAP = {}


async def _test_action_handler_none_does_not_crash() -> None:
    """action_handler=None with action nodes configured: pressing an action node
    must not crash the driver; the station path still works."""
    _apply_fast_config(node_map={CB1: ("CB1", "fwd")}, action_map=ACTION_MAP)
    server = MockOpcUaServer(ENDPOINT, {CB1: False, ACT_A: False})
    await server.start()
    disp = FakeDispatcher()
    driver = OpcUaCallbuttonDriver(disp)   # no action_handler
    driver.start()
    try:
        await asyncio.sleep(0.4)
        # Fire the action node â€” should be a no-op (logged + skipped), no crash.
        await server.set(ACT_A, True)
        await asyncio.sleep(0.4)
        # Station node still works â†’ proves the subscription is alive.
        await server.set(CB1, True)
        assert await _wait_for(lambda: ("CB1", "fwd") in disp.calls), "station broke after action no-op"
    finally:
        driver.stop()
        await server.stop()
        config.OPCUA_ACTION_MAP = {}


# pytest entrypoints (async bodies driven by asyncio.run so no pytest-asyncio needed)
def test_action_rising_edge_and_no_refire():
    asyncio.run(_test_action_rising_edge_and_no_refire())


def test_action_b_fires_request_empty():
    asyncio.run(_test_action_b_fires_request_empty())


def test_mixed_map_station_vs_action():
    asyncio.run(_test_mixed_map_station_vs_action())


def test_action_handler_none_does_not_crash():
    asyncio.run(_test_action_handler_none_does_not_crash())


# â”€â”€ Standalone runner (offline sandbox: no pytest) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
