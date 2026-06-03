import React, { useState } from 'react'
import { useParams, Link } from 'react-router'
import { Wrench, AlertTriangle, ChevronUp, ChevronDown, ChevronLeft, ChevronRight, RotateCw, RotateCcw, Square, Crosshair, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { useFleet } from '../state/store'
import { fleetApi, FleetApiError, fleetBaseUrl } from '../api/fleet'
import { MapCanvas } from '../components/MapCanvas'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import type { Robot, RelocalizeSuggestion, RelocalizeSuggestionsResponse } from '../api/types'

// ── Jog panel ─────────────────────────────────────────────────────────────────

// Sane operator button values; the backend clamps to the JOG_MAX_* envelope.
const JOG_V = 0.2          // m/s for translate/strafe
const JOG_W = 0.3          // rad/s for rotate
const JOG_DURATION = 0.5   // s — single short pulse per click

type JogCmd = 'forward' | 'back' | 'left' | 'right' | 'ccw' | 'cw' | 'stop'

const JOG_VECTORS: Record<JogCmd, { vx: number; vy: number; w: number }> = {
  forward: { vx:  JOG_V, vy: 0,      w: 0 },
  back:    { vx: -JOG_V, vy: 0,      w: 0 },
  left:    { vx: 0,      vy:  JOG_V, w: 0 },
  right:   { vx: 0,      vy: -JOG_V, w: 0 },
  ccw:     { vx: 0,      vy: 0,      w:  JOG_W },
  cw:      { vx: 0,      vy: 0,      w: -JOG_W },
  stop:    { vx: 0,      vy: 0,      w: 0 },
}

function JogPanel({ robot }: { robot: Robot }) {
  const [sending, setSending] = useState(false)

  async function sendVelocity(cmd: JogCmd) {
    setSending(true)
    try {
      const v = JOG_VECTORS[cmd]
      // 'stop' is single-shot (no duration); motion pulses auto-stop after JOG_DURATION.
      const res = await fleetApi.jog(robot.id, cmd === 'stop'
        ? { vx: 0, vy: 0, w: 0 }
        : { ...v, duration: JOG_DURATION })

      if (cmd === 'stop') {
        toast.success(`Stop sent to ${robot.id}`)
      } else if (res.clamped) {
        toast.warning(`Jog ${cmd} — clamped to safe limits`, {
          description: `vx=${res.vx.toFixed(2)} vy=${res.vy.toFixed(2)} w=${res.w.toFixed(2)}`,
        })
      } else {
        toast.success(`Jog ${cmd} sent`, {
          description: `vx=${res.vx.toFixed(2)} vy=${res.vy.toFixed(2)} w=${res.w.toFixed(2)} · ${res.duration ?? 0}s`,
        })
      }
    } catch (e) {
      if (e instanceof FleetApiError) {
        if (e.status === 409)      toast.error('Jog refused', { description: e.message })
        else if (e.status === 404) toast.error('Unknown robot', { description: e.message })
        else if (e.status === 400) toast.error('Invalid jog command', { description: e.message })
        else                       toast.error('Jog failed', { description: e.message })
      } else {
        toast.error('Jog failed', { description: 'Backend not reachable' })
      }
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
      <h3 className="text-xs text-[#8b949e] mb-3 font-medium uppercase tracking-wide">Manual Jog</h3>
      <p className="text-[#6e7681] text-xs mb-3">
        Each click sends one short pulse (POST /jog). Velocities are clamped to safe limits.
        Refused while the robot has an active task or is unhealthy.
      </p>

      {/* Direction pad */}
      <div className="grid grid-cols-3 gap-1.5 w-fit mx-auto mb-3">
        <div />
        <Button variant="outline" size="icon" onClick={() => sendVelocity('forward')} disabled={sending}>
          <ChevronUp className="w-4 h-4" />
        </Button>
        <div />
        <Button variant="outline" size="icon" onClick={() => sendVelocity('left')} disabled={sending}>
          <ChevronLeft className="w-4 h-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={() => sendVelocity('stop')} disabled={sending}
          className="border-red-800 text-red-400 hover:bg-red-900/20">
          <Square className="w-3.5 h-3.5" />
        </Button>
        <Button variant="outline" size="icon" onClick={() => sendVelocity('right')} disabled={sending}>
          <ChevronRight className="w-4 h-4" />
        </Button>
        <div />
        <Button variant="outline" size="icon" onClick={() => sendVelocity('back')} disabled={sending}>
          <ChevronDown className="w-4 h-4" />
        </Button>
        <div />
      </div>

      {/* Rotation */}
      <div className="flex gap-2 justify-center">
        <Button variant="outline" size="sm" onClick={() => sendVelocity('ccw')} disabled={sending}>
          <RotateCcw className="w-3.5 h-3.5 mr-1" /> CCW
        </Button>
        <Button variant="outline" size="sm" onClick={() => sendVelocity('cw')} disabled={sending}>
          <RotateCw className="w-3.5 h-3.5 mr-1" /> CW
        </Button>
      </div>
    </div>
  )
}

// ── Jack DO panel ─────────────────────────────────────────────────────────────

function JackPanel({ robot }: { robot: Robot }) {
  const [sending, setSending] = useState(false)
  const [lastAction, setLastAction] = useState<string | null>(null)

  async function jack(action: 'up' | 'down') {
    setSending(true)
    try {
      // DO IDs from controle_completo_robo.py defaults
      const doId = action === 'up' ? 1 : 2
      const r = await fetch(`${fleetBaseUrl()}/setdo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ robot_id: robot.id, do_id: doId, status: true }),
      })
      if (r.ok) setLastAction(action)
    } catch (e) { console.error(e) }
    finally { setSending(false) }
  }

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
      <h3 className="text-xs text-[#8b949e] mb-3 font-medium uppercase tracking-wide">Jack / Load Platform</h3>
      <div className="flex gap-2">
        <Button variant="outline" size="sm" disabled={sending} onClick={() => jack('up')}
          className="flex-1">
          <ChevronUp className="w-3.5 h-3.5 mr-1" /> Raise
        </Button>
        <Button variant="outline" size="sm" disabled={sending} onClick={() => jack('down')}
          className="flex-1">
          <ChevronDown className="w-3.5 h-3.5 mr-1" /> Lower
        </Button>
      </div>
      {lastAction && (
        <p className="text-xs text-[#3fb950] mt-2">Last: {lastAction}</p>
      )}
    </div>
  )
}

// ── Relocalize panel ──────────────────────────────────────────────────────────

function RelocalizePanel({ robot }: { robot: Robot }) {
  const { map, stations } = useFleet()
  const [x,     setX]     = useState(String(robot.x.toFixed(2)))
  const [y,     setY]     = useState(String(robot.y.toFixed(2)))
  const [theta, setTheta] = useState(String((robot.theta * 180 / Math.PI).toFixed(1)))
  const [sending, setSending] = useState(false)
  const [result,  setResult]  = useState<string | null>(null)

  // ── Relocalization assist ───────────────────────────────────────────────────
  const [assistLoading, setAssistLoading] = useState(false)
  const [assist, setAssist] = useState<RelocalizeSuggestionsResponse | null>(null)

  async function handleRelocalize() {
    setSending(true)
    setResult(null)
    try {
      const r = await fleetApi.relocalize(robot.id, parseFloat(x), parseFloat(y), parseFloat(theta) * Math.PI / 180)
      setResult(r.ok ? '✓ Relocalization sent' : '✗ Failed')
    } catch { setResult('✗ Error') }
    finally { setSending(false) }
  }

  async function handleGetSuggestions() {
    setAssistLoading(true)
    try {
      const res = await fleetApi.getRelocalizeSuggestions({ robotId: robot.id })
      setAssist(res)
    } catch (e) {
      setAssist(null)
      if (e instanceof FleetApiError) {
        if (e.status === 409)      toast.error('No map loaded', { description: 'Load a map before requesting suggestions.' })
        else if (e.status === 404) toast.error('Robot pose unavailable', { description: 'The system does not know where this robot is yet.' })
        else if (e.status === 400) toast.error('Missing parameters', { description: e.message })
        else                       toast.error('Could not get suggestions', { description: e.message })
      } else {
        toast.error('Could not get suggestions', { description: 'Backend not reachable' })
      }
    } finally {
      setAssistLoading(false)
    }
  }

  // Fill the pose fields from a landmark. Keep current θ when the landmark has none.
  function applySuggestion(s: RelocalizeSuggestion) {
    setX(s.x.toFixed(2))
    setY(s.y.toFixed(2))
    if (s.theta != null) setTheta((s.theta * 180 / Math.PI).toFixed(1))
    setResult(null)
  }

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
      <h3 className="text-xs text-[#8b949e] mb-3 font-medium uppercase tracking-wide">Relocalization</h3>
      <p className="text-[#6e7681] text-xs mb-3">
        Set initial pose estimate on the map. Click a landmark on the map to pre-fill coordinates.
      </p>
      <div className="grid grid-cols-3 gap-2 mb-3">
        {([['X (m)', x, setX], ['Y (m)', y, setY], ['θ (°)', theta, setTheta]] as [string, string, (v: string) => void][]).map(([lbl, val, set]) => (
          <div key={lbl}>
            <label className="text-xs text-[#8b949e] block mb-1">{lbl}</label>
            <input value={val} onChange={e => set(e.target.value)}
              className="w-full text-xs bg-[#0d1117] border border-[#30363d] text-[#c9d1d9] rounded px-2 py-1 font-mono" />
          </div>
        ))}
      </div>
      <Button variant="primary" size="sm" className="w-full" disabled={sending} onClick={handleRelocalize}>
        {sending ? 'Sending…' : 'Set Pose'}
      </Button>
      {result && <p className="text-xs mt-2 text-[#3fb950]">{result}</p>}

      {/* ── Relocalization Assist ───────────────────────────────────────────── */}
      <div className="mt-4 pt-3 border-t border-[#30363d]">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs text-[#8b949e] font-medium uppercase tracking-wide flex items-center gap-1.5">
            <Crosshair className="w-3.5 h-3.5" /> Relocalization Assist
          </h4>
          <Button variant="outline" size="sm" disabled={assistLoading} onClick={handleGetSuggestions}>
            {assistLoading ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : null}
            {assistLoading ? 'Finding…' : 'Get suggestions'}
          </Button>
        </div>
        <p className="text-[#6e7681] text-xs mb-2">
          Suggests the nearest map landmarks to where the system thinks {robot.id} is. Pick one to pre-fill the pose.
        </p>

        {assist && (
          <p className="text-[10px] text-[#6e7681] font-mono mb-2">
            pose used: x={assist.pose_used.x.toFixed(2)} y={assist.pose_used.y.toFixed(2)}
            {assist.pose_used.confidence != null ? ` · conf ${(assist.pose_used.confidence * 100).toFixed(0)}%` : ''}
            {' '}· {assist.source === 'robot_state' ? 'from robot' : 'explicit'}
          </p>
        )}

        {assist && assist.suggestions.length === 0 && (
          <p className="text-xs text-[#8b949e] py-2">No landmarks found.</p>
        )}

        {assist && assist.suggestions.length > 0 && (
          <ul className="space-y-1">
            {assist.suggestions.map(s => (
              <li key={s.lm_id}
                className="flex items-center gap-2 text-xs bg-[#0d1117] border border-[#30363d] rounded px-2 py-1.5">
                <span className="font-mono text-[#c9d1d9] truncate flex-1">{s.name}</span>
                <span className="text-[#8b949e] font-mono shrink-0">{s.dist_m.toFixed(1)} m</span>
                <Button variant="outline" size="sm" className="shrink-0 h-6 px-2"
                  onClick={() => applySuggestion(s)}>
                  Use
                </Button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Mini map with landmark click */}
      {map && (
        <div className="mt-3 rounded overflow-hidden border border-[#30363d]" style={{ height: 200 }}>
          <MapCanvas map={map} stations={stations} robots={[robot]}
            className="w-full h-full"
            onClickAP={s => { setX(s.x.toFixed(2)); setY(s.y.toFixed(2)) }}
          />
        </div>
      )}
    </div>
  )
}

// ── Root page ─────────────────────────────────────────────────────────────────

export function Calibration() {
  const { robotId } = useParams<{ robotId?: string }>()
  const { robots, connected } = useFleet()

  const robot = robotId ? robots.find(r => r.id === robotId) : robots[0]

  return (
    <div className="flex-1 flex flex-col bg-[#0d1117]">
      {/* Header */}
      <div className="border-b border-[#30363d] px-6 py-3 flex items-center gap-3 flex-shrink-0">
        <Wrench className="w-4 h-4 text-[#58a6ff]" />
        <h1 className="text-sm font-semibold text-[#e6edf3]">Calibration</h1>
        <div className={`w-2 h-2 rounded-full ml-2 ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        {robot && (
          <Badge variant="secondary" className="ml-1">{robot.id}</Badge>
        )}
        <div className="ml-auto flex gap-2">
          {/* Robot selector */}
          {robots.map(r => (
            <Link key={r.id} to={`/calibration/${r.id}`}
              className={`text-xs px-2 py-1 rounded transition-colors
                ${r.id === robot?.id
                  ? 'bg-[#21262d] text-[#e6edf3] border border-[#58a6ff]'
                  : 'text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#161b22]'}`}>
              {r.id}
            </Link>
          ))}
        </div>
      </div>

      {!robot ? (
        <div className="flex-1 flex items-center justify-center text-[#8b949e] text-sm">
          Select a robot above to begin calibration
        </div>
      ) : (
        <div className="flex-1 overflow-auto p-6">
          {/* Warning */}
          <div className="flex items-start gap-2 bg-yellow-900/20 border border-yellow-700/40 rounded-lg px-4 py-3 mb-5 text-xs text-yellow-300">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>
              Calibration commands bypass the dispatcher and send directly to the robot hardware.
              Ensure the area is clear before relocalization or jog movements.
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <RelocalizePanel robot={robot} />
            <JogPanel robot={robot} />
            <JackPanel robot={robot} />
          </div>
        </div>
      )}
    </div>
  )
}

