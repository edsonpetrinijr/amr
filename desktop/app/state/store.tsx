import React, { createContext, useContext, useEffect, useReducer } from 'react'
import { startFleetSSE, stopFleetSSE, onFleetMsg, onFleetStatus, fleetApi } from '../api/fleet'
import type { Robot, Station, Task, MapModel, AlarmMsg, ErpOrder } from '../api/types'

// ── State shape ───────────────────────────────────────────────────────────────

export interface FleetState {
  connected: boolean
  robots: Robot[]
  stations: Station[]
  tasks: Task[]       // live active tasks from world snapshots
  allTasks: Task[]    // full history (loaded once via REST + updated by task_update)
  map: MapModel | null
  alarms: AlarmMsg[]
  erpOrders: ErpOrder[]   // live ERP replenishment board (Reposição)
  amrReady: boolean       // a robot is idle/available at the envio station
  envioStation: string
  lastTs: number
}

const initial: FleetState = {
  connected: false,
  robots: [],
  stations: [],
  tasks: [],
  allTasks: [],
  map: null,
  alarms: [],
  erpOrders: [],
  amrReady: false,
  envioStation: '',
  lastTs: 0,
}

// ── Reducer ───────────────────────────────────────────────────────────────────

type Action =
  | { type: 'CONNECTED' }
  | { type: 'DISCONNECTED' }
  | { type: 'WORLD';      robots: Robot[]; stations: Station[]; tasks: Task[]; ts: number }
  | { type: 'MAP';        map: MapModel }
  | { type: 'TASK_UPDATE'; task: Task }
  | { type: 'ALARM';      alarm: AlarmMsg }
  | { type: 'ALL_TASKS';  tasks: Task[] }

function reducer(state: FleetState, action: Action): FleetState {
  switch (action.type) {
    case 'CONNECTED':
      return { ...state, connected: true }
    case 'DISCONNECTED':
      return { ...state, connected: false }
    case 'WORLD': {
      // Avoid replacing the stations array reference when content is unchanged —
      // stations are config-based and rarely change between world pushes.
      // Stable reference = no re-render for components that only read stations.
      const stations =
        state.stations.length === action.stations.length &&
        action.stations.every((s, i) => s.id === state.stations[i]?.id)
          ? state.stations
          : action.stations
      return { ...state, robots: action.robots, stations, tasks: action.tasks, lastTs: action.ts, connected: true }
    }
    case 'MAP':
      return { ...state, map: action.map }
    case 'TASK_UPDATE': {
      const updated = state.allTasks.some(t => t.id === action.task.id)
        ? state.allTasks.map(t => t.id === action.task.id ? action.task : t)
        : [action.task, ...state.allTasks]
      return { ...state, allTasks: updated }
    }
    case 'ALARM':
      return { ...state, alarms: [action.alarm, ...state.alarms].slice(0, 50) }
    case 'ALL_TASKS':
      return { ...state, allTasks: action.tasks }
    default:
      return state
  }
}

// ── Context ───────────────────────────────────────────────────────────────────

const FleetCtx = createContext<FleetState>(initial)
// eslint-disable-next-line react-refresh/only-export-components
export const useFleet = () => useContext(FleetCtx)

export function FleetProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initial)

  useEffect(() => {
    // Load full task history once on mount. Failure (backend offline) is non-fatal:
    // the shell still renders, just without history — never a blank window.
    fleetApi.getTasks().then((tasks: Task[]) => dispatch({ type: 'ALL_TASKS', tasks })).catch(() => {})

    // Subscribe to SSE
    const unsub = onFleetMsg((msg) => {
      if (msg.type === 'world') {
        dispatch({ type: 'WORLD', robots: msg.robots, stations: msg.stations, tasks: msg.tasks_active, ts: msg.ts })
      } else if (msg.type === 'map') {
        dispatch({ type: 'MAP', map: msg.map })
      } else if (msg.type === 'task_update') {
        dispatch({ type: 'TASK_UPDATE', task: msg.task })
      } else if (msg.type === 'alarm') {
        dispatch({ type: 'ALARM', alarm: msg })
      }
    })

    // Track the real connection state so the UI shows an accurate offline/disconnected
    // indicator instead of optimistically claiming "connected".
    const unsubStatus = onFleetStatus((connected) => {
      dispatch({ type: connected ? 'CONNECTED' : 'DISCONNECTED' })
    })

    startFleetSSE()

    return () => {
      unsub()
      unsubStatus()
      stopFleetSSE()
    }
  }, [])

  return <FleetCtx.Provider value={state}>{children}</FleetCtx.Provider>
}
