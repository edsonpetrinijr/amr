"""
Telemetry capture for a supervised soak run — DATA CAPTURE ONLY.

Dual sink, both stamped with a single ``run_id`` and the authoritative
``cycle_id`` / ``step`` supplied by the SoakRunner state machine:

  • JSONL firehose  — append-only, one JSON object per line, flushed per line.
                      Crash-proof source of truth, fully replayable.
  • sqlite fleet.db — queryable mirror (telemetry / events / cycles tables).
                      Telemetry inserts are BATCHED so the sampler/poll thread
                      never blocks on disk; events/cycles are low-volume and
                      committed promptly.

This is a module-level singleton (same pattern as db.py). Call ``init()`` once
at startup, then ``write_telemetry`` / ``write_event`` / ``write_cycle`` from
any thread.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time

from . import config

log = logging.getLogger(__name__)

# ── Column orders (single source of truth for INSERTs) ──────────────────────
TELEMETRY_COLS = [
    "run_id", "robot_id", "ts", "ts_mono", "cycle_id", "step",
    "x", "y", "theta", "vx", "vy", "w", "battery",
    "task_status", "target_id", "connected", "last_seen_age",
    "blocked", "confidence", "lift_di", "lift_do",
]
EVENT_COLS = ["run_id", "robot_id", "ts", "cycle_id", "step", "event", "target", "detail"]
CYCLE_COLS = [
    "run_id", "robot_id", "cycle_id", "t_start", "t_end", "duration_s",
    "goto_a_s", "time_to_lift_s", "goto_b_s", "time_to_lower_s",
    "dwell_a_s", "dwell_b_s", "idle_wait_s",
    "distance_m", "obstacle_stops", "nav_failures", "relocalizations",
    "max_pose_jump_m", "battery_start", "battery_end", "battery_delta",
    "stop_err_a_xy", "stop_err_a_theta", "stop_err_b_xy", "stop_err_b_theta",
    "conf_at_pick", "conf_at_drop", "lift_ok",
    "cycle_time_delta_vs_prev_s", "duration_mean_s", "duration_stddev_s",
]

_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS telemetry (
    {", ".join(c + _t for c, _t in [
        ("run_id", " TEXT"), ("robot_id", " TEXT"), ("ts", " REAL"), ("ts_mono", " REAL"),
        ("cycle_id", " INTEGER"), ("step", " TEXT"),
        ("x", " REAL"), ("y", " REAL"), ("theta", " REAL"),
        ("vx", " REAL"), ("vy", " REAL"), ("w", " REAL"), ("battery", " REAL"),
        ("task_status", " INTEGER"), ("target_id", " TEXT"), ("connected", " INTEGER"),
        ("last_seen_age", " REAL"), ("blocked", " INTEGER"), ("confidence", " REAL"),
        ("lift_di", " INTEGER"), ("lift_do", " INTEGER"),
    ])}
);
CREATE TABLE IF NOT EXISTS events (
    run_id TEXT, robot_id TEXT, ts REAL, cycle_id INTEGER, step TEXT,
    event TEXT, target TEXT, detail TEXT
);
CREATE TABLE IF NOT EXISTS cycles (
    run_id TEXT, robot_id TEXT, cycle_id INTEGER,
    t_start REAL, t_end REAL, duration_s REAL,
    goto_a_s REAL, time_to_lift_s REAL, goto_b_s REAL, time_to_lower_s REAL,
    dwell_a_s REAL, dwell_b_s REAL, idle_wait_s REAL,
    distance_m REAL, obstacle_stops INTEGER, nav_failures INTEGER, relocalizations INTEGER,
    max_pose_jump_m REAL, battery_start REAL, battery_end REAL, battery_delta REAL,
    stop_err_a_xy REAL, stop_err_a_theta REAL, stop_err_b_xy REAL, stop_err_b_theta REAL,
    conf_at_pick REAL, conf_at_drop REAL, lift_ok INTEGER,
    cycle_time_delta_vs_prev_s REAL, duration_mean_s REAL, duration_stddev_s REAL
);
CREATE INDEX IF NOT EXISTS idx_tel_run_cycle ON telemetry(run_id, cycle_id, ts);
CREATE INDEX IF NOT EXISTS idx_evt_run_cycle ON events(run_id, cycle_id, ts);
CREATE INDEX IF NOT EXISTS idx_cyc_run_cycle ON cycles(run_id, cycle_id);
"""


class _Writer:
    def __init__(self) -> None:
        self.run_id: str = config.RUN_ID
        self._jsonl = None
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()
        self._tel_buf: list[tuple] = []
        self._last_commit = 0.0
        self._started = False

    def init(self) -> None:
        if self._started:
            return
        os.makedirs(os.path.dirname(config.JSONL_PATH), exist_ok=True)
        self._jsonl = open(config.JSONL_PATH, "a", encoding="utf-8")
        self._conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        self._conn.execute("PRAGMA busy_timeout=5000")  # share fleet.db with db.py without lock errors
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        self._last_commit = time.monotonic()
        self._started = True
        log.info("telemetry: run_id=%s jsonl=%s db=%s", self.run_id, config.JSONL_PATH, config.DB_PATH)

    # ── JSONL helpers ──────────────────────────────────────────────────────
    def _jsonl_write(self, kind: str, row: dict) -> None:
        if self._jsonl is None:
            return
        line = json.dumps({"kind": kind, **row}, separators=(",", ":"), default=str)
        self._jsonl.write(line + "\n")
        self._jsonl.flush()  # per-line flush → crash-proof firehose

    # ── Public API ─────────────────────────────────────────────────────────
    def write_telemetry(self, row: dict) -> None:
        with self._lock:
            self._jsonl_write("telemetry", row)
            if self._conn is not None:
                self._tel_buf.append(tuple(row.get(c) for c in TELEMETRY_COLS))
                self._maybe_commit_locked()

    def write_event(self, row: dict) -> None:
        with self._lock:
            self._jsonl_write("event", row)
            if self._conn is not None:
                detail = row.get("detail")
                if not isinstance(detail, str):
                    detail = json.dumps(detail, default=str) if detail is not None else None
                vals = tuple(detail if c == "detail" else row.get(c) for c in EVENT_COLS)
                self._conn.execute(
                    f"INSERT INTO events({','.join(EVENT_COLS)}) VALUES ({','.join('?' * len(EVENT_COLS))})",
                    vals,
                )
                self._maybe_commit_locked(force=True)  # events are rare + diagnostic — keep durable

    def write_cycle(self, row: dict) -> None:
        with self._lock:
            self._jsonl_write("cycle", row)
            if self._conn is not None:
                vals = tuple(row.get(c) for c in CYCLE_COLS)
                self._conn.execute(
                    f"INSERT INTO cycles({','.join(CYCLE_COLS)}) VALUES ({','.join('?' * len(CYCLE_COLS))})",
                    vals,
                )
                self._maybe_commit_locked(force=True)

    # ── Batched commit ─────────────────────────────────────────────────────
    def _maybe_commit_locked(self, force: bool = False) -> None:
        if self._conn is None:
            return
        now = time.monotonic()
        if self._tel_buf and (force or len(self._tel_buf) >= 200
                              or now - self._last_commit >= config.TELEMETRY_COMMIT_S):
            self._conn.executemany(
                f"INSERT INTO telemetry({','.join(TELEMETRY_COLS)}) "
                f"VALUES ({','.join('?' * len(TELEMETRY_COLS))})",
                self._tel_buf,
            )
            self._tel_buf.clear()
        if force or now - self._last_commit >= config.TELEMETRY_COMMIT_S:
            self._conn.commit()
            self._last_commit = now

    def flush(self) -> None:
        with self._lock:
            self._maybe_commit_locked(force=True)

    def close(self) -> None:
        with self._lock:
            self._maybe_commit_locked(force=True)
            if self._conn is not None:
                self._conn.commit()
            if self._jsonl is not None:
                self._jsonl.flush()
                self._jsonl.close()
                self._jsonl = None


_writer = _Writer()


def init() -> None:
    _writer.init()


def write_telemetry(row: dict) -> None:
    _writer.write_telemetry(row)


def write_event(run_id: str, robot_id: str, cycle_id, step, event: str,
                target=None, detail=None, ts: float | None = None) -> None:
    _writer.write_event({
        "run_id": run_id, "robot_id": robot_id, "ts": ts if ts is not None else time.time(),
        "cycle_id": cycle_id, "step": step, "event": event, "target": target, "detail": detail,
    })


def write_cycle(row: dict) -> None:
    _writer.write_cycle(row)


def flush() -> None:
    _writer.flush()


def close() -> None:
    _writer.close()


def print_run_banner() -> None:
    """Prominent wall-clock + run_id banner so the human supervisor can sync
    their paper/text log to the telemetry timeline."""
    wall = time.time()
    human = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(wall))
    bar = "=" * 72
    msg = (
        f"\n{bar}\n"
        f"  SOAK TELEMETRY RUN STARTED\n"
        f"  RUN_ID        : {config.RUN_ID}\n"
        f"  WALL CLOCK    : {human}  (epoch {wall:.3f})\n"
        f"  MONOTONIC REF : {time.monotonic():.3f}\n"
        f"  SAMPLE_HZ     : {config.SAMPLE_HZ}\n"
        f"  JSONL         : {config.JSONL_PATH}\n"
        f"  SQLITE        : {config.DB_PATH}\n"
        f"  >>> SUPERVISOR: sync your paper log clock to the WALL CLOCK above <<<\n"
        f"{bar}\n"
    )
    log.info(msg)
    print(msg, flush=True)
