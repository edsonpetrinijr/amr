// Gym-like wrapper around SimulationEngine.
// Handles observation flattening, reward computation, episode lifecycle.

import { globalEngine, SimState, SwarmAction } from './SimulationEngine';
import { RewardConfig, DEFAULT_REWARD_CONFIG } from './RewardConfig';

export interface StepResult {
  observation: number[];
  reward: number;
  done: boolean;
  info: {
    step: number;
    collisions: number;
    goalsReached: number;
    aliveCount: number;
  };
}

// Flat observation vector per step:
//   Per robot (12 × 7): x/100, y/100, vx, vy, alive, dx_target/100, dy_target/100
//   Global (3): step/maxSteps, collisions/12, goalsReached/12
// Total: 12*7 + 3 = 87 features
function flattenObservation(state: SimState): number[] {
  const obs: number[] = [];
  const { target, robots, step, maxSteps, collisions, goalsReached } = state;

  for (const r of robots) {
    obs.push(
      r.x / 100,
      r.y / 100,
      r.vx,
      r.vy,
      r.alive ? 1 : 0,
      (target.x - r.x) / 100,
      (target.y - r.y) / 100,
    );
  }

  obs.push(
    step / maxSteps,
    collisions / robots.length,
    goalsReached / robots.length,
  );

  return obs;
}

function computeReward(
  prevState: SimState,
  newState: SimState,
  newCollisions: number,
  newGoals: number,
  config: RewardConfig,
): number {
  let reward = 0;

  // Frame-alive bonus for each still-alive robot
  const aliveCount = newState.robots.filter(r => r.alive).length;
  reward += aliveCount * config.frameAlive;

  // Collision penalty
  reward += newCollisions * config.collision;

  // Goal reward
  reward += newGoals * config.goalReached;

  // Distance-improvement bonus
  if (config.distanceBonus !== 0) {
    const { target } = newState;
    for (let i = 0; i < prevState.robots.length; i++) {
      const prev = prevState.robots[i];
      const next = newState.robots[i];
      if (!prev.alive) continue;
      const prevDist = Math.sqrt((prev.x - target.x) ** 2 + (prev.y - target.y) ** 2);
      const nextDist = Math.sqrt((next.x - target.x) ** 2 + (next.y - target.y) ** 2);
      reward += config.distanceBonus * (prevDist - nextDist);
    }
  }

  // Episode completion bonus
  if (newState.done && config.episodeCompletionBonus !== 0) {
    reward += config.episodeCompletionBonus;
  }

  return reward;
}

export class MLEnv {
  private config: RewardConfig;
  private prevState: SimState;

  static readonly ACTION_SIZE = 9;

  constructor(config: Partial<RewardConfig> = {}) {
    this.config = { ...DEFAULT_REWARD_CONFIG, ...config };
    this.prevState = globalEngine.getState();
  }

  reset(seed?: number): number[] {
    const state = globalEngine.reset(seed);
    globalEngine.setMLMode(true);
    this.prevState = state;
    return flattenObservation(state);
  }

  step(actions: SwarmAction): StepResult {
    const prevState = this.prevState;
    const { state, events } = globalEngine.advance(actions);

    const reward = computeReward(
      prevState,
      state,
      events.newCollisions,
      events.newGoals,
      this.config,
    );

    this.prevState = state;

    return {
      observation: flattenObservation(state),
      reward,
      done: state.done,
      info: {
        step: state.step,
        collisions: state.collisions,
        goalsReached: state.goalsReached,
        aliveCount: state.robots.filter(r => r.alive).length,
      },
    };
  }

  getState(): SimState { return globalEngine.getState(); }
  isDone(): boolean { return globalEngine.getState().done; }

  setRewardConfig(config: Partial<RewardConfig>) {
    this.config = { ...this.config, ...config };
  }
}

export const mlEnv = new MLEnv();
