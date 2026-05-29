// React hook — subscribes to globalEngine events, returns UI-friendly state.
// Drop-in replacement for the inline useState/useEffect pattern in ExperimentDetail.

import { useState, useEffect, useCallback } from 'react';
import { globalEngine, SimState } from './SimulationEngine';

export function useSimEngine() {
  const [simState, setSimState] = useState<SimState>(() => globalEngine.getState());
  const [isPlaying, setIsPlaying] = useState(false);

  // Mirror engine state into React on every engine update
  useEffect(() => {
    const onUpdate = (e: Event) => {
      setSimState((e as CustomEvent<SimState>).detail);
    };
    globalEngine.addEventListener('update', onUpdate);
    return () => globalEngine.removeEventListener('update', onUpdate);
  }, []);

  // UI-driven game loop — disabled when mlMode is active
  useEffect(() => {
    if (!isPlaying || simState.mlMode) return;

    const interval = setInterval(() => {
      const { state } = globalEngine.advance();
      if (state.done) setIsPlaying(false);
    }, 50 / simState.speed);

    return () => clearInterval(interval);
  }, [isPlaying, simState.speed, simState.mlMode]);

  const togglePlay = useCallback(() => {
    if (simState.done) globalEngine.reset();
    setIsPlaying(p => !p);
  }, [simState.done]);

  const resetSim = useCallback(() => {
    setIsPlaying(false);
    globalEngine.reset();
  }, []);

  const setSpeed = useCallback((speed: number) => {
    globalEngine.setSpeed(speed);
  }, []);

  const seekStep = useCallback((_step: number) => {
    // Seek not supported in live engine
  }, []);

  const setMLMode = useCallback((enabled: boolean) => {
    globalEngine.setMLMode(enabled);
    if (!enabled) setIsPlaying(false);
  }, []);

  const setObstacle = useCallback((index: number, patch: Partial<import('./SimulationEngine').ObstacleState>) => {
    globalEngine.setObstacle(index, patch);
  }, []);

  const setTarget = useCallback((patch: Partial<{ x: number; y: number; radius: number }>) => {
    globalEngine.setTarget(patch);
  }, []);

  const setSpawnArea = useCallback((patch: Partial<import('./SimulationEngine').SpawnArea>) => {
    globalEngine.setSpawnArea(patch);
  }, []);

  const setNumRobots = useCallback((n: number) => {
    globalEngine.setNumRobots(n);
  }, []);

  return {
    robots: simState.robots,
    step: simState.step,
    maxSteps: simState.maxSteps,
    speed: simState.speed,
    isPlaying,
    mlMode: simState.mlMode,
    collisions: simState.collisions,
    goalsReached: simState.goalsReached,
    done: simState.done,
    obstacles: simState.obstacles,
    target: simState.target,
    spawnArea: simState.spawnArea,
    numRobots: simState.numRobots,
    togglePlay,
    resetSim,
    setSpeed,
    seekStep,
    setMLMode,
    setObstacle,
    setTarget,
    setSpawnArea,
    setNumRobots,
  };
}
