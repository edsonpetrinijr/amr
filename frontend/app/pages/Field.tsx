import React, { useEffect, useRef, useState } from 'react'
import { Map, Radar } from 'lucide-react'
import { useFleet } from '../state/store'
import { fleetApi } from '../api/fleet'
import { MapCanvas } from '../components/MapCanvas'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import type { Robot, Station } from '../api/types'

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

function RobotPanel({ robot, stations, onClose }: { robot: Robot; stations: Station[]; onClose: () => void }) {
  const [sending, setSending] = useState(false)
  const [dropoffId, setDropoffId] = useState('')
  const aps = stations.filter(s => s.type === 'ap' || s.type === 'callbutton')
  const battColor = robot.battery < 25 ? 'text-red-400' : robot.battery < 50 ? 'text-yellow-400' : 'text-green-400'

  async function handleSendTask() {
    if (!dropoffId) return
    setSending(true)
    try { await fleetApi.createTask(robot.id, dropoffId) }
    catch (e) { console.error(e) }
    finally { setSending(false) }
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
        <span className="text-[#8b949e]">Battery</span>
        <span className={`${battColor} font-mono`}>{robot.battery}%</span>
        <span className="text-[#8b949e]">Position</span>
        <span className="text-[#c9d1d9] font-mono text-[10px]">({robot.x.toFixed(1)}, {robot.y.toFixed(1)})</span>
        <span className="text-[#8b949e]">Task</span>
        <span className="text-[#c9d1d9] font-mono">{robot.current_task ?? '—'}</span>
      </div>
      <div className="border-t border-[#30363d] pt-3">
        <p className="text-xs text-[#8b949e] mb-2">Send to station</p>
        <select className="w-full text-xs bg-[#0d1117] border border-[#30363d] text-[#c9d1d9] rounded px-2 py-1 mb-2"
          value={dropoffId} onChange={e => setDropoffId(e.target.value)}>
          <option value="">— select destination —</option>
          {aps.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
        <Button variant="primary" size="sm" className="w-full"
          disabled={!dropoffId || sending || robot.status === 'offline'}
          onClick={handleSendTask}>
          {sending ? 'Sending…' : 'Dispatch'}
        </Button>
      </div>
      {robot.current_task && (
        <Button variant="outline" size="sm" className="border-red-700 text-red-400 hover:bg-red-900/20"
          onClick={() => fleetApi.cancelTask(robot.current_task!)}>
          Cancel task
        </Button>
      )}
    </aside>
  )
}

function StationPanel({ station, robots, onClose }:
  { station: Station; robots: Robot[]; onClose: () => void }) {
  const [robotId, setRobotId] = useState('')
  const [sending, setSending] = useState(false)
  const available = robots.filter(r => r.status === 'idle' && !r.current_task)

  async function handleDispatch() {
    if (!robotId) return
    setSending(true)
    try { await fleetApi.createTask(robotId, station.id) }
    catch (e) { console.error(e) }
    finally { setSending(false) }
  }

  async function handleCallbutton() {
    setSending(true)
    try { await fleetApi.callbuttonPress(station.id) }
    catch (e) { console.error(e) }
    finally { setSending(false) }
  }

  return (
    <aside className="w-72 flex-shrink-0 bg-[#161b22] border-l border-[#30363d] p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[#e6edf3]">{station.label}</h2>
        <button onClick={onClose} className="text-[#8b949e] hover:text-[#c9d1d9] text-xs">✕</button>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <span className="text-[#8b949e]">Type</span>
        <span className="text-[#c9d1d9] capitalize">{station.type}</span>
        <span className="text-[#8b949e]">AP ID</span>
        <span className="text-[#c9d1d9] font-mono">{station.ap_id ?? '—'}</span>
        {station.type === 'callbutton' && <>
          <span className="text-[#8b949e]">State</span>
          <Badge variant={station.cb_state === 'called' ? 'default' : 'outline'} className="justify-self-end">
            {station.cb_state}
          </Badge>
        </>}
      </div>
      {station.type === 'callbutton' && (
        <Button variant="primary" size="sm" disabled={sending || station.cb_state === 'called'}
          onClick={handleCallbutton}>
          Simulate press
        </Button>
      )}
      {station.type !== 'base' && (
        <div className="border-t border-[#30363d] pt-3">
          <p className="text-xs text-[#8b949e] mb-2">Dispatch robot here</p>
          <select className="w-full text-xs bg-[#0d1117] border border-[#30363d] text-[#c9d1d9] rounded px-2 py-1 mb-2"
            value={robotId} onChange={e => setRobotId(e.target.value)}>
            <option value="">— select robot —</option>
            {available.map(r => <option key={r.id} value={r.id}>{r.id}</option>)}
          </select>
          <Button variant="primary" size="sm" className="w-full"
            disabled={!robotId || sending} onClick={handleDispatch}>
            {sending ? 'Sending…' : 'Dispatch'}
          </Button>
        </div>
      )}
    </aside>
  )
}

export function Field() {
  const { map, robots, stations, connected } = useFleet()
  const [selectedRobot, setSelectedRobot]     = useState<Robot | null>(null)
  const [selectedStation, setSelectedStation] = useState<Station | null>(null)

  // ── Laser layer (dedicated PULL endpoint, polled ~2.5 Hz while ON) ──────────
  const [laserOn, setLaserOn]       = useState(false)
  const [laserBeams, setLaserBeams] = useState<[number, number][]>([])
  // Refs keep the poller reading the latest selection/robots without re-arming
  // the interval on every 10 Hz SSE world frame.
  const robotsRef = useRef(robots);            robotsRef.current = robots
  const selectedRef = useRef(selectedRobot);   selectedRef.current = selectedRobot

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

  const selectedId = selectedRobot?.id ?? selectedStation?.id ?? null

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <div className="border-b border-[#30363d] px-6 py-3 flex items-center gap-3 flex-shrink-0">
        <Map className="w-4 h-4 text-[#58a6ff]" />
        <h1 className="text-sm font-semibold text-[#e6edf3]">Field View</h1>
        <div className={`w-2 h-2 rounded-full ml-2 ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        <span className="text-xs text-[#8b949e]">{connected ? 'Live' : 'Disconnected'}</span>
        <div className="ml-auto flex items-center gap-2 text-xs text-[#8b949e]">
          <button onClick={() => setLaserOn(v => !v)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded border transition-colors
              ${laserOn ? 'border-[#f0883e] text-[#f0883e] bg-[#f0883e]/10' : 'border-[#30363d] hover:bg-[#161b22]'}`}>
            <Radar className="w-3.5 h-3.5" />
            Laser
          </button>
          <span>{robots.length} robots</span>
          <span>·</span>
          <span>{stations.length} stations</span>
        </div>
      </div>

      {/* Main canvas + side panel */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-hidden">
          {map ? (
            <MapCanvas map={map} robots={robots} stations={stations}
              laser={laserOn ? { beams: laserBeams, ts: 0 } : undefined}
              selectedId={selectedId}
              onClickRobot={selectRobot}
              onClickAP={selectStation}
              className="w-full h-full"
            />
          ) : (
            <div className="h-full flex items-center justify-center text-[#8b949e] text-sm">
              {connected ? 'Loading map…' : 'Connecting to backend…'}
            </div>
          )}
        </div>
        {selectedRobot   && <RobotPanel   robot={selectedRobot}   stations={stations} onClose={() => setSelectedRobot(null)} />}
        {selectedStation && <StationPanel station={selectedStation} robots={robots}   onClose={() => setSelectedStation(null)} />}
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

