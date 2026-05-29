export interface RewardConfig {
  frameAlive: number;        // reward per robot per step alive
  collision: number;         // penalty per collision event
  goalReached: number;       // reward per robot reaching target
  distanceBonus: number;     // coefficient: reward += coeff * (prevDist - newDist)
  episodeCompletionBonus: number; // bonus when all robots finish (goal or collision)
}

export const DEFAULT_REWARD_CONFIG: RewardConfig = {
  frameAlive: 0.1,
  collision: -10,
  goalReached: 100,
  distanceBonus: 1.0,
  episodeCompletionBonus: 0,
};
