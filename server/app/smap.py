"""
.smap parser — loads SEER RoboShop Pro map files (JSON, single-line).

Exposes a MapModel with everything the UI and dispatcher need:
  - extents (minPos / maxPos in metres)
  - walls (normalLineList + lineList)
  - nav_points (normalPosList — drivable area for background rendering)
  - action_points (advancedPointList — pickup / dropoff APs)
  - areas (advancedAreaList — charging zones, rest areas, no-go zones)
  - landmarks (landmarkList — localization references)
  - robot_pos (initial pose if present)

Coordinates are kept in real metres (same frame as the SEER robot).
The frontend canvas is responsible for the world→pixel transform using
the extents.
"""
from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class Pos2D:
    x: float
    y: float

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}


@dataclass
class Pose2D:
    x: float
    y: float
    theta: float  # radians

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "theta": self.theta}


@dataclass
class Wall:
    start: Pos2D
    end: Pos2D

    def to_dict(self) -> dict:
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class ActionPoint:
    """advancedPointList entry — AP that robots can navigate to."""
    id: str           # e.g. "AP1"
    x: float
    y: float
    theta: float = 0.0
    ap_type: str = ""  # className from SEER e.g. "normalPoint"
    label: str = ""    # instanceName

    def to_dict(self) -> dict:
        return {
            "id": self.id, "x": self.x, "y": self.y,
            "theta": self.theta, "ap_type": self.ap_type, "label": self.label,
        }


@dataclass
class Area:
    """advancedAreaList entry — charging zone, rest area, no-go zone, etc."""
    id: str
    class_name: str   # e.g. "chargeArea", "restArea", "forbiddenArea"
    label: str
    points: list[Pos2D] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "class_name": self.class_name,
            "label": self.label,
            "points": [p.to_dict() for p in self.points],
        }


@dataclass
class Landmark:
    id: str
    x: float
    y: float
    label: str = ""   # optional human label (property key="label" → stringValue)

    def to_dict(self) -> dict:
        d = {"id": self.id, "x": self.x, "y": self.y}
        if self.label:
            d["label"] = self.label
        return d


@dataclass
class Route:
    """advancedCurveList entry — path connecting two LMs / APs (DegenerateBezier or BezierPath)."""
    id: str          # instanceName e.g. "LM2-LM1"
    start_id: str    # instanceName of start point  e.g. "LM2"
    end_id: str      # instanceName of end point    e.g. "LM1"
    start: Pos2D
    end: Pos2D
    ctrl1: Pos2D
    ctrl2: Pos2D
    direction: int   # 0 = bidirectional, 1 = start→end only, 2 = end→start only

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "start_id": self.start_id,
            "end_id": self.end_id,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "ctrl1": self.ctrl1.to_dict(),
            "ctrl2": self.ctrl2.to_dict(),
            "direction": self.direction,
        }


@dataclass
class MapModel:
    name: str
    map_type: str
    version: str
    resolution: float
    min_pos: Pos2D
    max_pos: Pos2D
    walls: list[Wall] = field(default_factory=list)
    nav_points: list[Pos2D] = field(default_factory=list)
    action_points: list[ActionPoint] = field(default_factory=list)
    areas: list[Area] = field(default_factory=list)
    landmarks: list[Landmark] = field(default_factory=list)
    routes: list[Route] = field(default_factory=list)
    robot_pos: Optional[Pose2D] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "map_type": self.map_type,
            "version": self.version,
            "resolution": self.resolution,
            "min_pos": self.min_pos.to_dict(),
            "max_pos": self.max_pos.to_dict(),
            "walls": [w.to_dict() for w in self.walls],
            "nav_points": [p.to_dict() for p in self.nav_points],
            "action_points": [ap.to_dict() for ap in self.action_points],
            "areas": [a.to_dict() for a in self.areas],
            "landmarks": [lm.to_dict() for lm in self.landmarks],
            "routes": [r.to_dict() for r in self.routes],
            "robot_pos": self.robot_pos.to_dict() if self.robot_pos else None,
        }

    def nearest_landmarks(
        self,
        x: float,
        y: float,
        k: int = 5,
        max_dist_m: Optional[float] = None,
    ) -> list[dict]:
        """Return the k nearest map landmarks to (x, y), sorted by Euclidean
        distance ascending. Coordinates are in METRES (smap frame) — no scaling.

        Each entry: {lm_id, name, x, y, theta, dist_m}. Landmark records in this
        firmware carry no heading, so `theta` is always None and `name` mirrors
        the landmark id. Tie-break is deterministic: equal distances order by
        lm_id ascending (independent of map insertion order)."""
        out: list[dict] = []
        for lm in self.landmarks:
            dist = math.hypot(lm.x - x, lm.y - y)
            if max_dist_m is not None and dist > max_dist_m:
                continue
            out.append({
                "lm_id": lm.id,
                "name": lm.id,
                "x": lm.x,
                "y": lm.y,
                "theta": None,
                "dist_m": round(dist, 6),
            })
        out.sort(key=lambda e: (e["dist_m"], e["lm_id"]))
        if k is not None and k >= 0:
            return out[:k]
        return out


# ── Parser ────────────────────────────────────────────────────────────────────

def load_map(path: str | Path) -> MapModel:
    """Parse a .smap file and return a MapModel.

    .smap files are single-line JSON (SEER convention). We strip after the
    first newline just in case.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read().strip()
        if "\n" in raw:
            raw = raw.split("\n")[0]
    data: dict = json.loads(raw)

    header = data.get("header", {})
    min_p = header.get("minPos", {})
    max_p = header.get("maxPos", {})

    # ── walls ─────────────────────────────────────────────────────────────────
    walls: list[Wall] = []
    # advancedLineList: {line: {startPos: {x,y}, endPos: {x,y}}}
    for entry in data.get("advancedLineList", []):
        ln = entry.get("line", {})
        sp = ln.get("startPos", {})
        ep = ln.get("endPos",   {})
        if "x" in sp and "y" in sp and "x" in ep and "y" in ep:
            walls.append(Wall(
                start=Pos2D(sp["x"], sp["y"]),
                end=Pos2D(ep["x"],   ep["y"]),
            ))
    # legacy keys (older SEER firmware)
    for src_key in ("lineList", "normalLineList"):
        for entry in data.get(src_key, []):
            sp = entry.get("startPos", entry.get("start", {}))
            ep = entry.get("endPos",   entry.get("end",   {}))
            if "x" in sp and "y" in sp and "x" in ep and "y" in ep:
                walls.append(Wall(
                    start=Pos2D(sp["x"], sp["y"]),
                    end=Pos2D(ep["x"],   ep["y"]),
                ))

    # ── nav points (drivable area, for background rendering only) ─────────────
    nav_points = [
        Pos2D(p["x"], p["y"])
        for p in data.get("normalPosList", [])
        if "x" in p and "y" in p
    ]

    # ── action points + landmarks ─────────────────────────────────────────────
    # advancedPointList holds two kinds of entries:
    #   • LocationMark / LM* → SEER *landmarks* (localization references). These
    #     are NOT navigable action points — the robot navigates to them by
    #     landmark id (see context/botoes_landmarks.py: ir_para_landmark("LM1")).
    #   • everything else     → action points (pickup/dropoff destinations).
    # We classify each entry into exactly one bucket so landmarks never leak into
    # the action-point set (which would wrongly satisfy ap_id validation).
    action_points: list[ActionPoint] = []
    landmarks: list[Landmark] = []

    for i, entry in enumerate(data.get("advancedPointList", [])):
        pos = entry.get("pos", entry)  # may be nested {"pos": {x,y}} or flat {x,y}
        px = pos.get("x", 0.0)
        py = pos.get("y", 0.0)
        theta = pos.get("theta", 0.0)
        instance_name = entry.get("instanceName", f"P{i+1}")
        class_name = entry.get("className", "")

        is_landmark = (
            "Location" in class_name
            or "Landmark" in class_name
            or instance_name.startswith("LM")
        )
        if is_landmark:
            # Extract optional human label from the property array (key="label").
            # InnovationBox copy.smap carries e.g. {"key":"label","type":"string","stringValue":"LOG01"}.
            lm_label = ""
            for prop in entry.get("property", []):
                if prop.get("key") == "label":
                    lm_label = str(prop.get("stringValue", ""))
                    break
            # Landmark only — do NOT also register it as an action point.
            landmarks.append(Landmark(id=instance_name, x=px, y=py, label=lm_label))
        else:
            action_points.append(ActionPoint(
                id=instance_name,
                x=px,
                y=py,
                theta=theta,
                ap_type=class_name,
                label=instance_name,
            ))

    # legacy landmarkList key
    for entry in data.get("landmarkList", []):
        lm_id = entry.get("id") or entry.get("instanceName", "")
        landmarks.append(Landmark(
            id=lm_id,
            x=entry.get("x", entry.get("pos", {}).get("x", 0)),
            y=entry.get("y", entry.get("pos", {}).get("y", 0)),
        ))

    # ── areas ─────────────────────────────────────────────────────────────────
    areas: list[Area] = []
    for i, entry in enumerate(data.get("advancedAreaList", [])):
        area_id = entry.get("instanceName") or entry.get("id") or f"AREA{i+1}"
        pts_raw = entry.get("areaList", entry.get("points", []))
        pts = [Pos2D(p.get("x", 0), p.get("y", 0)) for p in pts_raw if "x" in p]
        areas.append(Area(
            id=area_id,
            class_name=entry.get("className", ""),
            label=entry.get("instanceName", ""),
            points=pts,
        ))

    # ── routes (advancedCurveList — paths between LMs / APs) ─────────────────
    routes: list[Route] = []
    for entry in data.get("advancedCurveList", []):
        sp = entry.get("startPos", {})
        ep = entry.get("endPos", {})
        c1 = entry.get("controlPos1", {})
        c2 = entry.get("controlPos2", {})
        if not (sp and ep and c1 and c2):
            continue
        direction = 0
        for prop in entry.get("property", []):
            if prop.get("key") == "direction":
                direction = int(prop.get("int32Value", 0))
        start_pos = sp.get("pos", {})
        end_pos   = ep.get("pos", {})
        routes.append(Route(
            id=entry.get("instanceName", ""),
            start_id=sp.get("instanceName", ""),
            end_id=ep.get("instanceName", ""),
            start=Pos2D(start_pos.get("x", 0), start_pos.get("y", 0)),
            end=Pos2D(end_pos.get("x", 0),     end_pos.get("y", 0)),
            ctrl1=Pos2D(c1.get("x", 0), c1.get("y", 0)),
            ctrl2=Pos2D(c2.get("x", 0), c2.get("y", 0)),
            direction=direction,
        ))

    # ── initial robot pose ────────────────────────────────────────────────────
    robot_pos: Optional[Pose2D] = None
    if "robotPos" in data:
        rp = data["robotPos"]
        robot_pos = Pose2D(rp.get("x", 0), rp.get("y", 0), rp.get("theta", 0))

    model = MapModel(
        name=header.get("mapName", path.stem),
        map_type=header.get("mapType", "2D-Map"),
        version=header.get("version", ""),
        resolution=header.get("resolution", 0.02),
        min_pos=Pos2D(min_p.get("x", 0), min_p.get("y", 0)),
        max_pos=Pos2D(max_p.get("x", 0), max_p.get("y", 0)),
        walls=walls,
        nav_points=nav_points,
        action_points=action_points,
        areas=areas,
        landmarks=landmarks,
        routes=routes,
        robot_pos=robot_pos,
    )

    log.info(
        "smap loaded: %s | walls=%d nav_pts=%d aps=%d areas=%d lm=%d routes=%d",
        model.name, len(walls), len(nav_points),
        len(action_points), len(areas), len(landmarks), len(routes),
    )
    return model


def validate_stations(model: MapModel, stations: list[dict]) -> list[str]:
    """Cross-check station ap_id / seer_lm references against the loaded map.
    Returns list of warning strings (empty = all OK).
    """
    warnings: list[str] = []
    ap_ids  = {ap.id for ap in model.action_points}
    lm_ids  = {lm.id for lm in model.landmarks}

    for s in stations:
        if s.get("ap_id") and s["ap_id"] not in ap_ids:
            warnings.append(
                f"Station '{s['id']}': ap_id '{s['ap_id']}' not found in map"
            )
        if s.get("seer_lm") and s["seer_lm"] not in lm_ids:
            warnings.append(
                f"Station '{s['id']}': seer_lm '{s['seer_lm']}' not found in map"
            )
    return warnings
