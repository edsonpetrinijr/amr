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
from typing import Callable, Optional, TYPE_CHECKING

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


def build_action_map() -> dict[str, str]:
    """node_id_str → action name ("confirm-delivery" | "request-empty").

    Read from ``config.OPCUA_ACTION_MAP`` (added by backend; env-overridable JSON,
    defaults to {}). Fall back to an empty map if config doesn't define it yet so
    this module imports cleanly before the backend change lands.
    """
    return dict(getattr(config, "OPCUA_ACTION_MAP", {}) or {})


def _jsonable(value):
    """Coerce an OPC UA read value to a JSON-serializable scalar."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)) or value is None:
        return value
    try:
        return str(value)
    except Exception:
        return None


def probe_node(node_id: str, endpoint: Optional[str] = None,
               timeout: float = 3.0) -> dict:
    """Read a single OPC UA node value for diagnostics. NEVER raises.

    Returns a dict:
        {ok, value, error, configured, endpoint}

      * ok        — True only if the value was read successfully.
      * value     — JSON-serializable node value, else None.
      * error     — None on success, else a clear message (with the exception).
      * configured— whether an endpoint is configured/usable.
      * endpoint  — the endpoint used (or None when unconfigured).

    Called from a Flask request thread, so it spins up its own event loop.
    """
    if endpoint is None:
        endpoint = config.OPCUA_ENDPOINT

    if not HAS_ASYNCUA:
        return {"ok": False, "value": None, "error": "asyncua not installed",
                "configured": bool(endpoint), "endpoint": endpoint or None}

    if not endpoint or not str(endpoint).strip():
        return {"ok": False, "value": None,
                "error": "no OPC UA endpoint configured",
                "configured": False, "endpoint": None}

    endpoint = str(endpoint).strip()

    async def _read() -> dict:
        async def _connect_and_read():
            async with Client(endpoint) as client:
                node = client.get_node(node_id)
                return await node.read_value()
        value = await asyncio.wait_for(_connect_and_read(), timeout=timeout)
        return {"ok": True, "value": _jsonable(value), "error": None,
                "configured": True, "endpoint": endpoint}

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_read())
    except asyncio.TimeoutError:
        return {"ok": False, "value": None,
                "error": f"timeout after {timeout}s connecting to {endpoint}",
                "configured": True, "endpoint": endpoint}
    except Exception as e:  # noqa: BLE001 — diagnostics must never raise
        return {"ok": False, "value": None,
                "error": f"{type(e).__name__}: {e}",
                "configured": True, "endpoint": endpoint}
    finally:
        try:
            loop.close()
        except Exception:
            pass
        asyncio.set_event_loop(None)


class _SubscriptionHandler:
    """asyncua subscription handler: fires dispatcher/action on rising-edge True, debounced.

    A node-id present in ``action_map`` is routed to ``action_handler(action_name)``
    instead of the dispatcher. ``action_map`` takes precedence over ``node_map`` if a
    node-id appears in both.
    """

    def __init__(self, node_map: dict[str, tuple[str, str]], dispatcher: "Dispatcher",
                 debounce_s: float,
                 action_map: Optional[dict[str, str]] = None,
                 action_handler: Optional[Callable[[str], None]] = None) -> None:
        self._node_map = node_map
        self._dispatcher = dispatcher
        self._debounce_s = debounce_s
        self._action_map = action_map or {}
        self._action_handler = action_handler
        self._last: dict[str, bool] = {}
        self._last_fire: dict[str, float] = {}

    def seed(self, node_id: str, val: bool) -> None:
        """Record a node's current value WITHOUT firing (used on (re)connect)."""
        self._last[node_id] = bool(val)

    def datachange_notification(self, node, val, data):  # noqa: ANN001 (asyncua API)
        node_id = node.nodeid.to_string()
        action = self._action_map.get(node_id)         # action map wins over station map
        entry = None if action is not None else self._node_map.get(node_id)
        if action is None and entry is None:
            return

        prev = self._last.get(node_id, False)
        cur = bool(val)
        self._last[node_id] = cur

        if prev or not cur:
            return  # only False → True is a press

        now = time.monotonic()
        if now - self._last_fire.get(node_id, -1e9) < self._debounce_s:
            log.debug("[OpcUA] debounced rising edge node=%s", node_id)
            return
        self._last_fire[node_id] = now

        if action is not None:
            if self._action_handler is None:
                log.warning("[OpcUA] action node %s fired (%s) but no action_handler "
                            "configured — skipping", node_id, action)
                return
            log.info("[OpcUA] action button pressed: node=%s action=%s", node_id, action)
            try:
                self._action_handler(action)
            except Exception as e:  # noqa: BLE001 — never let a handler exception kill the sub
                log.exception("[OpcUA] action_handler failed for %s (%s): %s",
                              node_id, action, e)
            return

        station_id, direction = entry
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

    def __init__(self, dispatcher: "Dispatcher",
                 action_handler: Optional[Callable[[str], None]] = None) -> None:
        self._dispatcher = dispatcher
        self._action_handler = action_handler
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
        self._thread = None

    def restart(self, timeout: float = 5.0) -> None:
        """Hot-rebuild the driver: stop the monitor thread, then start again so it
        re-reads config.STATIONS (via build_node_map) and resubscribes with the
        edited OPC UA nodes. Safe to call when never started / asyncua missing /
        no endpoint — start() no-ops gracefully in those cases."""
        self.stop(timeout=timeout)
        self._stop.clear()
        self.start()
        log.info("OpcUaCallbuttonDriver restarted (node map rebuilt)")

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
        action_map = build_action_map()

        # Warn on any node configured as both station and action (action wins).
        overlap = set(node_map) & set(action_map)
        for nid in overlap:
            log.warning("[OpcUA] node %s in both station and action maps — treating as "
                        "action (%s)", nid, action_map[nid])

        if not node_map and not action_map:
            log.info("No OPC UA callbutton nodes configured")
            return

        if action_map and self._action_handler is None:
            log.warning("[OpcUA] %d action node(s) configured but no action_handler — "
                        "they will be subscribed but presses are skipped", len(action_map))

        # Union of node-ids to subscribe; action map takes precedence over station map.
        # value = ("action", name) | ("station", (station_id, direction))
        targets: dict[str, tuple[str, object]] = {}
        for nid, entry in node_map.items():
            targets[nid] = ("station", entry)
        for nid, name in action_map.items():
            targets[nid] = ("action", name)

        backoff = config.OPCUA_RECONNECT_MIN_S
        while not self._stop.is_set():
            try:
                async with Client(config.OPCUA_ENDPOINT) as client:
                    log.info("[OpcUA] connected to %s", config.OPCUA_ENDPOINT)
                    backoff = config.OPCUA_RECONNECT_MIN_S  # reset after a good connect

                    handler = _SubscriptionHandler(node_map, self._dispatcher,
                                                   config.OPCUA_DEBOUNCE_S,
                                                   action_map=action_map,
                                                   action_handler=self._action_handler)
                    subscription = await client.create_subscription(
                        config.OPCUA_SUB_PERIOD_MS, handler
                    )

                    subscribed = 0
                    for node_id, (kind, payload) in targets.items():
                        label = (f"action={payload}" if kind == "action"
                                 else f"{payload[0]}/{payload[1]}")
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
                            log.info("[OpcUA] subscribed %s → %s", node_id, label)
                        except Exception as e:  # noqa: BLE001 — skip bad node, keep the rest
                            log.warning("[OpcUA] node %s (%s) unavailable: %s — skipping",
                                        node_id, label, e)

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
