"""
Per-robot TCP connection manager.

Each RobotConn owns:
  - A persistent STATE socket (polling loc + task status)
  - Ephemeral connections for TASK / CTRL / OTHER commands

A background thread polls at POLL_HZ and writes to a shared RobotState.
Command methods open a fresh socket, send, read the ACK, close.
"""
from __future__ import annotations

import json
import logging
import math
import socket
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

from .protocol import (
    API_PORT_CTRL, API_PORT_OTHER, API_PORT_STATE, API_PORT_TASK,
    HEAD_SIZE, TASK_FAILED, TASK_FINISHED,
    pack_msg, unpack_head,
    robot_control_motion_req, robot_control_reloc_req,
    robot_other_setdo_req,
    robot_status_battery_req,
    robot_status_info_req, robot_status_laser_req, robot_status_loc_req,
    robot_status_speed_req, robot_status_task_req,
    robot_task_gotarget_req,
)

log = logging.getLogger(__name__)

CONN_TIMEOUT   = 3.0    # seconds to wait for connect
READ_TIMEOUT   = 5.0    # seconds to wait for a reply
POLL_INTERVAL  = 0.1    # seconds between pose polls (~10 Hz loc+speed+task)
SLOW_INTERVAL  = 1.0    # seconds between battery/info polls (~1 Hz)
LASER_INTERVAL = 0.5    # seconds between laser scans (~2 Hz; not every state tick adds load)
RECONNECT_WAIT = 5.0    # seconds before retry after disconnection

LASER_MAX_RANGE = 30.0  # metres; reject beams beyond this as noise/inf
LASER_MAX_POINTS = 720  # decimate world beams to bound payload size


def _laser_reply_to_world_beams(reply: dict, x: float, y: float, theta: float) -> list:
    """Convert a SEER 1009 laser reply into WORLD-frame [[x, y], …] beams.

    Real-HW firmware rarely returns ready-made world-frame `laser_beams`; it
    publishes a POLAR scan in the ROBOT frame. We handle several shapes
    defensively (field names are best-effort, to be CONFIRMED on first real-HW
    bring-up):
      0. `laser_beams` already a non-empty list of [x, y] pairs → pass through
         (sim/tests + any firmware that does the transform for us).
      a. parallel arrays `angle_min` + `angle_increment` + (`distance`|`ranges`).
      b. list of per-beam objects {angle, distance|dist}.
      c. list of robot-frame points {x, y}.
    Robot→world: wx = x + xr*cosθ - yr*sinθ ; wy = y + xr*sinθ + yr*cosθ.
    Returns [] on anything unexpected, decimated to ≤LASER_MAX_POINTS.
    """
    if not isinstance(reply, dict):
        return []
    try:
        # 0. Back-compat: already world-frame [x, y] pairs.
        lb = reply.get('laser_beams')
        if isinstance(lb, list) and lb and isinstance(lb[0], (list, tuple)) and len(lb[0]) >= 2:
            return _decimate(lb)

        cos_t, sin_t = math.cos(theta), math.sin(theta)

        def to_world(xr, yr):
            return [x + xr * cos_t - yr * sin_t, y + xr * sin_t + yr * cos_t]

        def valid(d):
            return d is not None and 0.0 < d < LASER_MAX_RANGE and not math.isinf(d) and not math.isnan(d)

        # Search common container keys for the scan payload.
        containers = [reply, reply.get('data'), reply.get('laserData')]
        lasers = reply.get('lasers')
        if isinstance(lasers, list):
            containers.extend(lasers)
        elif isinstance(lasers, dict):
            containers.append(lasers)

        for c in containers:
            if not isinstance(c, dict):
                continue

            # a. polar parallel arrays.
            angle_min = c.get('angle_min')
            angle_inc = c.get('angle_increment')
            ranges = c.get('distance')
            if ranges is None:
                ranges = c.get('ranges')
            if angle_min is not None and angle_inc is not None and isinstance(ranges, list):
                out = []
                for i, d in enumerate(ranges):
                    if not valid(d):
                        continue
                    ang = angle_min + i * angle_inc
                    out.append(to_world(d * math.cos(ang), d * math.sin(ang)))
                if out:
                    return _decimate(out)

            # b/c. list of per-beam objects under common keys.
            for key in ('beams', 'points', 'laser_beams'):
                seq = c.get(key)
                if not isinstance(seq, list) or not seq or not isinstance(seq[0], dict):
                    continue
                out = []
                for p in seq:
                    if 'angle' in p and ('distance' in p or 'dist' in p):
                        d = p.get('distance', p.get('dist'))
                        if not valid(d):
                            continue
                        ang = p['angle']
                        out.append(to_world(d * math.cos(ang), d * math.sin(ang)))
                    elif 'x' in p and 'y' in p:
                        out.append(to_world(p['x'], p['y']))
                if out:
                    return _decimate(out)
    except Exception:
        return []
    return []


def _decimate(beams: list) -> list:
    """Subsample to at most LASER_MAX_POINTS points, preserving order."""
    n = len(beams)
    if n <= LASER_MAX_POINTS:
        return [list(b) for b in beams]
    stride = (n + LASER_MAX_POINTS - 1) // LASER_MAX_POINTS
    return [list(beams[i]) for i in range(0, n, stride)]


@dataclass
class RobotState:
    """Thread-safe snapshot updated by the polling thread."""
    x:           float = 0.0
    y:           float = 0.0
    theta:       float = 0.0          # radians
    vx:          float = 0.0
    vy:          float = 0.0
    w:           float = 0.0
    battery:     float = 100.0        # percent
    charging:    bool  = False        # SEER `charging` flag (best-effort)
    task_status: int   = 0
    target_id:   str   = ""
    connected:   bool  = False
    # Robot model/name as reported by robot_status_info_req. Best-effort: SEER
    # firmwares vary on the exact field name (vehicle_id / model / version).
    # TODO(real HW): confirm the actual reply key on the unit.
    model:       str   = ""
    # Opportunistic diagnostics — only set if the SEER firmware exposes them.
    # TODO(real HW): confirm exact field names against the unit's API replies.
    confidence:  Optional[float] = None   # localization confidence / reloc score
    blocked:     bool  = False            # obstacle/blocked flag
    # Laser scan — array of [x, y] points in the WORLD/MAP frame (metres), as
    # published by request 1009 (reply field `laser_beams`). Pulled at ~2 Hz by
    # the poll thread and served via GET /robots/<id>/laser.
    laser_beams: list  = field(default_factory=list)
    laser_ts:    float = 0.0
    last_seen:   float = field(default_factory=time.time)
    _lock:       threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def update(self, **kw):
        with self._lock:
            for k, v in kw.items():
                setattr(self, k, v)
            self.last_seen = time.time()

    def snapshot(self) -> dict:
        with self._lock:
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


def _recv_reply(sock: socket.socket) -> Optional[dict]:
    """Read a full SEER response from an open socket. Returns parsed dict or None."""
    try:
        head = sock.recv(HEAD_SIZE)
        if len(head) < HEAD_SIZE:
            return None
        json_len, _ = unpack_head(head)
        if json_len == 0:
            return {}
        body = b''
        while len(body) < json_len:
            chunk = sock.recv(json_len - len(body))
            if not chunk:
                return None
            body += chunk
        return json.loads(body)
    except (socket.timeout, socket.error, json.JSONDecodeError):
        return None


def battery_pct_from_info(info: dict) -> Optional[float]:
    """Extract battery percent (0–100) from a SEER status reply (request 1007).

    SEER Robokit reports a FLAT `battery_level` float in 0.0–1.0 (not nested,
    not a percentage), so we multiply by 100. Falls back to the legacy nested
    `battery.percentage` (already 0–100) only when the real field is absent.
    Returns None when battery is genuinely missing so the caller can KEEP the
    last-known value — a present 0.0 yields 0.0, never None."""
    if not isinstance(info, dict):
        return None
    lvl = info.get('battery_level')
    if lvl is not None:
        return max(0.0, min(100.0, float(lvl) * 100.0))
    batt = info.get('battery')
    if isinstance(batt, dict) and batt.get('percentage') is not None:
        return max(0.0, min(100.0, float(batt['percentage'])))
    if isinstance(batt, (int, float)):
        # Bare number: SEER 0–1 level vs legacy 0–100 percent.
        pct = float(batt) * 100.0 if batt <= 1.0 else float(batt)
        return max(0.0, min(100.0, pct))
    return None


def _cmd(ip: str, port: int, req_id: int, msg_type: int, payload: dict) -> Optional[dict]:
    """Open a fresh connection, send one command, read the reply, close."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(CONN_TIMEOUT)
            s.connect((ip, port))
            s.settimeout(READ_TIMEOUT)
            s.sendall(pack_msg(req_id, msg_type, payload))
            return _recv_reply(s)
    except Exception as e:
        log.debug("cmd %s:%d type=%d → %s", ip, port, msg_type, e)
        return None


class RobotConn:
    """Manages TCP connections to one SEER AMR."""

    def __init__(self, robot_id: str, ip: str) -> None:
        self.robot_id = robot_id
        self.ip       = ip
        self.state    = RobotState()
        self._stop    = threading.Event()
        self._seq     = 0
        self._last_laser = 0.0    # monotonic-ish gate for laser fetch (~2 Hz)
        self._last_slow  = 0.0    # gate for battery/info fetch (~1 Hz)
        self._sock: Optional[socket.socket] = None   # persistent state socket
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the polling thread. Idempotent: a no-op if already running."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name=f"poll-{self.robot_id}")
        self._thread.start()
        log.info("[%s] polling thread started → %s", self.robot_id, self.ip)

    def shutdown(self) -> None:
        """Signal the poll thread to exit and tear down the persistent socket.

        Idempotent and safe to call repeatedly (add/update/remove lifecycle).
        Distinct from stop(), which halts motion via zero velocity."""
        self._stop.set()
        self.close()

    def close(self) -> None:
        """Close the persistent state socket so a blocking recv unblocks and
        the poll thread can exit promptly. Best-effort; never raises."""
        sock = self._sock
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                sock.close()
            except Exception:
                pass
            self._sock = None

    def join(self, timeout: float = 3.0) -> None:
        t = self._thread
        if t is not None and t.is_alive():
            t.join(timeout=timeout)

    def _next_seq(self) -> int:
        self._seq = (self._seq + 1) & 0xFFFF
        return self._seq

    # ── Polling loop ──────────────────────────────────────────────────────────

    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            sock = self._try_connect()
            if sock is None:
                self.state.update(connected=False)
                self._stop.wait(RECONNECT_WAIT)
                continue
            self._sock = sock
            self.state.update(connected=True)
            log.info("[%s] state socket connected", self.robot_id)
            try:
                while not self._stop.is_set():
                    ok = self._poll_once(sock)
                    if not ok:
                        break
                    time.sleep(POLL_INTERVAL)
            except Exception as e:
                log.warning("[%s] poll error: %s", self.robot_id, e)
            finally:
                try:
                    sock.close()
                except Exception:
                    pass
                self._sock = None
                self.state.update(connected=False)
            if not self._stop.is_set():
                log.info("[%s] reconnecting in %.0fs…", self.robot_id, RECONNECT_WAIT)
                self._stop.wait(RECONNECT_WAIT)

    def _try_connect(self) -> Optional[socket.socket]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(CONN_TIMEOUT)
            s.connect((self.ip, API_PORT_STATE))
            s.settimeout(READ_TIMEOUT)
            return s
        except Exception as e:
            log.debug("[%s] connect failed: %s", self.robot_id, e)
            return None

    def _poll_once(self, sock: socket.socket) -> bool:
        """Poll pose-critical state and update RobotState. Returns False on socket
        error. Cadence is decoupled: loc+speed+task every call (~10 Hz), while
        battery+info (1 Hz) and laser (2 Hz) are gated to avoid slowing the loop."""
        try:
            now = time.time()
            slow = now - self._last_slow >= SLOW_INTERVAL
            # ── Location ──────────────────────────────────────────────────────
            sock.sendall(pack_msg(self._next_seq(), robot_status_loc_req, {}))
            loc = _recv_reply(sock)
            if loc is None:
                return False
            # ── Task state ────────────────────────────────────────────────────
            sock.sendall(pack_msg(self._next_seq(), robot_status_task_req, {}))
            task = _recv_reply(sock)
            if task is None:
                return False
            # ── Speed (pose-critical) ─────────────────────────────────────────
            sock.sendall(pack_msg(self._next_seq(), robot_status_speed_req, {}))
            speed = _recv_reply(sock)  # None tolerated
            if speed is None:
                return False
            # ── Battery + info (gated to ~1 Hz; keep last-known when skipped) ──
            batt = info = None
            if slow:
                sock.sendall(pack_msg(self._next_seq(), robot_status_battery_req, {}))
                batt = _recv_reply(sock)  # None tolerated
                sock.sendall(pack_msg(self._next_seq(), robot_status_info_req, {}))
                info = _recv_reply(sock)  # None tolerated
                self._last_slow = now

            updates: dict = {}
            if loc:
                updates.update(x=loc.get('x', self.state.x),
                                y=loc.get('y', self.state.y),
                                theta=loc.get('angle', self.state.theta))
                # Opportunistic: SEER loc may carry a localization confidence /
                # reloc score and an obstacle/blocked flag. Keep last-known if absent.
                conf = loc.get('confidence', loc.get('reloc_status'))
                if conf is not None:
                    updates['confidence'] = conf
                blk = loc.get('blocked')
                if blk is not None:
                    updates['blocked'] = bool(blk)
            if speed:
                updates.update(vx=speed.get('vx', self.state.vx),
                                vy=speed.get('vy', self.state.vy),
                                w=speed.get('w', self.state.w))
            if task:
                updates.update(task_status=task.get('task_status', self.state.task_status),
                                target_id=task.get('target_id', self.state.target_id) or '')
            if batt:
                # SEER request 1007 reports a FLAT `battery_level` (0.0–1.0).
                # Keep the previous percent when genuinely absent; a present
                # 0.0 sticks. This is the authoritative battery source.
                pct = battery_pct_from_info(batt)
                if pct is not None:
                    updates['battery'] = pct
                # Charging flag from the 1007 reply (kept if firmware omits it).
                chg = batt.get('charging')
                if chg is not None:
                    updates['charging'] = bool(chg)
            if info:
                # Robot model/name (best-effort: field name varies by firmware).
                # Try the common SEER keys without crashing on absence.
                model = (info.get('model')
                         or info.get('vehicle_id')
                         or info.get('vehicle_model')
                         or info.get('version'))
                if isinstance(model, (str, int, float)) and str(model):
                    updates['model'] = str(model)

            self.state.update(**updates)

            # ── Laser scan (gated to ~2 Hz; INLINE on the persistent socket) ──
            # Fetched on the SAME poll socket (request→reply paired) instead of
            # opening a second concurrent 19204 connection via get_laser(), which
            # could fail/return nothing on real hardware. The 1009 reply is POLAR
            # in the ROBOT frame on real HW, so we transform to WORLD here using
            # the freshly-updated pose (loc applied above).
            if now - self._last_laser >= LASER_INTERVAL:
                sock.sendall(pack_msg(self._next_seq(), robot_status_laser_req, {'step': 4}))
                laser = _recv_reply(sock)  # None tolerated
                if laser is None:
                    return False
                beams = _laser_reply_to_world_beams(
                    laser, self.state.x, self.state.y, self.state.theta)
                self.state.update(laser_beams=beams, laser_ts=now)
                self._last_laser = now

            return True

        except (socket.timeout, socket.error) as e:
            log.debug("[%s] poll_once error: %s", self.robot_id, e)
            return False

    # ── Command API ───────────────────────────────────────────────────────────

    def get_laser(self, step: int = 4) -> list:
        """Pull one laser scan (request 1009) over a FRESH connection. `step` is
        the decimation stride (3–5; lower = more points). Returns WORLD-frame
        [x, y] beams (via _laser_reply_to_world_beams) or [] on failure. On real
        HW the 1009 reply is POLAR/robot-frame, so we transform using the last
        known pose. NOTE: the poll thread fetches laser INLINE on its persistent
        socket; this standalone method exists for the GET /robots/<id>/laser
        endpoint and deliberately opens its own connection."""
        reply = _cmd(self.ip, API_PORT_STATE, self._next_seq(),
                     robot_status_laser_req, {'step': step})
        if not reply:
            return []
        return _laser_reply_to_world_beams(
            reply, self.state.x, self.state.y, self.state.theta)

    def goto_target(self, landmark_id: str) -> bool:
        """Send the robot to a SEER landmark (LM1, LM2 …). Returns True if ACK received."""
        reply = _cmd(self.ip, API_PORT_TASK, self._next_seq(),
                     robot_task_gotarget_req, {'id': landmark_id})
        ok = reply is not None
        if ok:
            log.info("[%s] goto %s sent", self.robot_id, landmark_id)
        else:
            log.warning("[%s] goto %s — no ACK", self.robot_id, landmark_id)
        return ok

    def send_velocity(self, vx: float, vy: float, w: float) -> bool:
        reply = _cmd(self.ip, API_PORT_CTRL, self._next_seq(),
                     robot_control_motion_req, {'vx': vx, 'vy': vy, 'w': w})
        return reply is not None

    def stop(self) -> bool:
        return self.send_velocity(0, 0, 0)

    def relocalize(self, x: float, y: float, angle: float) -> bool:
        reply = _cmd(self.ip, API_PORT_CTRL, self._next_seq(),
                     robot_control_reloc_req, {'x': x, 'y': y, 'angle': angle})
        return reply is not None

    def set_do(self, do_id: int, status: bool) -> bool:
        reply = _cmd(self.ip, API_PORT_OTHER, self._next_seq(),
                     robot_other_setdo_req, {'id': do_id, 'status': status})
        return reply is not None

    def arrived(self) -> bool:
        """True ONLY when the robot has SUCCESSFULLY finished navigating to its
        last target (TASK_FINISHED == 3). A FAILED nav (4) is NOT an arrival —
        recovery handles it via navigation_failed()."""
        return self.state.task_status == TASK_FINISHED

    def navigation_failed(self) -> bool:
        return self.state.task_status == TASK_FAILED
