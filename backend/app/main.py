"""
Caterpillar Inc. Fleet — Flask backend entry point.
Uses Flask (already installed) + SSE for real-time push.
No extra dependencies needed.

Run:
    python -m backend.app.main          (from robotics/ folder)
    -- or --
    cd backend && python -m app.main

Server-Sent Events:  GET  /events  → EventSource stream (world @10Hz, task_update, alarm)
REST:
  GET  /health
  GET  /map
  GET  /stations
  GET  /robots
  GET  /tasks
  POST /tasks              body: {"pickup": "AP1", "dropoff": "CB1"}
  DELETE /tasks/<id>
  POST /callbutton/<id>    simulate callbutton press
  POST /relocalize         body: {"robot_id":"AMR-01","x":1.2,"y":0.8,"theta":0}
"""
from __future__ import annotations

import json
import logging
import os
import queue
import threading
import time
from pathlib import Path
from typing import Optional

# Carrega .env da raiz do projeto se existir
_env_file = Path(__file__).parents[2] / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith('#') and '=' in _line:
            _k, _v = _line.split('=', 1)
            os.environ.setdefault(_k.strip(), _v.strip())

from flask import Flask, Response, jsonify, request, stream_with_context

from . import config, db
from .dispatcher import Dispatcher
from .models import world_snapshot, alarm_msg, task_update_msg, IDLE, OFFLINE, CHARGING
from .opcua import OpcUaCallbuttonDriver
from .provider import SimProvider
from .seer import SeerProvider
from .smap import load_map, validate_stations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s"
)
log = logging.getLogger(__name__)

# ── App state ─────────────────────────────────────────────────────────────────

app = Flask(__name__)

_dispatcher: Optional[Dispatcher] = None
_map_model  = None

# Each SSE subscriber gets its own queue
_subscribers: list[queue.Queue] = []
_sub_lock = threading.Lock()


def _broadcast(msg: dict) -> None:
    data = json.dumps(msg)
    dead = []
    with _sub_lock:
        for q in _subscribers:
            try:
                q.put_nowait(data)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)


def _sync_broadcast(msg: dict) -> None:
    """Sync wrapper — dispatcher calls this from its thread."""
    _broadcast(msg)


# ── Background threads ────────────────────────────────────────────────────────

def _dispatcher_loop() -> None:
    """Runs the dispatcher + sim tick in a background thread."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_dispatcher.run())


def _world_push_loop() -> None:
    """Push world snapshots to SSE subscribers at ~10 Hz."""
    every = max(1, config.TELEMETRY_EVERY_TICKS)
    tick  = 0
    interval = 1.0 / config.TICK_HZ * every
    while True:
        time.sleep(interval)
        if not _dispatcher:
            continue
        robots   = list(_dispatcher.provider.robots.values())
        stations = list(_dispatcher.stations.values())
        active   = _dispatcher.active_tasks()
        snap = world_snapshot(robots, stations, active)
        _broadcast(snap)
        tick += 1
        if tick % every == 0:
            db.log_telemetry(robots)


def _startup() -> None:
    global _dispatcher, _map_model

    db.init()

    smap_path = os.getenv(
        "SMAP_PATH",
        str(Path(__file__).parents[2] / "maps" / "1007.smap")
    )
    if Path(smap_path).exists():
        _map_model = load_map(smap_path)
        warns = validate_stations(_map_model, config.STATIONS)
        for w in warns:
            log.warning("smap validation: %s", w)
    else:
        log.warning("No .smap found at %s — map will be empty", smap_path)

    if config.SIM_MODE:
        provider = SimProvider()
        log.info("Using SimProvider (SIM_MODE=true)")
    else:
        provider = SeerProvider()
        log.info("Using SeerProvider (SIM_MODE=false) — connecting to real AMRs")
    _dispatcher = Dispatcher(provider)

    # Sync broadcast wrapper (dispatcher is async internally but we bridge it)
    def _bridge(msg):
        _sync_broadcast(msg)

    # patch dispatcher broadcast to sync version
    import asyncio
    async def _async_bridge(msg):
        _sync_broadcast(msg)
    _dispatcher.set_broadcast(_async_bridge)

    threading.Thread(target=_dispatcher_loop, daemon=True).start()
    threading.Thread(target=_world_push_loop, daemon=True).start()

    # OPC UA callbutton driver (starts only if OPCUA_ENDPOINT is set and asyncua present)
    opcua_driver = OpcUaCallbuttonDriver(_dispatcher)
    opcua_driver.start()

    log.info("Caterpillar Inc. Fleet backend started (sim_mode=%s)", config.SIM_MODE)


# ── SSE endpoint ──────────────────────────────────────────────────────────────

@app.route("/events")
def sse_stream():
    q: queue.Queue = queue.Queue(maxsize=64)
    with _sub_lock:
        _subscribers.append(q)

    # Send immediate snapshot + map on connect
    if _dispatcher:
        robots   = list(_dispatcher.provider.robots.values())
        stations = list(_dispatcher.stations.values())
        active   = _dispatcher.active_tasks()
        snap = world_snapshot(robots, stations, active)
        q.put_nowait(json.dumps(snap))
        if _map_model:
            q.put_nowait(json.dumps({"type": "map", "map": _map_model.to_dict()}))

    def generate():
        try:
            while True:
                try:
                    data = q.get(timeout=15)
                    yield f"data: {data}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        except GeneratorExit:
            pass
        finally:
            with _sub_lock:
                if q in _subscribers:
                    _subscribers.remove(q)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ── REST endpoints ────────────────────────────────────────────────────────────

@app.after_request
def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,OPTIONS"
    return response


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "sim_mode": config.SIM_MODE,
        "version": "0.1.0",
        "robots": len(_dispatcher.provider.robots) if _dispatcher else 0,
        "sse_clients": len(_subscribers),
    })


@app.route("/config/sim_mode", methods=["POST"])
def set_sim_mode():
    """Toggle sim mode at runtime (takes effect on next backend restart)."""
    body = request.get_json(force=True)
    new_val = bool(body.get("sim_mode", True))
    config.SIM_MODE = new_val
    log.info("SIM_MODE set to %s", new_val)
    return jsonify({"sim_mode": config.SIM_MODE})


@app.route("/config/opcua", methods=["POST"])
def set_opcua():
    """Update OPC UA endpoint at runtime and restart the driver."""
    body = request.get_json(force=True)
    endpoint = str(body.get("endpoint", "")).strip()
    config.OPCUA_ENDPOINT = endpoint
    log.info("OPCUA_ENDPOINT updated to %r", endpoint)
    if _dispatcher:
        from .opcua import OpcUaCallbuttonDriver
        drv = OpcUaCallbuttonDriver(_dispatcher)
        drv.start()
    return jsonify({"opcua_endpoint": endpoint})


@app.route("/map")
def get_map():
    if not _map_model:
        return jsonify({"error": "No map loaded"}), 404
    return jsonify(_map_model.to_dict())


@app.route("/stations")
def get_stations():
    if not _dispatcher:
        return jsonify([])
    return jsonify([s.to_dict() for s in _dispatcher.stations.values()])


@app.route("/robots")
def get_robots():
    if not _dispatcher:
        return jsonify([])
    return jsonify([r.to_dict() for r in _dispatcher.provider.robots.values()])


@app.route("/tasks")
def get_tasks():
    if not _dispatcher:
        return jsonify([])
    return jsonify([t.to_dict() for t in _dispatcher.all_tasks()])


@app.route("/tasks", methods=["POST"])
def create_task():
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True)
    task = _dispatcher.create_task(body.get("pickup", ""), body.get("dropoff", ""))
    if not task:
        return jsonify({"error": "Pickup locked or station not found"}), 409
    return jsonify(task.to_dict()), 201


@app.route("/tasks/<task_id>", methods=["DELETE", "OPTIONS"])
def cancel_task(task_id: str):
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    ok = _dispatcher.cancel_task(task_id)
    if not ok:
        return jsonify({"error": "Task not found or already terminal"}), 404
    return jsonify({"ok": True, "id": task_id})


@app.route("/button/<station_id>", methods=["POST"])
def button_press(station_id: str):
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    direction = body.get("dir", request.args.get("dir", "fwd"))
    task = _dispatcher.button_pressed(station_id, direction)
    station = _dispatcher.stations.get(station_id)
    return jsonify({
        "task": task.to_dict() if task else None,
        "station": station.to_dict() if station else None,
        "dispatched": task is not None,
    })


@app.route("/reset/<station_id>", methods=["POST"])
def reset_pair(station_id: str):
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    ok = _dispatcher.reset_pair(station_id)
    return jsonify({"ok": ok})


@app.route("/callbutton/<station_id>", methods=["POST"])
def callbutton_press(station_id: str):
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    task = _dispatcher.callbutton_pressed(station_id)
    return jsonify({"task": task.to_dict() if task else None})


@app.route("/setdo", methods=["POST"])
def set_do():
    body   = request.get_json(force=True)
    rid    = body.get("robot_id")
    do_id  = int(body.get("do_id", 0))
    status = bool(body.get("status", False))
    log.info("setdo: robot=%s do_id=%d status=%s", rid, do_id, status)
    if not config.SIM_MODE and hasattr(_dispatcher.provider, 'set_do'):
        ok = _dispatcher.provider.set_do(rid, do_id, status)
        return jsonify({"ok": ok})
    return jsonify({"ok": True, "note": "sim mode"})


@app.route("/relocalize", methods=["POST"])
def relocalize():
    body = request.get_json(force=True)
    rid   = body.get("robot_id")
    x     = float(body.get("x",     0))
    y     = float(body.get("y",     0))
    theta = float(body.get("theta", 0))
    log.info("relocalize: robot=%s x=%.3f y=%.3f theta=%.3f", rid, x, y, theta)
    if not config.SIM_MODE and hasattr(_dispatcher.provider, 'relocalize'):
        ok = _dispatcher.provider.relocalize(rid, x, y, theta)
        return jsonify({"ok": ok, "note": "hardware command sent" if ok else "command failed"})
    return jsonify({"ok": True, "note": "sim mode — no hardware command sent"})


# ── Operator controls: manual jog / software STOP-ALL ─────────────────────────

@app.route("/jog", methods=["POST", "OPTIONS"])
def jog():
    """Manual operator jog. Body: {robot_id, vx, vy, w, duration?}.
    Velocities are clamped to the JOG_MAX_* envelope. Refuses (409) if the robot
    has an active task or is unhealthy/offline; (404) for unknown robot; (400)
    for non-numeric values. Allowed while STOP-ALL is engaged (operator recovery).
    """
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    rid = body.get("robot_id")
    if not rid:
        return jsonify({"error": "robot_id required"}), 400
    try:
        vx = float(body.get("vx", 0.0))
        vy = float(body.get("vy", 0.0))
        w  = float(body.get("w", 0.0))
    except (TypeError, ValueError):
        return jsonify({"error": "vx/vy/w must be numbers"}), 400
    if any(v != v or v in (float("inf"), float("-inf")) for v in (vx, vy, w)):
        return jsonify({"error": "vx/vy/w out of range"}), 400
    duration = body.get("duration")
    if duration is not None:
        try:
            duration = float(duration)
        except (TypeError, ValueError):
            return jsonify({"error": "duration must be a number"}), 400
        if duration <= 0 or duration != duration:
            return jsonify({"error": "duration must be > 0"}), 400

    code, payload = _dispatcher.jog(rid, vx, vy, w, duration)
    if code == 200:
        moving = bool(payload["vx"] or payload["vy"] or payload["w"])
        level = "warn" if moving else "info"
        _broadcast(alarm_msg(
            level,
            f"manual control of {rid} (jog vx={payload['vx']:.2f} vy={payload['vy']:.2f} w={payload['w']:.2f})",
            rid,
        ))
    return jsonify(payload), code


@app.route("/stop_all", methods=["POST", "OPTIONS"])
def stop_all():
    """Emergency SOFTWARE stop — NOT a substitute for a hardware E-stop.
    Stops every robot, cancels all active tasks, and halts auto-dispatch until
    POST /resume."""
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    cancelled = _dispatcher.stop_all()
    _broadcast(alarm_msg(
        "critical",
        "FLEET STOP-ALL engaged by operator — SOFTWARE stop only, NOT a hardware E-stop",
        None,
    ))
    for t in cancelled:
        _broadcast(task_update_msg(t, "cancelled"))
    return jsonify({
        "halted": True,
        "cancelled": [t.id for t in cancelled],
        "note": "software stop — NOT a hardware E-stop",
    })


@app.route("/resume", methods=["POST", "OPTIONS"])
def resume():
    """Clear the STOP-ALL halt and re-enable auto-dispatch."""
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    _dispatcher.resume()
    _broadcast(alarm_msg("info", "Fleet auto-dispatch resumed by operator", None))
    return jsonify({"halted": False})


# ── Telemetry / analytics queries (read-only, for the Dashboard) ──────────────

def _clamp_limit(raw, default: int) -> int:
    try:
        n = int(raw) if raw is not None else default
    except (TypeError, ValueError):
        n = default
    return max(1, min(n, config.TELEMETRY_QUERY_MAX_LIMIT))


@app.route("/telemetry/robots/<robot_id>")
def telemetry_for_robot(robot_id: str):
    since = request.args.get("since")
    since_ts = float(since) if since not in (None, "") else None
    limit = _clamp_limit(request.args.get("limit"), config.TELEMETRY_QUERY_DEFAULT_LIMIT)
    rows = db.query_telemetry(robot_id, since=since_ts, limit=limit)
    return jsonify({"robot_id": robot_id, "count": len(rows), "rows": rows})


@app.route("/tasks/history")
def tasks_history():
    since = request.args.get("since")
    since_ts = float(since) if since not in (None, "") else None
    limit = _clamp_limit(request.args.get("limit"), config.TELEMETRY_QUERY_DEFAULT_LIMIT)
    tasks = db.query_task_history(since=since_ts, limit=limit)
    return jsonify({"count": len(tasks), "tasks": tasks})


@app.route("/stats/summary")
def stats_summary():
    """Aggregate fleet KPIs for the Dashboard. Task counts/durations come from
    task_events (source of truth across restarts); utilization/battery from the
    live fleet state."""
    # Start of local day.
    lt = time.localtime()
    start_of_day = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, 0, 0, 0, 0, 0, -1))
    counts = db.task_counts_since(start_of_day)

    robots = list(_dispatcher.provider.robots.values()) if _dispatcher else []
    total = len(robots)
    active = sum(1 for r in robots if r.current_task or r.status not in (IDLE, OFFLINE, CHARGING))
    avg_batt = round(sum(r.battery for r in robots) / total, 1) if total else None

    return jsonify({
        "tasks_completed_today": counts["completed"],
        "tasks_failed_today": counts["failed"],
        "avg_task_duration_s": counts["avg_duration_s"],
        "fleet_total": total,
        "fleet_active": active,
        "fleet_utilization": round(active / total, 3) if total else 0.0,
        "avg_battery": avg_batt,
        "halted": _dispatcher.halted if _dispatcher else False,
    })





# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _startup()
    port = int(os.getenv("FLEET_PORT", config.WS_PORT))
    log.info("Listening on http://0.0.0.0:%d", port)
    app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)
