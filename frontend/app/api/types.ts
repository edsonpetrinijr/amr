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

/** GET /robots/<id>/laser — beams are WORLD/MAP-frame [x, y] metres (protocol
 *  PDF p.24). The canvas draws them directly via tx/ty with no pose composition.
 *  NOTE(real HW): if a real unit returns robot-relative/angle-distance instead,
 *  this no-transform contract breaks — confirm on first real-robot test. */
export interface LaserScan { beams: [number, number][]; ts: number }

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
  /** Real-world footprint in metres (top-down). length = along +theta (forward),
   *  width = perpendicular. Optional: falls back to DEFAULT_FOOTPRINT if absent. */
  footprint?: { length: number; width: number }
}

/** Shared default robot footprint in metres — mirror of backend
 *  models.DEFAULT_FOOTPRINT_* . PLACEHOLDER pending founder confirmation of the
 *  real chassis dimensions (AMR.step bbox is a sub-component, not the chassis). */
export const DEFAULT_FOOTPRINT = { length: 0.70, width: 0.50 } as const

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

/** Structured recovery alarm payload (present only on actionable loc-recovery alarms). */
export interface RelocalizeAssistPayload {
  robot_id: string
  task_id: string | null
  reason: 'NAV_FAILED' | 'STUCK' | 'LOW_CONFIDENCE'
  last_pose: { x: number | null; y: number | null; theta: number | null; confidence: number | null }
  action: 'RELOCALIZE_ASSIST_V1'
  suggestions_url: string
  timestamp: number
  incident_id: string
}
export interface AlarmMsg { type: 'alarm';        level: string; message: string; robot_id: string | null; ts: number; payload?: RelocalizeAssistPayload }

export type FleetMsg = WorldMsg | MapMsg | TaskMsg | CBMsg | AlarmMsg

// ── Relocalization assist (GET /relocalize/suggestions) ───────────────────────

/** One nearby map landmark. NOTE: landmarks carry no real name/theta —
 *  `name === lm_id` and `theta` may be null. */
export interface RelocalizeSuggestion {
  lm_id: string
  name: string
  x: number
  y: number
  theta: number | null
  dist_m: number
}

/** GET /relocalize/suggestions → nearest landmarks to the pose the system
 *  believes the robot is at. */
export interface RelocalizeSuggestionsResponse {
  frame: string
  source: 'robot_state' | 'explicit_pose'
  pose_used: { x: number; y: number; theta: number | null; confidence: number | null }
  suggestions: RelocalizeSuggestion[]
}

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
