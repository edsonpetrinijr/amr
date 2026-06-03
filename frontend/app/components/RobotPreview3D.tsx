// ─────────────────────────────────────────────────────────────────────────────
// RobotPreview3D — opt-in 3D preview of the selected AMR (Phase 2).
//
// ⚠️ STUB / NOT YET ACTIVE — this file is intentionally EXCLUDED from the build.
//    The 3D dependencies (three / @react-three/fiber / @react-three/drei /
//    @types/three) could NOT be installed: the npm registry was unreachable from
//    the build environment (ECONNRESET to registry.npmjs.org). The component is
//    written and ready; it is held out of `tsc`/`eslint`/`vite` until the deps
//    exist, so the pipeline stays green. See docs/phase2-3d-preview.md.
//
// TO ACTIVATE (one-time, when the npm registry is reachable):
//   1. npm install three @react-three/fiber @react-three/drei
//      npm install -D @types/three
//   2. Remove this file from `exclude` in tsconfig.json and from `ignores` in
//      eslint.config.mjs.
//   3. Wire the toggle + lazy panel into frontend/app/pages/Field.tsx
//      (exact diff in docs/phase2-3d-preview.md).
//   4. (Optional) Drop a real frontend/public/AMR.glb to replace the procedural
//      box — the loader below auto-detects it and auto-scales mm→m.
//
// Isolation guarantees: this component is lazy-loaded (so three.js is NOT in the
// initial bundle), only mounts when the 3D panel is toggled ON, and never reads
// the 10 Hz SSE stream or touches MapCanvas. It re-renders only when the selected
// robot's identity/theta/status/footprint change.
// ─────────────────────────────────────────────────────────────────────────────
import React, { Suspense, useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Grid, RoundedBox, useGLTF, Bounds } from '@react-three/drei'
import * as THREE from 'three'
import type { Robot } from '../api/types'
import { DEFAULT_FOOTPRINT, DEFAULT_HEIGHT_M } from '../api/types'

// Path is resolved by Vite from the public/ root at runtime. Swapping in a real
// model is a one-line change: drop frontend/public/AMR.glb and it's used.
const GLB_URL = '/AMR.glb'

// Map robot status → chassis colour (matches the 2D map's status semantics).
const STATUS_COLOR: Record<string, string> = {
  idle:           '#8b949e',
  enroute_pickup: '#58a6ff',
  at_pickup:      '#a5a5ff',
  enroute_drop:   '#58a6ff',
  returning:      '#a5d6a7',
  charging:       '#f0c674',
  error:          '#f85149',
  offline:        '#6e7681',
}

/** True-size chassis as a rounded box with a front/heading marker.
 *  length is along +X (forward / +theta), width along Z, height along Y. */
function ProceduralChassis({ robot }: { robot: Robot }) {
  const fp = robot.footprint ?? DEFAULT_FOOTPRINT
  const L = fp.length
  const W = fp.width
  const H = DEFAULT_HEIGHT_M
  const color = STATUS_COLOR[robot.status] ?? STATUS_COLOR.idle

  return (
    <group>
      {/* Chassis: sits on the floor (centre lifted by H/2). */}
      <RoundedBox args={[L, H, W]} radius={0.04} smoothness={4} position={[0, H / 2, 0]}>
        <meshStandardMaterial color={color} metalness={0.1} roughness={0.6} />
      </RoundedBox>
      {/* Heading marker: a cone pointing +X (forward). */}
      <mesh position={[L / 2 + 0.06, H * 0.6, 0]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.06, 0.14, 16]} />
        <meshStandardMaterial color="#e6edf3" emissive="#e6edf3" emissiveIntensity={0.2} />
      </mesh>
    </group>
  )
}

/** Real GLB model. STEP exports are often in mm; if the model's bounding box is
 *  > ~10 units we assume mm and scale by 0.001 so it renders at true metres. */
function GltfChassis() {
  const { scene } = useGLTF(GLB_URL)
  const { clone, scale } = useMemo(() => {
    const c = scene.clone(true)
    const box = new THREE.Box3().setFromObject(c)
    const size = new THREE.Vector3()
    box.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z)
    return { clone: c, scale: maxDim > 10 ? 0.001 : 1 }
  }, [scene])
  return <primitive object={clone} scale={scale} />
}

/** Decide GLB vs procedural at module scope. useGLTF will throw (caught by the
 *  parent <Suspense>/error path) if /AMR.glb is absent; we guard by attempting
 *  the load lazily and falling back. For simplicity we render procedural unless a
 *  GLB has been dropped in — toggle HAS_GLB true once you add public/AMR.glb. */
const HAS_GLB = false // ← set true after dropping frontend/public/AMR.glb

function Robot3D({ robot }: { robot: Robot }) {
  // theta is the 2D heading (radians, CCW). Floor is the XZ plane (Y up), so a
  // +theta turn about the vertical axis is rotation.y = -theta.
  return (
    <group rotation={[0, -robot.theta, 0]}>
      {HAS_GLB ? <GltfChassis /> : <ProceduralChassis robot={robot} />}
    </group>
  )
}

export interface RobotPreview3DProps {
  robot: Robot
  className?: string
}

export default function RobotPreview3D({ robot, className }: RobotPreview3DProps) {
  return (
    <div className={className ?? 'w-80 flex-shrink-0'}>
      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [1.6, 1.2, 1.6], fov: 45, near: 0.05, far: 50 }}
        frameloop="demand"
      >
        <color attach="background" args={['#0d1117']} />
        <hemisphereLight intensity={0.5} groundColor="#161b22" />
        <directionalLight position={[3, 5, 2]} intensity={1.1} castShadow />
        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.4}>
            <Robot3D robot={robot} />
          </Bounds>
        </Suspense>
        <Grid
          args={[10, 10]}
          cellSize={0.25}
          cellThickness={0.6}
          cellColor="#30363d"
          sectionSize={1}
          sectionThickness={1}
          sectionColor="#484f58"
          infiniteGrid
          fadeDistance={12}
          position={[0, 0, 0]}
        />
        <OrbitControls makeDefault enablePan target={[0, 0.15, 0]} minDistance={0.6} maxDistance={8} />
      </Canvas>
    </div>
  )
}

// Preload only matters once a real GLB exists; harmless no-op otherwise.
if (HAS_GLB) useGLTF.preload(GLB_URL)
