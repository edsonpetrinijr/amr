# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

BehaveX — React/TypeScript dashboard for multi-agent swarm simulation management. Visualizes experiments, runs, comparisons, and swarm configurations. Currently frontend-only with mock data (no backend integration).

## Build & Dev Commands

No build system configured yet. Once set up (likely Vite + npm):

```bash
npm install         # install deps
npm run dev         # dev server
npm run build       # production build
npm run lint        # ESLint
npm test            # test suite
npm test -- path/to/test  # single test
```

## Architecture

**Entry:** `src/app/App.tsx` → `src/app/routes.tsx` (React Router v7 `createBrowserRouter`)

**Routes:**
- `/` → `Dashboard` — recent experiments, active runs, metrics
- `/experiment/:id` → `ExperimentDetail` — simulation canvas with playback controls (500 steps, 12 agents)
- `/comparisons` → `Comparison` — side-by-side dual sim view with metrics diff
- `/configs` → `SwarmConfig` — behavior policy config (GitHub URL, seeds, agent count, obstacle density)

**Layout:** `src/app/components/Layout.tsx` — sidebar nav wrapping all pages. Brand: "AeroNet v2.4.1".

**UI Components:** `src/app/components/ui/` — 50+ shadcn/ui components. Use existing ones before adding new.

**Styling:** Tailwind CSS v4, dark GitHub-inspired theme (`#0d1117` bg, `#58a6ff` accent). Colors defined in `src/styles/theme.css` as OKLCH CSS vars. Utility helper `cn()` in `src/app/utils.ts` (clsx + tailwind-merge).

## Key Constraints

- All simulation data is currently mocked client-side — no API layer exists
- Robot/agent state tracked via `useState` + `useEffect` intervals in page components
- `ExperimentDetail` max 500 steps, `Comparison` max 400 steps, 8 robots per sim
- Divergence detection in Comparison highlights steps 150–200
