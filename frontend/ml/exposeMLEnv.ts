// Runs in renderer process. Exposes window.__ML_ENV and window.__METRICS
// for executeJavaScript calls from Electron main (ws-bridge).

import { mlEnv } from './MLEnv';
import { globalEngine, SwarmAction } from './SimulationEngine';
import { metricsStore, EpisodeMetrics } from './metricsStore';

declare global {
  interface Window {
    __ML_ENV: typeof ML_ENV_API;
    __METRICS: { push: (m: EpisodeMetrics) => void; clear: () => void };
  }
}

const ML_ENV_API = {
  reset(seed?: number) {
    return mlEnv.reset(seed);
  },

  step(actions: SwarmAction) {
    return mlEnv.step(actions);
  },

  getState() {
    return globalEngine.getState();
  },

  getObservation() {
    const state = globalEngine.getState();
    const { target, robots, step, maxSteps, collisions, goalsReached } = state;
    const obs: number[] = [];
    for (const r of robots) {
      obs.push(r.x / 100, r.y / 100, r.vx, r.vy, r.alive ? 1 : 0,
        (target.x - r.x) / 100, (target.y - r.y) / 100);
    }
    obs.push(step / maxSteps, collisions / robots.length, goalsReached / robots.length);
    return obs;
  },

  isDone() {
    return globalEngine.getState().done;
  },

  setMLMode(enabled: boolean) {
    globalEngine.setMLMode(enabled);
  },

  getConfig() {
    const n = globalEngine.getState().numRobots;
    return { numRobots: n, obsSize: n * 7 + 3, actionSize: 9 };
  },

  get obsSize() { return globalEngine.getState().numRobots * 7 + 3; },
  get actionSize() { return 9; },
  get numRobots() { return globalEngine.getState().numRobots; },
};

window.__ML_ENV = ML_ENV_API;
window.__METRICS = metricsStore;

export {};
