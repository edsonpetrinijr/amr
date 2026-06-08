"""ERP fixed-width parser test — the known IKS sample line.

Runnable under pytest or as a plain script (same shim as the other tests).
"""
from __future__ import annotations

try:
    import pytest  # noqa: F401
except ModuleNotFoundError:  # offline sandbox — minimal shim
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()

from server.app.erp.parser import parse_line

# A real IKS order line (cell BT09TC here is used ONLY to validate the parser).
IKS_LINE = (
    "IKS   3989602FBTLOG1  N169  5BT09TCFLBT10TC3000000198999614901708376160067295601/06/202604525489"
    "                                       LT28CASCF2RB8P80000182154"
)


def test_parse_iks_line_fields():
    rec = parse_line(IKS_LINE)
    assert rec.record_type == "IKS"
    assert rec.part_number == "3989602"
    assert rec.storage_loc == "BTLOG1"
    assert rec.cell == "BT09TC"
    assert rec.pou == "FLBT10TC3"


def test_date_stored_raw_not_parsed():
    rec = parse_line(IKS_LINE)
    # Stored verbatim — MM/DD/YYYY is unconfirmed so we never parse it.
    assert rec.order_date_raw == "01/06/2026"
    assert isinstance(rec.order_date_raw, str)


def test_fields_are_trimmed():
    rec = parse_line(IKS_LINE)
    for v in (rec.record_type, rec.part_number, rec.storage_loc, rec.cell, rec.pou):
        assert v == v.strip()


if __name__ == "__main__":
    test_parse_iks_line_fields()
    test_date_stored_raw_not_parsed()
    test_fields_are_trimmed()
    print("test_erp_parser OK")
