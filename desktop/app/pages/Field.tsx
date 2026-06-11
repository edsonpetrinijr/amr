import React, { useEffect, useRef, useState, Suspense, lazy } from 'react'
import { Map, Radar, Box, LayoutGrid, ChevronUp, ChevronDown, ChevronLeft, ChevronRight, RotateCw, RotateCcw, Square } from 'lucide-react'
import { toast } from 'sonner'
import { useFleet } from '../state/store'
import { fleetApi, FleetApiError } from '../api/fleet'
import { useJog, type JogDir } from '../hooks/useJog'
import { MapCanvas } from '../components/MapCanvas'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { PageHeader } from '@/app/components/PageHeader'
import type { Robot, Station, Landmark } from '../api/types'

// Lazy-loaded so three.js / R3F stay out of the initial bundle; only fetched when
// the 3D map is first rendered.
const RobotPreview3D = lazy(() => import('../components/RobotPreview3D'))
const MapCanvas3D    = lazy(() => import('../components/MapCanvas3D'))

const STATUS_VARIANT: Record<string, 'success' | 'destructive' | 'default' | 'secondary' | 'outline'> = {
  idle:           'outline',
  enroute_pickup: 'default',
  at_pickup:      'secondary',
  enroute_drop:   'default',
  returning:      'secondary',
  charging:       'secondary',
  error:          'destructive',
  offline:        'destructive',
}

function RobotPanel({ robot, landmarks, onClose }: { robot: Robot; landmarks: Landmark[]; onClose: () => void }) {
  const [sending, setSending] = useState(false)
  const [landmarkId, setLandmarkId] = useState('')
  const battColor = robot.battery < 25 ? 'text-red-400' : robot.battery < 50 ? 'text-yellow-400' : 'text-green-400'

  // Manual jog — keyboard listeners are global, so mounting this panel enables WASD.
  // Disabled while the robot is offline or busy (backend would 409 anyway).
  const jogDisabled = robot.status === 'offline' || robot.current_task != null
  const { active, startDir, stopDir, stopAll } = useJog(jogDisabled ? null : robot.id)

  const holdProps = (dir: JogDir) => ({
    onMouseDown: (e: React.MouseEvent) => { e.preventDefault(); startDir(dir) },
    onMouseUp: () => stopDir(dir),
    onMouseLeave: () => stopDir(dir),
    onTouchStart: (e: React.TouchEvent) => { e.preventDefault(); startDir(dir) },
    onTouchEnd: (e: React.TouchEvent) => { e.preventDefault(); stopDir(dir) },
  })
  const dirClass = (dir: JogDir) =>
    active.has(dir) ? 'border-[#58a6ff] bg-[#1f6feb]/20 text-[#58a6ff]' : ''

  async function handleNavigate() {
    if (!landmarkId) return
    setSending(true)
    try {
      const res = await fleetApi.navigateToLandmark(robot.id, landmarkId)
      toast.success('Navegando', { description: `${res.robot_id} → ${res.landmark_id}` })    } catch (e) {
      if (e instanceof FleetApiError) {
        if (e.status === 409)      toast.error('Navegação recusada', { description: e.message })
        else if (e.status === 404) toast.error('Não encontrado', { description: e.message })
        else if (e.status === 400) toast.error('Comando inválido', { description: e.message })
        else                       toast.error('Falha na navegação', { description: e.message })
      } else {
        toast.error('Falha na navegação', { description: 'Backend inacessível' })
      }
    } finally { setSending(false) }
  }

  return (
    <aside className="w-72 flex-shrink-0 bg-[#161b22] border-l border-[#30363d] p-4 flex flex-col gap-3 overflow-y-auto">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[#e6edf3]">{robot.id}</h2>
        <button onClick={onClose} className="text-[#8b949e] hover:text-[#c9d1d9] text-xs">✕</button>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <span className="text-[#8b949e]">Status</span>
        <Badge variant={STATUS_VARIANT[robot.status] ?? 'outline'} className="justify-self-end">
          {robot.status.replace('_', ' ')}
        </Badge>
        <span className="text-[#8b949e]">Bateria</span>
        <span className={`${battColor} font-mono`}>{robot.battery}%</span>
        <span className="text-[#8b949e]">Posição</span>
        <span className="text-[#c9d1d9] font-mono text-[10px]">({robot.x.toFixed(1)}, {robot.y.toFixed(1)})</span>
        <span className="text-[#8b949e]">Tarefa</span>
        <span className="text-[#c9d1d9] font-mono">{robot.current_task ?? '—'}</span>
      </div>

      {/* Send to landmark */}
      <div className="border-t border-[#30363d] pt-3">
        <p className="text-xs text-[#8b949e] mb-2">Enviar para marco</p>
        <select className="w-full text-xs bg-[#0d1117] border border-[#30363d] text-[#c9d1d9] rounded px-2 py-1 mb-2"
          value={landmarkId} onChange={e => setLandmarkId(e.target.value)}>
          <option value="">— selecione um marco —</option>
          {landmarks.map(lm => <option key={lm.id} value={lm.id}>{lm.id}</option>)}
        </select>
        <Button variant="primary" size="sm" className="w-full"
          disabled={!landmarkId || sending || robot.status === 'offline'}
          onClick={handleNavigate}>
          {sending ? 'Enviando…' : 'Navegar'}
        </Button>
      </div>

      {/* Manual jog D-pad */}
      <div className="border-t border-[#30363d] pt-3">
        <p className="text-xs text-[#8b949e] mb-1">Controle manual</p>
        <p className="text-[10px] text-[#6e7681] mb-2">
          <span className="text-[#c9d1d9] font-mono">WASD</span> para mover,
          {' '}<span className="text-[#c9d1d9] font-mono">Q/E</span> girar.
        </p>
        {jogDisabled ? (
          <p className="text-[10px] text-[#6e7681] py-2">
            {robot.status === 'offline' ? 'Robô offline.' : 'Indisponível com tarefa ativa.'}
          </p>
        ) : (
          <>
            <div className="grid grid-cols-3 gap-1.5 w-fit mx-auto mb-2">
              <div />
              <Button variant="outline" size="icon" {...holdProps('forward')} className={dirClass('forward')}>
                <ChevronUp className="w-4 h-4" />
              </Button>
              <div />
              <Button variant="outline" size="icon" {...holdProps('left')} className={dirClass('left')}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={stopAll}
                className="border-red-800 text-red-400 hover:bg-red-900/20">
                <Square className="w-3.5 h-3.5" />
              </Button>
              <Button variant="outline" size="icon" {...holdProps('right')} className={dirClass('right')}>
                <ChevronRight className="w-4 h-4" />
              </Button>
              <div />
              <Button variant="outline" size="icon" {...holdProps('back')} className={dirClass('back')}>
                <ChevronDown className="w-4 h-4" />
              </Button>
              <div />
            </div>
            <div className="flex gap-2 justify-center">
              <Button variant="outline" size="sm" {...holdProps('ccw')} className={dirClass('ccw')}>
                <RotateCcw className="w-3.5 h-3.5 mr-1" /> CCW
              </Button>
              <Button variant="outline" size="sm" {...holdProps('cw')} className={dirClass('cw')}>
                <RotateCw className="w-3.5 h-3.5 mr-1" /> CW
              </Button>
            </div>
          </>
        )}
      </div>

      {robot.current_task && (
        <Button variant="outline" size="sm" className="border-red-700 text-red-400 hover:bg-red-900/20"
          onClick={() => fleetApi.cancelTask(robot.current_task!)}>
          Cancelar tarefa
        </Button>
      )}
    </aside>
  )
}

function StationPanel({ station, onClose }:
  { station: Station; robots: Robot[]; onClose: () => void }) {
  const [sending, setSending] = useState(false)
  const [simEnabled, setSimEnabled] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const h = await fleetApi.health() as { sim_mode?: boolean }
        if (!cancelled && typeof h.sim_mode === 'boolean') {
          setSimEnabled(h.sim_mode)
        }
      } catch {
        // Keep optimistic UI state if health endpoint is temporarily unavailable.
      }
    })()
    return () => { cancelled = true }
  }, [])

  // NOTE: "Dispatch robot here" is hidden for the demo — see POST_DEMO_BACKLOG.md.
  // handleDispatch passed the robot id as the pickup station, producing a malformed
  // task (there is no backend contract to pin a task to a specific robot). The control
  // and its handler/state are commented out (not deleted) until a proper endpoint exists.
  //
  // const [robotId, setRobotId] = useState('')
  // const available = robots.filter(r => r.status === 'idle' && !r.current_task)
  // async function handleDispatch() {
  //   if (!robotId) return
  //   setSending(true)
  //   try { await fleetApi.createTask(robotId, station.id) }
  //   catch (e) {
  //     console.error(e)
  //     toast.error('Falha ao enviar comando ao robô')
  //   }
  //   finally { setSending(false) }
  // }

  async function handleCallbutton() {
    setSending(true)
    try {
      await fleetApi.pressCallbutton(station.id)
      toast.success('Botão de chamada acionado', { description: station.label })
    } catch (e) {
      console.error(e)
      if (e instanceof FleetApiError) toast.error('Falha ao simular acionamento', { description: e.message })
      else                           toast.error('Falha ao simular acionamento', { description: 'Backend inacessível' })
    }
    finally { setSending(false) }
  }

  return (
    <aside className="w-72 flex-shrink-0 bg-[#161b22] border-l border-[#30363d] p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[#e6edf3]">{station.label}</h2>
        <button onClick={onClose} className="text-[#8b949e] hover:text-[#c9d1d9] text-xs">✕</button>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <span className="text-[#8b949e]">Tipo</span>
        <span className="text-[#c9d1d9] capitalize">{station.type}</span>
        <span className="text-[#8b949e]">AP ID</span>
        <span className="text-[#c9d1d9] font-mono">{station.ap_id ?? '—'}</span>
        {station.type === 'callbutton' && <>
          <span className="text-[#8b949e]">Estado</span>
          <Badge variant={station.cb_state === 'called' ? 'default' : 'outline'} className="justify-self-end">
            {station.cb_state}
          </Badge>
        </>}
      </div>
      {station.type === 'callbutton' && (
        <Button variant="primary" size="sm" disabled={!simEnabled || sending || station.cb_state === 'called'}
          onClick={handleCallbutton}>
          {simEnabled ? 'Simular acionamento' : 'Simulação indisponível no modo hardware'}
        </Button>
      )}
      {/* "Dispatch robot here" hidden for the demo — malformed task contract.
          See POST_DEMO_BACKLOG.md. Re-enable once a robot-pinned task endpoint exists.
      {station.type !== 'base' && (
        <div className="border-t border-[#30363d] pt-3">
          <p className="text-xs text-[#8b949e] mb-2">Despachar robô para cá</p>
          <select className="w-full text-xs bg-[#0d1117] border border-[#30363d] text-[#c9d1d9] rounded px-2 py-1 mb-2"
            value={robotId} onChange={e => setRobotId(e.target.value)}>
            <option value="">— selecione um robô —</option>
            {available.map(r => <option key={r.id} value={r.id}>{r.id}</option>)}
          </select>
          <Button variant="primary" size="sm" className="w-full"
            disabled={!robotId || sending} onClick={handleDispatch}>
            {sending ? 'Enviando…' : 'Despachar'}
          </Button>
        </div>
      )}
      */}
    </aside>
  )
}

export function Field() {
  const { map, robots, stations, connected } = useFleet()
  const [selectedRobot, setSelectedRobot]     = useState<Robot | null>(null)
  const [selectedStation, setSelectedStation] = useState<Station | null>(null)

  // ── View mode: '3d' (default) or '2d' ────────────────────────────────────────
  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d')

  // ── Laser layer (dedicated PULL endpoint, polled ~2.5 Hz while ON) ──────────
  const [laserOn, setLaserOn]       = useState(false)
  const [show3DPanel, setShow3DPanel] = useState(false)
  const [laserBeams, setLaserBeams] = useState<[number, number][]>([])

  // Refs keep the poller reading the latest selection/robots without re-arming
  // the interval on every 10 Hz SSE world frame.
  const robotsRef   = useRef(robots);           robotsRef.current   = robots
  const selectedRef = useRef(selectedRobot);    selectedRef.current = selectedRobot

  useEffect(() => {
    if (!laserOn) { setLaserBeams([]); return }
    let cancelled = false
    async function poll() {
      const sel = selectedRef.current
      const ids = sel ? [sel.id] : robotsRef.current.map(r => r.id)
      try {
        const scans = await Promise.all(ids.map(id => fleetApi.getLaser(id)))
        if (!cancelled) setLaserBeams(scans.flatMap(s => s.beams))
      } catch { /* transient — keep last scan */ }
    }
    poll()
    const t = setInterval(poll, 400)   // ~2.5 Hz
    return () => { cancelled = true; clearInterval(t) }
  }, [laserOn])

  function selectRobot(r: Robot) {
    setSelectedStation(null)
    setSelectedRobot(prev => prev?.id === r.id ? null : r)
  }

  function selectStation(s: Station) {
    setSelectedRobot(null)
    setSelectedStation(prev => prev?.id === s.id ? null : s)
  }

  // Hide callbutton expansion placeholders (e.g. Linha A/B/C) from map rendering
  // while keeping backend station data intact for configuration screens.
  const visibleStations = stations.filter(s =>
    s.type !== 'callbutton' || Boolean(s.seer_lm && s.seer_lm.trim())
  )

  const selectedId = selectedRobot?.id ?? selectedStation?.id ?? null

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <PageHeader
        icon={<Map className="w-4 h-4 text-[#58a6ff]" />}
        title="Vista de Campo"
        status={
          <span className="ml-1 flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
            <span className="text-xs text-[#8b949e]">{connected ? 'Ao vivo' : 'Desconectado'}</span>
          </span>
        }
        actions={
          <div className="flex items-center gap-2 text-xs text-[#8b949e]">
            {/* 2D / 3D toggle */}
            <div className="flex items-center rounded border border-[#30363d] overflow-hidden">
              <button
                onClick={() => setViewMode('2d')}
                className={`flex items-center gap-1 px-2 py-1 transition-colors ${
                  viewMode === '2d'
                    ? 'bg-[#21262d] text-[#e6edf3]'
                    : 'text-[#8b949e] hover:bg-[#161b22]'
                }`}
              >
                <LayoutGrid className="w-3 h-3" />
                2D
              </button>
              <button
                onClick={() => setViewMode('3d')}
                className={`flex items-center gap-1 px-2 py-1 transition-colors border-l border-[#30363d] ${
                  viewMode === '3d'
                    ? 'bg-[#21262d] text-[#58a6ff]'
                    : 'text-[#8b949e] hover:bg-[#161b22]'
                }`}
              >
                <Box className="w-3 h-3" />
                3D
              </button>
            </div>

            {/* Laser toggle (only useful in 2D mode but kept available) */}
            <button onClick={() => setLaserOn(v => !v)}
              className={`flex items-center gap-1.5 px-2 py-1 rounded border transition-colors
                ${laserOn ? 'border-[#f0883e] text-[#f0883e] bg-[#f0883e]/10' : 'border-[#30363d] hover:bg-[#161b22]'}`}>
              <Radar className="w-3.5 h-3.5" />
              Laser
            </button>

            {/* Side 3D preview panel toggle */}
            <button onClick={() => setShow3DPanel(v => !v)}
              className={`flex items-center gap-1.5 px-2 py-1 rounded border transition-colors
                ${show3DPanel ? 'border-[#58a6ff] text-[#58a6ff] bg-[#58a6ff]/10' : 'border-[#30363d] hover:bg-[#161b22]'}`}>
              <Box className="w-3.5 h-3.5" />
              Painel 3D
            </button>
            <span>{robots.length} robôs</span>
            <span>·</span>
            <span>{visibleStations.length} estações</span>
          </div>
        }
      />

      {/* Main canvas + side panel */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-hidden">
          {map ? (
            viewMode === '3d' ? (
              <Suspense fallback={
                <div className="w-full h-full flex items-center justify-center text-[#8b949e] text-sm">
                  Carregando cena 3D…
                </div>
              }>
                <MapCanvas3D
                  map={map}
                  robots={robots}
                  stations={visibleStations}
                  robotsRef={robotsRef}
                  selectedId={selectedId}
                  onClickRobot={selectRobot}
                  onClickStation={selectStation}
                  laserBeams={laserOn ? laserBeams : undefined}
                  className="w-full h-full"
                />
              </Suspense>
            ) : (
              <MapCanvas map={map} robots={robots} stations={visibleStations}
                laser={laserOn ? { beams: laserBeams, ts: 0 } : undefined}
                selectedId={selectedId}
                onClickRobot={selectRobot}
                onClickAP={selectStation}
                className="w-full h-full"
              />
            )
          ) : (
            <div className="h-full flex items-center justify-center text-[#8b949e] text-sm">
              {connected ? 'Carregando mapa…' : 'Conectando ao backend…'}
            </div>
          )}
        </div>
        {selectedRobot   && <RobotPanel   robot={selectedRobot}   landmarks={map?.landmarks ?? []} onClose={() => setSelectedRobot(null)} />}
        {selectedStation && <StationPanel station={selectedStation} robots={robots}   onClose={() => setSelectedStation(null)} />}
        {/* Opt-in 3D side preview panel. Conditional mount = R3F canvas never loads while off. */}
        {show3DPanel && (selectedRobot?.id ?? robots[0]?.id) && (
          <Suspense fallback={<div className="w-80 flex-shrink-0 bg-[#161b22] border-l border-[#30363d]" />}>
            <RobotPreview3D robotId={(selectedRobot?.id ?? robots[0]?.id)!} robotsRef={robotsRef}
              className="w-80 flex-shrink-0 border-l border-[#30363d]" />
          </Suspense>
        )}
      </div>

      {/* Robot strip */}
      <div className="border-t border-[#30363d] px-4 py-2 flex items-center gap-2 overflow-x-auto flex-shrink-0">
        {robots.map(r => (
          <button key={r.id} onClick={() => selectRobot(r)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors
              ${selectedRobot?.id === r.id ? 'bg-[#21262d] border border-[#58a6ff]' : 'hover:bg-[#161b22]'}`}>
            <div className={`w-1.5 h-1.5 rounded-full ${
              r.status === 'error' || r.status === 'offline' ? 'bg-red-400' :
              r.status === 'idle' ? 'bg-green-400' : 'bg-blue-400'}`} />
            <span className="text-[#c9d1d9]">{r.id}</span>
            <span className="text-[#8b949e]">{r.battery}%</span>
          </button>
        ))}
      </div>
    </div>
  )
}

