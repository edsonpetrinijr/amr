"""Report v1 summary metrics.

This module computes the three reliability numbers requested by SQ2 Sprint 1
from persisted task events (SQLite task_events), without changing dispatch
behavior or runtime flows.
"""
from __future__ import annotations

import time
from typing import Any

from . import db


DEFAULT_WINDOW_S = 24 * 60 * 60
MAX_EVENTS_LIMIT = 50000


def _pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 3)


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def build_summary(from_ts: float | None, to_ts: float | None, limit: int = 10000) -> dict[str, Any]:
    """Compute report v1 summary for a bounded time window.

    Rules (audit-friendly, v1):
    - mission started: distinct task_id with event='created' inside the window
    - mission finished: distinct task_id with event='done' inside the window
    - physical intervention: distinct task_id with event='failed' inside the
      window (proxy that requires operator handling in v1)
    - MTBI: mean delta in seconds between consecutive failed events timestamps;
      undefined (null) with fewer than 2 interventions.
    """
    now = time.time()
    to_bound = float(to_ts) if to_ts is not None else now
    from_bound = float(from_ts) if from_ts is not None else (to_bound - DEFAULT_WINDOW_S)
    if from_bound > to_bound:
        raise ValueError("from_ts must be <= to_ts")

    clamped_limit = max(1, min(int(limit), MAX_EVENTS_LIMIT))
    rows = db.query_task_events(since=from_bound, to_ts=to_bound, limit=clamped_limit)

    missions_started: set[str] = set()
    missions_finished: set[str] = set()
    interventions_physical: set[str] = set()
    intervention_ts: list[float] = []

    for row in rows:
        task_id = row.get("task_id")
        event = row.get("event")
        ts = row.get("ts")
        if not task_id or not event:
            continue
        if event == "created":
            missions_started.add(task_id)
        elif event == "done":
            missions_finished.add(task_id)
        elif event == "failed":
            interventions_physical.add(task_id)
            if isinstance(ts, (int, float)):
                intervention_ts.append(float(ts))

    intervention_ts.sort()
    mtbi_values: list[float] = []
    for i in range(1, len(intervention_ts)):
        mtbi_values.append(intervention_ts[i] - intervention_ts[i - 1])

    started_n = len(missions_started)
    finished_n = len(missions_finished)
    interventions_n = len(interventions_physical)

    notes = [
        "v1 intervention proxy: distinct task_id with task_events.event='failed' in period.",
        "mission completion rate = missions_finished / missions_started * 100 (0 when missions_started=0).",
        "physical intervention rate = interventions_physical / missions_started * 100 (0 when missions_started=0).",
        "mtbi_seconds = mean delta between consecutive failed event timestamps; null when <2 interventions.",
    ]

    return {
        "period": {"from_ts": from_bound, "to_ts": to_bound},
        "intervention_physical_rate_pct": _pct(interventions_n, started_n),
        "mission_completion_rate_pct": _pct(finished_n, started_n),
        "mtbi_seconds": _mean(mtbi_values),
        "counts": {
            "missions_started": started_n,
            "missions_finished": finished_n,
            "interventions_physical": interventions_n,
        },
        "notes": notes,
    }
