# Post-Demo Backlog

Items deliberately deferred during the pre-demo polish pass on the operator desktop app
(Electron + React/TS, `desktop/`). Each was scoped out to keep the demo clean and
deterministic — not because it's hard, but because it needs a contract, asset, or shared
helper that didn't exist yet. Re-open these after the demo.

Each item records: **What it was** · **Where** · **Why deferred** · **What's needed**.

---

## 1. Field "Dispatch robot here" control

- **What it was:** A per-station "Despachar robô para cá" control (dropdown of idle robots +
  dispatch button) in the Field station panel, backed by `handleDispatch()`.
- **Where:** `desktop/app/pages/Field.tsx` ~163–169 (`handleDispatch`, plus its `robotId`
  state and `available` filter — all commented out, not deleted).
- **Why deferred:** `createTask(robotId, station.id)` passed the **robot id as the pickup
  station**, producing a malformed task. There is no backend contract to pin a task to a
  specific robot, so the control could never work correctly.
- **What's needed:** A backend endpoint — e.g. `POST /robots/<id>/dispatch { dropoff }` — OR
  `createTask` gaining an optional `robot_id` field. Once the contract exists, uncomment the
  control and its handler/state and wire it to the new call.

---

## 2. Favicon / window icon

- **What it was:** App had no favicon; no icon asset exists in `public/`.
- **Where:** `index.html` (no `<link rel="icon">`); `public/` (no icon file).
- **Why deferred:** No icon asset was available to ship, and an empty/broken `<link>` is worse
  than none for the demo.
- **What's needed:** Supply a real icon (e.g. `public/favicon.ico` or a PNG), then add
  `<link rel="icon" href="/favicon.ico">` to `index.html`. Consider also wiring it as the
  electron-builder app icon.

---

## 3. Mac traffic-light spacer on Windows

- **What it was:** A 32px-tall drag spacer at the top of the sidebar to clear the macOS
  traffic-light buttons (`hiddenInset` title bar).
- **Where:** `desktop/app/components/Layout.tsx:103` (`<div className="h-8 shrink-0" .../>`).
- **Why deferred:** The spacer is only needed on macOS; on Windows it wastes 32px of vertical
  space. The macOS-only `titleBarStyle` was already fixed in `electron/main.ts` (platform-
  conditional `hiddenInset`), but the renderer can't currently tell which platform it's on.
- **What's needed:** Expose `process.platform` to the renderer via `electron/preload.ts`
  (contextBridge), then gate the spacer on `platform === 'darwin'`.

---

## 4. Devices "Refresh" button

- **What it was:** A manual Refresh button on the Devices page.
- **Where:** `desktop/app/pages/Devices.tsx` (removed; previously called
  `window.location.reload()`).
- **Why deferred:** It caused a full white-flash reload, and the data is already live via SSE.
  A plain `getRobots()` re-fetch wouldn't help either — it wouldn't push results into the
  SSE-backed store.
- **What's needed (only if ever wanted):** A store action that merges a manual `getRobots()`
  refetch into the SSE-backed store, then a button that calls it (no page reload).

---

## 5. Orphan `ImageWithFallback.tsx`

- **What it was:** A leftover Figma-export component, imported nowhere.
- **Where:** `desktop/app/components/figma/ImageWithFallback.tsx` (deleted).
- **Why deferred:** Removed during cleanup to reduce cruft; nothing depended on it.
- **What's needed:** Nothing. Closed.

---

## 6. Task state badges in raw English

- **What it was:** Task STATE badges render the raw backend value (e.g. `assigned`,
  `in_progress`) via `task.state.replace(...)`, left untranslated.
- **Where:** `desktop/app/pages/Tasks.tsx` and `desktop/app/pages/Dashboard.tsx`.
- **Why deferred:** Kept consistent across both pages on purpose — translating one and not the
  other would look broken. Held until a single shared mapping exists.
- **What's needed:** A shared pt-BR `state → label` map (one helper, e.g. in `utils.ts`) used
  by both Tasks and Dashboard, then swap both call sites to it.

---

## 7. API dedupe — `callbuttonPress` → `pressCallbutton`

- **What it was:** Two overlapping callbutton helpers — an untyped `fleetApi.callbuttonPress`
  and a typed `fleetApi.pressCallbutton` (both `POST /callbutton/<id>`).
- **Where:** `desktop/app/api/fleet.ts` (untyped `callbuttonPress` removed; typed
  `pressCallbutton` kept). Field migrated its caller to `pressCallbutton`.
- **Why deferred:** This one is **done** — the dedupe landed. Recorded here for traceability.
- **What's needed:** Nothing. Note: `fleetApi.buttonPress` (`POST /button/<id>`, the
  directional fwd/ret endpoint used by `Callbuttons.tsx` DirectionRow) is a **separate**
  endpoint and was intentionally kept — do not fold it into `pressCallbutton`.
