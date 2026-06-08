"""Fixed-width ERP record parsing.

Layout (1-indexed inclusive columns → Python slice [start-1:end]); every parsed
field is whitespace-trimmed. The date is stored RAW (MM/DD/YYYY is unconfirmed).

    record_type   cols  1-3   [0:3]
    part_number   cols  7-13  [6:13]
    storage_loc   cols 15-20  [14:20]
    cell          cols 30-35  [29:35]
    pou           cols 36-44  [35:44]
    quantity      cols 45-53  [44:53]
    date (raw)    cols 79-88  [78:88]
    observation   cols 97-120 [96:120]
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass
class ErpRecord:
    record_type: str
    part_number: str
    storage_loc: str
    cell: str
    pou: str
    quantity: str
    order_date_raw: str
    observation: str
    raw_line: str


def parse_line(line: str) -> ErpRecord:
    """Parse one fixed-width feed line into an ErpRecord (fields trimmed)."""
    raw = line.rstrip("\r\n")
    return ErpRecord(
        record_type=raw[0:3].strip(),
        part_number=raw[6:13].strip(),
        storage_loc=raw[14:20].strip(),
        cell=raw[29:35].strip(),
        pou=raw[35:44].strip(),
        quantity=raw[44:53].strip(),
        order_date_raw=raw[78:88].strip(),
        observation=raw[96:120].strip(),
        raw_line=raw,
    )


def iter_records(path: str) -> Iterator[ErpRecord]:
    """Stream-parse a (already-copied) feed file. Skips blank lines."""
    with open(path, "r", encoding="latin-1", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            yield parse_line(line)
