// Fleet domain types — mirror of backend/app/models.py

export interface Pos2D { x: number; y: number }
export interface Pose2D { x: number; y: number; theta: number }

export interface Wall { start: Pos2D; end: Pos2D }

export interface ActionPoint {
  id: string; x: number; y: number; theta: number
  ap_type: string; label: string
}

export interface Area {
  id: string; class_name: string; label: string
  points: Pos2D[]
}

export interface Landmark { id: string; x: number; y: number }

export interface Route {
  id: string
  start_id: string; end_id: string
  start: Pos2D; end: Pos2D
  ctrl1: Pos2D; ctrl2: Pos2D
  direction: number  // 0=bidirectional, 1=start→end, 2=end→start
}

export interface MapModel {
  name: string; map_type: string; version: string; resolution: number
  min_pos: Pos2D; max_pos: Pos2D
  walls: Wall[]
  nav_points: Pos2D[]
  action_points: ActionPoint[]
  areas: Area[]
  landmarks: Landmark[]
  routes: Route[]
  robot_pos: Pose2D | null
}

export type RobotStatus =
  | 'idle' | 'enroute_pickup' | 'at_pickup'
  | 'enroute_drop' | 'returning' | 'charging' | 'error' | 'offline'

export interface Robot {
  id: string; name: string; ip: string
  x: number; y: number; theta: number
  battery: number; status: RobotStatus
  nav: string
  goal_x: number | null; goal_y: number | null; goal_station: string | null
  current_task: string | null; paused: boolean; last_seen: number
}

export type StationType = 'callbutton' | 'base' | 'ap'
export type CallbuttonState = 'idle' | 'ready' | 'called' | 'served'

export interface Station {
  id: string; type: StationType; label: string
  x: number; y: number
  seer_lm: string | null; ap_id: string | null; opcua_node: string | null
  cb_state: CallbuttonState
  cb_dir: 'fwd' | 'ret' | null
}

export type TaskState =
  | 'pending' | 'assigned' | 'enroute_pickup' | 'at_pickup'
  | 'enroute_drop' | 'done' | 'cancelled' | 'failed'

export interface Task {
  id: string; pickup: string; dropoff: string
  state: TaskState; robot: string | null; facility_id: string
  created_at: number; assigned_at: number | null; done_at: number | null
}

// ── SSE message envelopes ─────────────────────────────────────────────────────

export interface WorldMsg {
  type: 'world'; ts: number
  robots: Robot[]; stations: Station[]; tasks_active: Task[]
}
export interface MapMsg   { type: 'map';          map: MapModel }
export interface TaskMsg  { type: 'task_update';  event: string; task: Task }
export interface CBMsg    { type: 'callbutton';   station: Station }
export interface AlarmMsg { type: 'alarm';        level: string; message: string; robot_id: string | null; ts: number }

export type FleetMsg = WorldMsg | MapMsg | TaskMsg | CBMsg | AlarmMsg

// ── Manual control / analytics (Sprint endpoints) ─────────────────────────────

/** POST /jog → {ok, robot_id, vx, vy, w, duration, clamped, halted} */
export interface JogResult {
  ok: boolean
  robot_id: string
  vx: number
  vy: number
  w: number
  duration: number | null
  clamped: boolean
  halted: boolean
}

/** POST /stop_all → {halted:true, cancelled:[...], note} */
export interface StopAllResult {
  halted: boolean
  cancelled: string[]
  note: string
}

/** POST /resume → {halted:false} */
export interface ResumeResult {
  halted: boolean
}

/** GET /stats/summary */
export interface StatsSummary {
  tasks_completed_today: number
  tasks_failed_today: number
  avg_task_duration_s: number | null
  fleet_total: number
  fleet_active: number
  fleet_utilization: number
  avg_battery: number | null
  halted: boolean
}

export interface TelemetryRow {
  ts: number
  x: number
  y: number
  battery: number
  status: string
}

/** GET /telemetry/robots/<id> */
export interface RobotTelemetry {
  robot_id: string
  count: number
  rows: TelemetryRow[]
}

export interface TaskHistoryRow {
  id: string
  pickup: string
  dropoff: string
  robot: string | null
  state: string
  created_ts: number | null
  finished_ts: number | null
  duration_s: number | null
}

/** GET /tasks/history */
export interface TasksHistory {
  count: number
  tasks: TaskHistoryRow[]
}
