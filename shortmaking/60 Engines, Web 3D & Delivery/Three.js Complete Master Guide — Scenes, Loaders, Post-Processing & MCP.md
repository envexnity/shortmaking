---
title: Three.js Complete Master Guide — Scenes, Loaders, Post-Processing & MCP
tags: [threejs, webgl, webgpu, r3f, mcp, shaders, postprocessing, loaders]
updated: 2026-11-20
---

# Three.js Complete Master Guide — Scenes, Loaders, Post-Processing & MCP

> [!IMPORTANT]
> **Live Three.js MCP Active:** `threejs-devtools` (`threejs-devtools-mcp` v0.5.0 — **69 live verified tools**) is registered in `mcp_config.json`. Agents can inspect live Three.js / React Three Fiber scenes, tweak materials/lights/uniforms in real time, audit draw calls & memory leaks, capture video frames, and convert GLTF scenes directly to R3F JSX (`gltf_to_r3f`)!

Full 69-tool JSON catalog: `80 Tools & MCPs/artcraft-catalog/threejs-devtools-mcp-tools.json`.

---

## 1. Live `threejs-devtools` MCP Tool Groups (69 Tools)

| Domain | Verified Tools |
|---|---|
| **Scene & Hierarchy Inspection** | `scene_tree`, `object_details`, `find_objects`, `raycast`, `click_inspect`, `scene_diff`, `layer_details`, `bounding_boxes`, `highlight_object`, `toggle_wireframe`, `add_helper`, `remove_helper` |
| **Live Transform & Layer Control** | `set_object_transform`, `set_layers`, `pending_changes`, `revert_changes`, `run_js` |
| **Materials, Shaders & Textures** | `material_list`, `material_details`, `shader_list`, `shader_source`, `texture_list`, `texture_details`, `texture_preview`, `set_material_property`, `set_uniform`, `set_texture` |
| **Lighting, Sky, Fog & Shadows** | `shadow_details`, `scene_background`, `env_map_details`, `fog_details`, `set_light`, `set_shadow`, `set_fog` |
| **Cameras, Renderer & Post-FX** | `camera_details`, `renderer_info`, `renderer_settings`, `clipping_details`, `postprocessing_list`, `set_camera`, `set_renderer`, `set_clipping`, `set_postprocessing` |
| **Geometry, Instancing & Animation** | `geometry_details`, `instanced_mesh_details`, `batched_mesh_details`, `morph_targets`, `skeleton_details`, `animation_details`, `set_instanced_mesh`, `set_morph_target`, `set_animation` |
| **Performance & Leak Audits** | `web_audit`, `performance_snapshot`, `perf_monitor`, `draw_call_breakdown`, `memory_stats`, `dispose_check`, `console_capture` |
| **Visual Capture & Codegen** | `take_screenshot`, `annotated_screenshot`, `capture_frames`, `scene_export`, `gltf_to_r3f`, `bridge_status`, `set_dev_port`, `set_dev_url` |

---

## 2. Canonical Zero-Install Importmap (`three@0.187.0`)

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.187.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.187.0/examples/jsm/"
  }
}
</script>
```

Use our ready-to-run starter viewer at **`90 Templates/Three.js Studio Viewer Starter (Single-File r187).html`** to inspect any `.glb` exported from Blender 5.3 or TextureCraft in 1 second!

---

## 3. Production Asset Loading (`GLTF` + `Draco` + `KTX2` + `HDRI`)

```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const draco = new DRACOLoader();
draco.setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.187.0/examples/jsm/libs/draco/gltf/');

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(draco);

// Load HDRI via PMREM for physically accurate PBR reflections
const pmrem = new THREE.PMREMGenerator(renderer);
new RGBELoader().load('studio.hdr', (hdr) => {
  const envMap = pmrem.fromEquirectangular(hdr).texture;
  scene.environment = envMap;
  hdr.dispose();
  pmrem.dispose();
});

// Load GLB, enable shadows, ground & animate
gltfLoader.load('hero.glb', (gltf) => {
  const model = gltf.scene;
  model.traverse((obj) => {
    if (obj.isMesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });
  scene.add(model);

  if (gltf.animations.length > 0) {
    const mixer = new THREE.AnimationMixer(model);
    mixer.clipAction(gltf.animations[0]).play();
  }
});
```

---

## 4. High-Craft Post-Processing Stack (`EffectComposer`)

Order of passes is strict (wrong order breaks tone mapping or causes halos!):
1. **`RenderPass(scene, camera)`**
2. **Screen-space geometry passes BEFORE DOF** (e.g., `GTAOPass` ambient occlusion or Shortmaking's depth+normal `InkPass`!)
3. **Depth of Field** (`BokehPass` / `LensBlurEffect`)
4. **Selective Bloom** (`UnrealBloomPass`, `threshold = 1.05`, `strength = 0.35`, `radius = 0.45` — keep threshold `> 1.0` so only HDR emissives & specular glints bloom!)
5. **`OutputPass()`** (applies `THREE.AgXToneMapping` + `sRGB` encoding LAST!)

---

## 5. High-Density Optimization (`InstancedMesh` & `BatchedMesh`)

- **Repeated identical geometry (foliage, bolts, crowds, tiles):** Use `THREE.InstancedMesh(geo, mat, count)` — renders `10,000` instances in **1 draw call**!
- **Many different low-poly meshes sharing 1 material:** Use `THREE.BatchedMesh` (WebGL2/WebGPU) to cull per-instance on GPU with minimal draw calls.
- **Verify live:** Call `threejs-devtools` MCP `draw_call_breakdown`, `memory_stats`, and `dispose_check` before shipping!

---

## 6. Scroll-Driven 3D Camera Rig (`GSAP ScrollTrigger` + `CatmullRomCurve3`)

```javascript
const camPath = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 1.8, 6.0),
  new THREE.Vector3(3.2, 1.4, 3.0),
  new THREE.Vector3(0.5, 2.5, -4.0),
]);
const state = { t: 0 };

// Drive on ONE unified clock (gsap.ticker — matches Awwwards Vault Law #1!)
gsap.to(state, {
  t: 1,
  ease: 'none',
  scrollTrigger: { trigger: '#story', start: 'top top', end: 'bottom bottom', scrub: 1.0 }
});

gsap.ticker.add(() => {
  camera.position.copy(camPath.getPointAt(state.t));
  camera.lookAt(0, 0.8, 0);
  renderer.render(scene, camera);
});
```

## Related Notes
- [[Three.js + Blender 5.3 Live Parity & Asset Handoff]]
- [[Three.js 2D-in-3D Toon, InkPass & Low-Poly Shorts Engine]]
- [[GLSL, WGSL & Three.js TSL Custom Shaders]]
- [[Three.js, React Three Fiber & WebGPU Production]]
- [[GitHub 3D Modeling Skills Index]] (`cloudai-threejs-skills`, `threejs-game-skills`, `threejs-awesome-graphics`, `open-3d-skills`, `cesartevisual-threejs-webgpu-skills`, `three-agent-skills`)
