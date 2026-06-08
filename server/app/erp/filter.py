"""Configurable AMR trigger filter.

A record matches when its named TRIMMED field equals the configured value.
Swapping the trigger (e.g. cell/"C ILC" → observation/"AMR") is a one-line
config change (config.ERP_AMR_FILTER), never a code change.
"""
from __future__ import annotations


class AmrFilter:
    def __init__(self, spec: dict) -> None:
        self.field = str(spec["field"])
        self.value = str(spec["value"])

    def matches(self, record) -> bool:
        return getattr(record, self.field, None) == self.value

    def __repr__(self) -> str:  # pragma: no cover
        return f"AmrFilter(field={self.field!r}, value={self.value!r})"
