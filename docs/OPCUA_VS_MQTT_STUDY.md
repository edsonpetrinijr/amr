# OPC UA → MQTT Migration Study (Plant-Floor Call-Button Signaling)

**Status:** Planning / research only. No code change. (Recorded 2026-06-03.)
**Decision (TL;DR):** **Stay on OPC UA for the pilot. Do not migrate now.** Keep the door open by making the call-button driver a clean **integration provider** (mirror Sim↔SEER), so MQTT becomes a second implementation *if and when* a real plant hands us MQTT/Sparkplug instead of an OPC UA endpoint. MQTT (esp. Sparkplug B) is a **multi-site/IIoT scale play**, not a pilot necessity — and migrating now would *add* infrastructure (broker + PLC→MQTT bridge) we'd have to run and support on tight runway.

---

## 1. OPC UA vs MQTT — honest technical comparison (for our exact use case)

Our use case is narrow: **discrete boolean button/handshake signals, plant floor → our backend, event-driven, a handful of stations, one warm site.** That narrowness matters — most of MQTT's advantages are about scale and fan-out we don't have yet.

| Dimension | OPC UA (what we run today) | MQTT (incl. Sparkplug B) | Who wins for *our* case |
|---|---|---|---|
| **Data model** | Structured address space, typed nodes, browseable. Our buttons are typed Boolean nodes with stable string node-ids (`ns=2;s=CallButton.AP1_call`). | Lightweight pub/sub topics; payload is opaque (bytes/JSON) unless you adopt Sparkplug B, which re-adds a typed metric model + birth/death certs. | **OPC UA** — we already have typed, self-describing signals. Plain MQTT throws that away; Sparkplug rebuilds it (extra complexity). |
| **Discovery / browsing** | First-class: point UaExpert at the endpoint, see every node. Huge during cutover (validate node ids on-site). | None in plain MQTT — topics are by convention; you must *know* the topic. Sparkplug B adds birth messages that advertise metrics. | **OPC UA** — our entire on-site validation procedure leans on browsing. |
| **Security** | Mature but heavy: security policies (`Basic256Sha256`), Sign/SignAndEncrypt, X.509 cert exchange both directions. We currently run anonymous/None on an isolated VLAN. | TLS + username/password or client certs. Conceptually simpler. ACLs per topic on the broker. | **Tie** — both fine. MQTT's model is simpler to reason about; OPC UA's is richer. Neither is a reason to switch. |
| **QoS / delivery** | Subscriptions with publish interval, queue size, deadband; reliable session-based delivery; can miss very short pulses < publish period (known risk in our docs). | QoS 0/1/2. **Retained messages** + **Last Will (LWT)** are genuinely nice for state + presence. Sparkplug formalizes birth/death. | **Slight MQTT edge** on *presence/retained state* semantics. But our debounce + rising-edge + seed-on-connect already handle the press semantics we need. |
| **Reliability / reconnect** | We built bounded exponential backoff, resubscribe, liveness ping, per-node skip, seed-on-connect. **Already hardened (S2 sprint).** | paho reconnect is straightforward; LWT makes dead-publisher detection trivial. But we'd be rebuilding the hardening we already paid for. | **OPC UA** — sunk, hardened, tested. Switching = re-spend that effort. |
| **Latency** | Sub-second; gated by `OPCUA_SUB_PERIOD_MS` (200 ms) + `OPCUA_HEALTH_S`. | Typically lower per-message overhead; broker hop adds a small latency but negligible for button presses. | **Tie** — both far inside a human-button-press SLA. Irrelevant to our pilot metric. |
| **Firewall / network** | Single TCP endpoint (`opc.tcp://…:4840`). One hop, point-to-point. | Needs a **broker** reachable by both publisher and us. Adds a box/process and a port, plus the bridge. | **OPC UA** — fewer moving parts on an OT network. MQTT adds a broker to firewall, secure, and keep alive. |
| **Python tooling** | `asyncua` — mature, what we use. Works. | `paho-mqtt` — extremely mature, dead-simple, huge ecosystem. Sparkplug libs (e.g. `tahu`) less polished. | **MQTT (plain)** marginally nicer DX, but not enough to move. |
| **Event vs poll fit** | Subscription = true event push (no polling). We already get rising-edge events. | Pub/sub = natively event-driven. | **Tie** — both are event-driven; OPC UA subscriptions already give us push. |

**Honest takeaway:** For *discrete buttons from one site*, MQTT's real wins (retained state, LWT presence, lightweight fan-out to many subscribers, topic-based scale) **don't move our pilot needle**. We'd trade a hardened, browseable, typed integration for a lighter protocol that needs *more* infrastructure to reach parity (Sparkplug to get types/discovery back, plus a broker, plus a bridge).

---

## 2. Who actually produces the signal? (this decides everything)

**The right transport is dictated by what the plant floor can emit — not by our preference.** Buttons are physical contacts wired to a **PLC**. The question is what that PLC/gateway can speak:

| Plant reality | What it means for us |
|---|---|
| **(A) PLC exposes an OPC UA server** (on PLC or gateway) | This is the assumed baseline. We connect directly. **No new infra.** This is what our driver + cutover guide already target. |
| **(B) PLC can publish MQTT natively** (modern PLC, or Sparkplug-capable) | We'd need an **MQTT broker** somewhere both sides reach, and we subscribe. Still need to run/secure the broker. |
| **(C) PLC speaks only OPC UA / Modbus / raw I/O, no MQTT** | MQTT requires a **bridge**: an edge gateway, Node-RED flow, or Sparkplug edge node that reads PLC I/O and republishes to the broker. **We'd own/support that bridge + the broker.** This is *more* OT surface area, not less. |

**Critical point for the founder:** MQTT is **almost never a drop-in swap** for OPC UA here. Unless the plant explicitly *prefers* to hand us an MQTT/Sparkplug feed (some IIoT-forward sites do), choosing MQTT means **we add and operate a broker (Mosquitto/EMQX) and a PLC→MQTT bridge** — a strange thing for a solo founder to take on mid-pilot-prep when an OPC UA endpoint already gets us the same booleans with zero added boxes.

**Open item already on our list:** confirm real call/return node ids with the plant. **Fold one question into that conversation:** "Do you expose these buttons via OPC UA, or do you prefer to publish them over MQTT/Sparkplug?" Their answer is the whole decision.

---

## 3. Recommendation

**Stay on OPC UA for the pilot. Refactor the driver into a provider/integration interface so MQTT is a swap-in later — but don't build the MQTT side until a real plant requires it.**

Rationale, tied to pilot success + runway:

- **Pilot metric is on-time delivery SLA, not protocol elegance.** OPC UA already delivers the button events reliably and is hardened/tested. Migrating buys us *nothing* the SLA cares about.
- **Runway is tight (solo founder).** Migration spends scarce weeks rebuilding reconnect/debounce/test scaffolding we already have, plus introduces a broker + bridge to operate. That's negative ROI pre-pilot.
- **MQTT/Sparkplug is a scale story.** Its advantages (many subscribers, retained state, presence, unified namespace across sites/devices) pay off at **multi-site / IIoT fleet** scale — exactly the post-pilot world, not the one-warm-site world.
- **Defensibility doesn't live in the button transport.** It's in fleet orchestration, the SEER provider, the 10 Hz world loop, dispatch logic. Button signaling is plumbing; pick the lower-risk plumbing.
- **Optionality is cheap; commitment is not.** A clean `CallButtonProvider` interface (mirroring Sim↔SEER) costs little and means we can add MQTT in days if a plant demands it — without a migration.

**Do support *both* — but behind the abstraction, lazily.** Build the interface now (small, safe, no behavior change). Build the MQTT implementation only when a concrete plant hands us MQTT instead of OPC UA.

---

## 4. IF we migrate — high-level migration plan

Only execute if a plant requires MQTT. Keep it phased and mock-first.

**Where it slots — mirror the Sim↔SEER provider pattern:**
- Define a `CallButtonProvider` (a.k.a. `SignalProvider`) interface: `start()`, `stop()`, and a callback that ultimately calls `dispatcher.button_pressed(station_id, direction)`.
- `OpcUaCallbuttonProvider` = today's driver, refactored behind the interface (no behavior change).
- `MqttCallbuttonProvider` = new implementation. Config selects which (`SIGNAL_PROVIDER=opcua|mqtt`), exactly like provider selection for Sim↔SEER. Dispatcher stays untouched — same rising-edge → `button_pressed` contract, same debounce/seed semantics live above the transport.

**Broker:** **Mosquitto** for the pilot (tiny, boring, reliable, trivial to run). EMQX only if we later need clustering/observability/many tenants — overkill now. Reuse principle: boring tech on the floor.

**Sparkplug B vs plain topics:**
- **Plain topics** (e.g. `plant/lineA/CB1/call` → `1`/`0`, or JSON) — simplest, fastest to ship, fine for a handful of booleans. Use **retained** for last-known state + **LWT** for publisher-dead detection.
- **Sparkplug B** — only if the *plant* standardizes on it (then we conform). It re-adds typed metrics + birth/death/discovery (the things we'd lose vs OPC UA) at the cost of more complexity. Don't adopt Sparkplug just because; adopt it to match the site.

**Python libs:** `paho-mqtt` (mature, simple). For Sparkplug, `tahu`/eclipse libs — evaluate maturity before committing.

**Security:** TLS to the broker + per-client credentials and **topic ACLs** (we subscribe-only to button topics). Keep it on the isolated AMR VLAN as we do today. Don't run an unauthenticated broker on a routable network.

**Testing — mirror the mock OPC UA server:** build a **mock MQTT broker/publisher** test harness (embedded Mosquitto or an in-process paho publisher) that replays press/hold/bounce/reconnect scenarios, reusing the same behavioral assertions our OPC UA tests already encode (rising-edge only, debounce, seed-on-connect, per-node skip, reconnect). Port the **plant checklist** to an MQTT variant.

**Rough effort / phasing (only if triggered):**
1. **Refactor to provider interface** (~0.5–1 day, safe, do this regardless — it's the optionality investment). OPC UA behind the interface, tests still green.
2. **MqttCallbuttonProvider + mock broker tests** (~2–3 days): topic→(station,direction) map mirroring `OPCUA_NODE_MAP`, retained/LWT handling, reconnect, debounce parity.
3. **Broker stand-up + security** (~1 day): Mosquitto, TLS, ACLs, config.
4. **Bridge coordination** (variable, plant-owned): the PLC→MQTT bridge is *their* infrastructure ideally; if it's ours (Node-RED), add integration + on-site validation time.
5. **On-site validation** (mirror the existing cutover guide).

---

## 5. Risks, unknowns, and the cheapest experiment

**Unknowns:**
- Does the real plant expose buttons via OPC UA, MQTT, or only raw PLC I/O? (Decides everything — see §2.)
- If MQTT: who owns the broker and the PLC→MQTT bridge — them or us?
- Sparkplug required, or are plain topics acceptable?
- Real node-id/topic naming, security requirements (still open even for OPC UA).

**Risks of migrating now:**
- **Added OT surface area** (broker + bridge) for a solo founder to operate and secure — a new failure domain (broker down = all buttons dead, vs today's direct endpoint).
- **Re-spending** the hardening (reconnect/debounce/seed/test) we already shipped.
- **Schedule risk** to a tight pilot for zero SLA benefit.
- **Sparkplug complexity** if we adopt it prematurely.

**Risks of staying (small, manageable):**
- A plant that *only* speaks MQTT would block us — mitigated by the provider interface (days to add MQTT, not a rewrite).

**Cheapest experiment to learn if MQTT is worth it — no commitment:**
1. **Ask the plant one question** (free): OPC UA or MQTT/Sparkplug for these buttons, and who owns the bridge? This likely closes the whole question.
2. **If curious anyway, a ~half-day spike:** run Mosquitto locally, a `paho` subscriber that maps a topic to `button_pressed`, and a tiny publisher faking presses. Measure latency, reconnect/LWT behavior, and DX vs our OPC UA driver. Throwaway, no production code.
3. **Do the provider-interface refactor regardless** — it's the cheapest real insurance: turns any future "must use MQTT" from a migration into a plug-in.

**Bottom line:** The migration's value is gated almost entirely on a plant fact we haven't confirmed. Confirm it with one question before spending a single engineering hour. Until then: **OPC UA stays, interface gets cleaned, MQTT waits.**

---

## Mini-ADR

- **Context:** Founder asked whether to migrate plant-floor call-button signaling from OPC UA to MQTT. We have a hardened, tested OPC UA driver; one warm pilot site; tight solo-founder runway; pilot metric is delivery SLA. MQTT's benefits are scale-oriented and usually require adding a broker + PLC→MQTT bridge.
- **Decision:** Keep OPC UA for the pilot. Refactor the driver behind a `CallButtonProvider` interface (mirror Sim↔SEER) to make MQTT a future swap-in. Build the MQTT implementation only if a real plant requires it. If we do, use Mosquitto + paho-mqtt, plain topics unless the plant mandates Sparkplug B, with a mock-broker test harness mirroring the mock OPC UA server.
- **Consequences:** No pilot schedule/runway hit; we keep our hardened OPC UA path; we avoid operating a broker/bridge we don't need yet. We gain cheap optionality. Trade-off: a small upfront refactor cost, and we defer (don't eliminate) MQTT/Sparkplug work that becomes relevant at multi-site/IIoT scale.

---

*Recorded for reference only — no change planned at this time. Revisit when (a) the plant confirms its transport, or (b) we go multi-site / IIoT scale.*
