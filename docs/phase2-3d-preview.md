# Phase 2 — 3D robot preview panel

Opt-in 3D preview of the selected AMR, isolated from the 10 Hz SSE hot path and
from the 2D `MapCanvas`. **Currently a documented stub** — see "Status" below.

## Status: ready, not yet active (offline environment)

The 3D dependencies could **not** be installed in the build environment:

- `npm install three @react-three/fiber @react-three/drei` → `ECONNRESET` to
  `registry.npmjs.org` (no network access to the npm registry).
- The CAD asset `AMR.step` (repo root, AP242, SI = metre) could **not** be
  converted to `AMR.glb`: no local CAD tooling (`cadquery`/`OCP`/`build123d`/
  `trimesh`/`assimp`/`FreeCADCmd`/`gmsh` all absent) and PyPI was also
  unreachable (`pip install cascadio` → connection reset), so no STEP→mesh path
  was available.

So `frontend/app/components/RobotPreview3D.tsx` is fully written but held out of
the build (`exclude` in `tsconfig.json`, `ignores` in `eslint.config.mjs`) so
`typecheck`/`lint`/`build` stay green without the deps. No fake asset was
committed and the 2D map / Laser layer / selection are untouched.

## What the component renders

- A `@react-three/fiber` `<Canvas>` with `OrbitControls`, an infinite ground
  grid, hemisphere + directional lighting, and a camera auto-framed via `Bounds`.
- If `frontend/public/AMR.glb` exists: load it with drei `useGLTF` and
  auto-scale mm→m (if the model's max bbox dimension > ~10, multiply by 0.001).
  Flip `HAS_GLB` to `true` after dropping the file in.
- Otherwise: a **to-scale procedural rounded box** at the founder-confirmed
  `0.95 L × 0.65 W × 0.25 H m`, coloured by robot `status`, with a cone
  **heading marker** pointing forward (+theta). Oriented by `robot.theta`.

Swapping in the real model later is a one-line change (drop `public/AMR.glb`,
set `HAS_GLB = true`).

## To activate (when the npm registry is reachable)

```sh
npm install three @react-three/fiber @react-three/drei
npm install -D @types/three
```

1. Remove `frontend/app/components/RobotPreview3D.tsx` from `exclude` in
   `tsconfig.json` and from `ignores` in `eslint.config.mjs`.
2. Wire the opt-in panel into `frontend/app/pages/Field.tsx` (diff below).
3. Run `npm run typecheck && npm run lint && npm run build`.

### Field.tsx wiring (lazy-loaded so three.js stays out of the initial bundle)

```tsx
// top of file
import { Box } from 'lucide-react'
const RobotPreview3D = React.lazy(() => import('../components/RobotPreview3D'))

// in the Field component body, next to the other useState toggles:
const [show3D, setShow3D] = useState(false)

// in the header toolbar, right after the "Laser" <button> (~line 194):
<button onClick={() => setShow3D(v => !v)}
  className={`flex items-center gap-1.5 px-2 py-1 rounded border transition-colors
    ${show3D ? 'border-[#58a6ff] text-[#58a6ff] bg-[#58a6ff]/10' : 'border-[#30363d] hover:bg-[#161b22]'}`}>
  <Box className="w-3.5 h-3.5" />
  3D
</button>

// in the "Main canvas + side panel" row, after the StationPanel line (~line 219).
// Fall back to the first robot when none is selected. Conditional render means
// the R3F canvas never mounts (and three.js never loads) while the panel is off.
{show3D && (selectedRobot ?? robots[0]) && (
  <Suspense fallback={<div className="w-80 flex-shrink-0 bg-[#161b22] border-l border-[#30363d]" />}>
    <RobotPreview3D robot={(selectedRobot ?? robots[0])!} className="w-80 flex-shrink-0 border-l border-[#30363d]" />
  </Suspense>
)}
```

`React` and `Suspense` are already imported in `Field.tsx`.

## How to view (after activation)

Field View → click the **3D** toggle in the top-right toolbar (next to *Laser*).
A right-hand panel shows the selected robot in 3D (or the first robot if none is
selected). Orbit/zoom with the mouse. Toggle off to unmount it (zero cost).
