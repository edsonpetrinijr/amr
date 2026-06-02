// SSE client — connects to GET /events and dispatches typed messages.
// REST helpers for commands (create/cancel task, callbutton, relocalize).

import type { FleetMsg, Task } from './types'

const BASE = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_FLEET_URL) ?? 'http://localhost:8765'

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

async function _json(path: string, opts?: RequestInit) {
  const r = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!r.ok) throw new Error(`${opts?.method ?? 'GET'} ${path} → ${r.status}`)
  return r.json()
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
}
