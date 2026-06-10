"""POU/cell/storage_loc → station mapping, loaded from erp_mapping.yaml.

Prefers PyYAML; falls back to a tiny constrained loader (mappings only) so the
backend has zero hard dependency on PyYAML being installed.
"""
from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)


class ErpMapping:
    """Resolves an ERP record to a (pickup, dropoff) station pair.

    Match order: part_number → cell → pou → storage_loc → default. Returns
    (None, None) when nothing matches and there is no default (→ caller parks it
    blocked_unmapped).
    """

    def __init__(self, data: dict | None) -> None:
        self.data = data or {}

    def envio_station(self) -> str | None:
        return self.data.get("envio_station")

    def recebimento_station(self) -> str | None:
        return self.data.get("recebimento_station")

    def default_pickup(self) -> str | None:
        return (self.data.get("default") or {}).get("pickup")

    def default_dropoff(self) -> str | None:
        return (self.data.get("default") or {}).get("dropoff")

    def resolve(self, record) -> tuple[str | None, str | None]:
        # Match order: part_number → cell → pou → storage_loc → default.
        # Keys are compared as TRIMMED strings on both sides so a numeric YAML
        # key (PyYAML parses `3679579:` as int) still matches the string field.
        for key in ("part_number", "cell", "pou", "storage_loc"):
            section = self.data.get(key) or {}
            val = getattr(record, key, "")
            if not val:
                continue
            for sk, sv in section.items():
                if str(sk).strip() == str(val).strip():
                    m = sv or {}
                    return m.get("pickup"), m.get("dropoff")
        d = self.data.get("default")
        if d:
            return d.get("pickup"), d.get("dropoff")
        return None, None


def _parse_simple_yaml(text: str) -> dict:
    """Constrained YAML loader for our mapping file: nested mappings only,
    2-space indents, `key: value` / `key:` (nested) / `key: {}` (empty)."""
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(raw.rstrip())

    pos = [0]

    def parse_block(indent: int) -> dict:
        result: dict = {}
        while pos[0] < len(lines):
            line = lines[pos[0]]
            cur = len(line) - len(line.lstrip(" "))
            if cur < indent:
                break
            if cur > indent:  # defensive — malformed deeper indent
                pos[0] += 1
                continue
            key, _, val = line.strip().partition(":")
            key, val = key.strip(), val.strip()
            pos[0] += 1
            if val == "":
                result[key] = parse_block(indent + 2)
            elif val == "{}":
                result[key] = {}
            else:
                result[key] = val
        return result

    return parse_block(0)


def load_mapping(path: str) -> ErpMapping:
    """Load the mapping yaml. Missing/invalid file → empty mapping (logged)."""
    if not path or not os.path.exists(path):
        log.warning("ERP mapping not found: %s — using empty mapping", path)
        return ErpMapping({})
    try:
        text = open(path, "r", encoding="utf-8").read()
    except OSError as e:
        log.warning("ERP mapping unreadable (%s) — using empty mapping", e)
        return ErpMapping({})
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text) or {}
    except ImportError:
        data = _parse_simple_yaml(text)
    except Exception as e:  # noqa: BLE001 — bad yaml must not crash startup
        log.warning("ERP mapping parse failed (%s) — using empty mapping", e)
        data = {}
    return ErpMapping(data)
