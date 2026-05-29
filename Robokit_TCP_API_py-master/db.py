"""SQLite persistence — telemetry + task audit for later analytics."""
import sqlite3
import time
import threading
from . import config

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def init() -> None:
    global _conn
    _conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    _conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS telemetry (
            robot_id TEXT, ts REAL, x REAL, y REAL,
            battery REAL, status TEXT
        );
        CREATE TABLE IF NOT EXISTS task_events (
            task_id TEXT, ts REAL, event TEXT,
            robot_id TEXT, pickup TEXT, dropoff TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_tel_robot ON telemetry(robot_id, ts);
        CREATE INDEX IF NOT EXISTS idx_evt_task ON task_events(task_id, ts);
        """
    )
    _conn.commit()


def log_telemetry(robots) -> None:
    if _conn is None:
        return
    ts = time.time()
    rows = [(r.id, ts, r.x, r.y, r.battery, r.status) for r in robots]
    with _lock:
        _conn.executemany(
            "INSERT INTO telemetry(robot_id, ts, x, y, battery, status) VALUES (?,?,?,?,?,?)",
            rows,
        )
        _conn.commit()


def log_task_event(task, event: str) -> None:
    if _conn is None:
        return
    with _lock:
        _conn.execute(
            "INSERT INTO task_events(task_id, ts, event, robot_id, pickup, dropoff) VALUES (?,?,?,?,?,?)",
            (task.id, time.time(), event, task.robot, task.pickup, task.dropoff),
        )
        _conn.commit()
