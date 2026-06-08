"""Record classification + idempotency key.

classify() buckets a record_type into order | fulfillment | cancellation | other
using the CONFIGURABLE sets in config. order_key() is the dedup hash persisted in
fleet.db so the same order reappearing across rolling snapshots is never
duplicated nor re-dispatched.
"""
from __future__ import annotations

import hashlib

from .. import config


def classify(record_type: str) -> str:
    """order | fulfillment | cancellation | other (Phase 1 acts only on order)."""
    rt = (record_type or "").strip()
    if rt in config.ERP_FULFILLMENT_TYPES:
        return "fulfillment"
    if rt in config.ERP_CANCELLATION_TYPES:
        return "cancellation"
    if rt in config.ERP_ORDER_TYPES or rt[:2] in config.ERP_ORDER_PREFIXES:
        return "order"
    return "other"


def order_key(record_type_class: str, record) -> str:
    """sha1 over the content that identifies a unique order across snapshots."""
    parts = [
        record_type_class,
        record.part_number,
        record.storage_loc,
        record.cell,
        record.pou,
        record.quantity,
        record.order_date_raw,
    ]
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()


def raw_hash(record) -> str:
    return hashlib.sha1(record.raw_line.encode("utf-8", "replace")).hexdigest()
