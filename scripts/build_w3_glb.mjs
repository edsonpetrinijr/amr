// Build the full SEER W3-600B robot GLB from cached STL parts.
// Regenerates public/w3_600b.glb from the GilmarCorreia/sim_models *_simp STLs (GPL-3.0, internal dev/test only).
// Internal dev/test only. Inputs are GPL STLs cached in scripts/stl_cache/ (not committed) —
// re-download per docs/W3-600B_MODEL_NOTES.md before re-running.
//
// Pipeline: three STLLoader -> assemble scene with baked MeshStandardMaterial colors
//           -> bake URDF base_to_world (+90deg about X) -> recenter X/Z, drop to floor
//           -> GLTFExporter (binary) -> @gltf-transform Draco compress -> public/w3_600b.glb
//
// Usage: node scripts/build_w3_glb.mjs

import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { draco, dedup, prune } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// --- Minimal FileReader polyfill so three GLTFExporter binary path works under node.
// (Node 18+ has global Blob; only FileReader.readAsArrayBuffer is needed here.)
if (typeof globalThis.FileReader === 'undefined') {
  globalThis.FileReader = class FileReader {
    readAsArrayBuffer(blob) {
      blob.arrayBuffer()
        .then((buf) => { this.result = buf; this.onloadend && this.onloadend(); })
        .catch((err) => { this.onerror && this.onerror(err); });
    }
  };
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CACHE = path.join(__dirname, 'stl_cache');
const OUT = path.join(__dirname, '..', 'public', 'w3_600b.glb');

const loader = new STLLoader();
const loadGeom = (f) => {
  const buf = fs.readFileSync(path.join(CACHE, f));
  const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
  return loader.parse(ab);
};

// One MeshStandardMaterial per distinct color, so glTF keeps per-part colors.
const matCache = new Map();
const mat = (hex) => {
  if (!matCache.has(hex)) {
    matCache.set(hex, new THREE.MeshStandardMaterial({
      color: new THREE.Color(hex), metalness: 0.1, roughness: 0.8,
      name: 'm_' + hex.replace('#', ''),
    }));
  }
  return matCache.get(hex);
};

const SCALE = 0.001; // mm -> m

// Root group holds everything in base_link frame (metres).
const robot = new THREE.Group();
robot.name = 'w3_600b';

function addMesh(file, color, name, opts = {}) {
  const geom = loadGeom(file);
  const m = new THREE.Mesh(geom, mat(color));
  m.name = name;
  m.scale.setScalar(SCALE);
  if (opts.pos) m.position.set(opts.pos[0], opts.pos[1], opts.pos[2]);
  if (opts.rotY) m.rotation.y = opts.rotY;
  robot.add(m);
  return m;
}

// 1. base body (same-origin CAD export -> [0,0,0])
addMesh('base_link_v2_simp.stl', '#3399CC', 'base_link', { pos: [0, 0, 0] });

// 2. left wheel: effective world [0, 0.0575, -0.131553]
addMesh('left_wheel_simp.stl', '#333333', 'left_wheel', { pos: [0, 0.0575, -0.131553] });

// 3. right wheel: group pos [0,0.0575,0.27875] rotY=pi, child +z 0.147197
{
  const g = new THREE.Group();
  g.position.set(0, 0.0575, 0.27875);
  g.rotation.y = Math.PI;
  const geom = loadGeom('right_wheel_simp.stl');
  const m = new THREE.Mesh(geom, mat('#333333'));
  m.name = 'right_wheel';
  m.scale.setScalar(SCALE);
  m.position.set(0, 0, 0.147197);
  g.add(m);
  robot.add(g);
}

// 4. casters: 4 corners x 3 meshes
const corners = {
  back_right: [-0.309, 0.0131, 0.248],
  back_left: [-0.309, 0.0131, -0.248],
  front_right: [0.315, 0.0131, 0.177],
  front_left: [0.315, 0.0131, -0.177],
};
for (const [cname, pos] of Object.entries(corners)) {
  addMesh('BREP_WITH_VOIDS_6008_simp.stl', '#B2B2B2', `caster_fork_${cname}`, { pos });
  addMesh('MANIFOLD_SOLID_BREP_6641_simp.stl', '#333333', `caster_inner_${cname}`, { pos });
  addMesh('MANIFOLD_SOLID_BREP_7274_simp.stl', '#333333', `caster_outer_${cname}`, { pos });
}

// 5. back lidar (same-origin)
addMesh('back_lidar_simp.stl', '#B2B2B2', 'back_lidar', { pos: [0, 0, 0] });
// 6. front lidar = same mesh, rotY=pi
addMesh('back_lidar_simp.stl', '#B2B2B2', 'front_lidar', { pos: [0, 0, 0], rotY: Math.PI });
// 7. downward camera
addMesh('downward_camera_simp.stl', '#B2B2B2', 'downward_camera', { pos: [0, 0, 0] });
// 8. upward camera
addMesh('upward_camera_simp.stl', '#B2B2B2', 'upward_camera', { pos: [0, 0, 0] });
// 9. tray
addMesh('tray_simp.stl', '#999999', 'tray', { pos: [0, 0, 0] });

// STEP 3 — frame fix. NOTE: empirically the cached simp STLs are authored ALREADY
// in the final upright Y-up frame (base_link raw bbox = X0.954 len, Y0.205 height with
// min-Y~=0, Z0.651 width; tray sits on top at Y~=0.21). This matches the existing
// chassis-only public/w3_600b.glb exactly (X0.954/Y0.205/Z0.651, min-Y 0, X/Z centered).
// Applying the URDF base_to_world +90deg-about-X here would tip the robot onto its side
// (height->0.65), i.e. "lying down" — which the spec says to FIX. So the wrap rotation
// is identity (0). PoseDriver's rotation.y=-theta heading is preserved: forward=+X, up=+Y.
const wrap = new THREE.Group();
wrap.name = 'base_to_world';
wrap.rotation.x = 0; // see note above: STLs are pre-rotated to Y-up
wrap.add(robot);
wrap.updateMatrixWorld(true);

// Bake transforms: recenter X/Z on origin, drop min-Y to 0.
const box = new THREE.Box3().setFromObject(wrap);
const size = new THREE.Vector3(); box.getSize(size);
const center = new THREE.Vector3(); box.getCenter(center);
console.log('pre-recenter bbox size:', size.toArray().map(v => v.toFixed(4)));
console.log('pre-recenter bbox min :', box.min.toArray().map(v => v.toFixed(4)));
console.log('pre-recenter bbox max :', box.max.toArray().map(v => v.toFixed(4)));

const scene = new THREE.Scene();
scene.add(wrap);
// shift so X/Z centered, Y rests on floor (min Y -> 0)
wrap.position.set(-center.x, -box.min.y, -center.z);
wrap.updateMatrixWorld(true);

const box2 = new THREE.Box3().setFromObject(wrap);
const s2 = new THREE.Vector3(); box2.getSize(s2);
console.log('post-recenter bbox size:', s2.toArray().map(v => v.toFixed(4)));
console.log('post-recenter bbox min :', box2.min.toArray().map(v => v.toFixed(4)));
console.log('post-recenter bbox max :', box2.max.toArray().map(v => v.toFixed(4)));

// STEP 4 — export to GLB binary.
const exporter = new GLTFExporter();
const glb = await new Promise((resolve, reject) => {
  exporter.parse(scene, (res) => resolve(res), (err) => reject(err), { binary: true });
});
const rawPath = path.join(__dirname, 'stl_cache', '_w3_raw.glb');
fs.writeFileSync(rawPath, Buffer.from(glb));
console.log('raw GLB bytes:', Buffer.from(glb).length);

// Draco compress via gltf-transform.
const io = new NodeIO()
  .registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({
    'draco3d.encoder': await draco3d.createEncoderModule(),
    'draco3d.decoder': await draco3d.createDecoderModule(),
  });

const doc = await io.readBinary(new Uint8Array(glb));
await doc.transform(
  dedup(),
  prune(),
  draco(),
);
const outBin = await io.writeBinary(doc);
fs.writeFileSync(OUT, Buffer.from(outBin));
console.log('final Draco GLB bytes:', Buffer.from(outBin).length, '->', OUT);
