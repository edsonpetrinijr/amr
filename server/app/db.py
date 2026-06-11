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
        CREATE TABLE IF NOT EXISTS erp_order (
            order_key TEXT PRIMARY KEY,
            raw_hash TEXT,
            record_type TEXT,
            record_type_class TEXT,
            part_number TEXT,
            storage_loc TEXT,
            cell TEXT,
            pou TEXT,
            quantity TEXT,
            order_date_raw TEXT,
            observation TEXT,
            amr_flagged INTEGER,
            status TEXT,
            pickup_station TEXT,
            dropoff_station TEXT,
            task_id TEXT,
            first_seen_ts REAL,
            dispatched_ts REAL,
            delivered_ts REAL,
            cancelled_ts REAL,
            last_seen_ts REAL,
            note TEXT,
            raw_line TEXT
        );
        CREATE TABLE IF NOT EXISTS erp_snapshot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL,
            source_path TEXT,
            copied_path TEXT,
            total_lines INTEGER,
            order_count INTEGER,
            fulfillment_count INTEGER,
            cancellation_count INTEGER,
            matched_count INTEGER,
            new_count INTEGER,
            dispatched_count INTEGER,
            note TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_erp_status ON erp_order(status, first_seen_ts);
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


def query_task_events(
    since: float | None = None,
    to_ts: float | None = None,
    limit: int = 10000,
) -> list[dict]:
    """Raw task_events rows in ascending time order.

    This powers read-only report endpoints that need auditable event-level
    folding rules beyond the existing task_history summary.
    """
    if _conn is None:
        return []

    sql = "SELECT task_id, ts, event, robot_id, pickup, dropoff FROM task_events"
    args: list = []
    where: list[str] = []
    if since is not None:
        where.append("ts >= ?")
        args.append(float(since))
    if to_ts is not None:
        where.append("ts <= ?")
        args.append(float(to_ts))
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY ts ASC LIMIT ?"
    args.append(int(limit))

    with _lock:
        rows = _conn.execute(sql, args).fetchall()

    return [
        {
            "task_id": r[0],
            "ts": r[1],
            "event": r[2],
            "robot_id": r[3],
            "pickup": r[4],
            "dropoff": r[5],
        }
        for r in rows
    ]


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


# ── ERP "Reposição" orders + snapshot audit ─────────────────────────────────
# erp_order is keyed by a content hash (order_key) so the same order reappearing
# across rolling feed snapshots is deduped: a re-poll only bumps last_seen_ts.

# All DB columns in insert order.
_ERP_COLS = (
    "order_key", "raw_hash", "record_type", "record_type_class", "part_number",
    "storage_loc", "cell", "pou", "quantity", "order_date_raw", "observation",
    "amr_flagged", "status", "pickup_station", "dropoff_station", "task_id",
    "first_seen_ts", "dispatched_ts", "delivered_ts", "cancelled_ts",
    "last_seen_ts", "note", "raw_line",
)

# Columns the service may patch via update_erp_order_fields.
_ERP_UPDATABLE = {
    "record_type_class", "status", "pickup_station", "dropoff_station", "task_id",
    "dispatched_ts", "delivered_ts", "cancelled_ts", "last_seen_ts", "note", "amr_flagged",
}

# Keys returned to the API/SSE (the FROZEN ErpOrder contract). raw_hash/raw_line
# stay internal; amr_flagged is exposed as a bool.
_ERP_CONTRACT_KEYS = (
    "order_key", "record_type", "record_type_class", "part_number", "storage_loc",
    "cell", "pou", "quantity", "order_date_raw", "observation", "amr_flagged",
    "status", "pickup_station", "dropoff_station", "task_id", "first_seen_ts",
    "dispatched_ts", "delivered_ts", "cancelled_ts", "last_seen_ts", "note",
)


def _erp_row_to_contract(row) -> dict:
    """Map a full erp_order DB row (tuple over _ERP_COLS) to the API/SSE dict."""
    d = dict(zip(_ERP_COLS, row))
    out = {k: d.get(k) for k in _ERP_CONTRACT_KEYS}
    out["amr_flagged"] = bool(d.get("amr_flagged"))
    return out


def upsert_erp_order(o: dict) -> bool:
    """Insert a new erp_order, or (if order_key already exists) only bump
    last_seen_ts. Returns True when a NEW row was created, False otherwise."""
    if _conn is None:
        return False
    with _lock:
        exists = _conn.execute(
            "SELECT 1 FROM erp_order WHERE order_key=?", (o["order_key"],)
        ).fetchone() is not None
        if exists:
            _conn.execute(
                "UPDATE erp_order SET last_seen_ts=? WHERE order_key=?",
                (o.get("last_seen_ts"), o["order_key"]),
            )
            _conn.commit()
            return False
        _conn.execute(
            f"INSERT INTO erp_order({','.join(_ERP_COLS)}) "
            f"VALUES({','.join('?' for _ in _ERP_COLS)})",
            tuple(o.get(c) for c in _ERP_COLS),
        )
        _conn.commit()
        return True


def update_erp_order_fields(order_key: str, **fields) -> None:
    """Patch an existing erp_order. Unknown columns are ignored."""
    if _conn is None:
        return
    cols = [(k, v) for k, v in fields.items() if k in _ERP_UPDATABLE]
    if not cols:
        return
    set_sql = ", ".join(f"{k}=?" for k, _ in cols)
    args = [v for _, v in cols] + [order_key]
    with _lock:
        _conn.execute(f"UPDATE erp_order SET {set_sql} WHERE order_key=?", args)
        _conn.commit()


def get_erp_order(order_key: str) -> dict | None:
    if _conn is None:
        return None
    with _lock:
        row = _conn.execute(
            f"SELECT {','.join(_ERP_COLS)} FROM erp_order WHERE order_key=?", (order_key,)
        ).fetchone()
    return _erp_row_to_contract(row) if row else None


def list_erp_orders(limit: int = 200) -> list[dict]:
    """Newest-first (by first_seen_ts) — includes both order and empty_return lanes."""
    if _conn is None:
        return []
    with _lock:
        rows = _conn.execute(
            f"SELECT {','.join(_ERP_COLS)} FROM erp_order "
            f"ORDER BY first_seen_ts DESC LIMIT ?", (int(limit),)
        ).fetchall()
    return [_erp_row_to_contract(r) for r in rows]


def get_oldest_ready_order() -> dict | None:
    """FIFO: the earliest-seen erp_order still in 'ready_for_confirmation'."""
    if _conn is None:
        return None
    with _lock:
        row = _conn.execute(
            f"SELECT {','.join(_ERP_COLS)} FROM erp_order "
            f"WHERE status='ready_for_confirmation' "
            f"ORDER BY first_seen_ts ASC LIMIT 1"
        ).fetchone()
    return _erp_row_to_contract(row) if row else None


def insert_erp_snapshot(**fields) -> None:
    """Audit row for one poll cycle."""
    if _conn is None:
        return
    cols = ("ts", "source_path", "copied_path", "total_lines", "order_count",
            "fulfillment_count", "cancellation_count", "matched_count",
            "new_count", "dispatched_count", "note")
    with _lock:
        _conn.execute(
            f"INSERT INTO erp_snapshot({','.join(cols)}) "
            f"VALUES({','.join('?' for _ in cols)})",
            tuple(fields.get(c) for c in cols),
        )
        _conn.commit()
