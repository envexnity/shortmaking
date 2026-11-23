---
title: GLSL, WGSL & Three.js TSL Custom Shaders
tags: [shaders, glsl, wgsl, tsl, threejs, webgpu, webgl]
updated: 2026-11-20
---

# GLSL, WGSL & Three.js TSL Custom Shaders

Custom real-time shaders for **Three.js / WebGPU (TSL)**, **WebGL2 (GLSL)**, **Godot (GDShader)**, and **Unity/UE5 (HLSL)**.

> [!TIP]
> **Vendored Skills Ready in Vault:**
> - `80 Tools & MCPs/skills/cloudai-threejs-skills/` (★4,311)
> - `80 Tools & MCPs/skills/cesartevisual-threejs-webgpu-skills/` (WebGPU + TSL + R3F)
> - `80 Tools & MCPs/skills/emalorenzo-three-agent-skills/` (`three-agent-skills`)

---

## 1. Three.js Shading Language (TSL — WebGPU + WebGL Dual Target)

Modern Three.js (`r170+` / `r186+`) uses **TSL (`three/tsl`)**, which compiles automatically to **WGSL** on WebGPU and **GLSL** on WebGL2!

```javascript
import * as THREE from 'three/webgpu';
import {
  color, float, mix, pow, dot, normalize,
  positionViewDirection, normalView, time, sin, positionWorld
} from 'three/tsl';

// Iridescent Fresnel Hologram Material (compiles to WGSL + GLSL)
const mat = new THREE.MeshPhysicalNodeMaterial({
  roughness: 0.15,
  metalness: 0.2,
  transmission: 0.6,
  ior: 1.45,
});

const fresnel = pow(
  float(1.0).sub(dot(normalize(normalView), normalize(positionViewDirection)).abs()),
  3.0
);
const scanline = sin(positionWorld.y.mul(40.0).sub(time.mul(6.0))).mul(0.5).add(0.5);
const rimColor = mix(color('#00f0ff'), color('#ff2bd6'), scanline);

mat.emissiveNode = rimColor.mul(fresnel).mul(2.2);
```

---

## 2. Essential GLSL Building Blocks (Fragment & Vertex)

### Fresnel Rim Glow
```glsl
float fresnel = pow(1.0 - max(dot(normalize(vNormal), normalize(vViewDir)), 0.0), 3.0);
```

### PS1 Retro Vertex Snapping (Vertex Shader)
```glsl
vec4 clipPos = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
vec2 grid = vec2(160.0, 120.0); // PS1 jitter grid resolution
clipPos.xy = floor(clipPos.xy / clipPos.w * grid + 0.5) / grid * clipPos.w;
gl_Position = clipPos;
```

### Ordered Bayer 4×4 Dither (Pixel-Art / Obra Dinn / Retro 3D)
```glsl
float bayer4x4(vec2 p) {
  int x = int(mod(p.x, 4.0));
  int y = int(mod(p.y, 4.0));
  int idx = y * 4 + x;
  const float m[16] = float[16](
     0.0,  8.0,  2.0, 10.0,
    12.0,  4.0, 14.0,  6.0,
     3.0, 11.0,  1.0,  9.0,
    15.0,  7.0, 13.0,  5.0
  );
  return (m[idx] + 0.5) / 16.0;
}
```

### Smooth Cel Banding (Anti-Aliased Toon Step)
```glsl
float ndl = dot(normalize(vNormal), normalize(uLightDir));
float band = smoothstep(0.08 - fwidth(ndl), 0.08 + fwidth(ndl), ndl);
vec3 col = mix(uShadowColor, uBaseColor, band);
```

---

## 3. Performance Budget Rules for Web Shaders

- Keep fragment shader ALU ops **under ~120 ops/pixel** on fullscreen backgrounds (never run 6-octave 3D fBm + raymarching at full DPR 2.0 on mobile!).
- Cap renderer pixel ratio: `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))`.
- Always call `.dispose()` on geometries, materials, textures, and render targets when unmounting scenes.

## Related Notes
- [[Three.js, React Three Fiber & WebGPU Production]]
- [[Style 11 — PS1 - PS2 - N64 Retro & Vertex-Snapped Lo-Fi]]
- [[Style 18 — Abstract Motion Graphics, Glassmorphism & Iridescent (Cinema4D - Awwwards)]]
- [[Style 24 — Pixel-Art 3D (Dithered Orthographic Sprites & 2.5D HD-2D)]]
