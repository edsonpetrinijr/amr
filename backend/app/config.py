"""Fleet configuration — robots, stations, runtime flags.

Coordinates use a 0..100 normalized space (same as the frontend canvas %).
When mapping to the real plant, replace x/y with metric coords and fill
`seer_lm` / `ap_id` / `opcua_node` from RoboShop Pro and Adilson's OPC UA server.
"""
import os

# ── Runtime ───────────────────────────────────────────────────────────────
SIM_MODE = os.getenv("SIM_MODE", "true").lower() in ("1", "true", "yes")
WS_HOST = os.getenv("FLEET_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("FLEET_PORT", "8765"))
TICK_HZ = 10                      # backend simulation/poll rate
TELEMETRY_EVERY_TICKS = 10        # persist robot telemetry every N ticks
DB_PATH = os.getenv("FLEET_DB", os.path.join(os.path.dirname(__file__), "..", "fleet.db"))

# ── OPC UA (callbuttons, owned by Adilson) ──────────────────────────────────
# Filled in Fase 3. Until then sim-mode fakes button presses.
OPCUA_ENDPOINT = os.getenv("OPCUA_ENDPOINT", "")  # e.g. "opc.tcp://10.0.0.5:4840"

# ── Stations ────────────────────────────────────────────────────────────────
# type: "callbutton" | "base" | "ap"
#   callbutton — physical button; an operator calls a robot here
#   base       — home/charge; robots return when idle
#   ap         — Action Point (SEER); pickup/dropoff with orientation
STATIONS = [
    {"id": "BASE",  "type": "base",       "label": "Base",            "x": 50, "y": 92, "seer_lm": "LM1",  "ap_id": None,  "opcua_node": None},
    {"id": "CB1",   "type": "callbutton", "label": "Linha A · Posto 1","x": 12, "y": 18, "seer_lm": "LM10", "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB1"},
    {"id": "CB2",   "type": "callbutton", "label": "Linha A · Posto 2","x": 30, "y": 12, "seer_lm": "LM11", "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB2"},
    {"id": "CB3",   "type": "callbutton", "label": "Linha B · Posto 1","x": 55, "y": 14, "seer_lm": "LM12", "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB3"},
    {"id": "CB4",   "type": "callbutton", "label": "Linha B · Posto 2","x": 78, "y": 20, "seer_lm": "LM13", "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB4"},
    {"id": "CB5",   "type": "callbutton", "label": "Linha C · Posto 1","x": 86, "y": 48, "seer_lm": "LM14", "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB5"},
    {"id": "CB6",   "type": "callbutton", "label": "Linha C · Posto 2","x": 70, "y": 62, "seer_lm": "LM15", "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB6"},
    {"id": "AP1",   "type": "ap",         "label": "Almox · Doca 1",  "x": 18, "y": 58, "seer_lm": "LM20", "ap_id": "AP1", "opcua_node": "ns=1;s=boolBTN011", "opcua_ret": "ns=1;s=boolBTN021"},
    {"id": "CB1",   "type": "callbutton", "label": "Linha A · Posto 1","x": 12, "y": 18, "seer_lm": "LM10", "ap_id": None,  "opcua_node": "ns=1;s=boolBTN012", "opcua_ret": "ns=1;s=boolBTN022"},
]

# Pairs: supplier (quem faz a peça) → consumer (quem precisa da peça)
# Ambos precisam apertar o botão para o AMR ser despachado.
PAIRS = [
    {
        "supplier": "AP1", "consumer": "CB1",
        "fwd_label": "Almox → Linha",   # LM1 → LM2
        "ret_label": "Linha → Almox",   # LM2 → LM1
    }
]

# ── Robots ──────────────────────────────────────────────────────────────────
# Real deployment: 9 operational AMRs (1 of 10 is educational). Each gets an IP
# for the SEER Robokit TCP API (ports 19204/19205/19206). Start small.
ROBOTS = [
    {"id": "AMR-01", "name": "AMR-01", "ip": "192.168.0.101"},
    {"id": "AMR-02", "name": "AMR-02", "ip": "192.168.0.102"},
    {"id": "AMR-03", "name": "AMR-03", "ip": "192.168.0.103"},
    {"id": "AMR-04", "name": "AMR-04", "ip": "192.168.0.104"},
]

ROBOT_SPEED = 18.0   # units (0..100) per second in sim
ARRIVE_EPS = 1.2     # distance considered "arrived"

# ── Failure recovery policy (single-plant pilot) ────────────────────────────
# All env-overridable so tests can shrink the timers for fast runs.
BATTERY_LOW_THRESHOLD = float(os.getenv("BATTERY_LOW_THRESHOLD", "25.0"))  # % — route idle robot to charger below this
BATTERY_CRITICAL      = float(os.getenv("BATTERY_CRITICAL", "15.0"))       # % — abort in-flight task below this
ROBOT_STALE_S         = float(os.getenv("ROBOT_STALE_S", "6.0"))           # s — no telemetry → robot unhealthy/offline
STUCK_TIMEOUT_S       = float(os.getenv("STUCK_TIMEOUT_S", "30.0"))        # s — no progress → stuck
PROGRESS_EPS          = float(os.getenv("PROGRESS_EPS", "1.0"))            # units moved that counts as progress
MAX_TASK_RETRIES      = int(os.getenv("MAX_TASK_RETRIES", "2"))            # re-queue attempts before T_FAILED
ROBOT_COOLDOWN_S      = float(os.getenv("ROBOT_COOLDOWN_S", "20.0"))       # s — failed robot not retried on same task

# ── Telemetry capture (soak-run diagnostics) ────────────────────────────────
# A telemetry run is self-contained: one RUN_ID stamped on every row.
import time as _time
import uuid as _uuid

RUN_TS  = _time.strftime("%Y%m%d_%H%M%S", _time.localtime())
RUN_ID  = os.getenv("RUN_ID", f"run_{RUN_TS}_{_uuid.uuid4().hex[:6]}")

# Per-tick snapshot rate. Real SEER poll thread runs at 2 Hz (POLL_INTERVAL=0.5);
# a dedicated sampler matches that so sim and real behave identically.
SAMPLE_HZ = float(os.getenv("SAMPLE_HZ", "2"))

# Append-only JSONL firehose (crash-proof source of truth) lives next to fleet.db.
_RUNS_DIR = os.getenv("RUNS_DIR", os.path.join(os.path.dirname(__file__), "..", "runs"))
JSONL_PATH = os.getenv("JSONL_PATH", os.path.join(_RUNS_DIR, f"{RUN_ID}.jsonl"))

TELEMETRY_COMMIT_S = float(os.getenv("TELEMETRY_COMMIT_S", "3.0"))  # batch sqlite commits

# ── Soak run loop (A → lift → B → lower → repeat) ───────────────────────────
# DATA CAPTURE ONLY. No watchdog / SAFE-HOLD / alerting here (out of scope).
SOAK_MODE      = os.getenv("SOAK_MODE", "false").lower() in ("1", "true", "yes")
SOAK_ROBOT     = os.getenv("SOAK_ROBOT", ROBOTS[0]["id"] if ROBOTS else "AMR-01")
SOAK_A_STATION = os.getenv("SOAK_A_STATION", "AP1")   # pick / lift point
SOAK_B_STATION = os.getenv("SOAK_B_STATION", "CB1")   # drop / lower point
SOAK_LIFT_S    = float(os.getenv("SOAK_LIFT_S", "2.0"))
SOAK_LOWER_S   = float(os.getenv("SOAK_LOWER_S", "2.0"))
SOAK_IDLE_S    = float(os.getenv("SOAK_IDLE_S", "0.5"))   # gap between cycles
SOAK_LIFT_DO   = int(os.getenv("SOAK_LIFT_DO", "1"))      # digital-output id for the lift
SOAK_MAX_CYCLES = int(os.getenv("SOAK_MAX_CYCLES", "0"))  # 0 = run until stopped
# Optional target headings (radians) for stop-position heading error. None → skip.
SOAK_A_THETA   = float(os.environ["SOAK_A_THETA"]) if os.getenv("SOAK_A_THETA") else None
SOAK_B_THETA   = float(os.environ["SOAK_B_THETA"]) if os.getenv("SOAK_B_THETA") else None
# Localization-confidence floor (only meaningful if SEER exposes confidence).
SOAK_CONF_LOW  = float(os.getenv("SOAK_CONF_LOW", "0.5"))
