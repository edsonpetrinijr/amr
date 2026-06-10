// Fleet domain types — mirror of server/app/models.py

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

export interface Landmark { id: string; x: number; y: number; label?: string }

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
  /** Robot model string (e.g. "W3-600B"), pulled from the unit. */
  model: string
  /** Live reachability from GET /robots — true when the backend can reach the unit. */
  connected: boolean
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
 *  models.DEFAULT_FOOTPRINT_* . Founder-confirmed spec:
 *  0.95 × 0.65 × 0.25 m (with bumper strip). L×W×H, length is along +theta
 *  (forward), width is perpendicular, height is for the 3D preview only. */
export const DEFAULT_FOOTPRINT = { length: 0.95, width: 0.65 } as const
/** Robot height in metres — used by the 3D preview only (not the 2D map). */
export const DEFAULT_HEIGHT_M = 0.25

export type StationType = 'callbutton' | 'base' | 'ap'
export type CallbuttonState = 'idle' | 'ready' | 'called' | 'served'

export interface Station {
  id: string; type: StationType; label: string
  x: number; y: number
  seer_lm: string | null; ap_id: string | null; opcua_node: string | null
  /** OPC UA return/ack node id (paired button), if configured. */
  opcua_ret: string | null
  cb_state: CallbuttonState
  cb_dir: 'fwd' | 'ret' | null
}

// ── Devices configuration / diagnostics results ───────────────────────────────

/** Fields pulled from a unit on add/edit/probe. */
export interface RobotPulled {
  name: string; model: string; battery: number
  x: number; y: number; theta: number
}

/** POST /robots and PUT /robots/<id> response. */
export interface RobotMutationResult {
  robot: Robot
  connected: boolean
  pulled: RobotPulled
}

/** POST /robots/<id>/probe response. */
export interface ProbeResult {
  connected: boolean
  pulled: RobotPulled
}

/** POST /opcua/test response. */
export interface OpcuaTestResult {
  ok: boolean
  value: unknown
  error: string | null
  configured: boolean
  endpoint: string | null
  node: string
}

/** PUT /stations/<id> response. */
export interface StationMutationResult {
  station: Station
}

export type TaskState =
  | 'pending' | 'assigned' | 'enroute_pickup' | 'at_pickup'
  | 'enroute_drop' | 'done' | 'cancelled' | 'failed'

export interface Task {
  id: string; pickup: string; dropoff: string
  state: TaskState; robot: string | null; facility_id: string
  created_at: number; assigned_at: number | null; done_at: number | null
}

// ── ERP replenishment orders (Reposição) ──────────────────────────────────────

export type ErpOrderStatus =
  | 'seen' | 'blocked_unmapped' | 'ready_for_confirmation'
  | 'confirmed' | 'dispatched' | 'em_entrega' | 'delivered' | 'cancelled'

/** One ERP record surfaced for AMR replenishment. `record_type_class` splits the
 *  main order queue from the empties/return lane ('empty_return'). */
export interface ErpOrder {
  order_key: string
  record_type: string
  record_type_class: string   // 'order' | 'fulfillment' | 'cancellation' | 'empty_return'
  part_number: string
  storage_loc: string
  cell: string
  pou: string
  quantity: string
  order_date_raw: string
  observation: string
  amr_flagged: boolean
  status: ErpOrderStatus
  pickup_station: string | null
  dropoff_station: string | null
  task_id: string | null
  first_seen_ts: number
  dispatched_ts: number | null
  delivered_ts: number | null
  cancelled_ts: number | null
  last_seen_ts: number
  note: string | null
}

/** GET /erp/orders */
export interface ErpOrdersResponse {
  orders: ErpOrder[]
  amr_ready: boolean
  envio_station: string
}

/** POST /erp/confirm-delivery → 200 {ok, order} | 409 {ok:false, error} */
export interface ConfirmDeliveryResult {
  ok: boolean
  order?: ErpOrder
  error?: string
}

/** POST /erp/request-empty → 200 {ok, ...job} | 409 {ok:false, error} */
export interface RequestEmptyResult {
  ok: boolean
  error?: string
  [k: string]: unknown
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

/** SSE — emitted on every ERP order create / status change. */
export interface ErpOrderMsg { type: 'erp_order'; ts: number; order: ErpOrder }

export type FleetMsg = WorldMsg | MapMsg | TaskMsg | CBMsg | AlarmMsg | ErpOrderMsg

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

/** POST /robots/<id>/navigate response — robot dispatched to a map landmark. */
export interface NavigateResult {
  ok: boolean
  robot_id: string
  landmark_id: string
  x: number
  y: number
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

/** POST /jog/stop → {ok, robot_id} (immediately zeroes velocity). */
export interface JogStopResult {
  ok: boolean
  robot_id: string
}

/** POST /jack → {ok, robot_id, action} (full raise/lower DO pulse). */
export interface JackResult {
  ok: boolean
  robot_id: string
  action: 'up' | 'down'
}

/** POST /callbutton/<id> → simulate a physical press. The backend may include
 *  the resulting transport/callbutton state; all fields beyond `ok` are optional. */
export interface CallbuttonPressResult {
  ok: boolean
  station_id?: string
  state?: string
  message?: string
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
