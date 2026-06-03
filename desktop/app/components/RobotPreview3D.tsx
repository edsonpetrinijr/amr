// ─────────────────────────────────────────────────────────────────────────────
// RobotPreview3D — opt-in, display-only 3D preview of the selected AMR (Phase 2).
//
// This panel loads the real `/w3_600b.glb` model — the FULL multi-part SEER W3-600B
// assembly (chassis + left/right wheels + casters + back/front lidars + up/down
// cameras + tray), with each part's URDF colour baked in as a glTF material so the
// per-part colours render straight from the asset. All transforms are baked in at
// conversion time (units in metres, forward = +X, up = +Y, footprint centred over
// the origin, resting on the floor at y = 0), so it renders with NO runtime scale or
// rotation. The GLB is Draco-compressed and decoded with a LOCAL `/draco/` decoder
// set (vendored under public/draco) so it works fully offline inside Electron. If the
// model fails to load it degrades gracefully to a to-scale procedural placeholder box
// sized from the robot's footprint.
//
// Model provenance & licensing: see public/MODEL_NOTICE.md
// (source GilmarCorreia/sim_models, GPL-3.0 — internal dev/test use only).
//
// Isolation guarantees (CTO guardrails):
//   • Lazy-loaded by Field (three/r3f/drei live in a separate chunk — zero cost to
//     the Field/SSE path until the operator toggles the panel on).
//   • frameloop="demand": no always-on RAF; we render a frame only on user camera
//     interaction (OrbitControls) or an explicit invalidate() from the pose driver.
//   • Decoupled from the 10 Hz SSE stream: pose is READ FROM A REF (robotsRef),
//     polled ≤10 Hz inside the canvas — this component never subscribes to SSE via
//     React state, and React.memo stops it re-rendering when Field re-renders.
//   • Display-only: never sits in any command/motion path.
//   • Teardown: declarative geometries/materials are auto-disposed by R3F when the
//     Canvas unmounts (panel is gated behind the 3D toggle, unmounted by default).
// ─────────────────────────────────────────────────────────────────────────────
import React, { Suspense, useEffect, useMemo, useRef } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { OrbitControls, Grid, RoundedBox, useGLTF } from '@react-three/drei'
import type * as THREE from 'three'
import { MeshStandardMaterial } from 'three'
import type { Robot } from '../api/types'
import { DEFAULT_FOOTPRINT, DEFAULT_HEIGHT_M } from '../api/types'

// Real chassis model + local Draco decoder (both vendored under public/).
const MODEL_URL = '/w3_600b.glb'
const DRACO_PATH = '/draco/'

// Map robot status → chassis colour (mirrors the 2D map's status semantics).
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

/** To-scale chassis as a rounded box with a forward heading marker.
 *  length is along +X (forward / +theta), width along Z, height along Y. */
function PlaceholderChassis(
  { length, width, height, color }: { length: number; width: number; height: number; color: string },
) {
  return (
    <group>
      {/* Chassis sits on the floor: centre lifted by height/2. */}
      <RoundedBox args={[length, height, width]} radius={0.04} smoothness={4} position={[0, height / 2, 0]}>
        <meshStandardMaterial color={color} metalness={0.1} roughness={0.6} />
      </RoundedBox>
      {/* Heading marker: a cone pointing +X (forward). */}
      <mesh position={[length / 2 + 0.06, height * 0.6, 0]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.06, 0.14, 16]} />
        <meshStandardMaterial color="#e6edf3" emissive="#e6edf3" emissiveIntensity={0.2} />
      </mesh>
    </group>
  )
}

/** The full SEER W3-600B robot loaded from `/w3_600b.glb` (Draco, local `/draco/`
 *  decoder): the complete multi-part assembly (chassis + wheels + casters + lidars +
 *  cameras + tray), with per-part colours baked in as glTF materials that win at
 *  render time. Transforms are baked into the asset (metres, forward = +X, up = +Y,
 *  rests on the floor) so we render it with NO scale and NO rotation. The scene is
 *  cloned so the cached glTF graph is never mutated; the baked materials are left
 *  untouched, and ONLY a mesh that genuinely has no material gets a neutral PBR
 *  fallback (material-less safety). */
function RealChassis() {
  const gltf = useGLTF(MODEL_URL, DRACO_PATH)
  const scene = useMemo(() => {
    const cloned = gltf.scene.clone(true)
    cloned.traverse((obj) => {
      const mesh = obj as THREE.Mesh
      if (mesh.isMesh && !mesh.material) {
        mesh.material = new MeshStandardMaterial({ color: '#9099a2', metalness: 0.1, roughness: 0.6 })
      }
    })
    return cloned
  }, [gltf.scene])

  return <primitive object={scene} />
}

/** Catches a failed model load (missing/corrupt GLB, decoder error) and shows the
 *  to-scale placeholder instead, so the panel never hard-crashes the Field view. */
class ChassisErrorBoundary extends React.Component<
  { fallback: React.ReactNode; children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { fallback: React.ReactNode; children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() {
    return { hasError: true }
  }
  render() {
    return this.state.hasError ? this.props.fallback : this.props.children
  }
}

/** Drives heading from the live pose WITHOUT React re-renders: polls robotsRef at
 *  ≤10 Hz, and on a theta change rotates the group + calls invalidate() so the
 *  demand frameloop renders exactly one frame. theta is 2D heading (rad, CCW);
 *  floor is the XZ plane (Y up), so a +theta turn is rotation.y = -theta. */
function PoseDriver(
  { robotId, robotsRef, children }:
  { robotId: string; robotsRef: React.MutableRefObject<Robot[]>; children: React.ReactNode },
) {
  const groupRef = useRef<THREE.Group>(null)
  const invalidate = useThree((s) => s.invalidate)
  const lastTheta = useRef<number>(NaN)

  useEffect(() => {
    const apply = () => {
      const r = robotsRef.current.find((x) => x.id === robotId)
      if (!r || !groupRef.current) return
      if (r.theta !== lastTheta.current) {
        lastTheta.current = r.theta
        groupRef.current.rotation.y = -r.theta
        invalidate()
      }
    }
    apply()                              // set initial heading
    const id = setInterval(apply, 100)   // 10 Hz poll of the ref — never touches SSE/React state
    return () => clearInterval(id)
  }, [robotId, robotsRef, invalidate])

  return <group ref={groupRef}>{children}</group>
}

export interface RobotPreview3DProps {
  /** Identity of the robot to preview. Stable across SSE frames so React.memo
   *  keeps this panel out of the 10 Hz re-render path. */
  robotId: string
  /** Live fleet snapshot held in a ref by Field; read (not subscribed) for pose. */
  robotsRef: React.MutableRefObject<Robot[]>
  className?: string
}

function RobotPreview3D({ robotId, robotsRef, className }: RobotPreview3DProps) {
  // Snapshot for size/colour. Footprint + status change rarely; the live heading
  // is driven separately by PoseDriver via the ref (not via React state).
  const snap = robotsRef.current.find((r) => r.id === robotId)
  const fp = snap?.footprint ?? DEFAULT_FOOTPRINT
  const color = STATUS_COLOR[snap?.status ?? 'idle'] ?? STATUS_COLOR.idle

  // Preload the model on mount (and free its cache on unmount). Mount/unmount only —
  // this adds no always-on RAF, so the demand frameloop isolation is preserved.
  useEffect(() => {
    useGLTF.preload(MODEL_URL, DRACO_PATH)
    return () => useGLTF.clear(MODEL_URL)
  }, [])

  return (
    <div className={className ?? 'w-80 flex-shrink-0'}>
      <Canvas
        dpr={[1, 2]}
        camera={{ position: [1.6, 1.2, 1.6], fov: 45, near: 0.05, far: 50 }}
        frameloop="demand"
      >
        <color attach="background" args={['#0d1117']} />
        {/* Minimal lighting: ambient fill + one directional key. */}
        <ambientLight intensity={2.5} />
        <directionalLight position={[0, 10, 0]} intensity={2.0} />
        <directionalLight position={[5, 8, 5]} intensity={1.0} />

        <PoseDriver robotId={robotId} robotsRef={robotsRef}>
          {/* Real chassis inside the pose group; placeholder is the graceful fallback. */}
          <ChassisErrorBoundary
            fallback={<PlaceholderChassis length={fp.length} width={fp.width} height={DEFAULT_HEIGHT_M} color={color} />}
          >
            <Suspense fallback={null}>
              <RealChassis />
            </Suspense>
          </ChassisErrorBoundary>
        </PoseDriver>

        {/* Ground grid for scale reference (1 m sections, 0.25 m cells). */}
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

// React.memo: Field re-renders at 10 Hz from SSE; with stable props (robotId +
// the robotsRef object) this panel does NOT re-render on those frames.
export default React.memo(RobotPreview3D)
