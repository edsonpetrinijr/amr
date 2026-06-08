"""ERP AMR trigger-filter test — configurable field/value match."""
from __future__ import annotations

try:
    import pytest  # noqa: F401
except ModuleNotFoundError:
    class _PytestShim:
        @staticmethod
        def fixture(fn):
            return fn
    pytest = _PytestShim()

from server.app.erp.filter import AmrFilter
from server.app.erp.parser import parse_line


def make_line(record_type="IKS", part="1234567", storage="STLOC1",
              cell="C ILC", pou="POU123", qty="000000010",
              date="01/06/2026", obs="") -> str:
    """Build a fixed-width feed line from named fields (cols match parser)."""
    buf = [" "] * 120

    def put(s, start):
        for i, ch in enumerate(s):
            buf[start + i] = ch

    put(record_type[:3], 0)
    put(part[:7], 6)
    put(storage[:6], 14)
    put(cell[:6], 29)
    put(pou[:9], 35)
    put(qty[:9], 44)
    put(date[:10], 78)
    put(obs[:24], 96)
    return "".join(buf)


def test_cell_filter_matches_c_ilc():
    flt = AmrFilter({"field": "cell", "value": "C ILC"})
    match = parse_line(make_line(cell="C ILC"))
    nomatch = parse_line(make_line(cell="BT09TC"))
    assert match.cell == "C ILC"
    assert flt.matches(match) is True
    assert flt.matches(nomatch) is False


def test_filter_is_one_line_swappable_to_observation():
    flt = AmrFilter({"field": "observation", "value": "AMR"})
    amr_obs = parse_line(make_line(cell="BT09TC", obs="AMR"))
    plain = parse_line(make_line(cell="C ILC", obs=""))
    # cell no longer drives the trigger — only the observation field does.
    assert flt.matches(amr_obs) is True
    assert flt.matches(plain) is False


if __name__ == "__main__":
    test_cell_filter_matches_c_ilc()
    test_filter_is_one_line_swappable_to_observation()
    print("test_erp_filter OK")
