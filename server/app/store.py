"""Devices & callbutton config persistence (JSON file, config-as-source-of-truth).

Robot add/edit/delete and per-station OPC UA node overrides must survive a
backend restart. We keep ``config.ROBOTS`` / ``config.STATIONS`` as the live,
in-memory source of truth (every existing reader sees them) and mirror the
deltas to a small JSON file next to ``fleet.db``.

Design:
  * First run (file missing) → seed the JSON from current config defaults.
  * Subsequent runs → ``load_into_config()`` replaces ``config.ROBOTS`` contents
    in place and patches each station's ``opcua_node`` / ``opcua_ret``.
  * Every CRUD helper mutates the in-memory config list AND persists atomically
    (temp file + ``os.replace``) under a module-level lock.
  * Crash-safe: a corrupt/unreadable file logs a warning and falls back to the
    config defaults — it must never raise.
"""
from __future__ import annotations

import json
import logging
import os
import threading

from . import config

log = logging.getLogger(__name__)

_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "devices.json")
_lock = threading.Lock()


def _path() -> str:
    return getattr(config, "DEVICES_STORE_PATH", _DEFAULT_PATH)


def _station_overrides() -> dict:
    """Current per-station OPC UA fields from config.STATIONS."""
    return {
        s["id"]: {"opcua_node": s.get("opcua_node"), "opcua_ret": s.get("opcua_ret")}
        for s in config.STATIONS
    }


def _snapshot() -> dict:
    """Serializable view of what we persist."""
    return {
        "robots": [dict(r) for r in config.ROBOTS],
        "stations": _station_overrides(),
    }


def _atomic_write(data: dict) -> None:
    path = _path()
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _persist() -> None:
    """Write the current in-memory config snapshot to disk (best-effort)."""
    try:
        _atomic_write(_snapshot())
    except Exception as exc:  # noqa: BLE001 — persistence must never crash a request
        log.warning("devices store: persist failed (%s) — in-memory state kept", exc)


# ── Load / seed ───────────────────────────────────────────────────────────────

def load_into_config() -> None:
    """Hydrate config from the JSON store, seeding it on first run.

    On first run (file missing) seed the JSON from current config and write it.
    On later runs replace ``config.ROBOTS`` contents in place and patch each
    matching station's OPC UA fields. Corruption falls back to config defaults.
    """
    with _lock:
        path = _path()
        if not os.path.exists(path):
            try:
                _atomic_write(_snapshot())
            except Exception as exc:  # noqa: BLE001
                log.warning("devices store: seed write failed (%s)", exc)
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:  # noqa: BLE001 — corrupt file → fall back to defaults
            log.warning("devices store: unreadable (%s) — using config defaults", exc)
            return

        stored_robots = data.get("robots")
        if isinstance(stored_robots, list):
            config.ROBOTS[:] = [dict(r) for r in stored_robots if isinstance(r, dict)]

        stored_stations = data.get("stations")
        if isinstance(stored_stations, dict):
            by_id = {s["id"]: s for s in config.STATIONS}
            for sid, ov in stored_stations.items():
                s = by_id.get(sid)
                if s is None or not isinstance(ov, dict):
                    continue
                if "opcua_node" in ov:
                    s["opcua_node"] = ov["opcua_node"]
                if "opcua_ret" in ov:
                    s["opcua_ret"] = ov["opcua_ret"]


# ── Robot CRUD ────────────────────────────────────────────────────────────────

def _next_robot_id() -> str:
    existing = {r.get("id") for r in config.ROBOTS}
    n = 1
    while f"AMR-{n}" in existing:
        n += 1
    return f"AMR-{n}"


def add_robot(robot: dict) -> dict:
    """Append a robot to config.ROBOTS (assigning a unique id if missing) + persist."""
    with _lock:
        r = dict(robot)
        if not r.get("id"):
            r["id"] = _next_robot_id()
        if not r.get("name"):
            r["name"] = r["id"]
        r.setdefault("ip", "")
        config.ROBOTS.append(r)
        _persist()
        return r


def update_robot(robot_id: str, fields: dict) -> dict | None:
    """Update ip/name of a robot in config.ROBOTS + persist. None if unknown."""
    with _lock:
        for r in config.ROBOTS:
            if r.get("id") == robot_id:
                if "ip" in fields and fields["ip"] is not None:
                    r["ip"] = fields["ip"]
                if "name" in fields and fields["name"] is not None:
                    r["name"] = fields["name"]
                _persist()
                return r
        return None


def delete_robot(robot_id: str) -> bool:
    """Remove a robot from config.ROBOTS + persist. False if unknown."""
    with _lock:
        before = len(config.ROBOTS)
        config.ROBOTS[:] = [r for r in config.ROBOTS if r.get("id") != robot_id]
        if len(config.ROBOTS) == before:
            return False
        _persist()
        return True


# ── Station OPC UA override ────────────────────────────────────────────────────

def set_station_opcua(station_id: str, opcua_node: str | None, opcua_ret: str | None) -> bool:
    """Patch a station's opcua_node/opcua_ret in config.STATIONS + persist."""
    with _lock:
        for s in config.STATIONS:
            if s["id"] == station_id:
                s["opcua_node"] = opcua_node
                s["opcua_ret"] = opcua_ret
                _persist()
                return True
        return False
