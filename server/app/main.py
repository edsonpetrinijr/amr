"""
Caterpillar Inc. Fleet — Flask backend entry point.
Uses Flask (already installed) + SSE for real-time push.
No extra dependencies needed.

Run:
    python -m server.app.main          (from robotics/ folder)
    -- or --
    cd server && python -m app.main

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

from . import config, db, telemetry
from . import store
from . import opcua as opcua
from .dispatcher import Dispatcher
from .erp import ErpService, load_mapping
from .models import world_snapshot, alarm_msg, task_update_msg, IDLE, OFFLINE, CHARGING
from .opcua import OpcUaCallbuttonDriver
from .provider import SimProvider
from .seer import SeerProvider
from .smap import load_map, validate_stations
from . import preflight

# `opcua.probe_node` is delivered by the integration engineer. Provide a tiny
# graceful fallback ONLY if absent so main.py imports/runs before that lands.
# Tests monkeypatch `opcua.probe_node`, which works either way.
if not hasattr(opcua, "probe_node"):
    def _probe_node_fallback(node_id, endpoint=None, timeout=3.0):  # noqa: ANN001
        ep = endpoint if endpoint is not None else getattr(config, "OPCUA_ENDPOINT", "")
        return {"ok": False, "value": None,
                "error": None if not ep else "probe_node not implemented",
                "configured": bool(ep), "endpoint": ep}
    opcua.probe_node = _probe_node_fallback  # type: ignore[attr-defined]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s"
)
log = logging.getLogger(__name__)

# ── App state ─────────────────────────────────────────────────────────────────

app = Flask(__name__)

_dispatcher: Optional[Dispatcher] = None
_map_model  = None
_map_name: Optional[str] = None   # filename of the live map, e.g. "1007.smap"
_opcua_driver = None   # OpcUaCallbuttonDriver instance (set in _startup)
_erp_service: Optional[ErpService] = None   # ERP "Reposição" poller + actions

# Guards the rare map swap (mutate _map_model/_map_name + re-feed sim walls)
# against the running dispatcher/sim loop. NOT on the 10 Hz SSE hot path.
_map_lock = threading.Lock()


def _maps_dir() -> Path:
    """Directory holding *.smap files. Matches the startup default
    (Path(__file__).parents[2] / "maps"); MAPS_DIR env overrides it."""
    override = os.getenv("MAPS_DIR", "").strip()
    if override:
        return Path(override).resolve()
    return (Path(__file__).parents[2] / "maps").resolve()


def _resolve_map_path(name_or_filename: str) -> Path:
    """Resolve a bare .smap filename to an absolute path INSIDE the maps dir.
    Rejects path traversal, separators, absolute paths and anything outside the
    maps dir. Raises ValueError on any invalid/missing input."""
    if not name_or_filename or not str(name_or_filename).strip():
        raise ValueError("map name is required")
    name = str(name_or_filename).strip()
    # must be a bare filename — no separators, no parent refs
    if name in (".", "..") or name != Path(name).name:
        raise ValueError(f"invalid map name: {name!r}")
    if not name.endswith(".smap"):
        raise ValueError(f"map must be a .smap file: {name!r}")
    maps_dir = _maps_dir()
    path = (maps_dir / name).resolve()
    try:
        path.relative_to(maps_dir)   # defense in depth vs traversal
    except ValueError:
        raise ValueError(f"map path escapes maps dir: {name!r}")
    if not path.is_file():
        raise ValueError(f"map not found: {name!r}")
    return path


def _apply_map(name_or_filename: str) -> None:
    """Atomically swap in a new live map by filename. Validates the name is a
    safe *.smap inside the maps dir, loads it, sets _map_model/_map_name, logs
    station-validation warnings, and (SIM_MODE) re-feeds walls to the sim laser
    — exactly like startup. Raises ValueError on an invalid/missing map."""
    global _map_model, _map_name
    path = _resolve_map_path(name_or_filename)
    model = load_map(path)            # parse outside the lock (I/O)
    with _map_lock:
        _map_model = model
        _map_name = path.name
        warns = validate_stations(model, config.STATIONS)
        for w in warns:
            log.warning("smap validation: %s", w)
        if config.SIM_MODE and _dispatcher is not None:
            provider = _dispatcher.provider
            if hasattr(provider, "set_walls"):
                provider.set_walls([
                    ((w.start.x, w.start.y), (w.end.x, w.end.y))
                    for w in model.walls
                ])

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


def _telemetry_sampler_loop() -> None:
    """Dedicated per-tick snapshot sampler at SAMPLE_HZ for the soak robot.

    Mirrors the real SEER poll cadence (2 Hz) and works in BOTH sim and real
    mode — SimProvider has no RobotConn thread, so capture can't be bolted onto
    it. Every row is stamped with the authoritative (cycle_id, step) read
    atomically from the SoakRunner, so telemetry and events always join cleanly.
    """
    interval = 1.0 / max(0.1, config.SAMPLE_HZ)
    prev: dict = {"x": None, "y": None, "ts_mono": None,
                  "connected": None, "blocked": False, "low_conf": False}
    while True:
        time.sleep(interval)
        disp = _dispatcher
        if not disp or disp.soak is None:
            continue
        soak = disp.soak
        if not soak.running:
            break
        rid = soak.robot_id
        robot = disp.provider.robots.get(rid)
        if robot is None:
            continue
        raw = {}
        get_raw = getattr(disp.provider, "raw_state", None)
        if callable(get_raw):
            raw = get_raw(rid) or {}

        ts = time.time()
        ts_mono = time.monotonic()
        x, y = robot.x, robot.y
        battery = robot.battery
        connected = bool(raw.get("connected", True))
        blocked = bool(raw.get("blocked", False))
        confidence = raw.get("confidence")

        # Velocity: prefer real SEER speed, else derive from pose delta.
        vx, vy, w = raw.get("vx"), raw.get("vy"), raw.get("w")
        if vx is None and prev["x"] is not None and prev["ts_mono"] is not None:
            ddt = ts_mono - prev["ts_mono"]
            if ddt > 0:
                vx = (x - prev["x"]) / ddt
                vy = (y - prev["y"]) / ddt

        # Atomic tag + fold sample into the active cycle aggregates.
        tag = soak.observe(x, y, battery, blocked, confidence)

        last_seen = raw.get("last_seen", robot.last_seen)
        row = {
            "run_id": config.RUN_ID, "robot_id": rid, "ts": ts, "ts_mono": ts_mono,
            "cycle_id": tag["cycle_id"], "step": tag["step"],
            "x": x, "y": y, "theta": robot.theta, "vx": vx, "vy": vy, "w": w,
            "battery": battery,
            "task_status": raw.get("task_status"), "target_id": raw.get("target_id", ""),
            "connected": 1 if connected else 0,
            "last_seen_age": max(0.0, ts - last_seen) if last_seen else None,
            "blocked": 1 if blocked else 0,
            "confidence": confidence,
            "lift_di": 1 if tag["lift_di"] else 0,
            "lift_do": 1 if tag["lift_do"] else 0,
        }
        telemetry.write_telemetry(row)

        # ── Edge-detected discrete events (poll-thread responsibilities) ─────
        cyc, step = tag["cycle_id"], tag["step"]
        if prev["connected"] is not None and connected != prev["connected"]:
            ev = "comms_reconnect" if connected else "comms_lost"
            telemetry.write_event(config.RUN_ID, rid, cyc, step, ev)
        if blocked and not prev["blocked"]:
            soak.note_obstacle_stop()
            telemetry.write_event(config.RUN_ID, rid, cyc, step, "obstacle_stop")
        elif not blocked and prev["blocked"]:
            telemetry.write_event(config.RUN_ID, rid, cyc, step, "obstacle_clear")
        if confidence is not None:
            low = confidence < config.SOAK_CONF_LOW
            if low and not prev["low_conf"]:
                telemetry.write_event(config.RUN_ID, rid, cyc, step, "low_confidence",
                                      detail={"confidence": confidence})
            prev["low_conf"] = low

        prev.update(x=x, y=y, ts_mono=ts_mono, connected=connected, blocked=blocked)


def _startup() -> None:
    global _dispatcher, _map_model, _opcua_driver, _erp_service

    db.init()

    # Hydrate persisted device/station overrides BEFORE building provider/dispatcher
    # so the fleet and station OPC UA bindings reflect operator edits across restarts.
    store.load_into_config()

    smap_path = os.getenv(
        "SMAP_PATH",
        str(Path(__file__).parents[2] / "maps" / "1007.smap")
    )

    if config.SIM_MODE:
        provider = SimProvider()
        log.info("Using SimProvider (SIM_MODE=true)")
    else:
        provider = SeerProvider()
        log.info("Using SeerProvider (SIM_MODE=false) — connecting to real AMRs")
    _dispatcher = Dispatcher(provider)

    # Load the initial map through the SAME code path as runtime selection.
    # SMAP_PATH gives the default; its basename is resolved inside the maps dir.
    try:
        _apply_map(Path(smap_path).name)
    except ValueError as e:
        log.warning("No usable .smap (%s) — map will be empty", e)

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

    # ── Soak telemetry capture (DATA CAPTURE ONLY) ──────────────────────────
    if config.SOAK_MODE:
        telemetry.init()
        telemetry.print_run_banner()      # prominent wall-clock + run_id for the supervisor
        if _dispatcher.soak is not None:
            _dispatcher.soak.start()
        threading.Thread(target=_telemetry_sampler_loop, daemon=True).start()

        import atexit

        def _shutdown_telemetry() -> None:
            if _dispatcher and _dispatcher.soak is not None:
                _dispatcher.soak.stop()
            telemetry.close()
        atexit.register(_shutdown_telemetry)
        log.info("Soak telemetry capture active (run_id=%s)", config.RUN_ID)

    # ── ERP "Reposição" replenishment (Phase 1) ─────────────────────────────
    # Construct the service BEFORE the OPC UA driver so we can hand the driver
    # the action handler (confirm-delivery / request-empty button presses).
    erp_mapping = load_mapping(config.ERP_MAPPING_PATH)
    _erp_service = ErpService(_dispatcher, _sync_broadcast, erp_mapping)
    threading.Thread(target=_erp_service.poll_loop, daemon=True, name="erp-poller").start()
    log.info("ERP poller started (feed=%s, interval=%.1fs)",
             config.ERP_FEED_PATH, config.ERP_POLL_INTERVAL_S)

    # OPC UA callbutton driver (starts only if OPCUA_ENDPOINT is set and asyncua present)
    try:
        opcua_driver = OpcUaCallbuttonDriver(_dispatcher, action_handler=_erp_service.handle_action)
    except TypeError:
        # Integration engineer's action_handler kwarg not landed yet — degrade gracefully.
        opcua_driver = OpcUaCallbuttonDriver(_dispatcher)
    opcua_driver.start()
    _opcua_driver = opcua_driver

    # ── Preflight readiness — fail loud if the config can't support a pilot ──
    pf = preflight.validate(config.STATIONS, config.PAIRS, config.SIM_MODE, _map_model)
    if not pf.ok:
        for issue in pf.issues:
            log.error("preflight BLOCKED: %s", issue)
        _sync_broadcast(alarm_msg(
            "critical",
            "Preflight blocked — pilot not ready: " + "; ".join(pf.issues),
            None,
        ))
    else:
        log.info("preflight: readiness ok")

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
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


@app.route("/health")
def health():
    pf = preflight.validate(config.STATIONS, config.PAIRS, config.SIM_MODE, _map_model)
    return jsonify({
        "status": "ok",
        "sim_mode": config.SIM_MODE,
        "version": "0.1.0",
        "robots": len(_dispatcher.provider.robots) if _dispatcher else 0,
        "sse_clients": len(_subscribers),
        "readiness": pf.readiness,
        "issues": pf.issues,
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


@app.route("/maps")
def list_maps():
    """List available *.smap files in the maps dir.
    -> 200 [{"name": "1007.smap", "current": true}, ...] sorted by name."""
    maps_dir = _maps_dir()
    names = sorted(p.name for p in maps_dir.glob("*.smap")) if maps_dir.is_dir() else []
    return jsonify([{"name": n, "current": (n == _map_name)} for n in names])


@app.route("/maps/select", methods=["POST"])
def select_map():
    """Switch the live map at runtime.
    body: {"name": "InnovationBox.smap"} — must be an available *.smap.
    On success: re-feeds sim walls, broadcasts {"type":"map","map":...} to all
    SSE clients, and returns {"ok": true, "name": name, "map": {...}}.
    Invalid/missing/unknown name -> 400 {"error": "..."}."""
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    if not name or not isinstance(name, str):
        return jsonify({"error": "missing 'name'"}), 400
    name = name.strip()
    maps_dir = _maps_dir()
    available = {p.name for p in maps_dir.glob("*.smap")} if maps_dir.is_dir() else set()
    if name not in available:
        return jsonify({"error": f"unknown map: {name}"}), 400
    try:
        _apply_map(name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    with _map_lock:
        map_dict = _map_model.to_dict()
    _broadcast({"type": "map", "map": map_dict})
    log.info("map switched to %s (%d SSE clients notified)", name, len(_subscribers))
    return jsonify({"ok": True, "name": name, "map": map_dict})


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


@app.route("/robots/<robot_id>/laser")
def get_robot_laser(robot_id: str):
    """Dedicated PULL endpoint for the laser layer (frontend polls ~2–3 Hz only
    while the Laser toggle is ON — deliberately NOT pushed in the 10 Hz world
    SSE). Returns {"beams": [[x,y],…], "ts": float} in the WORLD/MAP frame."""
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    provider = _dispatcher.provider
    if robot_id not in provider.robots:
        return jsonify({"error": "Robot not found"}), 404
    if not hasattr(provider, "laser"):
        return jsonify({"beams": [], "ts": 0.0})
    return jsonify(provider.laser(robot_id))


@app.route("/robots/<robot_id>/navigate", methods=["POST", "OPTIONS"])
def navigate_robot(robot_id: str):
    """Navigate a robot directly to a map landmark. Body: {landmark_id}.
    Refuses (409) if the robot has an active task, no map is loaded; (404) for
    unknown robot/landmark; (400) for missing landmark_id."""
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    landmark_id = str(body.get("landmark_id", "")).strip()
    if not landmark_id:
        return jsonify({"error": "landmark_id required"}), 400
    provider = _dispatcher.provider
    if robot_id not in provider.robots:
        return jsonify({"error": "Robot not found"}), 404
    if _map_model is None:
        return jsonify({"error": "No map loaded"}), 409
    lm = next((m for m in _map_model.landmarks if m.id == landmark_id), None)
    if lm is None:
        return jsonify({"error": "Unknown landmark"}), 404
    robot = provider.robots[robot_id]
    if getattr(robot, "current_task", None):
        return jsonify({"error": "robot has an active task — cancel it first"}), 409
    ok = provider.goto_landmark(robot_id, landmark_id, lm.x, lm.y)
    _broadcast(alarm_msg("info", f"{robot_id} → {landmark_id}", robot_id))
    return jsonify({
        "ok": ok, "robot_id": robot_id, "landmark_id": landmark_id,
        "x": lm.x, "y": lm.y,
    })


# ── Devices & callbuttons: robot CRUD + OPC UA config/diagnostics ─────────────

def _find_robot_cfg(robot_id: str):
    return next((r for r in config.ROBOTS if r.get("id") == robot_id), None)


@app.route("/robots", methods=["POST", "OPTIONS"])
def add_robot():
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    ip = str(body.get("ip", "")).strip()
    if not ip:
        return jsonify({"error": "ip required"}), 400
    stored = store.add_robot({"ip": ip, "id": body.get("id"), "name": body.get("name")})
    robot = _dispatcher.provider.add_robot(stored)
    pulled = _dispatcher.provider.probe(robot.id)
    return jsonify({
        "robot": robot.to_dict(),
        "connected": bool(pulled.get("connected")),
        "pulled": pulled,
    }), 201


@app.route("/robots/<robot_id>", methods=["PUT", "OPTIONS"])
def update_robot(robot_id: str):
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    stored = store.update_robot(robot_id, {"ip": body.get("ip"), "name": body.get("name")})
    if stored is None:
        return jsonify({"error": "Robot not found"}), 404
    robot = _dispatcher.provider.update_robot(robot_id, ip=body.get("ip"), name=body.get("name"))
    if robot is None:
        return jsonify({"error": "Robot not found"}), 404
    pulled = _dispatcher.provider.probe(robot_id)
    return jsonify({
        "robot": robot.to_dict(),
        "connected": bool(pulled.get("connected")),
        "pulled": pulled,
    })


@app.route("/robots/<robot_id>", methods=["DELETE"])
def delete_robot(robot_id: str):
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    if _find_robot_cfg(robot_id) is None and robot_id not in _dispatcher.provider.robots:
        return jsonify({"error": "Robot not found"}), 404
    store.delete_robot(robot_id)
    _dispatcher.provider.remove_robot(robot_id)
    return jsonify({"ok": True, "id": robot_id})


@app.route("/robots/<robot_id>/probe", methods=["POST", "OPTIONS"])
def probe_robot(robot_id: str):
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    if robot_id not in _dispatcher.provider.robots:
        return jsonify({"error": "Robot not found"}), 404
    pulled = _dispatcher.provider.probe(robot_id)
    return jsonify({"connected": bool(pulled.get("connected")), "pulled": pulled})


@app.route("/stations/<station_id>", methods=["PUT", "OPTIONS"])
def update_station(station_id: str):
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    ok = store.set_station_opcua(station_id, body.get("opcua_node"), body.get("opcua_ret"))
    if not ok:
        return jsonify({"error": "Station not found"}), 404
    if "label" in body and body["label"] is not None:
        for s in config.STATIONS:
            if s["id"] == station_id:
                s["label"] = body["label"]
                break
    _dispatcher.reload_stations()
    # Re-apply the new node map to the running OPC UA driver (best-effort).
    if _opcua_driver is not None:
        try:
            _opcua_driver.restart()
        except Exception as exc:  # noqa: BLE001 — driver may be disabled
            log.warning("opcua driver restart failed: %s", exc)
    station = _dispatcher.stations.get(station_id)
    return jsonify({"station": station.to_dict() if station else None})


@app.route("/opcua/test", methods=["POST", "OPTIONS"])
def opcua_test():
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    node = body.get("node")
    if not node:
        sid = body.get("station_id")
        if sid:
            st = _dispatcher.stations.get(sid)
            node = st.opcua_node if st else None
    if not node:
        return jsonify({"error": "node or station_id required"}), 400
    res = opcua.probe_node(node)
    return jsonify({
        "ok": bool(res.get("ok")),
        "value": res.get("value"),
        "error": res.get("error"),
        "configured": bool(res.get("configured")),
        "endpoint": res.get("endpoint"),
        "node": node,
    })



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


# ── ERP "Reposição" (replenishment) — Phase 1 ───────────────────────────────

@app.route("/erp/orders")
def erp_orders():
    """List ERP orders (both order and empty_return lanes) + ENVIO readiness."""
    if not _erp_service:
        return jsonify({"orders": [], "amr_ready": False,
                        "envio_station": config.ERP_ENVIO_STATION})
    return jsonify({
        "orders": _erp_service.list_orders(200),
        "amr_ready": _erp_service.amr_ready(),
        "envio_station": config.ERP_ENVIO_STATION,
    })


@app.route("/erp/confirm-delivery", methods=["POST", "OPTIONS"])
def erp_confirm_delivery():
    """Dispatch the FIFO-oldest ready order to its AMR (simulates the button)."""
    if request.method == "OPTIONS":
        return "", 204
    if not _erp_service:
        return jsonify({"ok": False, "error": "erp not ready"}), 503
    res = _erp_service.confirm_delivery()
    return jsonify(res), (200 if res.get("ok") else 409)


@app.route("/erp/request-empty", methods=["POST", "OPTIONS"])
def erp_request_empty():
    """Dispatch an AMR from the POU back to RECEBIMENTO to fetch an empty rack."""
    if request.method == "OPTIONS":
        return "", 204
    if not _erp_service:
        return jsonify({"ok": False, "error": "erp not ready"}), 503
    res = _erp_service.request_empty()
    return jsonify(res), (200 if res.get("ok") else 409)


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
    """Simulate/forward a callbutton press (2-press transport model).
    First press on a callbutton = origin (pickup); next press on a DIFFERENT
    callbutton = destination (dropoff) → a transport task is dispatched.
    Response state: 'dispatched' | 'waiting_destination' | 'idle'.
    """
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    task = _dispatcher.callbutton_pressed(station_id)
    pending = _dispatcher.pending_origin
    if task is not None:
        state, message = "dispatched", f"transporte {task.pickup}→{task.dropoff} despachado"
    elif pending == station_id:
        state, message = "waiting_destination", "origem registrada — aperte o destino"
    else:
        state, message = "idle", "sem ação"
    return jsonify({
        "ok": True,
        "station_id": station_id,
        "state": state,
        "message": message,
        "pending_origin": pending,
        "task": task.to_dict() if task else None,
    })


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
    if _dispatcher and hasattr(_dispatcher.provider, 'relocalize'):
        ok = _dispatcher.provider.relocalize(rid, x, y, theta)
        note = "hardware command sent" if not config.SIM_MODE else "sim relocalize"
        return jsonify({"ok": ok, "note": note if ok else "command failed"})
    return jsonify({"ok": True, "note": "no relocalize support on provider"})


@app.route("/api/relocalize/suggestions")
def relocalize_suggestions():
    """Nearest map landmarks an operator can relocalize a robot onto.

    Query: robot_id (use its current/last-known est pose) OR explicit x & y.
    Optional k (default 5, clamped to [1, 20]) and max_dist_m. Everything is in
    METRES (smap frame) — no scaling. Response frame is "smap_meters"."""
    if not _map_model:
        return jsonify({"error": "MAP_NOT_LOADED"}), 409

    try:
        k = int(request.args.get("k", 5))
    except (TypeError, ValueError):
        k = 5
    k = max(1, min(k, 20))

    max_dist = request.args.get("max_dist_m")
    if max_dist is not None:
        try:
            max_dist = float(max_dist)
        except (TypeError, ValueError):
            max_dist = None

    robot_id = request.args.get("robot_id")
    x_arg = request.args.get("x")
    y_arg = request.args.get("y")

    if robot_id:
        provider = _dispatcher.provider if _dispatcher else None
        if provider is None or robot_id not in getattr(provider, "robots", {}):
            return jsonify({"error": "POSE_UNAVAILABLE"}), 404
        rs = {}
        get_raw = getattr(provider, "raw_state", None)
        if get_raw:
            try:
                rs = get_raw(robot_id) or {}
            except Exception:
                rs = {}
        if rs.get("x") is None or rs.get("y") is None:
            return jsonify({"error": "POSE_UNAVAILABLE"}), 404
        px, py = float(rs["x"]), float(rs["y"])
        pose_used = {
            "x": px, "y": py,
            "theta": rs.get("theta"),
            "confidence": rs.get("confidence"),
        }
        source = "robot_state"
    elif x_arg is not None and y_arg is not None:
        try:
            px, py = float(x_arg), float(y_arg)
        except (TypeError, ValueError):
            return jsonify({"error": "x and y must be numbers"}), 400
        theta_arg = request.args.get("theta")
        try:
            theta = float(theta_arg) if theta_arg is not None else None
        except (TypeError, ValueError):
            theta = None
        pose_used = {"x": px, "y": py, "theta": theta, "confidence": None}
        source = "explicit_pose"
    else:
        return jsonify({"error": "robot_id or x&y required"}), 400

    suggestions = _map_model.nearest_landmarks(px, py, k=k, max_dist_m=max_dist)
    return jsonify({
        "frame": "smap_meters",
        "source": source,
        "pose_used": pose_used,
        "suggestions": suggestions,
    })


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


@app.route("/jog/stop", methods=["POST", "OPTIONS"])
def jog_stop():
    """Stop a continuous jog immediately. Body: {robot_id}."""
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    rid = body.get("robot_id")
    if not rid:
        return jsonify({"error": "robot_id required"}), 400
    code, payload = _dispatcher.jog_stop(rid)
    return jsonify(payload), code


@app.route("/jack", methods=["POST", "OPTIONS"])
def jack():
    """Raise/lower the jack via a DO pulse. Body: {robot_id, action: 'up'|'down'}."""
    if request.method == "OPTIONS":
        return "", 204
    if not _dispatcher:
        return jsonify({"error": "Dispatcher not ready"}), 503
    body = request.get_json(force=True, silent=True) or {}
    rid = body.get("robot_id")
    action = body.get("action")
    if not rid:
        return jsonify({"error": "robot_id required"}), 400
    if action not in ("up", "down"):
        return jsonify({"error": "action must be 'up' or 'down'"}), 400
    code, payload = _dispatcher.jack(rid, action)
    if code == 200:
        _broadcast(alarm_msg("info", f"jack {action} on {rid}", rid))
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
