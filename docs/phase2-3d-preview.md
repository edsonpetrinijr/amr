# Phase 2 — 3D robot preview panel (DONE)

Opt-in 3D preview of the selected AMR, isolated from the 10 Hz SSE hot path and
from the 2D `MapCanvas`. **Active as of Phase 2.**

## What shipped

- **Real CAD model.** `AMR.step` was converted to `public/AMR.glb` (served at
  `/AMR.glb`) with `cascadio` (OCCT STEP→GLB). The model is authored ~1:10.5 and
  Z-up; `RobotPreview3D` fits its bounding box to the founder-confirmed real
  footprint **0.95 L × 0.65 W × 0.25 H m** and reorients it (Y up, length +X,
  width +Z) sitting on the floor, so it reads at true size against the 0.25 m
  grid. If the GLB ever fails to load, an error boundary falls back to a to-scale
  procedural rounded box (status-coloured, with a heading cone).
- **Deps:** `three`, `@react-three/fiber@8` (React 18), `@react-three/drei@9`,
  `@types/three`.
- **Isolation:** `RobotPreview3D` is `React.lazy`-loaded, so three.js is split
  into its own chunk and never enters the initial bundle. The panel only mounts
  when the **3D** toggle is on (zero cost when off) and never reads the SSE stream
  or `MapCanvas`.

## How to view

Field View → click the **3D** toggle in the top-right toolbar (next to *Laser*).
A right-hand panel shows the selected robot in 3D (or the first robot if none is
selected). Orbit/zoom with the mouse. Toggle off to unmount it.

## Regenerating the GLB (one-off, tooling not committed)

```sh
pip install cascadio trimesh
python -c "import cascadio; cascadio.step_to_glb('AMR.step', 'public/AMR.glb', tol_linear=0.1, tol_angular=0.5)"
```
