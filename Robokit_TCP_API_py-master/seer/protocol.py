"""
SEER Robokit NetProtocol — TCP wire protocol.

Reverse-engineered from XiaoxingChen/roboshopAPI_py (identical to the
netprotocol package used in controle_completo_robo.py / visualizadors).

Packet format  (big-endian, 16 bytes):
  magic   : 1 B  = 0x5A
  version : 1 B  = 1
  req_id  : 2 B  (H) — sequence number
  json_len: 4 B  (L)
  msg_type: 2 B  (H) — API command number
  reserved: 6 B  = 0x00...

Followed immediately by the UTF-8 JSON payload (json_len bytes).
"""
import json
import struct

# ── Port assignments ──────────────────────────────────────────────────────────
API_PORT_STATE  = 19204   # Status queries (loc, speed, battery, task state)
API_PORT_CTRL   = 19205   # Motion control & relocalization
API_PORT_TASK   = 19206   # Navigation tasks (go-to-target)
API_PORT_OTHER  = 19210   # Digital I/O

# ── Status API (port 19204) ───────────────────────────────────────────────────
robot_status_info_req    = 1000  # Robot info (firmware, battery, …)
robot_status_run_req     = 1002  # Run mode
robot_status_mode_req    = 1003  # Drive mode
robot_status_loc_req     = 1004  # Pose → {x, y, angle}
robot_status_speed_req   = 1005  # Velocity → {vx, vy, w}
robot_status_area_req    = 1011  # Areas → {area_ids:[…]}
robot_status_task_req    = 1020  # Task state → {task_status, target_id}
robot_status_alarm_res   = 1050  # Alarms

# ── Control API (port 19205) ──────────────────────────────────────────────────
robot_control_reloc_req  = 2002  # Relocalize → {x, y, angle}
robot_control_motion_req = 2010  # Velocity cmd → {vx, vy, w}

# ── Task API (port 19206) ─────────────────────────────────────────────────────
robot_task_gotarget_req  = 3051  # Go to landmark → {id:"LM1"}

# ── Other API (port 19210) ────────────────────────────────────────────────────
robot_other_setdo_req    = 6001  # Set digital output → {id, status}

# ── Task status codes ─────────────────────────────────────────────────────────
TASK_NONE      = 0
TASK_RUNNING   = 1
TASK_NEAR_GOAL = 2
TASK_FINISHED  = 3   # robot arrived
TASK_FAILED    = 4
TASK_SUSPENDED = 5   # paused

# ── Header ────────────────────────────────────────────────────────────────────
_HEAD_FMT = '!BBHLH6s'
_RSV      = b'\x00' * 6
HEAD_SIZE = struct.calcsize(_HEAD_FMT)   # 16 bytes


def pack_msg(req_id: int, msg_type: int, payload: dict | None = None) -> bytes:
    body = b''
    if payload:
        body = json.dumps(payload).encode('ascii')
    header = struct.pack(_HEAD_FMT, 0x5A, 1, req_id, len(body), msg_type, _RSV)
    return header + body


def unpack_head(data: bytes) -> tuple[int, int]:
    """Returns (json_len, req_id)."""
    parsed = struct.unpack(_HEAD_FMT, data[:HEAD_SIZE])
    json_len = parsed[3]
    req_id   = parsed[2]
    return json_len, req_id
