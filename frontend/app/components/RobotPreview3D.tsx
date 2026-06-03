// ─────────────────────────────────────────────────────────────────────────────
// RobotPreview3D — opt-in 3D preview of the selected AMR (Phase 2).
//
// Renders the real CAD model (public/AMR.glb, converted from AMR.step) fitted to
// the founder-confirmed real footprint (0.95 L × 0.65 W × 0.25 H m), or a to-scale
// procedural box if the GLB ever fails to load.
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

// Path is resolved by Vite from the public/ root at runtime (public/AMR.glb is
// served at /AMR.glb).
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

/** Real GLB model. The CAD model (AMR.step) is authored at ~1:10.5 scale and is
 *  Z-up, so we fit its bounding box to the founder-confirmed real footprint and
 *  reorient it to the app's convention: Y up, length along +X, width along +Z,
 *  sitting on the floor. This makes it render at true size against the 0.25 m grid
 *  regardless of the model's internal units/orientation. */
function GltfChassis({ robot }: { robot: Robot }) {
  const { scene } = useGLTF(GLB_URL)
  const node = useMemo(() => {
    const c = scene.clone(true)

    // Measure the model-local AABB (clone is still at identity here).
    const size = new THREE.Vector3()
    new THREE.Box3().setFromObject(c).getSize(size)

    // Rank the three local axes by extent: largest → length, middle → width,
    // smallest → height. Robust to whatever axis convention the CAD used.
    const fp = robot.footprint ?? DEFAULT_FOOTPRINT
    const real = [fp.length, fp.width, DEFAULT_HEIGHT_M] // by rank, desc
    const world = [
      new THREE.Vector3(1, 0, 0), // length → world +X (forward / +theta)
      new THREE.Vector3(0, 0, 1), // width  → world +Z
      new THREE.Vector3(0, 1, 0), // height → world +Y (up)
    ]
    const ranked = (['x', 'y', 'z'] as const)
      .map((axis) => ({ axis, ext: size[axis] }))
      .sort((a, b) => b.ext - a.ext)

    const scale = { x: 1, y: 1, z: 1 }
    const img: Record<'x' | 'y' | 'z', THREE.Vector3> = {
      x: new THREE.Vector3(),
      y: new THREE.Vector3(),
      z: new THREE.Vector3(),
    }
    ranked.forEach((r, i) => {
      scale[r.axis] = r.ext > 1e-6 ? real[i] / r.ext : 1
      img[r.axis].copy(world[i])
    })

    // Rotation that maps each local axis to its target world axis. Fix handedness
    // (a reflection would mirror the model) by flipping the width axis if needed.
    const m = new THREE.Matrix4().makeBasis(img.x, img.y, img.z)
    if (m.determinant() < 0) {
      img[ranked[1].axis].multiplyScalar(-1)
      m.makeBasis(img.x, img.y, img.z)
    }

    c.scale.set(scale.x, scale.y, scale.z)
    c.quaternion.setFromRotationMatrix(m)
    c.updateMatrixWorld(true)

    // Centre on X/Z and sit on the floor (min.y = 0).
    const fitted = new THREE.Box3().setFromObject(c)
    c.position.x -= (fitted.min.x + fitted.max.x) / 2
    c.position.z -= (fitted.min.z + fitted.max.z) / 2
    c.position.y -= fitted.min.y
    return c
  }, [scene, robot.footprint])

  return <primitive object={node} />
}

/** Error boundary: if the GLB fails to load/parse, render the to-scale procedural
 *  chassis instead so the panel never goes blank. */
class GlbBoundary extends React.Component<
  { robot: Robot; children: React.ReactNode },
  { failed: boolean }
> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  render() {
    if (this.state.failed) return <ProceduralChassis robot={this.props.robot} />
    return this.props.children
  }
}

// A real public/AMR.glb is committed; load it, falling back to the procedural box
// only if it fails to load.
const HAS_GLB = true

function Robot3D({ robot }: { robot: Robot }) {
  // theta is the 2D heading (radians, CCW). Floor is the XZ plane (Y up), so a
  // +theta turn about the vertical axis is rotation.y = -theta.
  return (
    <group rotation={[0, -robot.theta, 0]}>
      {HAS_GLB ? (
        <GlbBoundary robot={robot}>
          <GltfChassis robot={robot} />
        </GlbBoundary>
      ) : (
        <ProceduralChassis robot={robot} />
      )}
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

// Preload the GLB so it's ready when the panel is first opened.
if (HAS_GLB) useGLTF.preload(GLB_URL)
