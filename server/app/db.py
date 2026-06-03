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


# ── Read-only analytics queries (Dashboard) ─────────────────────────────────
# All bounded by an explicit LIMIT and served off the indexed columns
# (idx_tel_robot / idx_evt_task) so the request thread never does a huge scan.

_TERMINAL_EVENTS = ("done", "cancelled", "failed")


def query_telemetry(robot_id: str, since: float | None = None, limit: int = 500) -> list[dict]:
    """Recent telemetry rows for one robot, newest first."""
    if _conn is None:
        return []
    sql = "SELECT ts, x, y, battery, status FROM telemetry WHERE robot_id = ?"
    args: list = [robot_id]
    if since is not None:
        sql += " AND ts >= ?"
        args.append(since)
    sql += " ORDER BY ts DESC LIMIT ?"
    args.append(int(limit))
    with _lock:
        cur = _conn.execute(sql, args)
        rows = cur.fetchall()
    return [{"ts": r[0], "x": r[1], "y": r[2], "battery": r[3], "status": r[4]} for r in rows]


def query_task_history(since: float | None = None, limit: int = 500) -> list[dict]:
    """Per-task summary folded from task_events: created/finished ts, duration,
    final state, robot, pickup, dropoff. Newest (by creation) first."""
    if _conn is None:
        return []
    sql = "SELECT task_id, ts, event, robot_id, pickup, dropoff FROM task_events"
    args: list = []
    if since is not None:
        sql += " WHERE ts >= ?"
        args.append(since)
    sql += " ORDER BY ts ASC"
    with _lock:
        rows = _conn.execute(sql, args).fetchall()

    by_task: dict[str, dict] = {}
    for task_id, ts, event, robot_id, pickup, dropoff in rows:
        t = by_task.get(task_id)
        if t is None:
            t = by_task[task_id] = {
                "id": task_id, "robot": robot_id, "pickup": pickup, "dropoff": dropoff,
                "created_ts": ts, "finished_ts": None, "state": event, "duration_s": None,
            }
        # latest event in time order wins for state / robot
        t["state"] = event
        if robot_id:
            t["robot"] = robot_id
        if event in _TERMINAL_EVENTS:
            t["finished_ts"] = ts
            t["duration_s"] = round(ts - t["created_ts"], 3)

    out = sorted(by_task.values(), key=lambda d: d["created_ts"], reverse=True)
    return out[: int(limit)]


def task_counts_since(start_ts: float) -> dict:
    """Completed / failed counts and mean completed-task duration since start_ts."""
    if _conn is None:
        return {"completed": 0, "failed": 0, "avg_duration_s": None}
    with _lock:
        completed = _conn.execute(
            "SELECT COUNT(*) FROM task_events WHERE event='done' AND ts >= ?", (start_ts,)
        ).fetchone()[0]
        failed = _conn.execute(
            "SELECT COUNT(*) FROM task_events WHERE event='failed' AND ts >= ?", (start_ts,)
        ).fetchone()[0]
    # Mean duration from the folded history (small, capped).
    durs = [t["duration_s"] for t in query_task_history(since=start_ts, limit=2000)
            if t["state"] == "done" and t["duration_s"] is not None]
    avg = round(sum(durs) / len(durs), 3) if durs else None
    return {"completed": completed, "failed": failed, "avg_duration_s": avg}
