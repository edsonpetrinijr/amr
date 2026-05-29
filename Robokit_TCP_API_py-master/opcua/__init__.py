"""
OPC UA callbutton driver — Phase 4.

Connects to Adilson's OPC UA server (config.OPCUA_ENDPOINT) and subscribes
to callbutton node changes using asyncua (already installed).

When a boolean node transitions False → True, fires dispatcher.callbutton_pressed().
Runs as a background asyncio thread, independent of Flask.

Configuration:
  OPCUA_ENDPOINT=opc.tcp://10.0.0.5:4840    (env or config.py)
  SIM_MODE=false

Each station in config.STATIONS with type=="callbutton" and opcua_node set
will be subscribed to. On first True read the button is treated as pressed.
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
    from asyncua import Client, ua
    HAS_ASYNCUA = True
except ImportError:
    HAS_ASYNCUA = False
    log.warning("asyncua not available — OPC UA driver disabled")


class _SubscriptionHandler:
    """asyncua subscription handler: fires dispatcher on rising-edge True."""

    def __init__(self, node_map: dict[str, str], dispatcher: 'Dispatcher') -> None:
        # node_map: {node_id_str → station_id}
        self._node_map   = node_map
        self._dispatcher = dispatcher
        self._last: dict[str, bool] = {}   # last known bool value per node

    def datachange_notification(self, node, val, data):
        node_id = str(node.nodeid)
        station_id = self._node_map.get(node_id)
        if station_id is None:
            return
        prev = self._last.get(node_id, False)
        cur  = bool(val)
        self._last[node_id] = cur
        if not prev and cur:
            log.info("[OpcUA] callbutton pressed: node=%s station=%s", node_id, station_id)
            task = self._dispatcher.callbutton_pressed(station_id)
            if task:
                log.info("[OpcUA] task created: %s", task.id)

    def event_notification(self, event):
        pass


class OpcUaCallbuttonDriver:
    """
    Subscribes to OPC UA nodes and fires callbutton_pressed on True rising edge.

    Usage:
        driver = OpcUaCallbuttonDriver(dispatcher)
        driver.start()   # launches background thread
        ...
        driver.stop()    # clean shutdown
    """

    def __init__(self, dispatcher: 'Dispatcher') -> None:
        self._dispatcher = dispatcher
        self._stop       = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self) -> None:
        if not HAS_ASYNCUA:
            log.warning("OpcUaCallbuttonDriver: asyncua unavailable, running stub")
            return
        if not config.OPCUA_ENDPOINT:
            log.info("OpcUaCallbuttonDriver: no OPCUA_ENDPOINT configured — skipping")
            return

        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="opcua-driver"
        )
        self._thread.start()
        log.info("OpcUaCallbuttonDriver started → %s", config.OPCUA_ENDPOINT)

    def stop(self) -> None:
        self._stop.set()
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    # ── Private ──────────────────────────────────────────────────────────────

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._monitor())
        except Exception as e:
            log.error("OpcUA loop error: %s", e)
        finally:
            self._loop.close()

    async def _monitor(self) -> None:
        # Build node → station map from config
        cb_stations = [
            s for s in config.STATIONS
            if s['type'] == 'callbutton' and s.get('opcua_node')
        ]
        if not cb_stations:
            log.info("No OPC UA callbutton nodes configured")
            return

        reconnect_wait = 10.0
        while not self._stop.is_set():
            try:
                async with Client(config.OPCUA_ENDPOINT) as client:
                    log.info("[OpcUA] connected to %s", config.OPCUA_ENDPOINT)

                    # Map resolved NodeId → station_id
                    node_map: dict[str, str] = {}
                    nodes = []
                    for s in cb_stations:
                        node = client.get_node(s['opcua_node'])
                        resolved = str(node.nodeid)
                        node_map[resolved] = s['id']
                        nodes.append(node)
                        log.info("  subscribed: %s → %s", s['opcua_node'], s['id'])

                    handler      = _SubscriptionHandler(node_map, self._dispatcher)
                    subscription = await client.create_subscription(500, handler)
                    await subscription.subscribe_data_change(nodes)

                    # Keep alive until stop is requested or exception
                    while not self._stop.is_set():
                        await asyncio.sleep(1)

                    await subscription.delete()

            except Exception as e:
                if self._stop.is_set():
                    break
                log.warning("[OpcUA] connection error: %s — retry in %.0fs", e, reconnect_wait)
                await asyncio.sleep(reconnect_wait)

