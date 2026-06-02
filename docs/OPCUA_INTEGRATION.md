# OPC UA Call-Button Integration — Plant Cutover Guide

For the **plant / automation engineer** who owns the OPC UA / PLC server.
Our AMR fleet backend subscribes to your boolean call-button nodes and dispatches
an AMR when a button is pressed. This is what we need from you and how we validate
it on-site.

---

## 1. What we need from you (fill this in)

| Item | Example | Your value |
|------|---------|------------|
| **Endpoint URL** | `opc.tcp://10.0.0.5:4840/fleet` | `opc.tcp://________:____/____` |
| **Security policy** | `None` / `Basic256Sha256` | |
| **Message security mode** | `None` / `Sign` / `SignAndEncrypt` | |
| **Auth** | Anonymous / Username+Password / Certificate | |
| → Username / Password (if any) | | (send via secure channel, **not** email) |
| → Server cert + our client cert/key (if Sign/Encrypt) | `.der` / `.pem` files | |
| **Namespace index + URI** | `ns=2`, `urn:plc:callbuttons` | |

> Today our driver connects **anonymous, security `None`**. If you require
> Sign/Encrypt or credentials, tell us — it's a small driver change but we need
> the certs/creds first. Don't expose a security-`None` endpoint on a routable
> network; keep it on the isolated AMR VLAN.

### Per-button node list

One row per physical call button. The **node id** must be the exact OPC UA
address (namespace index + identifier). Each node must be a **Boolean** that is
**True while/for the press** and returns to **False** when released.

| Button (physical) | OPC UA node id | Boolean semantics | Our station id | Direction |
|-------------------|----------------|-------------------|----------------|-----------|
| Almox doca 1 | `ns=2;s=CallButton.AP1_call` | True=pressed | `AP1` | `fwd` |
| Linha A posto 1 | `ns=2;s=CallButton.CB1_call` | True=pressed | `CB1` | `fwd` |
| … | | | | |

**Boolean semantics we rely on:**
- We trigger on the **rising edge** (False → True). A held True does **not**
  re-trigger; the node must go back to False before the next press counts.
- A momentary pulse is fine as long as it stays True long enough for one
  subscription publish (≥ a few hundred ms; our default publish period is 200 ms).
- We **debounce** repeat rising edges within `OPCUA_DEBOUNCE_S` (default 1.0 s) to
  absorb contact bounce — make sure two *intentional* presses are ≥ ~1.5 s apart,
  or tell us to lower the debounce.
- `fwd` vs `ret`: a "forward" button (send the AMR one way) vs a "return" button
  (send it back). If a station has both, give us **two** node ids.

---

## 2. How your nodes map to our stations (the config we set)

We don't hardcode node ids. Mapping is driven by config on our side, two ways:

**A. Explicit map (recommended for the pilot)** — env var `OPCUA_NODE_MAP`, a JSON
object keyed by node id → `[station_id, direction]`:

```bash
OPCUA_ENDPOINT='opc.tcp://10.0.0.5:4840/fleet'
OPCUA_NODE_MAP='{
  "ns=2;s=CallButton.AP1_call": ["AP1","fwd"],
  "ns=2;s=CallButton.CB1_call": ["CB1","fwd"]
}'
```

**B. From the station table** — if `OPCUA_NODE_MAP` is empty we derive the map from
`backend/app/config.py:STATIONS` (`opcua_node` → `fwd`, `opcua_ret` → `ret`).

Station ids (`AP1`, `CB1`, …) and the supplier→consumer **pairs** live in
`config.py`. A task is dispatched only when **both** sides of a pair press the
same direction (the handshake) — confirm with us which buttons are paired.

### Driver tuning env vars (defaults are pilot-safe)

| Env var | Default | Meaning |
|---------|---------|---------|
| `OPCUA_ENDPOINT` | `""` (disabled) | opc.tcp endpoint; empty = driver off |
| `OPCUA_NODE_MAP` | from STATIONS | explicit node→station/direction JSON |
| `OPCUA_DEBOUNCE_S` | `1.0` | ignore repeat rising edges within this window |
| `OPCUA_RECONNECT_MIN_S` | `1.0` | first reconnect wait after a drop |
| `OPCUA_RECONNECT_MAX_S` | `30.0` | reconnect backoff cap |
| `OPCUA_SUB_PERIOD_MS` | `200` | subscription publish interval requested |
| `OPCUA_HEALTH_S` | `2.0` | liveness ping interval (drop detection latency) |

---

## 3. Driver behavior you can rely on

- **Disabled cleanly** if `OPCUA_ENDPOINT` is unset or `asyncua` isn't installed.
- **Rising-edge only**, debounced — held/noisy True won't spam dispatch.
- **Reconnect/resubscribe** with bounded exponential backoff if your server
  restarts or the link drops; the backend thread never crashes.
- **Missing node tolerance** — if one configured node id doesn't exist on your
  server, we log a warning and keep serving the others (the whole driver does not
  go down). So a typo in one node id won't take out every button.
- **No spurious press on (re)connect** — we read each node's current value on
  connect and seed it, so a button already True at connect time isn't treated as
  a fresh press.

---

## 4. On-site validation procedure

Pre-checks:
1. From the fleet host, confirm TCP reach: `Test-NetConnection <host> -Port <port>`.
2. Browse your endpoint with a generic client (UaExpert) and confirm each node id
   exists, is **Boolean**, and toggles True on a physical press.

Backend bring-up:
3. Set `OPCUA_ENDPOINT` (+ `OPCUA_NODE_MAP` if used) and start the backend.
4. Check the log for, per button:
   `[OpcUA] connected to …` then `[OpcUA] subscribed ns=2;s=… → CB1/fwd`.
   A `node … unavailable: … — skipping` line means a node id is wrong/missing.

Per-button walk (do this for **every** physical button):
5. Press the button. Confirm in the backend log:
   `[OpcUA] button pressed: node=… station=CB1 dir=fwd`.
6. Press the **paired** button for the same direction. Confirm a task is created
   (`task created: … AP1→CB1`) and an AMR is dispatched / appears in the dashboard.
7. Release both. Press again after ~2 s → confirm it re-triggers (rising edge
   re-arms). Press-and-hold → confirm it does **not** spam multiple tasks.

Resilience check:
8. Restart your OPC UA server (or pull the link) for ~10 s. Confirm the backend
   logs reconnect attempts and then `connected` + `subscribed` again, and that a
   button press after recovery still dispatches.

Sign-off: every physical button maps to the right station/direction, the
handshake dispatches the right AMR, and recovery works after a server restart.

---

## 5. Open risks for real-server cutover

- **Security**: validated only against an anonymous, security-`None` server. If
  the plant requires Sign/Encrypt or credentials, the driver needs the certs/creds
  and a small change (and a re-test) before cutover.
- **Node-id format / namespace index**: the index can shift if your server's
  namespace array changes between PLC builds. Pin it and re-verify after any PLC
  re-flash; prefer string identifiers over numeric.
- **Pulse width vs publish period**: a very short momentary pulse (< ~200 ms) can
  be missed. Either hold longer or we lower `OPCUA_SUB_PERIOD_MS`.
- **Debounce window**: default 1.0 s. If two legitimate rapid presses are needed,
  tune `OPCUA_DEBOUNCE_S` together.
- **Server datachange semantics**: we assume datachange notifications on Boolean
  writes (deadband/queue-size defaults). If your server coalesces or drops
  notifications under load, validate under realistic button traffic.
- **Clock/keepalive**: drop-detection latency is `OPCUA_HEALTH_S` (2 s default);
  shorten if you need faster failover.
