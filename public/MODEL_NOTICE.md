# 3D Model Notice

- **Source:** GitHub — [GilmarCorreia/sim_models](https://github.com/GilmarCorreia/sim_models)
- **License:** GPL-3.0
- **Author:** Gilmar Correia
- **Parts (full W3-600B assembly):**
  - `base_link_v2_simp` — chassis body
  - left + right drive wheels
  - 4 casters (each: 1 fork + 2 discs)
  - back + front lidars
  - up + down cameras
  - tray

> **INTERNAL DEV/TEST USE ONLY — do not distribute in a proprietary build; see
> `docs/W3-600B_MODEL_NOTES.md`.**

The shipped `w3_600b.glb` is the FULL multi-part SEER W3-600B robot assembled from
the source meshes above (mm → m, re-centered in X/Z, rests on the floor at y=0). Each
part's URDF colour is baked in as a glTF material (blue body, dark wheels/discs,
silver sensors/forks, gray tray), and the asset is Draco-compressed for the offline
desktop preview.
