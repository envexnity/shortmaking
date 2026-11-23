---
title: Three.js, React Three Fiber & WebGPU Production
tags: [threejs, r3f, webgpu, webgl, performance, gltf, web3d]
updated: 2026-11-20
---

# Three.js, React Three Fiber & WebGPU Production

> [!TIP]
> **6 Top-Starred Three.js GitHub Skill Suites Are Vendored Locally in This Vault:**
> - `80 Tools & MCPs/skills/cloudai-threejs-skills/` (★4,311)
> - `80 Tools & MCPs/skills/threejs-game-skills/` (★2,863)
> - `80 Tools & MCPs/skills/threejs-awesome-graphics/` (★1,018)
> - `80 Tools & MCPs/skills/threejs-architecture-effects/` (★746)
> - `80 Tools & MCPs/skills/open-3d-skills/` (★437)
> - `80 Tools & MCPs/skills/cesartevisual-threejs-webgpu-skills/` & `three-agent-skills/`

---

## 1. Zero-Defect Three.js Renderer Setup (r170+ / r187)

```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping; // Or THREE.AgXToneMapping!
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// Instant crisp IBL reflections so metals & glass NEVER render black!
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
```

---

## 2. Hard 60 FPS Web 3D Performance Budgets

| Metric | Target Budget (Desktop + Mobile) | How to Hit It |
|---|---|---|
| **GLB File Size** | `≤ 5 MB` hero (`≤ 15 MB` full interactive scene) | Draco + WebP/KTX2 (`2048` max hero, `1024` props) |
| **Draw Calls** | `≤ 60` (`≤ 120` max complex world) | `InstancedMesh` for repeated props, merged static meshes, texture atlases |
| **Triangles on Screen** | `≤ 150k` smooth mobile · `≤ 500k` desktop | Clean retopo, LODs, baked TextureCraft normals |
| **Memory Leaks** | `0` leaked buffers on route switch | Dispose `geometry`, `material`, `texture`, `renderTarget`, `pmrem` on unmount! |
| **Frame Loop** | **ONE** unified `requestAnimationFrame` (or `gsap.ticker`) | Never run competing animation loops alongside smooth scroll! |

---

## 3. Blender → Three.js Parity Checklist
1. Match tone mapping: `THREE.AgXToneMapping` matches Blender 5.3 `AgX`!
2. Load an environment HDRI (`RGBELoader` + `PMREMGenerator` or `RoomEnvironment`) — PBR metallics look pure black without an environment map!
3. Verify shadows: tighten directional light shadow frustum tightly around hero bounds (`shadow.bias = -0.0004`, `shadow.normalBias = 0.02`, `shadow.mapSize = 2048`).

## Related Notes
- [[GLSL, WGSL & Three.js TSL Custom Shaders]]
- [[glTF - GLB & USD Export Pipeline (Zero-Defect Rules)]]
- [[Style 18 — Abstract Motion Graphics, Glassmorphism & Iridescent (Cinema4D - Awwwards)]]
- [[GitHub 3D Modeling Skills Index]]
