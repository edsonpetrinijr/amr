"""ERP "Reposição" (replenishment) — Phase 1.

Reads a rolling fixed-width ERP feed, classifies records, filters the ones an
AMR should service, dedups them idempotently into fleet.db, and exposes operator
actions (confirm-delivery / request-empty) that drive the Dispatcher.

Public surface:
    ErpService — the poller worker + operator actions + SSE emit.
"""
from .service import ErpService
from .parser import ErpRecord, parse_line, iter_records
from .filter import AmrFilter
from .mapping import ErpMapping, load_mapping
from .reconcile import classify, order_key

__all__ = [
    "ErpService", "ErpRecord", "parse_line", "iter_records",
    "AmrFilter", "ErpMapping", "load_mapping", "classify", "order_key",
]
