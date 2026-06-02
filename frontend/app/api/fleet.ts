// SSE client — connects to GET /events and dispatches typed messages.
// REST helpers for commands (create/cancel task, callbutton, relocalize).

import type { FleetMsg, Task } from './types'
import type {
  JogResult, StopAllResult, ResumeResult,
  StatsSummary, RobotTelemetry, TasksHistory,
} from './types'

const BASE: string = import.meta.env?.VITE_FLEET_URL ?? 'http://localhost:8765'

/** Configured backend base URL — for callers that need raw fetch (e.g. /setdo). */
export function fleetBaseUrl(): string {
  return BASE
}

// ── SSE ───────────────────────────────────────────────────────────────────────

type Listener = (msg: FleetMsg) => void

let _es: EventSource | null = null
const _listeners = new Set<Listener>()
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null

function _connect() {
  if (_es) { _es.close() }

  const es = new EventSource(`${BASE}/events`)
  _es = es

  es.onmessage = (e) => {
    try {
      const msg: FleetMsg = JSON.parse(e.data)
      _listeners.forEach(fn => fn(msg))
    } catch { /* ignore malformed */ }
  }

  es.onerror = () => {
    es.close()
    _es = null
    if (_reconnectTimer) clearTimeout(_reconnectTimer)
    _reconnectTimer = setTimeout(_connect, 3000)
  }
}

export function startFleetSSE() {
  if (!_es) _connect()
}

export function stopFleetSSE() {
  if (_reconnectTimer) clearTimeout(_reconnectTimer)
  _es?.close()
  _es = null
}

export function onFleetMsg(fn: Listener): () => void {
  _listeners.add(fn)
  return () => _listeners.delete(fn)
}

// ── REST helpers ──────────────────────────────────────────────────────────────

/** Error carrying the HTTP status and the backend's JSON error message (if any). */
export class FleetApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'FleetApiError'
    this.status = status
  }
}

async function _json(path: string, opts?: RequestInit) {
  const r = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!r.ok) throw new Error(`${opts?.method ?? 'GET'} ${path} → ${r.status}`)
  return r.json()
}

/** Like _json but parses the backend's `{error}` body and throws a FleetApiError
 *  carrying the status — used where the UI needs to surface 4xx messages. */
async function _jsonOrError(path: string, opts?: RequestInit) {
  const r = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  let body: unknown = null
  try { body = await r.json() } catch { /* no/invalid JSON body */ }
  if (!r.ok) {
    const msg = (body && typeof body === 'object' && ('error' in body || 'message' in body) ? ((body as Record<string,string>).error || (body as Record<string,string>).message) : null) || `${opts?.method ?? 'GET'} ${path} → ${r.status}`
    throw new FleetApiError(r.status, msg)
  }
  return body
}

function _qs(opts?: { since?: number; limit?: number }): string {
  if (!opts) return ''
  const p = new URLSearchParams()
  if (opts.since != null) p.set('since', String(opts.since))
  if (opts.limit != null) p.set('limit', String(opts.limit))
  const s = p.toString()
  return s ? `?${s}` : ''
}

export const fleetApi = {
  health:          ()                             => _json('/health'),
  getMap:          ()                             => _json('/map'),
  getStations:     ()                             => _json('/stations'),
  getRobots:       ()                             => _json('/robots'),
  getTasks:        ()                             => _json('/tasks'),

  createTask: (pickup: string, dropoff: string)  =>
    _json('/tasks', { method: 'POST', body: JSON.stringify({ pickup, dropoff }) }) as Promise<Task>,

  cancelTask: (id: string)                       =>
    _json(`/tasks/${id}`, { method: 'DELETE' }),

  buttonPress: (stationId: string, dir: 'fwd' | 'ret') =>
    _json(`/button/${stationId}`, { method: 'POST', body: JSON.stringify({ dir }) }),

  resetPair: (stationId: string) =>
    _json(`/reset/${stationId}`, { method: 'POST' }),

  callbuttonPress: (stationId: string)           =>
    _json(`/callbutton/${stationId}`, { method: 'POST' }),

  relocalize: (robot_id: string, x: number, y: number, theta: number) =>
    _json('/relocalize', { method: 'POST', body: JSON.stringify({ robot_id, x, y, theta }) }),

  // ── Manual control ──────────────────────────────────────────────────────────

  /** Single-shot manual jog. Velocities are clamped server-side to the JOG
   *  envelope. Throws FleetApiError on 404 (unknown robot) / 409 (active task or
   *  unhealthy) / 400 (bad values) so callers can surface the message. */
  jog: (robot_id: string, body: { vx: number; vy: number; w: number; duration?: number }) =>
    _jsonOrError('/jog', {
      method: 'POST',
      body: JSON.stringify({ robot_id, ...body }),
    }) as Promise<JogResult>,

  /** Software STOP-ALL — halts every robot and cancels active tasks. */
  stopAll: () =>
    _json('/stop_all', { method: 'POST' }) as Promise<StopAllResult>,

  /** Clear the STOP-ALL halt and re-enable auto-dispatch. */
  resume: () =>
    _json('/resume', { method: 'POST' }) as Promise<ResumeResult>,

  // ── Analytics / telemetry (read-only) ───────────────────────────────────────

  getStatsSummary: () =>
    _json('/stats/summary') as Promise<StatsSummary>,

  getRobotTelemetry: (robot_id: string, opts?: { since?: number; limit?: number }) =>
    _json(`/telemetry/robots/${robot_id}${_qs(opts)}`) as Promise<RobotTelemetry>,

  getTasksHistory: (opts?: { since?: number; limit?: number }) =>
    _json(`/tasks/history${_qs(opts)}`) as Promise<TasksHistory>,
}
