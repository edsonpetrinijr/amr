// Pure simulation physics — no React, no UI deps.
// Drives ExperimentDetail visually AND exposes RL control surface.

export interface RobotState {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  alive: boolean;
  reachedGoal: boolean;
}

export interface ObstacleState {
  x: number; // percent of canvas
  y: number;
  w: number;
  h: number;
}

export interface SpawnArea {
  x: number; // percent top-left
  y: number;
  w: number;
  h: number;
}

export interface SimState {
  robots: RobotState[];
  obstacles: ObstacleState[];
  target: { x: number; y: number; radius: number };
  spawnArea: SpawnArea;
  numRobots: number;
  step: number;
  maxSteps: number;
  speed: number;
  done: boolean;
  collisions: number;
  goalsReached: number;
  mlMode: boolean;
}

// 9-direction discrete action space per robot
export type RobotAction = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;
export type SwarmAction = RobotAction[]; // length = NUM_ROBOTS

const DEFAULT_NUM_ROBOTS = 12;
const MAX_NUM_ROBOTS = 500;
const MAX_STEPS = 500;
const STEP_SIZE = 1.5;

// Match hardcoded obstacles from ExperimentDetail.tsx
const DEFAULT_OBSTACLES: ObstacleState[] = [
  { x: 30, y: 20, w: 15, h: 15 },
  { x: 60, y: 50, w: 10, h: 30 },
  { x: 20, y: 70, w: 20, h: 10 },
];

const DEFAULT_TARGET = { x: 88, y: 12, radius: 5 };
const DEFAULT_SPAWN: SpawnArea = { x: 5, y: 40, w: 30, h: 50 };

// Direction vectors for actions 0–8
const DIRS: [number, number][] = [
  [0, 0],   // 0 idle
  [0, -1],  // 1 N
  [0, 1],   // 2 S
  [1, 0],   // 3 E
  [-1, 0],  // 4 W
  [1, -1],  // 5 NE
  [-1, -1], // 6 NW
  [1, 1],   // 7 SE
  [-1, 1],  // 8 SW
];

function initRobots(n: number, seed?: number, spawn: SpawnArea = DEFAULT_SPAWN): RobotState[] {
  let rng = seed ?? Date.now();
  const rand = () => {
    rng = (rng * 1664525 + 1013904223) & 0xffffffff;
    return (rng >>> 0) / 0xffffffff;
  };
  return Array.from({ length: n }, (_, i) => ({
    id: i,
    x: spawn.x + rand() * spawn.w,
    y: spawn.y + rand() * spawn.h,
    vx: 0,
    vy: 0,
    alive: true,
    reachedGoal: false,
  }));
}

function hitsObstacle(x: number, y: number, obstacles: ObstacleState[]): boolean {
  return obstacles.some(o => x >= o.x && x <= o.x + o.w && y >= o.y && y <= o.y + o.h);
}

function hitsBoundary(x: number, y: number): boolean {
  return x <= 0 || x >= 100 || y <= 0 || y >= 100;
}

export interface StepEvents {
  newCollisions: number;
  newGoals: number;
}

export interface EngineStepResult {
  state: SimState;
  events: StepEvents;
}

export class SimulationEngine extends EventTarget {
  state: SimState;
  private _seed: number;

  constructor(seed?: number) {
    super();
    this._seed = seed ?? 42089;
    this.state = this._buildInitialState();
  }

  private _buildInitialState(): SimState {
    const prev = (this as any).state as SimState | undefined;
    const spawnArea = prev?.spawnArea ?? DEFAULT_SPAWN;
    const obstacles = prev?.obstacles ?? DEFAULT_OBSTACLES;
    const target = prev?.target ?? DEFAULT_TARGET;
    const numRobots = prev?.numRobots ?? DEFAULT_NUM_ROBOTS;
    return {
      robots: initRobots(numRobots, this._seed, spawnArea),
      obstacles,
      target,
      spawnArea,
      numRobots,
      step: 0,
      maxSteps: MAX_STEPS,
      speed: 1,
      done: false,
      collisions: 0,
      goalsReached: 0,
      mlMode: prev?.mlMode ?? false,
    };
  }

  reset(seed?: number): SimState {
    if (seed !== undefined) this._seed = seed;
    this.state = this._buildInitialState();
    this._emit();
    return this.state;
  }

  setObstacle(index: number, patch: Partial<ObstacleState>) {
    const obstacles = this.state.obstacles.map((o, i) => i === index ? { ...o, ...patch } : o);
    this.state = { ...this.state, obstacles };
    this._emit();
  }

  setTarget(patch: Partial<SimState['target']>) {
    this.state = { ...this.state, target: { ...this.state.target, ...patch } };
    this._emit();
  }

  setSpawnArea(patch: Partial<SpawnArea>) {
    this.state = { ...this.state, spawnArea: { ...this.state.spawnArea, ...patch } };
    this._emit();
  }

  setNumRobots(n: number) {
    const clamped = Math.max(1, Math.min(MAX_NUM_ROBOTS, n));
    this.state = { ...this.state, numRobots: clamped };
    this._emit();
  }

  // Advance one simulation step. actions[i] is RobotAction for robot i.
  // If actions omitted, all robots idle.
  advance(actions?: SwarmAction): EngineStepResult {
    if (this.state.done) {
      return { state: this.state, events: { newCollisions: 0, newGoals: 0 } };
    }

    let newCollisions = 0;
    let newGoals = 0;
    const { obstacles, target } = this.state;

    const robots = this.state.robots.map((r, i) => {
      if (!r.alive) return r;

      const action = (actions?.[i] ?? 0) as RobotAction;
      const [dx, dy] = DIRS[action];
      const nx = r.x + dx * STEP_SIZE * this.state.speed;
      const ny = r.y + dy * STEP_SIZE * this.state.speed;

      if (hitsBoundary(nx, ny) || hitsObstacle(nx, ny, obstacles)) {
        newCollisions++;
        return { ...r, alive: false };
      }

      const dist = Math.sqrt((nx - target.x) ** 2 + (ny - target.y) ** 2);
      if (dist <= target.radius) {
        newGoals++;
        return { ...r, x: nx, y: ny, vx: dx, vy: dy, alive: false, reachedGoal: true };
      }

      return { ...r, x: nx, y: ny, vx: dx, vy: dy };
    });

    const nextStep = this.state.step + 1;
    const done = nextStep >= MAX_STEPS || robots.every(r => !r.alive);

    this.state = {
      ...this.state,
      robots,
      step: nextStep,
      done,
      collisions: this.state.collisions + newCollisions,
      goalsReached: this.state.goalsReached + newGoals,
    };

    this._emit();
    return { state: this.state, events: { newCollisions, newGoals } };
  }

  setSpeed(speed: number) {
    this.state = { ...this.state, speed };
    this._emit();
  }

  setMLMode(enabled: boolean) {
    this.state = { ...this.state, mlMode: enabled };
    this._emit();
  }

  getState(): SimState { return this.state; }

  private _emit() {
    this.dispatchEvent(new CustomEvent('update', { detail: this.state }));
  }
}

export const globalEngine = new SimulationEngine();
