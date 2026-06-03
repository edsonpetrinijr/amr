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
    robot_status_info_req, robot_status_laser_req, robot_status_loc_req,
    robot_status_speed_req, robot_status_task_req,
    robot_task_gotarget_req,
)

log = logging.getLogger(__name__)

CONN_TIMEOUT   = 3.0    # seconds to wait for connect
READ_TIMEOUT   = 5.0    # seconds to wait for a reply
POLL_INTERVAL  = 0.5    # seconds between state polls
LASER_INTERVAL = 0.5    # seconds between laser scans (~2 Hz; not every state tick adds load)
RECONNECT_WAIT = 5.0    # seconds before retry after disconnection


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
        """Send loc + task queries and update state. Returns False on socket error."""
        try:
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
            # ── Battery (best-effort) ─────────────────────────────────────────
            sock.sendall(pack_msg(self._next_seq(), robot_status_info_req, {}))
            info = _recv_reply(sock)  # None is tolerated here

            sock.sendall(pack_msg(self._next_seq(), robot_status_speed_req, {}))
            speed = _recv_reply(sock)  # None tolerated

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
            if info:
                batt = info.get('battery', {})
                if isinstance(batt, dict):
                    updates['battery'] = float(batt.get('percentage', self.state.battery))
                elif isinstance(batt, (int, float)):
                    updates['battery'] = float(batt)
                # Robot model/name (best-effort: field name varies by firmware).
                # Try the common SEER keys without crashing on absence.
                model = (info.get('model')
                         or info.get('vehicle_id')
                         or info.get('vehicle_model')
                         or info.get('version'))
                if isinstance(model, (str, int, float)) and str(model):
                    updates['model'] = str(model)

            self.state.update(**updates)

            # ── Laser scan (gated to ~2 Hz; separate socket via _cmd) ─────────
            now = time.time()
            if now - self._last_laser >= LASER_INTERVAL:
                beams = self.get_laser()
                self.state.update(laser_beams=beams, laser_ts=now)
                self._last_laser = now

            return True

        except (socket.timeout, socket.error) as e:
            log.debug("[%s] poll_once error: %s", self.robot_id, e)
            return False

    # ── Command API ───────────────────────────────────────────────────────────

    def get_laser(self, step: int = 4) -> list:
        """Pull one laser scan (request 1009). `step` is the decimation stride
        (3–5; lower = more points). Returns the `laser_beams` array or [] on
        failure. NOTE(real HW): the protocol PDF (p.24) states beams are already
        in the WORLD/MAP frame as [x, y] metres — the frontend renders them with
        NO pose composition. If a real unit ever returns robot-relative or
        angle/distance instead, this assumption (and the frontend render) breaks.
        Confirm field shape on the first real-robot test."""
        reply = _cmd(self.ip, API_PORT_STATE, self._next_seq(),
                     robot_status_laser_req, {'step': step})
        if not reply:
            return []
        return reply.get('laser_beams', [])

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
