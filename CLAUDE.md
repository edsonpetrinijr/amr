# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

An AMR (Autonomous Mobile Robot) fleet-orchestration desktop app. An Electron + React/TypeScript
frontend talks to a Python Flask backend (port `8765`) over Server-Sent Events (`/events`) plus REST.
The backend dispatches tasks to SEER AMRs over TCP (`19204` state / `19205` control / `19206` task /
`19210` IO) and ships a Sim provider for offline development. An OPC UA callbutton driver handles
plant-floor triggers, and SQLite (`fleet.db`) stores telemetry.

## Build & Dev Commands

```bash
npm install         # install deps
npm run dev         # Electron + Vite dev (vite)
npm run web         # browser-only dev (vite --config vite.web.config.ts)
npm run build       # tsc + vite build + electron-builder
npm run lint        # ESLint (eslint src --ext ts,tsx)
```

The Python backend runs separately (see `backend/` and `run-backend.bat`) and listens on port `8765`.

## Architecture

**Frontend entry:** `frontend/app/App.tsx` → `frontend/app/routes.tsx` (React Router v7
`createBrowserRouter`).

**Routes** (all wrapped by `frontend/app/components/Layout.tsx`):
- `/` → `Dashboard` — fleet overview
- `/field` → `Field` — live map / robot positions
- `/devices` → `Devices` — robot & device inventory
- `/calibration` → `Calibration` (also `/calibration/:robotId`)
- `/tasks` → `Tasks` — task definitions / dispatch
- `/callbuttons` → `Callbuttons` — OPC UA callbutton bindings
- `/settings` → `SettingsPage`

**Backend:** `backend/app/` — Flask app exposing REST + SSE (`/events`). Dispatches to SEER Robokit
over TCP with a Sim provider for offline dev; OPC UA driver for callbuttons; SQLite (`fleet.db`)
telemetry. (Do not edit the backend from frontend tasks unless asked.)

**Electron:** `electron/main.ts` (main process) + `electron/preload.ts`.

**UI Components:** `frontend/app/components/ui/` — shadcn/ui components. Reuse existing ones before
adding new.

**Styling:** Tailwind CSS v4, dark GitHub-inspired theme (`#0d1117` bg, `#58a6ff` accent). Colors
defined in `frontend/styles/theme.css` as OKLCH CSS vars. Utility helper `cn()` (clsx +
tailwind-merge) in `frontend/app/utils.ts`.

## Maps & Tasks

Map and task files live in `maps/`. The backend loads these for routing and task dispatch.
