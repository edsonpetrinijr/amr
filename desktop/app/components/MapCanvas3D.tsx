// ─────────────────────────────────────────────────────────────────────────────
// MapCanvas3D — React-Three-Fiber 3D replacement for the SVG MapCanvas.
//
// Isolation guarantees (same as RobotPreview3D):
//   • Lazy-loaded by Field (three/r3f/drei in a separate chunk — zero cost until toggled).
//   • frameloop="always": robots move continuously so we need the RAF running.
//   • Decoupled from the 10 Hz SSE stream: robot pose is READ FROM robotsRef
//     (a ref polled at 10 Hz inside useFrame) — this component never subscribes
//     to SSE via React state; React.memo stops it re-rendering on SSE frames.
//   • Map geometry (walls, nav pts, stations) built once in useMemo.
//   • Teardown: geometries/materials auto-disposed by R3F on Canvas unmount.
// ─────────────────────────────────────────────────────────────────────────────
import React, { Suspense, useMemo, useRef, useEffect, useCallback } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import {
  OrbitControls,
  useGLTF,
  Html,
} from '@react-three/drei'
import * as THREE from 'three'
import { MeshStandardMaterial } from 'three'
import type { MapModel, Robot, Station } from '../api/types'
import { DEFAULT_FOOTPRINT, DEFAULT_HEIGHT_M } from '../api/types'

// ── Constants ─────────────────────────────────────────────────────────────────

const MODEL_URL = '/w3_600b.glb'
const DRACO_PATH = '/draco/'
const MAX_NAV_PTS = 3000

const STATION_COLOR: Record<string, string> = {
  callbutton: '#d29922',
  base:       '#3fb950',
  ap:         '#58a6ff',
}

const STATUS_COLOR: Record<string, string> = {
  idle:           '#3fb950',
  enroute_pickup: '#58a6ff',
  at_pickup:      '#a5a5ff',
  enroute_drop:   '#58a6ff',
  returning:      '#a5d6a7',
  charging:       '#f0c674',
  error:          '#f85149',
  offline:        '#6e7681',
}

// ── Coordinate helpers ────────────────────────────────────────────────────────
// SEER map coords: x/y in metres, y-up.
// Three.js floor = XZ plane (y=0 is the floor, Y is up).
// Mapping: seer.x → three.x,  seer.y → three.z  (y stays 0 for floor).

// ── Floor plane ───────────────────────────────────────────────────────────────

function FloorPlane({ minX, maxX, minZ, maxZ }: { minX: number; maxX: number; minZ: number; maxZ: number }) {
  const w = maxX - minX
  const d = maxZ - minZ
  const cx = (minX + maxX) / 2
  const cz = (minZ + maxZ) / 2

  return (
    <mesh position={[cx, -0.01, cz]} receiveShadow rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[w + 10, d + 10, Math.ceil((w + 10) / 2), Math.ceil((d + 10) / 2)]} />
      <meshStandardMaterial color="#0d1117" roughness={1} metalness={0} />
    </mesh>
  )
}

// ── Grid overlay ──────────────────────────────────────────────────────────────

function MapGrid({ minX, maxX, minZ, maxZ }: { minX: number; maxX: number; minZ: number; maxZ: number }) {
  // Render as line segments
  const geom = useMemo(() => {
    const pts: number[] = []
    const startX = Math.floor(minX - 5)
    const endX   = Math.ceil(maxX + 5)
    const startZ = Math.floor(minZ - 5)
    const endZ   = Math.ceil(maxZ + 5)

    for (let x = startX; x <= endX; x++) {
      pts.push(x, 0.001, startZ, x, 0.001, endZ)
    }
    for (let z = startZ; z <= endZ; z++) {
      pts.push(startX, 0.001, z, endX, 0.001, z)
    }

    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3))
    return g
  }, [minX, maxX, minZ, maxZ])

  return (
    <lineSegments geometry={geom}>
      <lineBasicMaterial color="#21262d" transparent opacity={0.6} />
    </lineSegments>
  )
}

// ── Walls ─────────────────────────────────────────────────────────────────────

function Walls({ walls }: { walls: MapModel['walls'] }) {
  // Build a single LineSegments geometry for all walls — one draw call.
  const geom = useMemo(() => {
    const g = new THREE.BufferGeometry()
    const pts: number[] = []
    for (const w of walls) {
      pts.push(w.start.x, 0.05, w.start.y)
      pts.push(w.end.x,   0.05, w.end.y)
    }
    g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3))
    return g
  }, [walls])

  return (
    <lineSegments geometry={geom}>
      <lineBasicMaterial color="#58a6ff" transparent opacity={0.75} linewidth={1} />
    </lineSegments>
  )
}

// ── Nav cloud ─────────────────────────────────────────────────────────────────

function NavCloud({ navPoints }: { navPoints: MapModel['nav_points'] }) {
  const geom = useMemo(() => {
    const step = Math.max(1, Math.floor(navPoints.length / MAX_NAV_PTS))
    const sampled = navPoints.filter((_, i) => i % step === 0)
    const g = new THREE.BufferGeometry()
    const pts: number[] = []
    for (const p of sampled) { pts.push(p.x, 0.01, p.y) }
    g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3))
    return g
  }, [navPoints])

  return (
    <points geometry={geom}>
      <pointsMaterial color="#1f6feb" size={0.08} sizeAttenuation transparent opacity={0.6} />
    </points>
  )
}

// ── Laser cloud ───────────────────────────────────────────────────────────────
// World/map-frame [x,y] beams (same contract as the 2D canvas), drawn just above
// the floor. Decimated like NavCloud to keep the point count bounded.

const MAX_LASER_PTS = 1500

function LaserPoints({ beams }: { beams: [number, number][] }) {
  const geom = useMemo(() => {
    const step = Math.max(1, Math.floor(beams.length / MAX_LASER_PTS))
    const g = new THREE.BufferGeometry()
    const pts: number[] = []
    for (let i = 0; i < beams.length; i += step) {
      const b = beams[i]
      pts.push(b[0], 0.06, b[1])   // seer x → three.x, seer y → three.z
    }
    g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3))
    return g
  }, [beams])

  if (beams.length === 0) return null

  return (
    <points geometry={geom}>
      <pointsMaterial color="#f0883e" size={0.09} sizeAttenuation transparent opacity={0.85} />
    </points>
  )
}

// ── Stations ──────────────────────────────────────────────────────────────────

function Stations({ stations, onClickStation, selectedId }: {
  stations: Station[]
  onClickStation?: (s: Station) => void
  selectedId?: string | null
}) {
  return (
    <>
      {stations.map(s => {
        const color = STATION_COLOR[s.type] ?? '#58a6ff'
        const isSelected = s.id === selectedId
        const r = s.type === 'base' ? 0.25 : 0.18
        return (
          <group key={s.id} position={[s.x, 0, s.y]}>
            <mesh
              onClick={onClickStation ? (e) => { e.stopPropagation(); onClickStation(s) } : undefined}
              position={[0, r, 0]}
            >
              <cylinderGeometry args={[r, r, r * 2, 16]} />
              <meshStandardMaterial
                color={color}
                emissive={color}
                emissiveIntensity={isSelected ? 0.6 : 0.2}
                roughness={0.4}
                metalness={0.2}
              />
            </mesh>
            {/* Label */}
            <Html position={[0, r * 2 + 0.3, 0]} center style={{ pointerEvents: 'none' }}>
              <span style={{
                fontSize: '9px', fontFamily: 'monospace', color,
                background: '#0d111790', padding: '1px 3px', borderRadius: 2, whiteSpace: 'nowrap',
              }}>
                {s.label.length > 12 ? s.label.slice(0, 11) + '…' : s.label}
              </span>
            </Html>
          </group>
        )
      })}
    </>
  )
}

// ── Landmarks ─────────────────────────────────────────────────────────────────

function Landmarks({ landmarks }: { landmarks: MapModel['landmarks'] }) {
  return (
    <>
      {landmarks.map(lm => (
        <mesh key={lm.id} position={[lm.x, 0.12, lm.y]}>
          <sphereGeometry args={[0.12, 12, 12]} />
          <meshStandardMaterial color="#8b949e" emissive="#8b949e" emissiveIntensity={0.1} roughness={0.6} />
        </mesh>
      ))}
    </>
  )
}

// ── Robot GLB ─────────────────────────────────────────────────────────────────

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

function PlaceholderChassis({ length, width, color }: { length: number; width: number; color: string }) {
  const h = DEFAULT_HEIGHT_M
  return (
    <group>
      <mesh position={[0, h / 2, 0]}>
        <boxGeometry args={[length, h, width]} />
        <meshStandardMaterial color={color} metalness={0.1} roughness={0.6} />
      </mesh>
      <mesh position={[length / 2 + 0.06, h * 0.6, 0]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.06, 0.14, 16]} />
        <meshStandardMaterial color="#e6edf3" emissive="#e6edf3" emissiveIntensity={0.2} />
      </mesh>
    </group>
  )
}

class ChassisErrorBoundary extends React.Component<
  { fallback: React.ReactNode; children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { fallback: React.ReactNode; children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() { return { hasError: true } }
  render() { return this.state.hasError ? this.props.fallback : this.props.children }
}

// ── Per-robot mesh driven by ref (no React state per SSE frame) ───────────────

function RobotMesh({ robot, robotsRef, onClickRobot, selectedId }: {
  robot: Robot
  robotsRef: React.MutableRefObject<Robot[]>
  onClickRobot?: (r: Robot) => void
  selectedId?: string | null
}) {
  const groupRef = useRef<THREE.Group>(null)
  // Currently-displayed pose, initialised to the robot's real pose so a freshly
  // mounted robot starts in the right place (no lerp-in from origin).
  const dispX = useRef(robot.x)
  const dispZ = useRef(robot.y)
  const dispTheta = useRef(robot.theta)

  const fp = robot.footprint ?? DEFAULT_FOOTPRINT
  const color = STATUS_COLOR[robot.status] ?? '#8b949e'
  const isSelected = robot.id === selectedId

  // Read the latest target pose from robotsRef each frame and ease toward it.
  // The 10 Hz pose stream would step visibly if snapped; smoothing at 60fps
  // removes the stutter. `k` is framerate-aware (≈200ms catch-up) so it looks
  // identical regardless of refresh rate.
  useFrame((_state, delta) => {
    const r = robotsRef.current.find(x => x.id === robot.id)
    if (!r || !groupRef.current) return
    const k = 1 - Math.pow(0.001, delta)
    dispX.current += (r.x - dispX.current) * k
    dispZ.current += (r.y - dispZ.current) * k
    // Shortest-angle interpolation so theta never spins the long way round.
    let d = r.theta - dispTheta.current
    d = Math.atan2(Math.sin(d), Math.cos(d))
    dispTheta.current += d * k
    groupRef.current.position.set(dispX.current, 0, dispZ.current)
    groupRef.current.rotation.set(0, -dispTheta.current, 0)
  })

  return (
    <group
      ref={groupRef}
      position={[robot.x, 0, robot.y]}
      rotation={[0, -robot.theta, 0]}
      onClick={onClickRobot ? (e) => { e.stopPropagation(); onClickRobot(robot) } : undefined}
    >
      {/* Selection ring */}
      {isSelected && (
        <mesh position={[0, 0.005, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[Math.max(fp.length, fp.width) * 0.7, Math.max(fp.length, fp.width) * 0.75 + 0.12, 32]} />
          <meshBasicMaterial color={color} transparent opacity={0.5} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Robot body — GLB with placeholder fallback */}
      <ChassisErrorBoundary
        fallback={<PlaceholderChassis length={fp.length} width={fp.width} color={color} />}
      >
        <Suspense fallback={<PlaceholderChassis length={fp.length} width={fp.width} color={color} />}>
          <RealChassis />
        </Suspense>
      </ChassisErrorBoundary>

      {/* ID label floating above */}
      <Html position={[0, DEFAULT_HEIGHT_M + 0.4, 0]} center style={{ pointerEvents: 'none' }}>
        <span style={{
          fontSize: '10px', fontFamily: 'monospace', color,
          background: '#0d111790', padding: '1px 4px', borderRadius: 2, whiteSpace: 'nowrap',
          fontWeight: 'bold',
        }}>
          {robot.id.replace('AMR-', '')}
        </span>
      </Html>
    </group>
  )
}

// ── Camera reset controller ───────────────────────────────────────────────────

function CameraResetHandler({
  resetSignal, mapCX, mapCZ,
}: { resetSignal: number; mapCX: number; mapCZ: number }) {
  const { camera, invalidate } = useThree()

  useEffect(() => {
    if (resetSignal === 0) return
    camera.position.set(mapCX, 60, mapCZ)
    camera.lookAt(mapCX, 0, mapCZ)
    invalidate()
  }, [resetSignal, mapCX, mapCZ, camera, invalidate])

  return null
}

// ── Inner scene ───────────────────────────────────────────────────────────────

function MapScene({
  map, robots, stations, robotsRef, onClickRobot, onClickStation, selectedId, resetSignal, laserBeams,
}: {
  map: MapModel
  robots: Robot[]
  stations: Station[]
  robotsRef: React.MutableRefObject<Robot[]>
  onClickRobot?: (r: Robot) => void
  onClickStation?: (s: Station) => void
  selectedId?: string | null
  resetSignal: number
  laserBeams?: [number, number][]
}) {
  const { minX, maxX, minZ, maxZ, mapCX, mapCZ } = useMemo(() => {
    const minX = map.min_pos.x
    const maxX = map.max_pos.x
    const minZ = map.min_pos.y   // SEER y → three.js z
    const maxZ = map.max_pos.y
    return { minX, maxX, minZ, maxZ, mapCX: (minX + maxX) / 2, mapCZ: (minZ + maxZ) / 2 }
  }, [map])

  return (
    <>
      {/* ── Lighting (bright, flat — technical top-down view) ── */}
      <ambientLight intensity={2.5} />
      <directionalLight position={[0, 10, 0]} intensity={2.0} />
      <directionalLight position={[5, 8, 5]} intensity={1.0} />

      {/* ── Camera reset on double-click ── */}
      <CameraResetHandler resetSignal={resetSignal} mapCX={mapCX} mapCZ={mapCZ} />

      {/* ── OrbitControls ── */}
      <OrbitControls
        makeDefault
        enablePan
        maxPolarAngle={Math.PI / 2}
        minDistance={2}
        maxDistance={300}
        target={[mapCX, 0, mapCZ]}
      />

      {/* ── Map geometry (static after mount) ── */}
      <FloorPlane minX={minX} maxX={maxX} minZ={minZ} maxZ={maxZ} />
      <MapGrid    minX={minX} maxX={maxX} minZ={minZ} maxZ={maxZ} />
      <Walls      walls={map.walls} />
      <NavCloud   navPoints={map.nav_points} />
      <LaserPoints beams={laserBeams ?? []} />
      <Stations   stations={stations} onClickStation={onClickStation} selectedId={selectedId} />
      <Landmarks  landmarks={map.landmarks} />

      {/* ── Robots (ref-driven pose, no React state per SSE frame) ── */}
      {robots.map(r => (
        <RobotMesh
          key={r.id}
          robot={r}
          robotsRef={robotsRef}
          onClickRobot={onClickRobot}
          selectedId={selectedId}
        />
      ))}
    </>
  )
}

// ── Public props (drop-in replacement for MapCanvas) ─────────────────────────

export interface MapCanvas3DProps {
  map: MapModel
  robots?: Robot[]
  stations?: Station[]
  onClickRobot?: (r: Robot) => void
  onClickStation?: (s: Station) => void
  selectedId?: string | null
  robotsRef: React.MutableRefObject<Robot[]>
  className?: string
  laserBeams?: [number, number][]
}

// ── Root export ───────────────────────────────────────────────────────────────

function MapCanvas3DInner(props: MapCanvas3DProps) {
  const { map, robots = [], stations = [], onClickRobot, onClickStation, selectedId, robotsRef, className, laserBeams } = props

  const mapCX = (map.min_pos.x + map.max_pos.x) / 2
  const mapCZ = (map.min_pos.y + map.max_pos.y) / 2
  const span  = Math.max(
    map.max_pos.x - map.min_pos.x,
    map.max_pos.y - map.min_pos.y,
  )
  const camY = Math.max(span * 0.7, 20)

  const [resetSignal, setResetSignal] = React.useState(0)
  const triggerReset = useCallback(() => setResetSignal(s => s + 1), [])

  // Preload GLB on mount; clear on unmount.
  useEffect(() => {
    useGLTF.preload(MODEL_URL, DRACO_PATH)
    return () => { useGLTF.clear(MODEL_URL) }
  }, [])

  return (
    <div className={className ?? 'w-full h-full'} onDoubleClick={triggerReset} style={{ cursor: 'grab' }}>
      <Canvas
        dpr={[1, 2]}
        camera={{
          position: [mapCX, camY, mapCZ + camY * 0.01],
          fov: 50,
          near: 0.1,
          far: 2000,
          up: [0, 1, 0],
        }}
        frameloop="always"
      >
        <color attach="background" args={['#0d1117']} />
        <MapScene
          map={map}
          robots={robots}
          stations={stations}
          robotsRef={robotsRef}
          onClickRobot={onClickRobot}
          onClickStation={onClickStation}
          selectedId={selectedId}
          resetSignal={resetSignal}
          laserBeams={laserBeams}
        />
      </Canvas>
    </div>
  )
}

export const MapCanvas3D = React.memo(MapCanvas3DInner)
export default MapCanvas3D
