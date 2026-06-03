# Project Timeline

> Living log of what was built, decided, and shipped. Maintained by the **CEO agent** — append a new entry at the top whenever meaningful work lands. Newest first.
>
> Entry format:
> ```
> ## YYYY-MM-DD — <short title>
> - **Done:** what was actually completed/shipped
> - **Decided:** key decisions made (and why, one line)
> - **Next:** what comes next
> - **Refs:** commits / files / PRs (optional)
> ```

---

---

## 2026-06-03 — Folder rename shipped: frontend/→desktop/, backend/→server/
- **Done:** Completed the deferred top-level rename, finishing the **server / desktop / web** three-way structure. `frontend/`→`desktop/` (operator Electron renderer) and `backend/`→`server/` (Python/Flask control-plane), both via `git mv` (history preserved). Updated every reference: `index.html` (`/desktop/main.tsx`), `vite.config.ts`+`vite.web.config.ts` (`@`→`./desktop`), `tsconfig.json` (paths+include), `eslint.config.mjs` (globs + `server/**` ignore), `.gitignore` (`server/devices.json`), `run-backend.bat`/`start.bat`, `server/app/main.py` run-docstring, 9 backend test files (`backend.app`→`server.app`, incl. a runtime `server.tests.opcua_mock_server` import caught in review), `CLAUDE.md`, `docs/OPCUA_INTEGRATION.md`. `electron/` left as its own top-level host (references only `dist/`, no path changes). `web/` marketing app untouched. Then committed the previously-untracked `desktop/app/components/ErrorBoundary.tsx` (imported by `App.tsx` — fresh clones would have failed to build).
- **Decided:** Keep `electron/` separate from `desktop/` (privileged host ≠ renderer). Internal Python imports unchanged — package is named `app`, not `backend`, so moving the folder didn't touch `from . import ...`; only absolute test/run paths changed. Run backend with `python -m server.app.main` (or `cd server && python -m app.main`).
- **Next:** **Heads-up for founder —** the in-flight jog/jack/2-press-callbutton backend WIP (prior entry) had uncommitted edits to `config.py`/`dispatcher.py`/`main.py`/`seer/*.py` when the folders moved, so that feature content got **bundled into the rename commit `957a91c`** (content preserved, all green) rather than living in its own commit as planned. If you want it as a separate logical commit, say so and I'll reconstruct it. Cosmetic: operator `index.html` still titled "Caterpillar Inc. Fleet".
- **Refs:** commits `957a91c` (rename), `1d2e8e2` (ErrorBoundary); verifications: tsc 0 errors, lint 0 warnings, operator+marketing builds green, server boots SIM `/health` 200 on :8765, ~64 backend tests pass.

## 2026-06-03 — Full colored W3-600B model in 3D preview (was chassis-only)
- **Done:** Diagnosed why the 3D preview showed only a flat-grey chassis: we'd baked a single mesh (`base_link_v2_simp.stl`) with no material. The real W3-600B is a **20-piece assembly from 10 STLs** with per-part colors in the URDF. Rebuilt `public/w3_600b.glb` as the **full, colored, floor-standing robot**: body `#3399CC`, drive wheels + caster discs `#333333`, caster forks + 2 lidars + 2 cameras `#B2B2B2`, tray `#999999` (motors skipped — URDF references no motor link; unused `front_lidar.stl` skipped). Final GLB **266 KB** Draco (20 instances, 10 deduped geos, 4 baked materials), upright bbox 0.954×0.651×0.251 m, floor-aligned, **same anchor/orientation as before so PoseDriver heading is unchanged**. Component material logic already lets baked per-part colors win (neutral fallback only for material-less meshes). Repro build script at `scripts/build_w3_glb.mjs`. Cleaned scratch cache + added `scripts/`,`dist-marketing/` to eslint ignores → lint+typecheck+build all exit 0; three/r3f/GLB stay in the lazy chunk (main bundle 434 kB, un-bloated).
- **Decided:** Keep the GPL-3.0 internal-dev/test posture unchanged (asset still from GilmarCorreia/sim_models). The `_simp` STLs are already Y-up — the planned +90°X frame-wrap was NOT needed (would tip the robot on its side); identity wrap reproduces the correct upright anchor.
- **Next:** unchanged license gate before any external build (exclude `public/w3_600b.glb`+`public/draco/`). Optional: add motors/full-res meshes if the founder wants more fidelity. Heads-up: repo is mid-refactor `frontend/` → `desktop/` (RobotPreview3D now under `desktop/app/components/`).
- **Refs:** `public/w3_600b.glb`, `public/MODEL_NOTICE.md`, `scripts/build_w3_glb.mjs`, `desktop/app/components/RobotPreview3D.tsx`, `eslint.config.mjs`, `docs/W3-600B_MODEL_NOTES.md`; source GilmarCorreia/sim_models (GPL-3.0)

## 2026-06-03 — Manual control + 2-press callbutton transport (WIP, uncommitted)
- **Done:** Big in-flight backend feature set on top of today's committed work, all still uncommitted in the working tree. (1) **Continuous jog / WASD hold-to-move** — backend resends the last velocity to the SEER robot at ~10 Hz (its velocity watchdog needs continuous commands) with an idle keepalive auto-stop so a dropped client/released key never runs away; new `POST /jog/stop`. (2) **Jack / load platform** — `POST /jack {action: up|down}` pulses a SEER Digital Output (req 6001, port 19210) for `JACK_PULSE_S`. (3) **Callbutton 2-press transport model** — Action Points + supplier/consumer `PAIRS` removed; now the operator presses ORIGIN then DESTINATION (two different callbuttons) → a transport task LM_origin→LM_dest is dispatched; lone origin expires after `CALLBUTTON_ORIGIN_TIMEOUT_S`. `AP1`→`CB-ALMOX` (callbutton on LM1). (4) **`frontend/` → `desktop/` rename** started (the rename deferred in the marketing-split entry), plus new docs `OPCUA_VS_MQTT_STUDY.md`, `W3-600B_MODEL_NOTES.md`, root `AMR.png`/`AMR.step`, `IDEAS.md`.
- **Decided:** Drop the dual-button-same-direction pairing model in favor of a simpler origin→destination 2-press flow (matches the plant-walkthrough decision that the fabrication line is callbutton-driven). Keep `direction` arg only for OPC-UA back-compat.
- **Next:** (1) Commit this in logical chunks — keep the `frontend/→desktop/` rename as its own commit, separate from the jog/jack/callbutton backend feature, separate from docs. (2) Run `backend` pytest (tests were touched) + frontend tsc/lint before committing. (3) Confirm on the real W3-600B: jack DO IDs (`JACK_UP_DO_ID`/`JACK_DOWN_DO_ID`) and jog resend rate. (4) `dist-marketing/` is generated and currently untracked — add to `.gitignore` before it gets committed.
- **Refs:** `backend/app/config.py`, `backend/app/dispatcher.py`, `backend/app/main.py`, `backend/app/seer/robot_conn.py`, `backend/app/seer/protocol.py`, `backend/tests/*`, `electron/main.ts`, `desktop/` (renamed from `frontend/`)

## 2026-06-03 — Marketing site split shipped (web/ standalone build)
- **Done:** eng-lead (frontend + senior engineers in parallel) extracted the landing page into a standalone `web/` app with its own Vite build, SEO/OG meta shell (`lang="pt-BR"`, og tags), and CSS — and removed `/landing` from the operator router. LandingPage was already clean (no router/ui/api imports; only change was the brand import path). Single package.json kept (no workspaces); new scripts `dev:marketing`/`build:marketing` → `dist-marketing/`. tsconfig+eslint extended to cover `web/`. **All 5 verifications green:** tsc 0, lint 0, operator bundle has 0 marketing strings, marketing bundle has 0 operator/API code (`/stop_all`,`/jog`,`fleet.ts`,`VITE_FLEET_URL`,`EventSource` all absent). Commits `7a7a59f`, `576f77e`.
- **Decided:** Did ONLY the cheap decisive third of the server/desktop/web model — the web carve-out. **Deferred** the physical rename of `backend/`→server and `electron/`→desktop (riskier, no urgency mid-pilot).
- **Next:** Founder needs real domain + inbox (currently `piloto@fluxofleet.com`), an OG image, product screenshots for placeholders, and `WHATSAPP_URL` to enable that CTA. Future: operator `index.html` still titled "Caterpillar Inc. Fleet" — branding pass later.
- **Refs:** `web/`, `vite.marketing.config.ts`, `frontend/app/routes.tsx`, `package.json`, `tsconfig.json`, `eslint.config.mjs`

## 2026-06-03 — Plant walkthrough: assembly vs. fabrication lines (field findings)
- **Done:** Morning walkthrough of two target areas. **Assembly line (motor/transmission):** ran very well — strong candidate for first implementation. **Fabrication line:** network-connectivity analysis — a robot stayed connected to the *same* network for too long (didn't roam/hand off), reinforcing the **dead-zone / shadow region** spotted Monday afternoon on the fabrication line. Also observed the **cart currently used to move parts has heavy chip/swarf (cavaco) buildup on its wheels** — flagged to Zampim, who confirmed it's a real concern and that the robot will likely need a modification (e.g. a front brush/sweeper) to keep swarf off the wheels.
- **Decided:** **Input method splits by line** — **assembly line → primary input via web/desktop interface**; **fabrication line → primary input via physical callbutton** (the other option is the backup/reserve in each case). Assembly line is the first implementation target.
- **Next:** (1) Afternoon session today to brainstorm concrete implementation ideas for the **assembly line**. (2) **Zampim + Victor** to verify whether the fabrication-line network shadow region meets the **robot supplier's connectivity requirements**. (3) **Jurandir(?) + Pedra** to investigate the "stuck on one network too long" / roaming behavior. (4) Zampim to scope the **anti-swarf wheel mod** (front brush/sweeper) for the fabrication-line robot.
- **Refs:** field visit (no code); follows Monday PM fabrication-line shadow-region observation.


- **Done:** Root-caused the "blank window on the robot WLAN" report and fixed it defensively. Scan confirmed **no Google Fonts / CDN / external runtime dependency** anywhere (frontend, index.html, public/, theme.css, built dist/ — fonts are system, Draco/GLB vendored locally), so it was *not* a hanging internet fetch. Real latent defects, all offline/packaged-build correlated: (1) **primary** — `createBrowserRouter` under Electron `file://` makes `location.pathname` the on-disk path, matching no route → blank; switched to `createHashRouter`. (2) No React error boundary → any boot throw = silent blank; added root `ErrorBoundary` with inline-styled visible message + Reload. (3) Store dispatched `CONNECTED` optimistically → now subscribes to real SSE `onopen`/`onerror` status (`onFleetStatus()`), so backend-down shows a truthful "Connecting…/red dot" instead of lying or blocking. (4) Added `did-fail-load` logging in `electron/main.ts`. App shell now boots with zero internet dependency and renders even when Flask/SSE is unreachable.
- **Decided:** Use hash routing for the packaged app (path-independent under `file://`); make backend-unreachable a non-fatal, visible state rather than ever rendering blank.
- **Next:** **Founder to confirm the symptom split:** the hash-router fix is network-independent, so "works on my normal network, blank on WLAN-SZ1" most likely means you were running the *dev* build on one PC and the *packaged* build on the robot-network PC. Re-test the new packaged build on WLAN-SZ1. If it's *still* blank only on that network, there's a network-specific blocker we haven't reproduced (e.g., captive portal / proxy) — capture the new `did-fail-load` log and the window's devtools console and send them over.
- **Refs:** `frontend/app/routes.tsx`, `frontend/app/components/ErrorBoundary.tsx` (new), `frontend/app/App.tsx`, `frontend/app/api/fleet.ts`, `frontend/app/state/store.tsx`, `electron/main.ts`. lint + tsc + vite build green (only electron-builder's binary download blocked by sandbox proxy — unrelated to code).

## 2026-06-03 — Fix: battery stuck at 100% (SEER field mapping)
- **Done:** Root-caused the "battery always 100%" bug to the SEER poll loop reading a non-existent nested `battery.percentage` and silently falling back to the 100.0 default every cycle. Rewrote the extraction in `backend/app/seer/robot_conn.py`: new pure helper `battery_pct_from_info()` reads SEER's real flat `battery_level` (0.0–1.0 → ×100 → percentage), falls back to legacy nested/bare shapes, returns `None` only when truly absent so the caller keeps the last value — and a real `0.0` is no longer mistaken for "missing". Clamped 0–100; added opportunistic `charging` flag to `RobotState`. Sim drain (drains only while moving) confirmed working, untouched. Verified via unit-smoke of the helper (0.5→50, 0.0→0.0, nested→87, etc.) and a 25s sim run (100→94.6%).
- **Decided:** Default to SEER's `battery_level` 0–1 field but parse defensively across shapes, since exact firmware key isn't confirmed yet.
- **Next:** **Founder to confirm against the real W3-600B firmware:** exact battery key (`battery_level` 0–1 vs already-0–100), which request carries it (status 1000 vs a dedicated battery query), and the charging flag key (`charging` vs `is_charging`). I'll tighten the mapping once confirmed.
- **Refs:** `backend/app/seer/robot_conn.py` (`battery_pct_from_info`, `_poll_once`, `RobotState.charging`)

## 2026-06-03 — Fixed "LM20 does not exist" — only LM1/LM2 remain, now landmarks (not action points)
- **Done:** Root-caused the runtime "LM20 not found" error to stale station bindings in `backend/app/config.py` (AP1→`LM20`, CB1→`LM10`, CB2–CB6→`LM11`–`LM15`) that the map↔station cross-check (`smap.validate_stations` / `preflight` rule #4) rejected, since the live maps only carry **LM1, LM2**. Fixes: AP1→`LM1` (dropped stale `ap_id`), CB1→`LM2`, CB2–CB6→`None` (unsurveyed). Reworked `smap.py` parser so `LocationMark`/`LM*` entries classify as **landmarks only** (no longer double-pushed into `action_points`) — LM1/LM2 are now true landmarks, not action points. Updated test fixtures.
- **Decided:** Landmarks = localization + nav targets reached by landmark id; stations reference them via `seer_lm`; no station claims an `ap_id` (live map has zero action points). Only LM1+LM2 exist and both are landmarks.
- **Next:** Founder to confirm physical mapping (AP1=LM1 Almox/supplier, CB1=LM2 Linha/consumer) and return-button OPC UA node IDs (021/022 vs reusing 011/012). **Flag:** `1007.smap` actually parses landmarks `[LM1, LM2, LM4]` — there's an LM4 in the map file; confirm whether LM4 should exist or be removed.
- **Refs:** `backend/app/config.py`, `backend/app/smap.py`, `backend/tests/test_preflight.py`; preflight runner 6/6 passed, validate_stations warnings: [] against both real maps.

## 2026-06-03 — Real W3-600B 3D mesh in app(dev/test) + GPL-3.0 notes doc
- **Done:** Replaced the placeholder box in the opt-in 3D preview with the **real SEER W3-600B chassis mesh**. Fetched `base_link_v2_simp.stl` (GilmarCorreia/sim_models) via proxy, converted via in-repo three.js STLLoader→GLTFExporter (mm→m scale 0.001, re-centered, floor-aligned) + Draco → **`public/w3_600b.glb` ~130 KB** with local Draco decoder (`public/draco/`, offline-safe for Electron). Wired into `RobotPreview3D.tsx` at the `TODO(GLB)` seam (`useGLTF` + `<primitive>`, neutral PBR fallback material, `preload`/`clear` on mount/unmount) with the to-scale **placeholder kept as graceful fallback** via Suspense + error boundary. Measured mesh bbox 0.954×0.205×0.650 m (chassis-only; casters/lidars excluded). Provenance in `public/MODEL_NOTICE.md`. typecheck/lint/build green; three/r3f/GLB stay in the **lazy chunk** (917 kB), main bundle un-bloated (446 kB). Orphan wrong `AMR.glb` gone. Wrote **`docs/W3-600B_MODEL_NOTES.md`** documenting the license posture + future path.
- **Decided:** Use the real GPL-3.0 mesh for **internal dev/test only** — copyleft triggers on **distribution**, not private use, so we're clean now. **Hard gate:** it must NOT ship in any external/customer build (vite currently copies it to `dist/`). Durable path = ask Gilmar Correia for a permissive license, else model our own clean GLB (FreeCAD/Blender pipeline) at the same swap seam; placeholder box is the license-clean fallback for shipped builds.
- **Next:** Before any external/pilot build — add build-time exclusion of `public/w3_600b.glb`+`public/draco/` (or `DEV_MODEL` flag); legal-compliance sign-off on third-party assets. Founder: confirm pilot robot is a W3-600B; choose license-ask vs own-mesh. (Heads-up: custom FE/integration subagents reported success without writes landing in the real tree — eng-lead caught & re-ran; verify tree on future runs.)
- **Refs:** `frontend/app/components/RobotPreview3D.tsx`, `frontend/app/pages/Field.tsx`, `public/w3_600b.glb`, `public/draco/`, `public/MODEL_NOTICE.md`, `docs/W3-600B_MODEL_NOTES.md`; source GilmarCorreia/sim_models (GPL-3.0)

## 2026-06-03 — Runtime map selector shipped (pick .smap live, no restart)
- **Done:** Map is now switchable at runtime from **Settings → Map file** dropdown. Backend (`backend/app/main.py`): new globals `_map_name`/`_map_lock`, traversal-safe `_maps_dir()`/`_resolve_map_path()`, and a single atomic `_apply_map()` path (load→set→validate_stations→re-feed sim walls) that startup now reuses (`SMAP_PATH` default preserved). New endpoints `GET /maps` (lists `*.smap` with `current` flag) and `POST /maps/select {name}` → hot-swaps `_map_model`, re-feeds SimProvider walls, and **broadcasts `{type:"map"}` over SSE to all clients** (store already handles it → canvas refreshes everywhere). Frontend: `getMaps()`/`selectMap()` in `api/fleet.ts`, hardcoded `InnovationBox.smap` span replaced by a `<MapSelector/>` (fetch-on-mount, optimistic select, revert-on-error) in `Settings.tsx`. typecheck + lint clean; SIM smoke verified walls re-fed 699→57 on switch, traversal/unknown/missing all 400. Backend+frontend built in parallel, integrated first try.
- **Decided:** Selection limited to `.smap` files already in `maps/` (no upload), validated against path traversal; switching is a rare control action guarded by a lock, never touches the 10Hz hot path. Default still via `SMAP_PATH` env.
- **Next:** (optional) surface backend's specific error string in the selector via `_jsonOrError`; add a focused `/maps` pytest. Founder: confirm if map upload/import is wanted later.
- **Refs:** `backend/app/main.py` (`66b0278`), `frontend/app/api/fleet.ts` (`5957af8`), `frontend/app/pages/Settings.tsx`

## 2026-06-03 — AMR render shipped: to-scale 2D footprint + isolated 3D preview
- **Done:** **Phase 1** — robot now renders to real-world scale in Field view. Added a data-driven `footprint` field to the Robot model (`types.ts` + `models.py`, serialized into the SSE world payload) with a shared default constant; `MapCanvas` draws a status-colored rounded-rect at `length·scale × width·scale` rotated by θ (replacing the hardcoded `bodyR=10` circle), heading/label/battery/selection preserved. **Phase 2** — opt-in, isolated 3D preview: lazy-loaded `RobotPreview3D.tsx` (react-three-fiber + drei: orbit, grid, lighting) renders a **to-scale procedural chassis box** sized from the footprint, with a single marked `TODO(GLB)` swap point for a future real mesh. three.js is a separate chunk loaded only on the "3D" toggle (mimics the Laser toggle) — zero cost to the initial bundle / 10 Hz SSE path. typecheck + lint + `tsc && vite build` all green; three.js confirmed lazy-split out of the initial bundle.
- **Decided:** Robot dimensions = **founder-confirmed spec L×W×H = 0.95 × 0.65 × 0.25 m (with bumper strip)** — applied across FE/BE/3D (`DEFAULT_FOOTPRINT={length:0.95,width:0.65}`, `DEFAULT_HEIGHT_M=0.25`). The `.smap` carries no robot size (only map bounds + resolution), so size lives in the robot model as data, not hardcoded. **`AMR.step` was NOT usable as a mesh:** every conversion (cascadio/OCCT → trimesh inspection: 10 parts, ~3.7k verts, AABB ~0.065×0.090×0.029 m) showed it's a thin bracket/fastener **sub-part**, not the full chassis. We did **not** fake a robot from it — kept the honest to-scale box and **removed the orphan `public/AMR.glb`**. A real in-app mesh awaits a proper **full-assembly** STEP/GLB export from the founder. 3D stays an isolated opt-in panel, never in the 10 Hz hot path or the 2D source-of-truth map.
- **Course-correct:** A specialist briefly overrode the founder's confirmed dims with online-researched values (a guessed third-party model + its license concerns) — **rejected and reverted.** Founder's verbatim spec is the single source of truth; no invented provenance in code or docs.
- **Next:** Founder — provide a full-assembly STEP/GLB if you want the real mesh in the 3D panel (one-line swap at the `TODO(GLB)`); eyeball the on-map footprint + 3D box scale on a real map. (optional) per-robot footprint from real hardware config instead of the shared default.
- **Refs:** commits `10873ac`, `2cd4bca`; `frontend/app/api/types.ts`, `components/{MapCanvas,RobotPreview3D}.tsx`, `pages/Field.tsx`, `backend/app/models.py`, `docs/phase2-3d-preview.md`

## 2026-06-03 — OPC UA → MQTT migration study (planning only, no change)
- **Done:** CTO produced a decision-grade study on whether to move plant-floor call-button signaling from OPC UA to MQTT. Saved to `docs/OPCUA_VS_MQTT_STUDY.md` (honest protocol comparison for our exact use case, "who produces the signal" analysis, recommendation, high-level migration plan, risks + cheapest experiment, mini-ADR).
- **Decided:** **Stay on OPC UA for the pilot — do not migrate now.** MQTT/Sparkplug is a multi-site/IIoT scale play, not a pilot necessity; migrating now would *add* infra (broker + PLC→MQTT bridge) for zero SLA benefit and re-spend our hardened S2 OPC UA work. Cheap insurance = (later) refactor the button driver behind a `CallButtonProvider` interface (mirror Sim↔SEER) so MQTT is a plug-in if a plant ever requires it. Founder confirmed: no change for now.
- **Next:** Fold ONE question into the plant node-id conversation — "buttons via OPC UA or MQTT/Sparkplug, and who owns the bridge?" Their answer decides everything. Revisit at multi-site scale.
- **Refs:** `docs/OPCUA_VS_MQTT_STUDY.md`, `docs/OPCUA_INTEGRATION.md`, `backend/app/opcua/`

## 2026-06-03 — Devices & Callbuttons config + diagnostics (floor-prep) shipped
- **Done:** Made robots and callbuttons **editable + testable from the UI** so the founder can configure and verify everything before going on-floor. **Robots:** full CRUD — add by IP (id/name/battery/pose auto-pulled from the robot via SEER, connection ✅/❌ shown), edit IP (rebuilds the SEER connection, no full restart), re-probe, delete. **Callbuttons:** edit `opcua_node`/`opcua_ret` per station + a **Test** button (`POST /opcua/test`) that reads the node and returns value/clear error/"no endpoint" — never a 500. Config now **persists across restart** via a JSON store (`backend/app/devices.json`, seeded from `config.ROBOTS`/`STATIONS` on first run; `config.*` patched in place so all existing readers keep working). New endpoints: `POST/PUT/DELETE /robots`, `POST /robots/<id>/probe`, `PUT /stations/<id>`, `POST /opcua/test`. **66 backend tests green** (+18 new), tsc 0 errors, ESLint 0 warnings. 10Hz SSE loop + dispatcher untouched.
- **Decided:** Persist device config in a JSON store (lowest-risk vs schema migration) seeded from the hardcoded config; hot-rebuild the SEER conn / OPC UA subscription on edit rather than forcing a process restart.
- **Next:** Confirm on real hardware — the SEER `robot_status_info_req` field names (model/battery keys are best-effort guesses) and that an edited IP / OPC UA node takes effect live without restart. Optional: `device_update` SSE event for instant multi-client refresh.
- **Refs:** `backend/app/{store.py,models.py,dispatcher.py,provider.py,main.py}`, `backend/app/seer/{provider.py,robot_conn.py}`, `backend/app/opcua/__init__.py`, `frontend/app/pages/{Devices,Callbuttons}.tsx`, `frontend/app/api/{types,fleet}.ts`; tests `test_devices_api.py`, `test_opcua_driver.py`

## 2026-06-03 — Project kickoff: to-scale AMR render in Field view (STEP → app)
- **Done:** Recon of the viz stack for the founder's `AMR.step` (Onshape/STEP AP242). Findings: `MapCanvas` is **2D SVG top-down**, robot is a hardcoded `bodyR=10` circle with **no real-world scale**; **no robot-dimension field exists** anywhere (frontend `types.ts`, backend `models.py`/`smap.py`); **no 3D libs** installed. Corrected a wrong assumption: the **scale reference is NOT in the `.smap`** (it only carries map bounds + `resolution` 0.02 m/px) — the true robot footprint comes from the **STEP file's own CAD units** (bounding box).
- **Decided:** Two-track, phased to not disrupt in-flight features. **Track A (offline asset pipeline):** convert `AMR.step` → `AMR.glb` (+ extract true L×W×H) once, commit the lightweight asset; no runtime STEP parser. **Track B (render):** **Phase 1** — data-driven, to-scale **top-down footprint** on the existing SVG map (correct scale, low risk, ships first). **Phase 2** — optional **3D "bonitinho" preview** panel (react-three-fiber + drei) loading the GLB, isolated from the 10Hz SSE hot path. Add a `footprint`/`dimensions` field to the robot model so size is data-driven, not hardcoded.
- **Next:** senior-engineer runs Track A (pipeline + dims) → Phase 1 footprint; cto-architect signs off the GLB pipeline + 3D panel isolation; defer Phase 2 until current feature work lands. Founder: confirm real robot model (length/width/height) so we sanity-check the STEP bbox.
- **Refs:** `AMR.step`, `frontend/app/components/MapCanvas.tsx`, `frontend/app/pages/Field.tsx`, `frontend/app/api/types.ts`, `backend/app/{models,smap}.py`

## 2026-06-03 — Relocalization-assist loop (backend) shipped + full-day plan
- **Done:** Built **Feature 3** (nearest-landmarks API `GET /api/relocalize/suggestions` — robot_id or explicit pose, meters frame, sorted+clamped, proper 4xx/409) and **Feature 4** (dispatcher recovery-alarm enrichment — structured SSE payload `action=RELOCALIZE_ASSIST_V1` with last_pose/reason/suggestions_url/incident_id, **latched** so it fires once per incident and re-arms after recovery). 45 backend tests green (was 36). Frontend `AlarmMsg.payload` typed for the UI engineer. Team planned the full day; marketing delivered full PT-BR landing copy.
- **Decided:** Product name recommendation = **FluxoFleet** (PT/EN-friendly, needs trademark check). Landing = static React/Tailwind route, single CTA "Solicitar piloto", mailto/WhatsApp today. **Defer** handshake floor-proofing (F6) + full runbook (F7) to next week. Landmarks have no theta/name in `.smap` (id/x/y only) — suggestions use lm_id as name, theta null.
- **Next:** Feature 5 — Assist UI panel (consume alarm payload → fetch suggestions → one-click fill X/Y/θ → reuse /relocalize). Then landing page v1. Founder: confirm name + 2 app screenshots + contact email.
- **Refs:** `backend/app/smap.py`, `main.py`, `dispatcher.py`, `models.py`, `frontend/app/api/types.ts`; product day plan + marketing copy

## 2026-06-03 — Repo hygiene: build artifacts untracked + recovered lost files
- **Done:** Fixed `.gitignore` — added a clean `# Build artifacts` block (`dist`, `dist-electron`, `release`) and removed the duplicate stray `dist`. Untracked already-committed artifacts without deleting from disk (`git rm --cached`): `dist-electron` (2 files), `dist` (3 files). Restored `TIMELINE.md`, `CLAUDE.md`, `run-backend.bat` from HEAD — they'd been deleted from the working tree (unstaged, pre-existing; not caused by the artifact untrack). Left unstaged for founder review (not committed).
- **Decided:** Build outputs stay out of version control (regenerated by `npm run build`). Kept `electron/` as a top-level sibling — rejected moving it under `frontend/`: main/preload is the privileged desktop host, not renderer code, and the main/renderer split is a security boundary worth keeping visible. No monorepo tooling (overhead for solo founder mid-pilot).
- **Next:** Optional follow-up hygiene pass for other tracked runtime artifacts (`__pycache__/*.pyc`, `backend/fleet.db`). Founder to confirm before commit.
- **Refs:** `.gitignore`; cto-architect layout review

---

## 2026-06-02 — Timeline consolidated + history rewritten
- **Done:** Snapshotted the previous `TIMELINE.md` into `context/TIMELINE_snapshot_2026-06-02.md` (untouched backup) and rewrote the "Project history" section to be tighter and current — now covering the engineering hardening sprints (S0–S4), the no-hardware pivot (dual-pose sim, preflight), and the laser/LiDAR layer that the old narrative stopped short of.
- **Decided:** Dated log = canonical running record; narrative = concise evolution story. Both live in one file; raw backups go to `context/`.
- **Next:** keep appending dated entries as work lands; refresh the narrative only at major phase boundaries.
- **Refs:** `TIMELINE.md`, `context/TIMELINE_snapshot_2026-06-02.md`

## 2026-06-02 — LiDAR/laser-scan visualization shipped (sim-first)
- **Done:** Reverse-engineered the SEER laser API the founder was missing — `robot_status_laser_req = 1009` on port 19204, response `laser_beams` = list of `[x,y]` points already in **world/map frame** (from netprotocol PDF p.24). Built end-to-end: backend `GET /robots/<id>/laser` pull endpoint (off the 10Hz SSE path, ~2Hz, `step` decimation); `SeerProvider.laser()` for real robot; `SimProvider.laser()` synthesizes a realistic scan via ray-cast against `.smap` walls from est_pose (works fully offline); Field "Laser" toggle + `MapCanvas` renders beams over the map. Deterministic backend test + lint/tsc clean.
- **Decided:** Transport = dedicated pull endpoint polled only while the layer is ON (not in world SSE) to protect the 10Hz loop. Render directly with world→pixel transform (no pose composition) per PDF contract.
- **Next:** Confirm on first real robot that `laser_beams` is truly world-frame `[x,y]` (vs robot-relative/angle-distance) — flagged in code at all 3 sites. Fast-follows available nearly free: 1010 planned-path overlay, 1006 block-point marker.
- **Refs:** commit `8dd8905`; `backend/app/seer/protocol.py`,`robot_conn.py`,`provider.py`, `backend/app/provider.py`, `main.py`, `frontend/app/pages/Field.tsx`, `components/MapCanvas.tsx`

## 2026-06-02 — No-robot pivot: "Pilot Hardening" runs fully in sim
- **Done:** Founder has no physical robot access right now. CTO designed a no-hardware path: turn `SimProvider` into a **dual-pose localization model** (true pose vs estimated pose + confidence decay / loss / mislocalization / relocalize-success-by-proximity) so the recovery FSM and relocalization-assist loop are exercised end-to-end in sim with deterministic tests. Defined the honest "irreducible 60-min on-robot confirmation checklist" (TCP semantics, relocalize tolerances, STOP/RESUME, map alignment, OPC UA node wiring) — everything else ships from sim.
- **Decided:** Build order = preflight config validation → dual-pose sim model → nearest-landmarks API → recovery-alarm enrichment → assist UI → handshake floor-proofing → dry-run runbook. The eventual robot session becomes a *confirmation*, not discovery.
- **Next:** senior-engineer builds steps 1–2 (preflight + sim localization model) first (shippable + tested); then chain the assist API/UI. GTM SOW proceeds in parallel.
- **Refs:** cto-architect design; `backend/app/provider.py`, `dispatcher.py`, `smap.py`

## 2026-06-02 — Next-sprint decision: "Pilot Hardening" (team review)
- **Done:** Full team review (product-manager + domain-expert + gtm-sales). Strong convergence: plumbing is strong, but a real pilot dies on (a) relocalization-assist being only a manual endpoint, not a guided workflow; (b) the 2-button handshake surviving demo but not real shift behavior (timeouts, dedup, deadlocks, "who acts next"); (c) recovery FSM never validated on real SEER signals.
- **Decided:** Next sprint = **Pilot Hardening** (relocalization-assist v1 + handshake floor-proofing + preflight config validation + real-robot dry-run runbook). In parallel, GTM **formalizes the warm site into a paid, time-boxed pilot SOW** with a go/no-go date. The one pilot metric = **on-time delivery SLA to the consumer station**. De-risk first with the cheapest experiment: one real robot, real map, prove pose-frame sanity + relocalize recovery BEFORE building more.
- **Next:** senior-engineer/cto-architect scope Sprint "Pilot Hardening"; gtm-sales drafts 1-page pilot SOW; founder confirms OPC UA node IDs + plant access.
- **Refs:** delegations (PM/domain/GTM), `docs/OPCUA_INTEGRATION.md`

## 2026-06-02 — Sprints 0–4 shipped (engineering)
- **Done:** S0 cleanup (deleted dead swarm/ML UI, live Dashboard). S1 failure-recovery FSM (fixed real bug: failed nav was treated as arrival; re-queue + cooldown + park + alarms, 6 tests). S2 OPC UA hardening (backoff reconnect, per-node subscribe, debounce, seed-on-connect; fixed real node-id-matching bug; mock server + 4 tests + plant checklist). S3 operator completeness (/jog, software STOP-ALL/RESUME, telemetry/history/stats; UI jog d-pad, global STOP button, analytics strip; 10 tests). S4 tooling hygiene (ESLint 9, lint 0 warnings, tsc 0 errors, soak/telemetry committed).
- **Decided:** Software STOP-ALL is explicitly NOT a hardware E-stop (labeled in 3 UI places). Provider abstraction (Sim↔SEER) keeps dispatch logic hardware-agnostic.
- **Next:** validate recovery on real hardware; build relocalization-assist (see entry above).
- **Refs:** commits `0ea0a03`→`27487e2`, `eslint.config.mjs`, `backend/tests/`

## 2026-06-02 — Repo tidy-up (Repo Steward)
- **Done:** Merged `HISTORICO.md` into `TIMELINE.md` (rich history now the "Project history" section below the log) and removed the duplicate. Moved loose strategy docs to `docs/` (ACTION_PLAN, COMPETITOR_ANALYSIS, PRICING_STUDY, Guidelines). Kept `CLAUDE.md` at root (tooling file). Fixed references to moved files.
- **Decided:** `TIMELINE.md` is the single canonical project log; `docs/` holds strategy/analysis docs; tooling files stay at root.
- **Next:** Repo Steward sweeps after future changes so clutter never accumulates.
- **Refs:** `docs/`, `TIMELINE.md`

## 2026-06-02 — Estudo de precificação + análise de concorrentes
- **Done:** Pesquisa de mercado (competitive-analyst + market-specialist). Salvo em `docs/PRICING_STUDY.md` e `docs/COMPETITOR_ANALYSIS.md`.
- **Decided:** Preço = modelo **híbrido** (setup único + por-robô/mês). Piloto: R$12–18k setup + R$1.5–2.5k/mês (≤5 robôs). Escala: R$300–450/robô/mês. Âncora de mercado = Meili FMS €500/mês.
- **Next:** gtm-sales transforma em proposta de piloto; finance monta unit economics; validar preço em discovery real.
- **Refs:** `docs/PRICING_STUDY.md`, `docs/COMPETITOR_ANALYSIS.md`

## 2026-06-02 — AI team + project tracking set up
- **Done:** Built the AI-agent "company" in `.github/agents/` (CEO hub + 10 specialists). Made agents answer-first/concise. CEO became the single point of contact (hub-and-spoke). Added Senior Software Engineer. Started this timeline.
- **Decided:** Talk only to the CEO; it delegates and synthesizes. CEO owns and updates this timeline. Engineers commit to git constantly.
- **Next:** Resolve "app won't open" (suspected `Callbuttons.tsx`); implement real `1007.task` (LM1↔LM2) on dispatch; confirm return-button OPC UA node IDs.
- **Refs:** `.github/agents/`, commit `911ff5e`

<!-- Add new entries ABOVE this line, newest first. -->

---

# Project history (narrative background)

> Folded in from the former HISTORICO.md (rich narrative of how the project evolved). The dated log above is the running record; this section is the deeper background.

# 📜 Histórico do Projeto — da BehaveX à Orquestração de Frota AMR

> Documento vivo. Linha do tempo das features, decisões de arquitetura e marcos do projeto.
> Mantido como memória do que foi construído e por quê. Atualizar a cada marco relevante.
>
> Última atualização: **2026-06-02**

---

## 🧭 Resumo em uma frase

Começou como **BehaveX** — um dashboard React de simulação de enxames (swarm), só frontend com dados mock — e virou um **app desktop de orquestração de frota de AMRs industriais** (Electron + React + backend Flask), integrado a robôs SEER via TCP e a botões de chamada (callbuttons) de chão de fábrica via OPC UA.

---

## 🗓️ Linha do Tempo

### Fase 0 — BehaveX: dashboard de simulação de swarm  _(~abr/2026)_
O ponto de partida. Aplicação **somente frontend**, dados mockados no cliente, sem backend.

- **Stack:** React + TypeScript + Vite + Tailwind v4, tema dark estilo GitHub (`#0d1117` / `#58a6ff`), shadcn/ui (50+ componentes), React Router v7.
- **Marca/identidade:** "AeroNet v2.4.1".
- **Telas:**
  - `/` Dashboard — experimentos recentes, runs ativos, métricas
  - `/experiment/:id` — canvas de simulação com playback (500 steps, 12 agentes)
  - `/comparisons` — visão dupla lado a lado com diff de métricas (divergência destacada nos steps 150–200)
  - `/configs` — config de política de comportamento (URL GitHub, seeds, nº de agentes, densidade de obstáculos)
- **Estado:** simulação via `useState` + `useEffect` (intervalos), engine mock (`useSimEngine`).
- **Backlog documentado:** `docs/ACTION_PLAN.md` (2026-04-25) catalogou **18 itens de UI não implementados** — 11 botões "mortos", 2 interações quebradas (scrubber de timeline, validação de URL), 3 rotas placeholder, 2 implementações mock.
- **Ideia futura (na época):** otimização GPU/ML no Mac (mlx / WebGPU / ONNX) e um backend FastAPI servindo inferência real via WebSocket para substituir o engine mock.

> 🔑 **Decisão de fundação:** todo o estado de simulação era client-side. Isso forçou, mais tarde, a separação clara entre UI e um motor/backend real.

---

### Fase 1 — Aprendendo o robô SEER: protocolo, mapas e visualizadores  _(maio/2026)_
Mergulho no ecossistema **SEER Robotics** (a base dos AMRs). Foco em **entender o protocolo e os mapas** antes de integrar.

- **Protocolo Robokit Netprotocol** estudado e documentado (`context/README.md`): formato de pacote (magic `0x5A`, header 16 bytes big-endian + payload JSON) e portas:
  - `19204` estado/localização/bateria · `19205` controle de movimento/relocalização · `19206` tarefas de navegação · `19210` I/O digital.
- **Scripts de referência** (`context/`): demos de giro, relocalização, leitura de I/O, query de erros, etc. (`rbkDemo*.py`, `rbkApi*.py`).
- **Parser de mapas `.smap`** (formato RoboShop Pro / Protobuf-as-JSON):
  - `ANALISE_REPOSITORIO_SEER.md` — engenharia reversa da estrutura (`header`, `normalPosList`, `normalLineList`, `advancedPointList`, `advancedAreaList`…), descoberta de que os campos são **camelCase** (`minPos`, `maxPos`).
  - `RESUMO_ALTERACOES.md` — carregamento automático do `.smap` local (landmarks, paredes, pontos navegáveis, posição inicial, limites do mapa).
  - `RESUMO_MODO_OFFLINE.md` — **modo offline** nos visualizadores + cadeia de fallback (`.smap` local → robô via API → mapa vazio) e correção de bugs de parsing (JSON compacto em linha única, campos aninhados).
- **Visualizadores Python:** `visualizador_auto.py`, `visualizador_offline.py`, `visualizador_robo.py`, `visualizador_multi_robo.py` — render do mapa + posição do robô (com e sem robô conectado).
- **Mapas reais:** `maps/InnovationBox.smap`, `maps/1007.smap`.

> 🔑 **Aprendizado-chave:** o robô fala TCP + JSON, e os mapas têm tudo que precisamos (landmarks/estações = `advancedPointList`). Dá pra desenvolver **offline** com o `.smap` — isso virou princípio de arquitetura (Sim provider).

---

### Fase 2 — O pivô: de simulação de swarm para orquestração de frota  _(final de maio/2026)_
A BehaveX deixa de ser brinquedo de simulação e vira **plataforma de orquestração de frota AMR** real. O frontend foi reaproveitado; nasce o backend.

- **Nova arquitetura (3 camadas):**
  - **Electron** (`electron/main.ts` + `preload.ts`) — wrapper desktop.
  - **Frontend React** — reescrito para operação de frota.
  - **Backend Flask** (porta `8765`) — REST + **SSE `/events`** (stream ~10 Hz), `fleet.db` (SQLite) para telemetria.
- **Novas telas:** `/` Dashboard (visão da frota), `/field` (mapa/posições ao vivo), `/devices` (inventário de robôs), `/calibration` (+ `/:robotId`, jog manual), `/tasks` (definição/despacho), `/callbuttons` (vínculos OPC UA), `/settings`.
- **Backend modular:**
  - `models.py` — `Robot`, `Station`, `Task`, `MapModel` + máquinas de estado (status do robô e da tarefa).
  - `dispatcher.py` — máquina de estados da frota (asyncio): atribuição do melhor robô ocioso (distância + bateria), travas por estação (1 tarefa por pickup), auto-carga (<25% bateria), coalescência de chamadas.
  - `provider.py` — interface `Provider` + `SimProvider` (move robôs fake rumo ao goal) → **dev 100% offline**.
  - `seer/` — `protocol.py` (codec TCP), `robot_conn.py` (conexão por robô), `provider.py` (`SeerProvider` mapeia estações → landmarks SEER).
  - `db.py` + `telemetry.py` — persistência e captura dupla (JSONL + SQLite) com `run_id`/`cycle_id`/`step`.
  - `smap.py` — parser `.smap` portado para o backend.

> 🔑 **Decisão de arquitetura:** abstração `Provider` (Sim ↔ SEER) — mesma lógica de despacho roda em simulação ou em robô real. Foi o que permitiu evoluir rápido sem hardware na mesa.

---

### Fase 3 — ⚡ O sprint dos Callbuttons  _(quinta 28 e sexta 29/maio/2026)_
**O grande salto.** Em dois dias o projeto saiu de "peças soltas" para um **fluxo ponta-a-ponta funcionando** com botões de chamada de chão de fábrica.

- **Driver OPC UA** (`opcua/callbuttons.py`, lib `asyncua`): assina nós booleanos das estações, detecção de **borda de subida** (False→True = botão pressionado) → `dispatcher.button_pressed(station_id, direction)`, com reconexão (backoff ~10s).
- **Fluxo pareado supplier→consumer:** ex. **Almox → Linha**, com estados de pressão (`idle`/`ready`/`called`/`served`) e direção (`fwd`/`ret`). UI em `Callbuttons.tsx`.
- **Resultado:** apertar o botão físico → backend cria/atribui tarefa → robô (sim ou SEER) é despachado → estado reflete na UI ao vivo via SSE.
- **Marco em git:** commit `ec7357e` "mudanças de hoje" (sex **29/05**) — primeira versão do repositório com a integração funcionando.

> 🏁 **Por que importa:** este é o "momento da verdade" do produto — o gatilho real do operador no chão de fábrica dispara a frota. É a feature que prova o valor (one pilot done well).

---

### Fase 4 — Consolidação "all the features"  _(terça 02/jun/2026)_
- **Marco em git:** commit `911ff5e` "Last version with all the features".
- Estado consolidado: 7 telas + backend modular + Sim/SEER + OPC UA + telemetria.
- Onboarding do "time de agentes de IA" (CEO + especialistas) como forma de trabalho — CEO é o ponto único de contato e mantém esta timeline.

---

### Fase 5 — Endurecimento de engenharia (Sprints 0–4)  _(02/jun/2026)_
De "tudo funciona na demo" para "aguenta turno real". Cinco sprints encadeados:

- **S0 — Limpeza:** removidas as telas/ML mortas da era BehaveX (swarm, ws-bridge); Dashboard ligado a dados ao vivo; `CLAUDE.md` reescrito.
- **S1 — Recuperação de falhas (FSM):** corrigido bug real — navegação falha era tratada como chegada. Agora há re-fila, cooldown, park, offline/stuck/bateria e alarmes (6 testes). `arrived()` ⇒ só `TASK_FINISHED`.
- **S2 — Endurecimento OPC UA:** reconexão com backoff, subscribe por nó, debounce, seed na conexão; corrigido bug real de match de node-id. Mock server + 4 testes + checklist de planta.
- **S3 — Completude do operador:** `/jog`, STOP-ALL/RESUME por software, telemetria/histórico/stats; UI com d-pad de jog, botão global STOP e faixa de analytics (10 testes).
- **S4 — Higiene de tooling:** ESLint 9 (0 warnings), `tsc` (0 erros), soak runner + telemetria firehose commitados.

> 🔑 **Decisão:** STOP-ALL de software **não** é E-stop de hardware (rotulado em 3 lugares da UI). A abstração `Provider` mantém o despacho agnóstico de hardware.

---

### Fase 6 — Pilot Hardening sem hardware  _(02/jun/2026 — hoje)_
Founder sem acesso a robô físico no momento → estratégia de provar tudo em simulação, deixando a sessão no robô como **confirmação**, não descoberta.

- **Preflight + readiness:** validação de config na subida + `/health` reporta prontidão.
- **Modelo de dupla pose no `SimProvider`:** pose verdadeira vs. pose estimada + confiança (decay/perda/mislocalização/relocalize por proximidade) → o FSM de recuperação e o loop de relocalização-assist rodam ponta-a-ponta em sim, com testes determinísticos.
- **Camada LiDAR/laser:** engenharia reversa da API SEER (`1009` na 19204, `laser_beams` = `[x,y]` em frame do mapa). Endpoint pull `GET /robots/<id>/laser` (~2Hz, fora do SSE 10Hz), `SimProvider.laser()` via ray-cast contra paredes do `.smap` (offline) e `SeerProvider.laser()` para robô real; toggle "Laser" no Field renderiza os feixes.

> 🔑 **Decisão estratégica (revisão de time):** próximo foco = **Pilot Hardening** (relocalização-assist guiada + handshake à prova de turno + preflight + runbook de dry-run no robô). GTM formaliza o site morno num **piloto pago time-boxed**; métrica única = **SLA de entrega on-time na estação de consumo**.

---

## 🧩 Inventário atual de features  _(snapshot 2026-06-02)_

### Frontend (Electron + React + Vite + Tailwind v4)
| Rota | Tela | Função |
|------|------|--------|
| `/` | Dashboard | Visão geral da frota: robôs ativos, tarefas, alarmes |
| `/field` | Field | Mapa SVG ao vivo, posições dos robôs, criação manual de tarefa |
| `/devices` | Devices | Tabela da frota: IP, status, bateria, posição, tarefa atual |
| `/calibration` | Calibration | Jog manual do robô (frente/trás/giro/stop), por robô |
| `/tasks` | Tasks | Lista de tarefas ativas/histórico com badges de estado |
| `/callbuttons` | Callbuttons | Fluxo pareado de botões (Almox→Linha) via OPC UA |
| `/settings` | Settings | URL do backend, status de conexão, health check |

- Componentes: `Layout` (sidebar, 7 itens), `MapCanvas` (transform metros→pixels, robôs/estações/paredes), kit shadcn/ui (50+).

### Backend (Flask + asyncio + Python)
| Módulo | Função |
|--------|--------|
| `main.py` | Flask :8765, SSE `/events` ~10 Hz, REST (robots/tasks/stations, `/health` readiness, POST callbutton/relocalize, `/robots/<id>/laser`, `/jog`, STOP-ALL/RESUME) |
| `models.py` | `Robot`/`Station`/`Task`/`MapModel` + máquinas de estado + campos de recuperação |
| `dispatcher.py` | Despacho da frota: melhor robô ocioso, travas de estação, auto-carga, recuperação de falhas (re-fila/cooldown/park) |
| `provider.py` | Interface `Provider` + `SimProvider` (dev offline, dupla pose + laser sintético) |
| `seer/protocol.py` | Codec TCP Netprotocol (ports 19204/19205/19206/19210) + laser `1009` |
| `seer/robot_conn.py` · `seer/provider.py` | Conexão por robô + `SeerProvider` (estação→landmark, laser real) |
| `opcua/callbuttons.py` | Driver OPC UA, detecção de borda de subida (backoff, debounce) |
| `smap.py` | Parser de mapas `.smap` (SEER) |
| `db.py` · `telemetry.py` | SQLite `fleet.db` + captura dupla (JSONL + SQLite) |
| `soak.py` | Runner de soak test (cycle/step) para fidelidade de dados |

### Plataforma
- **Electron** v33 (build macOS `.dmg`, appId `com.behavex.app`).
- **Mapas:** `maps/InnovationBox.smap`, `maps/1007.smap`.
- **App:** `behavex` v`0.1.0`.

---

## 🧱 Decisões de arquitetura (e como mudaram)

| # | Decisão | Antes | Agora | Por quê |
|---|---------|-------|-------|---------|
| 1 | Origem dos dados | Mock client-side (BehaveX) | Backend Flask + SSE ao vivo | Operação real de frota exige estado de servidor |
| 2 | Abstração de robô | — | Interface `Provider` (Sim ↔ SEER) | Desenvolver e testar sem hardware |
| 3 | Gatilho de tarefa | Botão de UI | **Callbutton físico via OPC UA** | Fluxo real de chão de fábrica |
| 4 | Mapas | Hardcoded/mock | Parser `.smap` real (SEER) | Posições/landmarks reais |
| 5 | Persistência | Nenhuma | SQLite + JSONL firehose | Telemetria e soak tests |
| 6 | Empacotamento | Web only | Electron desktop | Implantação no cliente |
| 7 | Validação sem robô | Só na demo/robô | Sim de dupla pose + testes determinísticos | Provar FSM/relocalização offline; robô vira confirmação |

---

## 🗺️ Próximos passos  _(sprint "Pilot Hardening")_
- Relocalização-assist v1: de endpoint manual para **workflow guiado** (nearest-landmarks API + UI de assist).
- Handshake do callbutton à prova de turno: timeouts, dedup, deadlocks, "quem age a seguir".
- Confirmar no **primeiro robô real**: frame do `laser_beams` ([x,y] mundo vs. relativo), tolerâncias de relocalização, STOP/RESUME, alinhamento de mapa, node IDs OPC UA (≈60 min de checklist).
- GTM: fechar o site morno como **piloto pago time-boxed** com data de go/no-go.

---

## ✏️ A adicionar (pendências de memória)
- [ ] **Rascunhos de arquitetura original** (papel) — o founder vai enviar; documentar como foi pensada vs. como ficou.
- [ ] Datas exatas da Fase 0 (BehaveX) e Fase 1 (pré-git, anteriores a 29/05).
- [ ] Screenshots/GIFs de cada marco (Dashboard BehaveX → Field AMR → Callbuttons → Laser).
- [ ] Lista nominal de bugs marcantes resolvidos no sprint dos callbuttons.

---

_Notas: a história anterior a 29/05/2026 é anterior ao git (reconstruída a partir do código, dos docs em `context/` e do `docs/ACTION_PLAN.md`). Datas dessas fases são aproximadas._
