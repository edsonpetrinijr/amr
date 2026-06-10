"""Configurable AMR trigger filter.

A record matches when its named TRIMMED field equals the configured `value`
(single) OR is one of the configured `values` (a set). The PoC Conversor de
Torque triggers on a SET of part numbers ({"field":"part_number",
"values":[...]}); swapping back to a single trigger (e.g. cell/"C ILC") is a
one-line config change (config.ERP_AMR_FILTER), never a code change.
"""
from __future__ import annotations


class AmrFilter:
    def __init__(self, spec: dict) -> None:
        self.field = str(spec["field"])
        # Accept either a single `value` (equality) or a `values` list/set
        # (membership). Internally always a set of trimmed strings.
        if "values" in spec and spec["values"] is not None:
            self.values = {str(v).strip() for v in spec["values"]}
        else:
            self.values = {str(spec["value"]).strip()}

    def matches(self, record) -> bool:
        return getattr(record, self.field, None) in self.values

    def __repr__(self) -> str:  # pragma: no cover
        return f"AmrFilter(field={self.field!r}, values={sorted(self.values)!r})"
