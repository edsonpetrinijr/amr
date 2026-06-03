# W3-600B 3D Model — Usage & License Notes

> **TL;DR:** We use the SEER **W3-600B** 3D mesh in the app **for internal dev/test only**.
> The source is **GPL-3.0**, so this asset **must NOT ship in any distributed or
> commercial build** until it is removed or replaced with a license-clean mesh.
> Status: ✅ wired into the 3D preview panel · ⛔ blocked from external/customer builds.

---

## 1. What this is

- **Robot:** SEER Robotics **W3-600B** — a differential-drive logistics AMR with a
  motorized payload tray (our pilot's robot class).
- **Asset in app:** `public/w3_600b.glb` (~130 KB, Draco-compressed) + local Draco
  decoder at `public/draco/`. Derived from the chassis mesh `base_link_v2_simp.stl`.
- **Where it renders:** the opt-in **3D preview panel** (`RobotPreview3D.tsx`),
  behind the "3D" toggle in the Field view. It replaces the to-scale placeholder box;
  the placeholder is kept as a **graceful fallback** if the GLB fails to load.
- **Source repo:** [`GilmarCorreia/sim_models`](https://github.com/GilmarCorreia/sim_models)
  — author **Gilmar Correia**.

### Measured geometry (after mm→m scaling)
| Axis | Extent | Notes |
|------|--------|-------|
| Length (X, forward) | **0.954 m** | chassis-only; casters/lidars excluded |
| Height (Y, up) | **0.205 m** | chassis body only (tray/lidars add height) |
| Width (Z, lateral) | **0.650 m** | matches the URDF tray/chassis width exactly |

> Authoritative full-robot dimensions (from the W3-600B URDF) are
> **0.85 × 0.65 × 0.30 m** (lidar-to-lidar length, tray width, tray-raised height).
> These drive the data-driven 2D footprint and the placeholder box. The 3D mesh is
> chassis-only, so its bbox differs (longer/lower) — that's expected.

---

## 2. The license situation (read this before any release)

The source repo is licensed **GPL-3.0** (a strong **copyleft** license). The repo's
`package.xml` license field is literally `TODO`, but the root `LICENSE` file is
unambiguous GPLv3.

### What that means in practice
| Use | Allowed? | Why |
|-----|----------|-----|
| **Internal dev/test** (run locally, demos on our own machines, screenshots for ourselves) | ✅ Yes | GPL obligations trigger on **distribution**, not private use. |
| **Distributing our app** (Electron build to a customer / pilot site / download) with this GLB inside | ⛔ **No** | Distributing a GPL-3.0 asset would obligate us to release the **combined work** under GPL-3.0 — incompatible with our proprietary stack. |
| **Selling / commercial pilot build** containing this mesh | ⛔ **No** | Same copyleft trigger. |
| Using only the **measured dimensions/numbers** (0.85×0.65×0.30, wheel track, etc.) | ✅ Yes | Facts/measurements are not copyrightable; we already do this for the 2D footprint. |

> ⚠️ **Build-time exposure:** `vite build` currently copies `public/w3_600b.glb` and
> `public/draco/` verbatim into `dist/`. So **any** packaged build today contains the
> GPL asset. Before shipping anything externally, this file **must** be excluded or
> replaced (see §4).

*(This is a practical engineering note, not formal legal advice — get
`legal-compliance` / counsel sign-off before any external distribution.)*

---

## 3. Why we're using it now anyway

- The founder wants the **real robot** in the preview now, not a placeholder box — it
  makes the Field view read as a real fleet tool for demos/validation.
- For **internal testing**, GPL-3.0 imposes **no obligations** — we can freely use it.
- It de-risks the 3D pipeline (mesh load, scale, orientation, isolation) **today**, so
  swapping to a clean asset later is a one-file change at the marked `TODO(GLB)` seam.

---

## 4. Path to a shippable model (pick one before external release)

Ordered cheapest → most robust:

1. **Build-time exclusion (interim, fastest).** Gate the GLB out of customer builds:
   keep it for dev, strip `public/w3_600b.glb` + `public/draco/` from `dist/` in the
   release/packaging step (or behind a `DEV_MODEL` env flag). Removes legal exposure
   while we source a clean mesh. *Falls back to the placeholder box automatically.*
2. **Produce our own clean GLB.** Commission/model our own W3-600B (or generic AMR)
   mesh, or convert from a **license-clean** CAD source we own, via the offline
   FreeCAD/Blender → Draco GLB pipeline. Drop it at the same `TODO(GLB)` seam. This is
   the durable answer and removes all dependency on GPL assets.
3. **Get permission.** Ask Gilmar Correia for a permissive (MIT/Apache/BSD) or
   commercial-use license/dual-license for the W3-600B assets. Cheap to ask; if granted,
   we can ship as-is.
4. **Ship the placeholder.** The to-scale procedural box already exists and is fully
   license-clean — acceptable for a customer build if no clean mesh is ready in time.

**Recommended sequence:** ship internal/test with the real mesh now (done) → **(1)**
build-time exclusion before any external build → pursue **(3)** in parallel, fall back
to **(2)** if permission isn't granted.

---

## 5. Engineering anchors (for whoever does the swap)

- **Swap seam:** single `TODO(GLB)` region in
  `frontend/app/components/RobotPreview3D.tsx` — `useGLTF(MODEL_URL, DRACO_PATH)` →
  `<primitive>`, with `useGLTF.preload`/`useGLTF.clear` on mount/unmount.
- **Isolation guarantees to preserve:** lazy-loaded chunk (three/r3f/drei +
  GLB are NOT in the main bundle), `frameloop="demand"`, ref-based pose at ≤10 Hz,
  `React.memo`, unmounted by default. The 3D panel is **display-only** — never in any
  robot command/motion path.
- **Provenance marker:** `public/MODEL_NOTICE.md` + header comment in the `.tsx`.
- **Do NOT use** the old `AMR.glb` (was derived from `AMR.step`, which is only a
  **sub-component**, not the chassis) — wrong geometry; already removed.

---

## 6. Open decisions for the founder

- [ ] Confirm the physical pilot robot is truly a **W3-600B** (locks the 0.85×0.65×0.30 dims).
- [ ] Approve adding the **build-time exclusion (§4.1)** before any external/pilot build.
- [ ] Decide the durable path: **ask for a license (§4.3)** vs. **own clean mesh (§4.2)**.
- [ ] `legal-compliance` sign-off before any distribution containing third-party assets.

---

*Source: `GilmarCorreia/sim_models` (GPL-3.0), file `base_link_v2_simp.stl`,
author Gilmar Correia. Internal dev/test use only.*
