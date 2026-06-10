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
OPCUA_ENDPOINT = os.getenv("OPCUA_ENDPOINT", "")  # e.g. "opc.tcp://10.0.0.5:4840/fleet"

# Driver hardening knobs — all env-overridable so tests can shrink them.
#   OPCUA_DEBOUNCE_S      — ignore repeat rising edges on a node within this window
#                           (kills bounce/chatter from a noisy or held button).
#   OPCUA_RECONNECT_MIN_S — first reconnect wait after a drop (doubles each retry).
#   OPCUA_RECONNECT_MAX_S — cap for the exponential reconnect backoff.
#   OPCUA_SUB_PERIOD_MS   — subscription publish interval requested from the server.
#   OPCUA_HEALTH_S        — how often we ping the server to detect a silent drop.
OPCUA_DEBOUNCE_S      = float(os.getenv("OPCUA_DEBOUNCE_S", "1.0"))
OPCUA_RECONNECT_MIN_S = float(os.getenv("OPCUA_RECONNECT_MIN_S", "1.0"))
OPCUA_RECONNECT_MAX_S = float(os.getenv("OPCUA_RECONNECT_MAX_S", "30.0"))
OPCUA_SUB_PERIOD_MS   = float(os.getenv("OPCUA_SUB_PERIOD_MS", "200"))
OPCUA_HEALTH_S        = float(os.getenv("OPCUA_HEALTH_S", "2.0"))

# Explicit node → (station_id, direction) mapping override. JSON object keyed by
# OPC UA node-id string, value [station_id, direction]. When empty the driver
# derives the map from STATIONS (opcua_node→fwd, opcua_ret→ret). Example:
#   OPCUA_NODE_MAP='{"ns=2;s=CallButton.CB1": ["CB1","fwd"]}'
import json as _json
OPCUA_NODE_MAP: dict[str, tuple[str, str]] = {}
_opcua_raw = os.getenv("OPCUA_NODE_MAP", "").strip()
if _opcua_raw:
    try:
        OPCUA_NODE_MAP = {str(k): (str(v[0]), str(v[1])) for k, v in _json.loads(_opcua_raw).items()}
    except Exception as _e:  # noqa: BLE001 — bad config must not crash the backend
        print(f"[config] ignoring invalid OPCUA_NODE_MAP: {_e}")
        OPCUA_NODE_MAP = {}

# ── OPC UA action bindings (ERP buttons — contract with integration engineer) ─
# node-id string → action name ("confirm-delivery" | "request-empty"). The OPC
# UA driver calls ErpService.handle_action(<name>) on a rising edge of one of
# these nodes. Empty in sim; env-overridable JSON like OPCUA_NODE_MAP. Example:
#   OPCUA_ACTION_MAP='{"ns=1;s=boolBTN030": "confirm-delivery"}'
OPCUA_ACTION_MAP: dict[str, str] = {}
_opcua_action_raw = os.getenv("OPCUA_ACTION_MAP", "").strip()
if _opcua_action_raw:
    try:
        OPCUA_ACTION_MAP = {str(k): str(v) for k, v in _json.loads(_opcua_action_raw).items()}
    except Exception as _e:  # noqa: BLE001 — bad config must not crash the backend
        print(f"[config] ignoring invalid OPCUA_ACTION_MAP: {_e}")
        OPCUA_ACTION_MAP = {}

# ── ERP "Reposição" (replenishment) feed — Phase 1 ──────────────────────────
# A rolling ~375k-line fixed-width snapshot refreshed ~15 min. We NEVER open the
# source in place — always copy it locally (ERP_WORK_COPY) and parse the copy.
ERP_FEED_PATH    = os.getenv("ERP_FEED_PATH", os.path.join(os.path.dirname(__file__), "..", "fixtures", "poc_conversor.txt"))
ERP_WORK_COPY    = os.getenv("ERP_WORK_COPY", os.path.join(os.path.dirname(__file__), "..", "erp_feed_copy.txt"))
ERP_MAPPING_PATH = os.getenv("ERP_MAPPING_PATH", os.path.join(os.path.dirname(__file__), "..", "config", "erp_mapping.yaml"))
ERP_POLL_INTERVAL_S = float(os.getenv("ERP_POLL_INTERVAL_S", "10.0"))
# Cap NEW dispatchable order rows created per poll cycle so a test run never
# turns 28k matching rows into 28k jobs in one go.
ERP_MAX_DISPATCH = int(os.getenv("ERP_MAX_DISPATCH", "5"))
# Stations (Sim PoC). ENVIO = where the AMR loads/leaves; RECEBIMENTO = where an
# empty rack returns. Both = BTLOG1 (estoque) no PoC Conversor de Torque.
ERP_ENVIO_STATION       = os.getenv("ERP_ENVIO_STATION", "BTLOG1")
ERP_RECEBIMENTO_STATION = os.getenv("ERP_RECEBIMENTO_STATION", "BTLOG1")

# AMR trigger filter — the named TRIMMED field must equal `value` OR be one of
# `values` (set membership). PoC Conversor de Torque dispara por PART NUMBER
# (3 PNs da sub do conversor). Trocar p/ {"field":"cell","value":"C ILC"} ou
# {"field":"observation","value":"AMR"} é mudança de UMA linha de config.
ERP_AMR_FILTER: dict = {"field": "part_number",
                        "values": ["3679579", "4175193", "3989602"]}
_erp_filter_raw = os.getenv("ERP_AMR_FILTER", "").strip()
if _erp_filter_raw:
    try:
        _f = _json.loads(_erp_filter_raw)
        if "values" in _f and _f["values"] is not None:
            ERP_AMR_FILTER = {"field": str(_f["field"]),
                              "values": [str(v) for v in _f["values"]]}
        else:
            ERP_AMR_FILTER = {"field": str(_f["field"]), "value": str(_f["value"])}
    except Exception as _e:  # noqa: BLE001
        print(f"[config] ignoring invalid ERP_AMR_FILTER: {_e}")

# Record-type classification sets (CONFIGURABLE). ORDER also matches any
# record_type whose 2-char prefix is in ERP_ORDER_PREFIXES (I5*/N5* variants).
def _erp_set(env_name: str, default: set[str]) -> set[str]:
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return set(default)
    try:
        return {str(x).strip() for x in _json.loads(raw)}
    except Exception as _e:  # noqa: BLE001
        print(f"[config] ignoring invalid {env_name}: {_e}")
        return set(default)

ERP_ORDER_TYPES       = _erp_set("ERP_ORDER_TYPES",
                                 {"IKS", "I5F", "N5A", "N5F", "NFM", "NKS", "NS3", "I5U", "I5M", "I5A"})
ERP_ORDER_PREFIXES    = _erp_set("ERP_ORDER_PREFIXES", {"I5", "N5"})
ERP_FULFILLMENT_TYPES = _erp_set("ERP_FULFILLMENT_TYPES", {"I6A", "N6A", "N6K", "N6L", "I6F"})
ERP_CANCELLATION_TYPES = _erp_set("ERP_CANCELLATION_TYPES", {"I7Q", "N02", "N7A", "N7V"})

# ── Stations ────────────────────────────────────────────────────────────────
# type: "callbutton" | "base" | "ap"
#   callbutton — physical button; an operator calls a robot here
#   base       — home/charge; robots return when idle
#   ap         — Action Point (SEER); pickup/dropoff with orientation
STATIONS = [
    {"id": "BASE",  "type": "base",       "label": "Base",            "x": 50, "y": 92, "seer_lm": "LM1",  "ap_id": None,  "opcua_node": None},
    # CB1 is the pilot pair's consumer (AP1↔CB1). Its real OPC UA bindings
    # (boolBTN012/022) match AP1's boolBTN0xx scheme. NOTE: a duplicate "CB1"
    # entry (placeholder ns=2;s=CallButton.CB1, no opcua_ret) was removed — it
    # silently shadowed this one in _load_stations and broke preflight uniqueness.
    # FLAG for Product: confirm the boolBTN012/022 node ids are the live buttons.
    # The live map (1007.smap) only has landmarks LM1 + LM2; the pilot shuttles
    # LM1 (Almox/AP1) ↔ LM2 (Linha/CB1), matching context/botoes_landmarks.py.
    {"id": "CB1",   "type": "callbutton", "label": "BT-09TC · Linha","x": 12, "y": 18, "seer_lm": "LM2",  "ap_id": None,  "opcua_node": "ns=1;s=boolBTN012", "opcua_ret": "ns=1;s=boolBTN022"},
    # CB2–CB6 are future expansion stations (Linhas A/B/C) that are NOT yet on the
    # live map — it only has LM1 + LM2. Their old LM11–LM15 bindings were stale
    # phantoms, so seer_lm is None until they're surveyed and added to the .smap.
    {"id": "CB2",   "type": "callbutton", "label": "Linha A · Posto 2","x": 30, "y": 12, "seer_lm": None, "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB2"},
    {"id": "CB3",   "type": "callbutton", "label": "Linha B · Posto 1","x": 55, "y": 14, "seer_lm": None, "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB3"},
    {"id": "CB4",   "type": "callbutton", "label": "Linha B · Posto 2","x": 78, "y": 20, "seer_lm": None, "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB4"},
    {"id": "CB5",   "type": "callbutton", "label": "Linha C · Posto 1","x": 86, "y": 48, "seer_lm": None, "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB5"},
    {"id": "CB6",   "type": "callbutton", "label": "Linha C · Posto 2","x": 70, "y": 62, "seer_lm": None, "ap_id": None,  "opcua_node": "ns=2;s=CallButton.CB6"},
    # CB-ALMOX (ex-AP1): Action Points foram REMOVIDOS — agora é um callbutton
    # comum ligado ao landmark LM1. O modelo novo: o operador aperta o botão da
    # ORIGEM e depois o do DESTINO; o robô faz o transporte LM_origem → LM_destino.
    {"id": "CB-ALMOX", "type": "callbutton", "label": "LOG01 · Estoque", "x": 18, "y": 58, "seer_lm": "LM1", "ap_id": None, "opcua_node": "ns=1;s=boolBTN011", "opcua_ret": "ns=1;s=boolBTN021"},

    # ── PoC Conversor de Torque (Sim) ────────────────────────────────────────
    # Gatilho por PART NUMBER (3 PNs da sub do conversor). Pickup único BTLOG1
    # (estoque) → 3 pontos de uso FISICAMENTE DISTINTOS na linha. Coords no
    # espaço sim 0..100; seer_lm=None até o survey físico do mapa real.
    {"id": "BTLOG1",    "type": "callbutton", "label": "BTLOG1 · Estoque",      "x": 20, "y": 78, "seer_lm": None, "ap_id": None, "opcua_node": None},
    {"id": "FLBT10TC1", "type": "callbutton", "label": "BT10TC · POU FLBT10TC1", "x": 14, "y": 22, "seer_lm": None, "ap_id": None, "opcua_node": None},
    {"id": "FLBT10TC2", "type": "callbutton", "label": "BT10TC · POU FLBT10TC2", "x": 30, "y": 16, "seer_lm": None, "ap_id": None, "opcua_node": None},
    {"id": "FLBT10TC3", "type": "callbutton", "label": "BT09TC · POU FLBT10TC3", "x": 46, "y": 22, "seer_lm": None, "ap_id": None, "opcua_node": None},
]

# Action Points removidos: o despacho não usa mais pares supplier/consumer. Um
# transporte é formado por DOIS apertos de callbutton (origem e destino).
PAIRS: list[dict] = []

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

# ── SimProvider localization model (high-fidelity sim of SEER loc quality) ──
# The sim keeps a ground-truth pose (motion physics) and a reported est_pose so
# the recovery FSM is genuinely exercised. Units are the sim's 0..100 space,
# treated as metres for threshold purposes. All env-overridable so tests can
# force fast, deterministic transitions.
LOC_CONFIDENCE_DECAY_RATE     = float(os.getenv("LOC_CONFIDENCE_DECAY_RATE", "0.15"))   # /s — confidence trends up (OK) / down (DEGRADED,LOST)
LOC_DRIFT_RATE_OK             = float(os.getenv("LOC_DRIFT_RATE_OK", "0.05"))           # m/s — est noise amplitude in OK
LOC_DRIFT_RATE_DEGRADED       = float(os.getenv("LOC_DRIFT_RATE_DEGRADED", "0.3"))      # m/s — est drift in DEGRADED
LOC_DRIFT_RATE_LOST           = float(os.getenv("LOC_DRIFT_RATE_LOST", "1.5"))          # m/s — est drift in LOST
LOC_LOST_CONFIDENCE_THRESHOLD = float(os.getenv("LOC_LOST_CONFIDENCE_THRESHOLD", "0.3"))
NAV_FAIL_POSE_ERROR_THRESHOLD_M = float(os.getenv("NAV_FAIL_POSE_ERROR_THRESHOLD_M", "3.0"))  # m — est↔true error that blocks nav
LOC_STUCK_TIMEOUT_S           = float(os.getenv("LOC_STUCK_TIMEOUT_S", "5.0"))          # s — pose-error past threshold → blocked
LOC_NAV_FAIL_TIMEOUT_S        = float(os.getenv("LOC_NAV_FAIL_TIMEOUT_S", "10.0"))      # s — pose-error past threshold → nav_failed
RELOCALIZE_SUCCESS_RADIUS_M   = float(os.getenv("RELOCALIZE_SUCCESS_RADIUS_M", "1.0"))  # m — seed within this of true pose → success
RELOCALIZE_SUCCESS_THETA_DEG  = float(os.getenv("RELOCALIZE_SUCCESS_THETA_DEG", "30.0"))  # deg — heading tolerance for relocalize

# ── Operator manual controls & analytics queries (single-plant pilot) ───────
# Manual JOG safety envelope. vx/vy/w are clamped to ±MAX before being sent to
# the robot (units match SeerProvider.send_velocity → SEER ctrl port 19205:
# vx/vy m/s, w rad/s). Conservative defaults — an operator nudging a robot on a
# live floor should move slowly. All env-overridable.
JOG_MAX_VX = float(os.getenv("JOG_MAX_VX", "0.30"))   # m/s — forward/back
JOG_MAX_VY = float(os.getenv("JOG_MAX_VY", "0.30"))   # m/s — strafe (omni only)
JOG_MAX_W  = float(os.getenv("JOG_MAX_W",  "0.40"))   # rad/s — yaw
# A jog with a duration auto-stops after this many seconds; without a duration
# the command is single-shot and the operator must send zeros / call stop.
JOG_DEFAULT_DURATION_S = float(os.getenv("JOG_DEFAULT_DURATION_S", "0.5"))
JOG_MAX_DURATION_S     = float(os.getenv("JOG_MAX_DURATION_S", "3.0"))

# ── Continuous jog / WASD streaming ─────────────────────────────────────────
# The SEER robot has a velocity watchdog: a single motion command makes it move
# only for an instant, then it stops. To hold motion the backend must RE-SEND
# the velocity continuously. The frontend (WASD hold-to-move) re-POSTs /jog at
# ~150 ms; the backend resends the last commanded velocity to the robot every
# JOG_RESEND_INTERVAL_S, and auto-stops if no /jog refresh arrives within
# JOG_KEEPALIVE_S (so a dropped client or released key never leaves a runaway).
JOG_RESEND_INTERVAL_S = float(os.getenv("JOG_RESEND_INTERVAL_S", "0.1"))   # 10 Hz resend
JOG_KEEPALIVE_S       = float(os.getenv("JOG_KEEPALIVE_S", "0.4"))         # idle watchdog

# ── Jack / load platform (Digital Output pulse) ─────────────────────────────
# The jack is raised/lowered by PULSING a SEER Digital Output (req 6001, port
# 19210): set DO true → wait JACK_PULSE_S → set DO false. (Matches the
# controle_completo_robo.py controlar_jack() reference.) DO IDs are robot-
# specific — confirm on the unit.
JACK_UP_DO_ID   = int(os.getenv("JACK_UP_DO_ID", "1"))
JACK_DOWN_DO_ID = int(os.getenv("JACK_DOWN_DO_ID", "2"))
JACK_PULSE_S    = float(os.getenv("JACK_PULSE_S", "3.0"))

# ── Callbutton transport (2-press model) ────────────────────────────────────
# First press = origin (pickup LM), second press on a different callbutton =
# destination (dropoff LM) → a transport task is created. A lone origin press is
# discarded after this many seconds so a stale origin never lingers.
CALLBUTTON_ORIGIN_TIMEOUT_S = float(os.getenv("CALLBUTTON_ORIGIN_TIMEOUT_S", "30.0"))

# Read-only telemetry/analytics query caps — never scan unbounded rows on the
# request thread.
TELEMETRY_QUERY_DEFAULT_LIMIT = int(os.getenv("TELEMETRY_QUERY_DEFAULT_LIMIT", "500"))
TELEMETRY_QUERY_MAX_LIMIT     = int(os.getenv("TELEMETRY_QUERY_MAX_LIMIT", "5000"))

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
