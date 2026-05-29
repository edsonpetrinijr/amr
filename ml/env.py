"""
BehaveXEnv — Gym-compatible wrapper over the Electron simulation via WebSocket.

Protocol: JSON over WebSocket at ws://localhost:8765
Actions: list of 12 integers (0–8), one per robot
Observation: flat float32 array of length 87
"""

import json
import numpy as np
import websocket  # pip install websocket-client
from typing import Optional, Tuple, Dict, Any

ACTION_SIZE = 9   # per-robot discrete
WS_URL = "ws://localhost:8765"

# Module-level defaults (overridden by sim config on connect)
OBS_SIZE = 87
NUM_ROBOTS = 12


class BehaveXEnv:
    """
    Gym-like environment for the BehaveX swarm simulation.

    Action space:  MultiDiscrete([9] * 12)  — one direction per robot
    Observation:   Box(shape=(87,), dtype=float32)

    Direction encoding per robot:
        0 idle, 1 N, 2 S, 3 E, 4 W, 5 NE, 6 NW, 7 SE, 8 SW
    """

    def __init__(self, url: str = WS_URL, timeout: float = 10.0):
        self.url = url
        self.timeout = timeout
        self._ws: Optional[websocket.WebSocket] = None
        self.num_robots: int = NUM_ROBOTS
        self.obs_size:   int = OBS_SIZE
        self._connect()

    def _connect(self):
        self._ws = websocket.create_connection(self.url, timeout=self.timeout)
        info = self._call({"type": "ping"})
        assert info.get("pong"), f"Unexpected handshake: {info}"
        self.num_robots = int(info.get("numRobots", NUM_ROBOTS))
        self.obs_size   = int(info.get("obsSize",   self.num_robots * 7 + 3))
        self._call({"type": "setMLMode", "enabled": True})

    def _call(self, msg: dict) -> dict:
        assert self._ws is not None, "Not connected"
        self._ws.send(json.dumps(msg))
        return json.loads(self._ws.recv())

    def reset(self, seed: Optional[int] = None) -> np.ndarray:
        msg: dict = {"type": "reset"}
        if seed is not None:
            msg["seed"] = seed
        resp = self._call(msg)
        return np.array(resp["observation"], dtype=np.float32)

    def step(self, actions: list) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        actions: list of 12 ints (RobotAction per robot)
        returns: (observation, reward, done, info)
        """
        assert len(actions) == self.num_robots, f"Need {self.num_robots} actions, got {len(actions)}"
        actions = [int(a) for a in actions]
        resp = self._call({"type": "step", "actions": actions})
        obs = np.array(resp["observation"], dtype=np.float32)
        reward = float(resp["reward"])
        done = bool(resp["done"])
        info = resp.get("info", {})
        return obs, reward, done, info

    def get_state(self) -> dict:
        return self._call({"type": "getState"})

    def send_metrics(self, episode: int, total_reward: float, info: dict):
        self._call({
            "type": "metrics",
            "episode": episode,
            "totalReward": round(total_reward, 2),
            "goals": int(info.get("goalsReached", 0)),
            "collisions": int(info.get("collisions", 0)),
            "steps": int(info.get("step", 0)),
            "aliveAtEnd": int(info.get("aliveCount", 0)),
        })

    def close(self):
        if self._ws:
            self._call({"type": "setMLMode", "enabled": False})
            self._ws.close()
            self._ws = None

    # Gym compatibility stubs
    @property
    def observation_space(self):
        return _Box(low=0.0, high=1.0, shape=(self.obs_size,))

    @property
    def action_space(self):
        return _MultiDiscrete([ACTION_SIZE] * self.num_robots)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# Minimal space stubs (avoids hard gym dependency)
class _Box:
    def __init__(self, low, high, shape):
        self.low = low
        self.high = high
        self.shape = shape
        self.dtype = np.float32

    def sample(self):
        return np.random.uniform(self.low, self.high, self.shape).astype(self.dtype)


class _MultiDiscrete:
    def __init__(self, nvec):
        self.nvec = nvec
        self.n = len(nvec)

    def sample(self):
        return [np.random.randint(0, n) for n in self.nvec]
