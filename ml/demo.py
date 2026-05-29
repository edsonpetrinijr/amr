"""
demo.py — visual demo agent for BehaveX Electron app.

Connects via WebSocket, runs a simple heuristic (move toward target),
prints live feedback. No training — just watch the robots move.

Usage:
    1. npm run dev  (start Electron app)
    2. Click "ENABLE ML MODE" in the experiment page
    3. python ml/demo.py
"""

import json
import time
import math
import numpy as np
import websocket

WS_URL = "ws://localhost:8765"
NUM_ROBOTS = 50
NUM_EPISODES = 20
STEP_DELAY = 0.05   # seconds between steps — increase to slow down


def call(ws, msg):
    ws.send(json.dumps(msg))
    return json.loads(ws.recv())


def heuristic_actions(obs: np.ndarray) -> list[int]:
    """
    Each robot moves toward the target using 8-direction discrete actions.
    obs layout (per robot, 7 floats): x, y, vx, vy, alive, dx_target, dy_target
    """
    # Direction lookup: action → (dx, dy)
    DIRS = [
        (0, 0),   # 0 idle
        (0, -1),  # 1 N
        (0, 1),   # 2 S
        (1, 0),   # 3 E
        (-1, 0),  # 4 W
        (1, -1),  # 5 NE
        (-1, -1), # 6 NW
        (1, 1),   # 7 SE
        (-1, 1),  # 8 SW
    ]

    actions = []
    for i in range(NUM_ROBOTS):
        base = i * 7
        alive = obs[base + 4]
        if not alive:
            actions.append(0)
            continue
        dx = obs[base + 5]  # (target.x - robot.x) / 100
        dy = obs[base + 6]  # (target.y - robot.y) / 100

        # Pick direction closest to vector toward target
        best_action = 0
        best_dot = -999
        for a, (ddx, ddy) in enumerate(DIRS):
            dot = ddx * dx + ddy * dy
            if dot > best_dot:
                best_dot = dot
                best_action = a
        actions.append(best_action)
    return actions


def run_demo():
    print(f"Connecting to {WS_URL}...")
    ws = websocket.create_connection(WS_URL, timeout=10)

    info = call(ws, {"type": "ping"})
    print(f"Connected: obsSize={info['obsSize']} actionSize={info['actionSize']} robots={info['numRobots']}")

    call(ws, {"type": "setMLMode", "enabled": True})
    print("ML mode enabled — you should see the badge in the app\n")

    for ep in range(1, NUM_EPISODES + 1):
        resp = call(ws, {"type": "reset", "seed": ep * 100})
        obs = np.array(resp["observation"], dtype=np.float32)

        total_reward = 0.0
        step = 0

        print(f"── Episode {ep}/{NUM_EPISODES} ──────────────────────")

        while True:
            actions = heuristic_actions(obs)
            resp = call(ws, {"type": "step", "actions": actions})

            obs = np.array(resp["observation"], dtype=np.float32)
            reward = resp["reward"]
            done = resp["done"]
            ep_info = resp.get("info", {})

            total_reward += reward
            step += 1

            alive = ep_info.get("aliveCount", "?")
            goals = ep_info.get("goalsReached", "?")
            collisions = ep_info.get("collisions", "?")

            print(
                f"  step={step:3d}  alive={alive:2}  goals={goals}  "
                f"collisions={collisions}  reward={reward:+.2f}  total={total_reward:.1f}",
                end="\r",
                flush=True,
            )

            time.sleep(STEP_DELAY)

            if done:
                print()
                print(f"  Done! total_reward={total_reward:.1f}  goals={goals}  collisions={collisions}")
                alive_count = ep_info.get("aliveCount", 0)
                call(ws, {
                    "type": "metrics",
                    "episode": ep,
                    "totalReward": round(total_reward, 2),
                    "goals": int(goals) if isinstance(goals, (int, float)) else 0,
                    "collisions": int(collisions) if isinstance(collisions, (int, float)) else 0,
                    "steps": step,
                    "aliveAtEnd": int(alive_count),
                })
                break

        time.sleep(0.5)

    call(ws, {"type": "setMLMode", "enabled": False})
    ws.close()
    print("\nML mode disabled. Demo complete.")


if __name__ == "__main__":
    run_demo()
