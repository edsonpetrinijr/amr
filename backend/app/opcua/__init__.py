"""
OPC UA callbutton driver — Phase 4.

Connects to the plant's OPC UA server (``config.OPCUA_ENDPOINT``) and subscribes
to callbutton boolean nodes using asyncua (pinned in requirements.txt).

When a boolean node transitions False → True (rising edge) it fires
``dispatcher.button_pressed(station_id, direction)``. Runs as a background
asyncio thread, independent of Flask.

Disabled cleanly when:
  * ``asyncua`` is not importable (logs "asyncua not available — OPC UA driver disabled"); or
  * ``OPCUA_ENDPOINT`` is empty.

Node → (station_id, direction) mapping comes from config:
  * ``config.OPCUA_NODE_MAP`` (explicit override) if set, else
  * derived from ``config.STATIONS`` (``opcua_node`` → fwd, ``opcua_ret`` → ret).

Hardening (single-plant pilot):
  * Bounded exponential reconnect/resubscribe backoff if the server drops.
  * A liveness ping (``OPCUA_HEALTH_S``) so a silent TCP drop is actually noticed.
  * Per-node subscribe: a missing/bad node logs a warning and is skipped — the
    rest of the buttons keep working.
  * Rising-edge debounce (``OPCUA_DEBOUNCE_S``) so a noisy/held button cannot
    spam the dispatcher.
  * On (re)connect each node's current value is seeded so an already-held True
    does not produce a spurious press.

Configuration (all env-overridable, see config.py):
  OPCUA_ENDPOINT, OPCUA_NODE_MAP, OPCUA_DEBOUNCE_S, OPCUA_RECONNECT_MIN_S,
  OPCUA_RECONNECT_MAX_S, OPCUA_SUB_PERIOD_MS, OPCUA_HEALTH_S
"""
from __future__ import annotations

import asyncio
import logging
import threading
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..dispatcher import Dispatcher

from .. import config

log = logging.getLogger(__name__)

# asyncua may not be available in all envs — we guard gracefully
try:
    from asyncua import Client, ua  # noqa: F401  (ua kept for parity / future use)
    HAS_ASYNCUA = True
except ImportError:
    HAS_ASYNCUA = False
    log.warning("asyncua not available — OPC UA driver disabled")


def build_node_map() -> dict[str, tuple[str, str]]:
    """node_id_str → (station_id, direction). Config override wins; else STATIONS."""
    if config.OPCUA_NODE_MAP:
        return dict(config.OPCUA_NODE_MAP)
    node_map: dict[str, tuple[str, str]] = {}
    for s in config.STATIONS:
        if s.get("opcua_node"):
            node_map[s["opcua_node"]] = (s["id"], "fwd")
        if s.get("opcua_ret"):
            node_map[s["opcua_ret"]] = (s["id"], "ret")
    return node_map


class _SubscriptionHandler:
    """asyncua subscription handler: fires dispatcher on rising-edge True, debounced."""

    def __init__(self, node_map: dict[str, tuple[str, str]], dispatcher: "Dispatcher",
                 debounce_s: float) -> None:
        self._node_map = node_map
        self._dispatcher = dispatcher
        self._debounce_s = debounce_s
        self._last: dict[str, bool] = {}
        self._last_fire: dict[str, float] = {}

    def seed(self, node_id: str, val: bool) -> None:
        """Record a node's current value WITHOUT firing (used on (re)connect)."""
        self._last[node_id] = bool(val)

    def datachange_notification(self, node, val, data):  # noqa: ANN001 (asyncua API)
        node_id = node.nodeid.to_string()
        entry = self._node_map.get(node_id)
        if entry is None:
            return
        station_id, direction = entry
        prev = self._last.get(node_id, False)
        cur = bool(val)
        self._last[node_id] = cur

        if prev or not cur:
            return  # only False → True is a press

        now = time.monotonic()
        if now - self._last_fire.get(node_id, -1e9) < self._debounce_s:
            log.debug("[OpcUA] debounced rising edge node=%s station=%s", node_id, station_id)
            return
        self._last_fire[node_id] = now

        log.info("[OpcUA] button pressed: node=%s station=%s dir=%s", node_id, station_id, direction)
        try:
            task = self._dispatcher.button_pressed(station_id, direction)
        except Exception as e:  # noqa: BLE001 — never let a handler exception kill the sub
            log.exception("[OpcUA] dispatcher.button_pressed failed for %s: %s", station_id, e)
            return
        if task:
            log.info("[OpcUA] task created: %s", task.id)

    def event_notification(self, event):  # noqa: ANN001 (asyncua API)
        pass

    def status_change_notification(self, status):  # noqa: ANN001 (asyncua API)
        pass


class OpcUaCallbuttonDriver:
    """
    Subscribes to OPC UA nodes and fires button_pressed on True rising edge.

    Usage:
        driver = OpcUaCallbuttonDriver(dispatcher)
        driver.start()   # launches background thread
        ...
        driver.stop()    # clean shutdown
    """

    def __init__(self, dispatcher: "Dispatcher") -> None:
        self._dispatcher = dispatcher
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self) -> None:
        if not HAS_ASYNCUA:
            log.warning("OpcUaCallbuttonDriver: asyncua unavailable, running stub")
            return
        if not config.OPCUA_ENDPOINT:
            log.info("OpcUaCallbuttonDriver: no OPCUA_ENDPOINT configured — skipping")
            return

        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="opcua-driver"
        )
        self._thread.start()
        log.info("OpcUaCallbuttonDriver started → %s", config.OPCUA_ENDPOINT)

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        t = self._thread
        if t and t.is_alive():
            t.join(timeout=timeout)

    # ── Private ──────────────────────────────────────────────────────────────

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._monitor())
        except Exception as e:  # noqa: BLE001 — must not crash the process
            log.error("OpcUA loop error: %s", e)
        finally:
            self._loop.close()

    async def _sleep_interruptible(self, seconds: float) -> None:
        """Sleep up to `seconds`, but wake promptly when stop is requested."""
        waited = 0.0
        while waited < seconds and not self._stop.is_set():
            await asyncio.sleep(min(0.1, seconds - waited))
            waited += 0.1

    async def _monitor(self) -> None:
        node_map = build_node_map()
        if not node_map:
            log.info("No OPC UA callbutton nodes configured")
            return

        backoff = config.OPCUA_RECONNECT_MIN_S
        while not self._stop.is_set():
            try:
                async with Client(config.OPCUA_ENDPOINT) as client:
                    log.info("[OpcUA] connected to %s", config.OPCUA_ENDPOINT)
                    backoff = config.OPCUA_RECONNECT_MIN_S  # reset after a good connect

                    handler = _SubscriptionHandler(node_map, self._dispatcher,
                                                   config.OPCUA_DEBOUNCE_S)
                    subscription = await client.create_subscription(
                        config.OPCUA_SUB_PERIOD_MS, handler
                    )

                    subscribed = 0
                    for node_id, (station, direction) in node_map.items():
                        node = client.get_node(node_id)
                        key = node.nodeid.to_string()
                        try:
                            # Seed current value so a held True doesn't fire on connect.
                            try:
                                handler.seed(key, await node.read_value())
                            except Exception:  # noqa: BLE001 — read may fail; assume not pressed
                                handler.seed(key, False)
                            await subscription.subscribe_data_change(node)
                            subscribed += 1
                            log.info("[OpcUA] subscribed %s → %s/%s", node_id, station, direction)
                        except Exception as e:  # noqa: BLE001 — skip bad node, keep the rest
                            log.warning("[OpcUA] node %s (%s/%s) unavailable: %s — skipping",
                                        node_id, station, direction, e)

                    if subscribed == 0:
                        raise RuntimeError("no OPC UA nodes could be subscribed")

                    # Keep alive + actively detect a silent drop via a liveness ping.
                    while not self._stop.is_set():
                        await self._sleep_interruptible(config.OPCUA_HEALTH_S)
                        if self._stop.is_set():
                            break
                        await client.check_connection()

                    try:
                        await subscription.delete()
                    except Exception:  # noqa: BLE001 — best-effort cleanup
                        pass

            except Exception as e:  # noqa: BLE001 — reconnect, never crash the thread
                if self._stop.is_set():
                    break
                log.warning("[OpcUA] connection/subscription error: %s — retry in %.1fs",
                            e, backoff)
                await self._sleep_interruptible(backoff)
                backoff = min(backoff * 2, config.OPCUA_RECONNECT_MAX_S)
