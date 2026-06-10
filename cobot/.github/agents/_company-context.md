# Company Context (shared)

> This file is shared context referenced by every agent persona. Keep it current — it is the single source of truth about the venture.

## The venture
A **solo-founder startup** building **fleet-orchestration software for industrial Autonomous Mobile Robots (AMRs)**. The company is run by **one human founder augmented by a team of specialized AI agents** — each agent owns a function (strategy, market, product, engineering, growth, finance, legal).

## The product
A control-plane application that orchestrates a fleet of AMRs on a factory floor.

- **Frontend**: Electron + React (TypeScript), Vite, Tailwind.
- **Backend**: Python + Flask, Server-Sent Events for real-time telemetry.
- **Integrations**:
  - **SEER Robokit TCP API** (ports 19204–19210) — robot status, navigation, I/O.
  - **OPC UA (Kepware)** — physical call buttons on the factory floor.
  - **RoboShop Pro** — maps (`.smap`) and task files (`.task`).

## Core use case (first pilot)
Part delivery between a **supplier station** (who makes the part) and a **consumer station** (who needs it). A **2-button handshake**: both sides confirm before an AMR is dispatched. Bidirectional flow (supplier→consumer and the reverse). Includes a **relocalization-assist** strategy because the plant map is very large and stock relocalization fails.

## Strategic posture
- Lean, capital-efficient, one-person + AI agents.
- Industrial / intralogistics / smart-manufacturing market.
- Differentiation should come from **orchestration UX, safety, and ease of integration**, not from building robots.

## How agents should operate
- Be concrete and decision-oriented; the founder's time is the scarcest resource.
- State assumptions explicitly, then proceed.
- Always tie recommendations back to runway, pilot success, and defensibility.
