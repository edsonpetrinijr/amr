"""ErpService — the ERP "Reposição" poller worker + operator actions.

Lifecycle of an order (Phase 1):
    seen → blocked_unmapped | ready_for_confirmation
         → confirmed/dispatched → em_entrega → delivered

Orders do NOT auto-dispatch on detection. They wait for an operator confirmation
(callbutton / REST / OPC UA action), which is what confirm_delivery() performs.
"""
from __future__ import annotations

import logging
import os
import shutil
import threading
import time
import uuid

from .. import config, db
from ..models import (
    IDLE, T_DONE, T_ASSIGNED, T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP,
)
from .filter import AmrFilter
from .mapping import ErpMapping
from .parser import iter_records
from .reconcile import classify, order_key, raw_hash

log = logging.getLogger(__name__)

# erp_order statuses we still want to advance toward delivered.
_IN_FLIGHT_TASK_STATES = (T_ASSIGNED, T_ENROUTE_PICKUP, T_AT_PICKUP, T_ENROUTE_DROP)
_RECONCILE_STATUSES = ("confirmed", "dispatched", "em_entrega")


class ErpService:
    def __init__(self, dispatcher, emit, mapping: ErpMapping) -> None:
        self._dispatcher = dispatcher
        self._emit = emit                  # _broadcast(msg) callback (may be None)
        self._mapping = mapping
        self._lock = threading.RLock()     # serializes actions + poll mutations
        self._stop = threading.Event()

    # ── Poller ────────────────────────────────────────────────────────────────

    def poll_loop(self) -> None:
        """Background daemon entry point (started like the other main.py loops)."""
        first = True
        while not self._stop.is_set():
            try:
                self.poll_once()
            except Exception:  # noqa: BLE001 — a bad feed must never kill the thread
                log.exception("erp poll cycle failed")
            self._stop.wait(0.5 if first else config.ERP_POLL_INTERVAL_S)
            first = False

    def stop(self) -> None:
        self._stop.set()

    def poll_once(self) -> dict:
        """One cycle: copy feed → parse → classify → filter → dedup/create →
        reconcile deliveries → write audit row. Returns a small stats dict."""
        src = config.ERP_FEED_PATH
        if not src or not os.path.exists(src):
            log.warning("ERP feed not found: %s — skipping poll", src)
            return {"skipped": True}

        # SAFETY: never read the source in place — always parse a local copy.
        work = config.ERP_WORK_COPY
        shutil.copy2(src, work)

        flt = AmrFilter(config.ERP_AMR_FILTER)
        cap = config.ERP_MAX_DISPATCH
        now = time.time()
        total = order_c = ful_c = can_c = matched = new_c = 0
        created_new = 0

        with self._lock:
            for rec in iter_records(work):
                total += 1
                cls = classify(rec.record_type)
                if cls == "fulfillment":
                    ful_c += 1
                    log.debug("erp fulfillment (log-only): %s %s", rec.record_type, rec.part_number)
                    continue
                if cls == "cancellation":
                    can_c += 1
                    log.debug("erp cancellation (log-only): %s %s", rec.record_type, rec.part_number)
                    continue
                if cls != "order":
                    continue
                order_c += 1
                if not flt.matches(rec):
                    continue
                matched += 1

                key = order_key(cls, rec)
                if db.get_erp_order(key) is not None:
                    db.update_erp_order_fields(key, last_seen_ts=now)
                    continue
                # NEW matching order — cap new creations this cycle.
                if created_new >= cap:
                    continue
                self._create_order(key, cls, rec, now)
                created_new += 1
                new_c += 1

            self.reconcile_deliveries()

        db.insert_erp_snapshot(
            ts=now, source_path=src, copied_path=work, total_lines=total,
            order_count=order_c, fulfillment_count=ful_c, cancellation_count=can_c,
            matched_count=matched, new_count=new_c, dispatched_count=0, note=None,
        )
        log.info("erp poll: lines=%d order=%d matched=%d new=%d", total, order_c, matched, new_c)
        return {"total": total, "order": order_c, "matched": matched, "new": new_c}

    def _create_order(self, key: str, cls: str, rec, now: float) -> None:
        pickup, dropoff = self._mapping.resolve(rec)
        status = "ready_for_confirmation" if (pickup and dropoff) else "blocked_unmapped"
        o = self._blank_order(key)
        o.update(
            raw_hash=raw_hash(rec), record_type=rec.record_type, record_type_class=cls,
            part_number=rec.part_number, storage_loc=rec.storage_loc, cell=rec.cell,
            pou=rec.pou, quantity=rec.quantity, order_date_raw=rec.order_date_raw,
            observation=rec.observation, amr_flagged=1, status=status,
            pickup_station=pickup, dropoff_station=dropoff,
            first_seen_ts=now, last_seen_ts=now, raw_line=rec.raw_line,
            note=None if status == "ready_for_confirmation" else "no station mapping",
        )
        db.upsert_erp_order(o)
        self._emit_order(key)

    # ── Delivery reconciliation ─────────────────────────────────────────────

    def reconcile_deliveries(self) -> None:
        """Advance dispatched orders to em_entrega / delivered by observing the
        underlying dispatcher task state. Broadcasts every status change."""
        tasks = {t.id: t for t in self._dispatcher.all_tasks()}
        for o in db.list_erp_orders(500):
            if o["status"] not in _RECONCILE_STATUSES:
                continue
            tid = o.get("task_id")
            if not tid:
                continue
            t = tasks.get(tid)
            if t is None:
                continue
            if t.state == T_DONE:
                new_status = "delivered"
            elif t.state in _IN_FLIGHT_TASK_STATES:
                new_status = "em_entrega"
            else:
                continue
            if new_status == o["status"]:
                continue
            fields = {"status": new_status}
            if new_status == "delivered":
                fields["delivered_ts"] = time.time()
            db.update_erp_order_fields(o["order_key"], **fields)
            self._emit_order(o["order_key"])

    # ── Operator actions ────────────────────────────────────────────────────

    def confirm_delivery(self) -> dict:
        """FIFO: dispatch the oldest ready_for_confirmation order to its AMR."""
        with self._lock:
            order = db.get_oldest_ready_order()
            if order is None:
                return {"ok": False, "error": "no_ready_order"}
            task = self._dispatcher.create_task(order["pickup_station"], order["dropoff_station"])
            if task is None:
                return {"ok": False, "error": "dispatch_failed"}
            now = time.time()
            db.update_erp_order_fields(
                order["order_key"], status="dispatched", task_id=task.id, dispatched_ts=now,
            )
            updated = db.get_erp_order(order["order_key"])
            self._emit_order(order["order_key"])
            return {"ok": True, "order": updated}

    def request_empty(self) -> dict:
        """Dispatch an AMR from the POU back to RECEBIMENTO to fetch an empty
        rack. POU origin = most-recent order's dropoff, else mapping default."""
        with self._lock:
            pou_station = self._recent_pou_station()
            receb = config.ERP_RECEBIMENTO_STATION
            if not pou_station or not receb:
                return {"ok": False, "error": "no_pou_station"}
            task = self._dispatcher.create_task(pou_station, receb)
            if task is None:
                return {"ok": False, "error": "dispatch_failed"}
            now = time.time()
            key = f"empty_return:{uuid.uuid4().hex[:12]}"
            o = self._blank_order(key)
            o.update(
                record_type="EMPTY", record_type_class="empty_return", amr_flagged=1,
                status="dispatched", pickup_station=pou_station, dropoff_station=receb,
                task_id=task.id, first_seen_ts=now, dispatched_ts=now, last_seen_ts=now,
                note="empty rack return",
            )
            db.upsert_erp_order(o)
            self._emit_order(key)
            return {"ok": True, "order": db.get_erp_order(key)}

    def handle_action(self, action_name: str) -> dict:
        """Dispatch table for physical OPC UA action presses (thread-safe)."""
        if action_name == "confirm-delivery":
            return self.confirm_delivery()
        if action_name == "request-empty":
            return self.request_empty()
        log.warning("erp: unknown action %r", action_name)
        return {"ok": False, "error": "unknown_action"}

    # ── Read API ─────────────────────────────────────────────────────────────

    def list_orders(self, limit: int = 200) -> list[dict]:
        return db.list_erp_orders(limit)

    def amr_ready(self) -> bool:
        """True if at least one robot is idle/available for the ENVIO station."""
        for r in self._dispatcher.provider.robots.values():
            if r.status == IDLE and not r.current_task:
                return True
        return False

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _recent_pou_station(self) -> str | None:
        for o in db.list_erp_orders(50):
            if o["record_type_class"] == "order" and o.get("dropoff_station"):
                return o["dropoff_station"]
        return self._mapping.default_dropoff()

    def _emit_order(self, key: str) -> None:
        if not self._emit:
            return
        o = db.get_erp_order(key)
        if o is not None:
            self._emit({"type": "erp_order", "ts": time.time(), "order": o})

    @staticmethod
    def _blank_order(key: str) -> dict:
        ts = time.time()
        return {
            "order_key": key, "raw_hash": "", "record_type": "", "record_type_class": "",
            "part_number": "", "storage_loc": "", "cell": "", "pou": "", "quantity": "",
            "order_date_raw": "", "observation": "", "amr_flagged": 0, "status": "seen",
            "pickup_station": None, "dropoff_station": None, "task_id": None,
            "first_seen_ts": ts, "dispatched_ts": None, "delivered_ts": None,
            "cancelled_ts": None, "last_seen_ts": ts, "note": None, "raw_line": "",
        }
