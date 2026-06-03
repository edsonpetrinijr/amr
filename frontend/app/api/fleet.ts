// SSE client — connects to GET /events and dispatches typed messages.
// REST helpers for commands (create/cancel task, callbutton, relocalize).

import type { FleetMsg, Task } from './types'
import type {
  JogResult, StopAllResult, ResumeResult,
  StatsSummary, RobotTelemetry, TasksHistory, LaserScan,
  RelocalizeSuggestionsResponse,
  RobotMutationResult, ProbeResult, OpcuaTestResult, StationMutationResult,
} from './types'

const BASE: string = import.meta.env?.VITE_FLEET_URL ?? 'http://localhost:8765'

/** One entry from GET /maps — an available .smap and whether it's the active one. */
export type MapInfo = { name: string; current: boolean }

/** Result of POST /maps/select. `map` is the freshly-loaded MapModel (the canvas
 *  refreshes via the broadcast SSE `map` message, so callers rarely read it). */
export type SelectMapResult = { ok: boolean; name: string; map: unknown }

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

  /** GET /maps — list available .smap files and which one is currently loaded. */
  getMaps:         ()                             => _json('/maps') as Promise<MapInfo[]>,

  /** POST /maps/select — switch the active map. Backend broadcasts a `map` SSE
   *  message on success, so the canvas refreshes automatically. */
  selectMap: (name: string) =>
    _json('/maps/select', { method: 'POST', body: JSON.stringify({ name }) }) as Promise<SelectMapResult>,
  getStations:     ()                             => _json('/stations'),
  getRobots:       ()                             => _json('/robots'),

  // ── Devices config / diagnostics (surface 4xx via FleetApiError) ────────────

  /** POST /robots — register a unit by IP; backend probes it and returns the
   *  connection status + pulled fields. */
  addRobot: (body: { ip: string; id?: string; name?: string }) =>
    _jsonOrError('/robots', { method: 'POST', body: JSON.stringify(body) }) as Promise<RobotMutationResult>,

  /** PUT /robots/<id> — change IP and/or name; re-probes and returns status. */
  updateRobot: (id: string, body: { ip?: string; name?: string }) =>
    _jsonOrError(`/robots/${id}`, { method: 'PUT', body: JSON.stringify(body) }) as Promise<RobotMutationResult>,

  /** DELETE /robots/<id> — remove a unit. */
  deleteRobot: (id: string) =>
    _jsonOrError(`/robots/${id}`, { method: 'DELETE' }) as Promise<{ ok: true; id: string }>,

  /** POST /robots/<id>/probe — re-check reachability and re-pull fields. */
  probeRobot: (id: string) =>
    _jsonOrError(`/robots/${id}/probe`, { method: 'POST' }) as Promise<ProbeResult>,

  /** PUT /stations/<id> — edit OPC UA node / return node / label. */
  updateStation: (id: string, body: { opcua_node?: string | null; opcua_ret?: string | null; label?: string }) =>
    _jsonOrError(`/stations/${id}`, { method: 'PUT', body: JSON.stringify(body) }) as Promise<StationMutationResult>,

  /** POST /opcua/test — read a node (by id or station) to verify wiring. */
  testOpcua: (body: { node?: string; station_id?: string }) =>
    _jsonOrError('/opcua/test', { method: 'POST', body: JSON.stringify(body) }) as Promise<OpcuaTestResult>,

  /** Dedicated PULL for the laser layer — frontend polls ~2–3 Hz only while the
   *  Laser toggle is ON. Beams are WORLD/MAP-frame [x,y] metres (no transform). */
  getLaser: (robot_id: string) =>
    _json(`/robots/${robot_id}/laser`) as Promise<LaserScan>,
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

  /** GET /relocalize/suggestions — nearest map landmarks to where the system
   *  thinks the robot is. Pass robotId (preferred) OR explicit x & y. Throws
   *  FleetApiError on 409 (no map) / 404 (pose unavailable) / 400 (missing params). */
  getRelocalizeSuggestions: (params: { robotId?: string; x?: number; y?: number; k?: number }) => {
    const p = new URLSearchParams()
    if (params.robotId != null) p.set('robot_id', params.robotId)
    if (params.x != null)       p.set('x', String(params.x))
    if (params.y != null)       p.set('y', String(params.y))
    if (params.k != null)       p.set('k', String(params.k))
    return _jsonOrError(`/api/relocalize/suggestions?${p.toString()}`) as Promise<RelocalizeSuggestionsResponse>
  },

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
