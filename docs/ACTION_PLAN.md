# Caterpillar Inc. Fleet — Action Plan: Unimplemented UI Features

> Generated: 2026-04-25  
> Status: Review & prioritize before implementing

---

## Priority Tiers

| Tier | Criteria |
|------|----------|
| 🔴 P1 | Core flow broken without it |
| 🟡 P2 | Important UX, non-blocking |
| 🟢 P3 | Nice-to-have / polish |

---

## 1. Dead Buttons — No onClick Handler

### Dashboard (`src/app/pages/Dashboard.tsx`)

| # | Label | Line | Expected Behavior | Priority |
|---|-------|------|-------------------|----------|
| 1 | **New Experiment (GitHub Repo)** | 169 | Open dialog/form to create experiment from GitHub repo URL | 🔴 P1 |
| 2 | **Link External Policy File** | 173 | Open dialog to attach an external `.policy` or config file | 🟡 P2 |
| 3 | **Open Metric Dashboard** | 177 | Navigate to `/metrics` or open metrics panel | 🟡 P2 |
| 4 | **Run again** (RotateCcw icon, per experiment row) | 114 | Re-run experiment with same parameters | 🔴 P1 |

### SwarmConfig (`src/app/pages/SwarmConfig.tsx`)

| # | Label | Line | Expected Behavior | Priority |
|---|-------|------|-------------------|----------|
| 5 | **Fetch** | 56 | Validate GitHub URL, fetch available branches/tags | 🔴 P1 |
| 6 | **Save Preset** | 26 | Save current config as named preset (local storage or file) | 🟡 P2 |
| 7 | **Apply & Run** | 30 | Apply config and start new simulation run | 🔴 P1 |

### Comparison (`src/app/pages/Comparison.tsx`)

| # | Label | Line | Expected Behavior | Priority |
|---|-------|------|-------------------|----------|
| 8 | **Swap Views** | 108 | Swap left/right simulation panels | 🟢 P3 |
| 9 | **Maximize** (×2, one per MockSimulation panel) | 32 | Expand panel to fullscreen | 🟢 P3 |

### ExperimentDetail (`src/app/pages/ExperimentDetail.tsx`)

| # | Label | Line | Expected Behavior | Priority |
|---|-------|------|-------------------|----------|
| 10 | **Expand** (icon button, simulation viewer) | 88 | Expand simulation canvas to fullscreen | 🟢 P3 |
| 11 | **Search** (icon button, logs panel) | 176 | Filter/search runtime logs by keyword | 🟡 P2 |

---

## 2. No-op / Broken Interactions

| # | Element | File | Line | Problem | Priority |
|---|---------|------|------|---------|----------|
| 12 | **Timeline scrubber** (range input) | `ExperimentDetail.tsx` | 139 | `seekStep()` is no-op — dragging slider does nothing | 🔴 P1 |
| 13 | **Repository URL input** | `SwarmConfig.tsx` | 53 | Input exists but value never validated/used (Fetch broken) | 🔴 P1 (linked to #5) |

> Note: `seekStep` no-op is in `src/ml/useSimEngine.ts` line 46–49, comment: _"Seek not supported in live engine; kept for API compat"_

---

## 3. Placeholder Routes (Blank Pages)

| # | Route | Component | Current State | Priority |
|---|-------|-----------|---------------|----------|
| 14 | `/experiments` | Placeholder | Empty screen with title text only | 🔴 P1 |
| 15 | `/runs` | Placeholder | Empty screen with title text only | 🔴 P1 |
| 16 | `/settings` | Placeholder | Empty screen with title text only | 🟡 P2 |

Files: `src/app/routes.tsx` lines 9–32

---

## 4. Mock / Stub Implementations (Not Real Data)

| # | Component | File | Problem | Priority |
|---|-----------|------|---------|----------|
| 17 | **MockSimulation** | `Comparison.tsx` | Deterministic fake robot positions from seed math — not real experiment data | 🔴 P1 |
| 18 | **All experiment/run data** | `Dashboard.tsx`, `ExperimentDetail.tsx` | Hardcoded mock arrays, no API layer | 🔴 P1 (arch-level) |

---

## 5. Future: GPU / ML Optimization (Mac)

> Planned separately — implement after core features stabilize.

### Options to evaluate

| Option | Notes |
|--------|-------|
| **Metal (via Python `mlx`)** | Apple's ML framework, best perf on Apple Silicon. Use for agent policy inference. |
| **WebGPU (browser-native)** | Run simulation/rendering on GPU from browser. Chrome 113+ supported. Good for canvas-heavy rendering. |
| **ONNX Runtime Web (WebAssembly + GPU)** | Run pre-trained agent models in browser without Python backend. |
| **Offload to local FastAPI + `mlx`** | Backend process on Mac, frontend calls local REST/WebSocket. Clean separation. |

**Recommended starting point:** Local FastAPI service using `mlx` for policy inference → WebSocket stream to frontend. Replaces current `useSimEngine` mock with real engine.

---

## Suggested Implementation Order

```
Phase 1 — Core flow (P1)
  1. /experiments route (real list page)
  2. /runs route (real list page)  
  3. SwarmConfig: Fetch button + Apply & Run
  4. Dashboard: New Experiment button (dialog)
  5. Dashboard: Run again button
  6. Timeline scrubber seekStep fix
  7. Replace MockSimulation with real data

Phase 2 — UX completeness (P2)
  8. /settings route
  9. Log search in ExperimentDetail
  10. Link External Policy File
  11. Open Metric Dashboard
  12. Save Preset

Phase 3 — Polish (P3)
  13. Swap Views (Comparison)
  14. Maximize buttons
  15. Expand button (ExperimentDetail)

Phase 4 — GPU/ML optimization
  16. Design backend architecture (mlx / WebGPU / ONNX)
  17. Implement real sim engine
  18. Replace all mock data with live data
```

---

## Quick Count

- Dead buttons: **11**
- Broken interactions: **2**
- Placeholder routes: **3**
- Mock implementations: **2**
- **Total items: 18**
