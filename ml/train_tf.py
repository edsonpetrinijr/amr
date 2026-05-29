"""
PPO training with TensorFlow Metal (M4 GPU) + multiprocessing CPU workers.

Stack:
  - tensorflow-macos + tensorflow-metal  → GPU via Metal (M4 GPU cores + Neural Engine)
  - tf.function JIT                       → compiled graph ops on Metal
  - multiprocessing.Pool                  → parallel GAE on CPU cores
  - tf.data.Dataset                       → prefetch minibatches async

M4 Air: 8 CPU cores, 10 GPU cores, 16-core Neural Engine
CPU workers handle data prep; Metal GPU handles all NN forward/backward.

Usage:
    pip install -r requirements_tf.txt
    python ml/train_tf.py
"""

import os
import time
import numpy as np
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from functools import partial

# macOS: fork after Metal init corrupts GPU context — must use spawn
if mp.get_start_method(allow_none=True) != "spawn":
    mp.set_start_method("spawn", force=True)

# Suppress TF spam before import
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_METAL_DEVICE_PLACEMENT_LOG", "0")

import tensorflow as tf
from env import BehaveXEnv, ACTION_SIZE

# ── Hardware detection ─────────────────────────────────────────────────────────

def setup_metal():
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"[metal] {len(gpus)} Metal GPU(s) found: {[g.name for g in gpus]}")
    else:
        print("[metal] No Metal GPU found — running on CPU")

    cpus = mp.cpu_count()
    print(f"[cpu]   {cpus} CPU cores available")
    tf.config.threading.set_inter_op_parallelism_threads(cpus)
    tf.config.threading.set_intra_op_parallelism_threads(cpus)
    return len(gpus) > 0

# ── Hyperparameters ────────────────────────────────────────────────────────────

LR              = 3e-4
GAMMA           = 0.99
GAE_LAMBDA      = 0.95
CLIP_EPS        = 0.2
ENTROPY_COEF    = 0.01
VALUE_COEF      = 0.5
MAX_GRAD_NORM   = 0.5

# Bigger rollout + batch to saturate M4 GPU
ROLLOUT_STEPS   = 2048
UPDATE_EPOCHS   = 6
MINIBATCH_SIZE  = 256
TOTAL_STEPS     = 2_000_000
LOG_INTERVAL    = 10

# CPU workers for parallel GAE (leave 2 cores for main + env)
N_GAE_WORKERS   = max(1, mp.cpu_count() - 2)

# ── Actor-Critic (Keras) ───────────────────────────────────────────────────────

def build_actor_critic(obs_size: int, num_robots: int):
    """Shared trunk → actor head (logits) + critic head (value)."""
    obs_in = tf.keras.Input(shape=(obs_size,), name="obs", dtype=tf.float32)

    h = tf.keras.layers.Dense(512, activation="tanh", name="trunk_1")(obs_in)
    h = tf.keras.layers.Dense(256, activation="tanh", name="trunk_2")(h)
    h = tf.keras.layers.Dense(128, activation="tanh", name="trunk_3")(h)

    logits = tf.keras.layers.Dense(
        num_robots * ACTION_SIZE, name="actor_logits"
    )(h)
    logits = tf.keras.layers.Reshape((num_robots, ACTION_SIZE), name="logits_reshape")(logits)

    # Critic: scalar value
    value = tf.keras.layers.Dense(1, name="critic_value")(h)
    value = tf.keras.layers.Reshape((), name="value_reshape")(value)

    return tf.keras.Model(inputs=obs_in, outputs=[logits, value], name="ActorCritic")


# ── PPO policy (tf.function → compiled on Metal) ───────────────────────────────

class PPOPolicy:
    def __init__(self, obs_size: int, num_robots: int):
        self.num_robots = num_robots
        self.model = build_actor_critic(obs_size, num_robots)
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=LR, epsilon=1e-5)
        print(self.model.summary())

    def act(self, obs_np: np.ndarray):
        """numpy in → (actions list, log_prob float, value float). No gradients."""
        obs = tf.constant(obs_np[None], dtype=tf.float32)          # (1, OBS)
        logits, value = self.model(obs, training=False)             # (1,R,A), (1,)

        # Sample one action per robot: reshape to (R, 1, A), categorical, squeeze
        logits_per_robot = tf.transpose(logits[0], [0, 1])         # (R, A)
        sampled = tf.cast(
            tf.squeeze(
                tf.random.categorical(logits_per_robot, 1),         # (R, 1)
                axis=1,
            ),
            tf.int32,
        )                                                           # (R,)
        actions_np = sampled.numpy().tolist()

        # log_prob for the sampled actions
        actions_t = sampled[None]                                   # (1, R)
        log_prob  = _log_prob(logits, actions_t)                    # (1,)
        return actions_np, float(log_prob[0].numpy()), float(value[0].numpy())

    @tf.function(jit_compile=True)
    def train_step(self, obs_b, act_b, old_lp_b, ret_b, adv_b):
        """One PPO minibatch update. jit_compile → XLA on Metal."""
        with tf.GradientTape() as tape:
            logits, values = self.model(obs_b, training=True)

            # New log probs
            log_probs = _log_prob(logits, act_b)                       # (B,)
            entropy   = _entropy(logits)                               # (B,)

            ratio = tf.exp(log_probs - old_lp_b)
            adv_norm = (adv_b - tf.reduce_mean(adv_b)) / (tf.math.reduce_std(adv_b) + 1e-8)

            pg1 = -adv_norm * ratio
            pg2 = -adv_norm * tf.clip_by_value(ratio, 1 - CLIP_EPS, 1 + CLIP_EPS)
            pg_loss = tf.reduce_mean(tf.maximum(pg1, pg2))
            v_loss  = 0.5 * tf.reduce_mean(tf.square(values - ret_b))
            loss    = pg_loss + VALUE_COEF * v_loss - ENTROPY_COEF * tf.reduce_mean(entropy)

        grads = tape.gradient(loss, self.model.trainable_variables)
        grads, _ = tf.clip_by_global_norm(grads, MAX_GRAD_NORM)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))
        return loss, pg_loss, v_loss

    def save(self, path: str):
        self.model.save_weights(path)
        print(f"[save] weights → {path}")

    def load(self, path: str):
        self.model.load_weights(path)
        print(f"[load] weights ← {path}")


# ── Helpers (outside tf.function so they stay pure) ───────────────────────────

def _log_prob(logits, actions):
    """logits: (B, NUM_ROBOTS, ACTION_SIZE), actions: (B, NUM_ROBOTS) → (B,)"""
    dist = tf.keras.backend  # unused, manual below
    log_softmax = tf.nn.log_softmax(logits, axis=-1)               # (B, R, A)
    one_hot = tf.one_hot(actions, ACTION_SIZE, dtype=tf.float32)   # (B, R, A)
    per_robot = tf.reduce_sum(log_softmax * one_hot, axis=-1)      # (B, R)
    return tf.reduce_sum(per_robot, axis=-1)                       # (B,)


def _entropy(logits):
    """logits: (B, NUM_ROBOTS, ACTION_SIZE) → (B,)"""
    probs = tf.nn.softmax(logits, axis=-1)
    log_p = tf.nn.log_softmax(logits, axis=-1)
    per_robot = -tf.reduce_sum(probs * log_p, axis=-1)             # (B, R)
    return tf.reduce_sum(per_robot, axis=-1)                       # (B,)


# ── GAE — runs in worker processes (CPU parallel) ──────────────────────────────

def _gae_chunk(args):
    """Compute GAE for a contiguous chunk. Called in Pool workers."""
    rewards, values, dones, last_val, gamma, lam = args
    T = len(rewards)
    advantages = np.zeros(T, dtype=np.float32)
    gae = 0.0
    for t in reversed(range(T)):
        nxt = last_val if t == T - 1 else values[t + 1]
        delta = rewards[t] + gamma * nxt * (1.0 - dones[t]) - values[t]
        gae = delta + gamma * lam * (1.0 - dones[t]) * gae
        advantages[t] = gae
    returns = advantages + np.array(values, dtype=np.float32)
    return advantages, returns


def compute_gae_parallel(rewards, values, dones, last_value, pool: mp.Pool):
    """Split rollout across CPU workers, compute GAE in parallel, merge."""
    T = len(rewards)
    chunk = max(1, T // N_GAE_WORKERS)
    chunks = []
    for start in range(0, T, chunk):
        end = min(start + chunk, T)
        lv = values[end] if end < T else last_value
        chunks.append((
            rewards[start:end],
            values[start:end],
            dones[start:end],
            lv, GAMMA, GAE_LAMBDA,
        ))

    results = pool.map(_gae_chunk, chunks)
    advantages = np.concatenate([r[0] for r in results])
    returns    = np.concatenate([r[1] for r in results])
    return advantages, returns


# ── tf.data pipeline ──────────────────────────────────────────────────────────

def make_dataset(obs, actions, old_lps, returns, advantages):
    ds = tf.data.Dataset.from_tensor_slices({
        "obs":    tf.constant(obs,      dtype=tf.float32),
        "act":    tf.constant(actions,  dtype=tf.int32),
        "old_lp": tf.constant(old_lps,  dtype=tf.float32),
        "ret":    tf.constant(returns,  dtype=tf.float32),
        "adv":    tf.constant(advantages, dtype=tf.float32),
    })
    return (
        ds
        .shuffle(len(obs))
        .batch(MINIBATCH_SIZE, drop_remainder=True)
        .prefetch(tf.data.AUTOTUNE)   # async prefetch on CPU while GPU trains
    )


# ── Training loop ──────────────────────────────────────────────────────────────

def train():
    has_gpu = setup_metal()

    # Connect to sim first — reads numRobots/obsSize from current UI config
    env = BehaveXEnv()
    num_robots = env.num_robots
    obs_size   = env.obs_size
    print(f"[env]   numRobots={num_robots}  obsSize={obs_size}")

    policy = PPOPolicy(obs_size, num_robots)

    checkpoint_path = "ml/behavex_tf.weights.h5"
    if os.path.exists(checkpoint_path):
        policy.load(checkpoint_path)

    pool = mp.Pool(processes=N_GAE_WORKERS, maxtasksperchild=100)
    print(f"[pool]  {N_GAE_WORKERS} GAE workers spawned")

    recent_rewards = deque(maxlen=LOG_INTERVAL)
    global_step = episode = 0
    t_start = time.time()

    with env:
        obs = env.reset(seed=42)

        buf_obs      = []
        buf_actions  = []
        buf_log_probs= []
        buf_rewards  = []
        buf_values   = []
        buf_dones    = []
        ep_reward    = 0.0

        while global_step < TOTAL_STEPS:
            # ── Collect rollout ──────────────────────────────────────────
            for _ in range(ROLLOUT_STEPS):
                actions, log_prob, value = policy.act(obs)
                next_obs, reward, done, info = env.step(actions)

                buf_obs.append(obs)
                buf_actions.append(actions)
                buf_log_probs.append(log_prob)
                buf_rewards.append(reward)
                buf_values.append(value)
                buf_dones.append(float(done))

                ep_reward  += reward
                obs         = next_obs
                global_step += 1

                if done:
                    episode += 1
                    recent_rewards.append(ep_reward)
                    env.send_metrics(episode, ep_reward, info)

                    if episode % LOG_INTERVAL == 0:
                        elapsed = time.time() - t_start
                        sps = global_step / elapsed
                        mean_r = float(np.mean(recent_rewards))
                        print(
                            f"ep={episode:6d}  step={global_step:9d}  "
                            f"sps={sps:6.0f}  mean_r={mean_r:8.2f}  "
                            f"goals={info.get('goalsReached',0)}  "
                            f"col={info.get('collisions',0)}"
                        )

                    ep_reward = 0.0
                    obs = env.reset()

            # ── Parallel GAE on CPU cores ────────────────────────────────
            _, _, last_value = policy.act(obs)
            advantages, returns = compute_gae_parallel(
                buf_rewards, buf_values, buf_dones, last_value, pool
            )

            # ── PPO update on Metal GPU ──────────────────────────────────
            ds = make_dataset(
                np.array(buf_obs,       dtype=np.float32),
                np.array(buf_actions,   dtype=np.int32),
                np.array(buf_log_probs, dtype=np.float32),
                returns,
                advantages,
            )

            total_loss = 0.0
            n_updates  = 0
            for _ in range(UPDATE_EPOCHS):
                for batch in ds:
                    loss, _, _ = policy.train_step(
                        batch["obs"],
                        batch["act"],
                        batch["old_lp"],
                        batch["ret"],
                        batch["adv"],
                    )
                    total_loss += float(loss)
                    n_updates  += 1

            print(f"  [update] avg_loss={total_loss/max(1,n_updates):.4f}  batches={n_updates}")

            # Save checkpoint every rollout
            policy.save(checkpoint_path)

            # Clear buffers
            buf_obs.clear(); buf_actions.clear(); buf_log_probs.clear()
            buf_rewards.clear(); buf_values.clear(); buf_dones.clear()

    pool.close()
    pool.join()
    print("Training complete.")


if __name__ == "__main__":
    train()
