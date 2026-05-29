"""
PPO training loop for BehaveXEnv.

Dependencies:
    pip install websocket-client torch numpy

Usage:
    1. Start the Electron app (npm run electron:dev)
    2. python ml/train_ppo.py
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from env import BehaveXEnv, OBS_SIZE, ACTION_SIZE, NUM_ROBOTS

# ── Hyperparameters ────────────────────────────────────────────────────────────
LR = 3e-4
GAMMA = 0.99
GAE_LAMBDA = 0.95
CLIP_EPS = 0.2
ENTROPY_COEF = 0.01
VALUE_COEF = 0.5
MAX_GRAD_NORM = 0.5

ROLLOUT_STEPS = 512    # steps per rollout before each update
UPDATE_EPOCHS = 4
MINIBATCH_SIZE = 64
TOTAL_STEPS = 1_000_000
LOG_INTERVAL = 10       # episodes


# ── Network ────────────────────────────────────────────────────────────────────

class ActorCritic(nn.Module):
    """Shared trunk, separate actor/critic heads.

    Actor: OBS_SIZE → 256 → 128 → NUM_ROBOTS * ACTION_SIZE  (logits)
    Critic: same trunk → scalar value
    """
    def __init__(self):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(OBS_SIZE, 256),
            nn.Tanh(),
            nn.Linear(256, 128),
            nn.Tanh(),
        )
        self.actor = nn.Linear(128, NUM_ROBOTS * ACTION_SIZE)
        self.critic = nn.Linear(128, 1)

    def forward(self, x: torch.Tensor):
        h = self.trunk(x)
        logits = self.actor(h).view(-1, NUM_ROBOTS, ACTION_SIZE)
        value = self.critic(h).squeeze(-1)
        return logits, value

    def act(self, obs: np.ndarray):
        """Sample actions + return log_probs and value (numpy in, numpy out)."""
        with torch.no_grad():
            x = torch.FloatTensor(obs).unsqueeze(0)
            logits, value = self(x)
            dist = torch.distributions.Categorical(logits=logits)
            actions = dist.sample()                           # (1, NUM_ROBOTS)
            log_probs = dist.log_prob(actions).sum(-1)        # (1,)
        return (
            actions.squeeze(0).numpy().tolist(),
            log_probs.squeeze(0).item(),
            value.squeeze(0).item(),
        )

    def evaluate(self, obs: torch.Tensor, actions: torch.Tensor):
        """Forward pass for PPO update (batched)."""
        logits, value = self(obs)
        dist = torch.distributions.Categorical(logits=logits)
        log_probs = dist.log_prob(actions).sum(-1)
        entropy = dist.entropy().sum(-1)
        return log_probs, value, entropy


# ── PPO Update ─────────────────────────────────────────────────────────────────

def ppo_update(model, optimizer, rollout):
    obs_t    = torch.FloatTensor(np.array(rollout["obs"]))
    act_t    = torch.LongTensor(np.array(rollout["actions"]))      # (T, NUM_ROBOTS)
    old_lp_t = torch.FloatTensor(np.array(rollout["log_probs"]))   # (T,)
    ret_t    = torch.FloatTensor(np.array(rollout["returns"]))      # (T,)
    adv_t    = torch.FloatTensor(np.array(rollout["advantages"]))   # (T,)
    adv_t    = (adv_t - adv_t.mean()) / (adv_t.std() + 1e-8)

    T = obs_t.shape[0]
    indices = np.arange(T)

    for _ in range(UPDATE_EPOCHS):
        np.random.shuffle(indices)
        for start in range(0, T, MINIBATCH_SIZE):
            mb = indices[start:start + MINIBATCH_SIZE]
            log_probs, values, entropy = model.evaluate(obs_t[mb], act_t[mb])
            ratio = torch.exp(log_probs - old_lp_t[mb])

            pg_loss1 = -adv_t[mb] * ratio
            pg_loss2 = -adv_t[mb] * torch.clamp(ratio, 1 - CLIP_EPS, 1 + CLIP_EPS)
            pg_loss  = torch.max(pg_loss1, pg_loss2).mean()
            v_loss   = 0.5 * (values - ret_t[mb]).pow(2).mean()
            loss     = pg_loss + VALUE_COEF * v_loss - ENTROPY_COEF * entropy.mean()

            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
            optimizer.step()


# ── GAE ────────────────────────────────────────────────────────────────────────

def compute_gae(rewards, values, dones, last_value):
    advantages = []
    gae = 0.0
    for t in reversed(range(len(rewards))):
        next_val = last_value if t == len(rewards) - 1 else values[t + 1]
        delta = rewards[t] + GAMMA * next_val * (1 - dones[t]) - values[t]
        gae = delta + GAMMA * GAE_LAMBDA * (1 - dones[t]) * gae
        advantages.insert(0, gae)
    returns = [a + v for a, v in zip(advantages, values)]
    return advantages, returns


# ── Training loop ──────────────────────────────────────────────────────────────

def train():
    model = ActorCritic()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    recent_rewards = deque(maxlen=LOG_INTERVAL)
    global_step = 0
    episode = 0

    with BehaveXEnv() as env:
        obs = env.reset(seed=42)

        rollout = {k: [] for k in ("obs", "actions", "log_probs", "rewards", "values", "dones")}
        ep_reward = 0.0

        while global_step < TOTAL_STEPS:
            # ── Collect rollout ───────────────────────────────────────────
            for _ in range(ROLLOUT_STEPS):
                actions, log_prob, value = model.act(obs)
                next_obs, reward, done, info = env.step(actions)

                rollout["obs"].append(obs)
                rollout["actions"].append(actions)
                rollout["log_probs"].append(log_prob)
                rollout["rewards"].append(reward)
                rollout["values"].append(value)
                rollout["dones"].append(float(done))

                ep_reward += reward
                obs = next_obs
                global_step += 1

                if done:
                    episode += 1
                    recent_rewards.append(ep_reward)
                    ep_reward_just_ended = ep_reward
                    ep_reward = 0.0
                    obs = env.reset()

                    # Push metrics to Training Dashboard
                    env.send_metrics(episode, ep_reward_just_ended, info)

                    if episode % LOG_INTERVAL == 0:
                        mean_r = np.mean(recent_rewards)
                        print(
                            f"ep={episode:6d}  "
                            f"step={global_step:8d}  "
                            f"mean_reward={mean_r:8.2f}  "
                            f"collisions={info.get('collisions', 0)}  "
                            f"goals={info.get('goalsReached', 0)}"
                        )

            # ── PPO update ────────────────────────────────────────────────
            _, _, last_value = model.act(obs)
            rollout["advantages"], rollout["returns"] = compute_gae(
                rollout["rewards"], rollout["values"], rollout["dones"], last_value
            )
            ppo_update(model, optimizer, rollout)
            rollout = {k: [] for k in rollout}  # clear

    torch.save(model.state_dict(), "ml/behavex_ppo.pt")
    print("Training complete. Model saved to ml/behavex_ppo.pt")


if __name__ == "__main__":
    train()
