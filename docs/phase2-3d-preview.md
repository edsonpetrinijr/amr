# Phase 2 — 3D robot preview panel

Opt-in 3D preview of the selected AMR, isolated from the 10 Hz SSE hot path and
from the 2D `MapCanvas`. **Active as of Phase 2.**

## What shipped

- **To-scale procedural preview (dimensionally honest).** The only CAD we
  received was `AMR.step`. On inspection (trimesh) it is a
  **~0.065 × 0.090 × 0.029 m sub-component** — a bracket/fastener sub-assembly of
  ~3.7k vertices / ~4.5k faces across 10 parts — **not** the full robot
  chassis. We do **not** fake a robot from it. Instead `RobotPreview3D` renders a
  **to-scale procedural rounded box** sized from the robot's real footprint
  (**0.95 L × 0.65 W × 0.25 H m**, the founder-confirmed spec from `types.ts`
  `DEFAULT_FOOTPRINT`/`DEFAULT_HEIGHT_M`; status-coloured, with a forward heading
  cone), sitting on the floor (Y up, length +X, width +Z) so it reads at true size
  against the 0.25 m grid. A **real full-assembly model is pending a proper STEP
  export from the founder**. The converted orphan `public/AMR.glb` (from the
  sub-component `AMR.step`) was only a sub-part — never loaded — and has been
  **removed from the repo** to avoid a misleading unused asset. Do not re-add a
  mesh until a full-assembly model is cleared.
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

## When the real model arrives

Once a full-assembly GLB exists, drop it in `public/` and replace the
`<PlaceholderChassis/>` inside `PoseDriver` with a drei `useGLTF` loader: compute
the loaded scene's bounding box at runtime (`THREE.Box3.setFromObject`), scale
uniformly so the two largest horizontal dims match `fp.length × fp.width`, put it
on the floor (Y up; reorient if the CAD is Z-up), keep `rotation.y = -theta` from
`PoseDriver`, add `useGLTF.preload(...)`, and keep `PlaceholderChassis` as the
Suspense/error fallback.
