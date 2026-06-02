import React, { createContext, useContext, useEffect, useReducer, useRef } from 'react'
import { startFleetSSE, stopFleetSSE, onFleetMsg, fleetApi } from '../api/fleet'
import type { Robot, Station, Task, MapModel, AlarmMsg } from '../api/types'

// ── State shape ───────────────────────────────────────────────────────────────

export interface FleetState {
  connected: boolean
  robots: Robot[]
  stations: Station[]
  tasks: Task[]       // live active tasks from world snapshots
  allTasks: Task[]    // full history (loaded once via REST + updated by task_update)
  map: MapModel | null
  alarms: AlarmMsg[]
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
    case 'WORLD':
      return { ...state, robots: action.robots, stations: action.stations, tasks: action.tasks, lastTs: action.ts, connected: true }
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
export const useFleet = () => useContext(FleetCtx)

export function FleetProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initial)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    // Load full task history once on mount
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

    startFleetSSE()
    dispatch({ type: 'CONNECTED' })

    return () => {
      unsub()
      stopFleetSSE()
    }
  }, [])

  return <FleetCtx.Provider value={state}>{children}</FleetCtx.Provider>
}
