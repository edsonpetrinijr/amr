"""Preflight config validation — fail fast, clearly, before a pilot run.

A single cheap, pure `validate()` answers one question: can this config (plus an
optional loaded map) actually support a pilot? It does no I/O so it is trivially
unit-testable and is called both on startup and behind GET /health.

Blocking issues (readiness == "blocked"):
  1. Duplicate station ids.
  2. A pair references a station that doesn't exist.
  3. Real-robot mode: a paired station has no SEER landmark (seer_lm) binding.
  4. A map is loaded but a paired station's seer_lm is missing from it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PreflightResult:
    ok: bool
    issues: list[str] = field(default_factory=list)

    @property
    def readiness(self) -> str:
        return "ok" if self.ok else "blocked"

    def to_dict(self) -> dict:
        return {"readiness": self.readiness, "issues": list(self.issues)}


def validate(
    stations: list[dict],
    pairs: list[dict],
    sim_mode: bool,
    map_model: Optional[object] = None,
) -> PreflightResult:
    """Return a structured readiness result for the given config + map.

    `map_model` is an optional smap.MapModel (anything exposing `.landmarks`
    with `.id`). Passing None skips the map-landmark cross-check.
    """
    issues: list[str] = []

    # 1) Station ids must be unique.
    seen: set[str] = set()
    reported: set[str] = set()
    for s in stations:
        sid = s.get("id")
        if sid in seen and sid not in reported:
            issues.append(f"Duplicate station id '{sid}' in STATIONS")
            reported.add(sid)
        seen.add(sid)

    # Last-write-wins, matching dispatcher._load_stations' dict build.
    by_id = {s.get("id"): s for s in stations}

    # 2) Every station referenced in a pair must exist.
    paired_ids: list[str] = []
    for p in pairs:
        for role in ("supplier", "consumer"):
            sid = p.get(role)
            if sid is None:
                issues.append(f"Pair missing '{role}' station")
                continue
            paired_ids.append(sid)
            if sid not in by_id:
                issues.append(f"Pair {role} '{sid}' not found in STATIONS")

    # 3) Real-robot mode: paired stations need a SEER landmark binding.
    if not sim_mode:
        for sid in paired_ids:
            st = by_id.get(sid)
            if st is None:
                continue  # already reported as missing
            if not (st.get("seer_lm") or "").strip():
                issues.append(
                    f"Station '{sid}' has no seer_lm landmark binding "
                    f"(required in real mode)"
                )

    # 4) Required landmarks must exist in the loaded map.
    if map_model is not None:
        lm_ids = {lm.id for lm in getattr(map_model, "landmarks", [])}
        for sid in paired_ids:
            st = by_id.get(sid)
            if st is None:
                continue
            lm = (st.get("seer_lm") or "").strip()
            if lm and lm not in lm_ids:
                issues.append(
                    f"Station '{sid}': seer_lm '{lm}' not found in loaded map "
                    f"landmarks"
                )

    return PreflightResult(ok=not issues, issues=issues)
