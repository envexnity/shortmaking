---
title: Style 1 — 2D-in-3D Toon World (Remotion + Three.js)
tags:
  - engine
  - remotion
  - threejs
  - cartoon-3d-short
  - 2d-in-3d
area: engines
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete engineering architecture for Track 1 (cartoon-3d-short) — flat 2D Canvas2D bean-head character cards inside a stylized, outlined, depth-blurred Three.js world rendered via Remotion.
---

# Style 1 — 2D-in-3D Toon World (`cartoon-3d-short` — Remotion + Three.js)

> [!NOTE] Vendored Skill & Starter Kit
> - **Skill Path**: `.agents/skills/cartoon-3d-short/SKILL.md`
> - **Full Starter Code**: `90 Templates & Starter Kits/cartoon-3d-short-kit/bridge/`

This engine reproduces the viral **Nutshell Animations / Brew / Mr omi** hybrid style: **flat 2D illustrated bean-head characters (`#241726` plum ink, variable-width outlines, stick limbs) standing inside a tactile, painted 3D environment** with screen-space depth/normal ink lines, two-tone stylized lighting, thin-lens depth of field, and a warm 7-knot colour grade.

---

## 1. File Ownership & Module Architecture

The `bridge/` template separates every concern into a dedicated TypeScript module so 4 parallel agents can edit the scene simultaneously without merge conflicts:

| File | Sandbox Owner | Responsibility |
| :--- | :--- | :--- |
| `Bridge.tsx` | `post` / root | Remotion composition (`1080×1920 @ 30fps`), WebGL renderer setup (`shadowMap.enabled = true`, `NoToneMapping`), postprocessing `EffectComposer` order, and per-frame `useCurrentFrame()` loop. |
| `toon.ts` | `char` | `600×1000` Canvas2D character painter (`Pen` variable-width Bezier inker, superellipse bean head, lidded/dot/wide/happy/dead/wink eyes, 5 mouths, hats, props, and `Pose` driver). |
| `cast.ts` | `char` | Instantiates the character planes (`1.32m × 2.20m` → `2.15m` world height), contact shadow blobs (`0.7 × 1.1m`), speech mouth cycling, and 4-frame blink scheduling. |
| `world.ts` | `world` | Builds the 3D set (terrain heightfield, river, suspension bridge, barracks, park swing, tavern, props) using procedural Canvas2D textures (`paint.ts`) and two-tone `shade()` materials. |
| `story.ts` | `cam` | Defines `SHOTS`, `CAMS`, `GLIDES`, `KICKS`, camera hold creeps (`push()`), and per-beat character acting (`Pose` keyframes synced to `words.json`). |
| `shade.ts` | `mat` | `onBeforeCompile` shader injection capturing shadow-map `sunVis` and blending explicit `uShadeCol` and `uLitCol` with normal-mapped surface relief. |
| `cardshade.ts` | `mat` | Custom shader for 2D character billboards (`V ≥ 0.86` brightness floor, subtle horizontal gradient toward key light, zero bloom bleed). |
| `lights.ts` | `mat` | Per-shot lighting & atmosphere presets (`day`, `golden` backlit with violet-blue shadows, `tense` overcast, `splash` aftermath). |
| `ink.ts` | `post` | Custom postprocessing `InkPass` (Sobel depth + view-normal edge detector running **before** DOF, honoring `NOINK = 3` layer mask). |
| `lensblur.ts` | `post` | Thin-lens 32-tap golden-angle Poisson disc blur (`LensBlurEffect`) with foreground bleed. |
| `grade.ts` | `post` | 7-knot monotone Hermite tone curve, 3-zone saturation boost (`1.26×` midtones), Cb/Cr shadow/highlight tint, and radial vignette. |
| `paint.ts` | `world` / `mat` | Procedural Canvas2D texture + bump map generators (`planksHD`, `stoneHD`, `grassHD`, `waterNear`, `waterFar`, `cloudHD`, `skyTex`). |

---

## 2. The Exact Post-Processing Composer Order (`Bridge.tsx`)

The order of passes in `Bridge.tsx` is critical—changing it breaks either outline softness or highlight roll-off:

```typescript
// Inside Bridge.tsx EffectComposer initialization:
const composer = new EffectComposer(renderer, {
  frameBufferType: THREE.HalfFloatType,
});

// 1. Base 3D Scene + 2D Character Cards
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

// 2. Screen-Space Depth + Normal Outlines (MUST be a Pass BEFORE LensBlurEffect!)
// Character cards, sky, clouds, and water have layer NOINK=3 enabled so they are skipped.
const inkPass = new InkPass(scene, camera, {
  inkCol: new THREE.Color(0x0b0a0c),
  inkStr: 0.88,
});
composer.addPass(inkPass);

// 3. Thin-Lens DOF -> Mipmap Bloom -> Neutral Tone Mapping -> 7-Knot Color Grade
const lensBlur = new LensBlurEffect({ focusDist: 6.5, focusRange: 2.2, maxCoc: 14.0 });
const bloom = new BloomEffect({
  luminanceThreshold: 1.0,
  luminanceSmoothing: 0.25,
  intensity: 0.5,
  mipmapBlur: true,
  levels: 6,
  radius: 0.6,
});
const toneMapping = new ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL });
const grade = new GradeEffect();

const effectPass = new EffectPass(camera, lensBlur, bloom, toneMapping, grade);
composer.addPass(effectPass);
```

> [!WARNING] Why `InkPass` Must Be a Separate `Pass` Before `LensBlurEffect`
> In the `postprocessing` library, `Effect`s merged inside a single `EffectPass` cannot sample the scene depth buffer *before* `LensBlurEffect` scrambles pixel neighborhoods. Making `InkPass` a standalone `Pass` ahead of `EffectPass` guarantees crisp outlines on the in-focus subject while background outlines blur naturally with the lens bokeh.

---

## 3. Step-by-Step Workflow to Build a New Short in Track 1

1. **Scaffold from the Template**:
   Copy `90 Templates & Starter Kits/cartoon-3d-short-kit/` into a new workspace directory.
2. **Write the Script & Generate `words.json`**:
   Follow [[Script Architecture - 3.7 WPS & The 'You See' Pivot]] (`~165 words` for `45s`), generate the ElevenLabs voiceover, and extract word-level frame numbers (`f = Math.round(t * 30)`).
3. **Design Distinct 3D Zones in `world.ts`**:
   Instead of putting every shot in one spot, build **3–4 spatially separated zones** (e.g., Zone A at `z = 0` Bridge, Zone B at `x = 80` Barracks, Zone C at `x = -80` Park Swing, Zone D at `z = -90` Tavern) so camera cuts change the background silhouette completely.
4. **Author Camera Cuts, Creeps & Acting in `story.ts`**:
   - Every shot entry in `SHOTS` specifies `[startFrame, endFrame, camKey, lightPreset, dofFocusDist, dofMaxCoc]`.
   - Every hold calls `push(cam, 0.0025)` so no frame is ever frozen.
   - Sync `Pose` changes (`brows`, `eyes`, `mouth`, `point`, `walk`) with a **2-frame lead** ahead of spoken punch words.
5. **Render Contact Sheet & Run the 12-Agent Look-Match Loop**:
   ```powershell
   node scripts/bridge-stills.mjs
   python scripts/sbs_sheet.py
   ```
   Inspect `out/sbs_sheet.png` against [[Readability Traps & Anti-Slop Rules]].
6. **Synthesize Audio, Render 2K Master & Run QA**:
   ```powershell
   python audio/timeline.py
   $env:TMPDIR = "$PWD\tmp_remotion"
   npx remotion render Bridge out/master_2k.mp4 --scale=1.3333
   python scripts/short_qa.py out/master_2k.mp4
   ```

---

## 4. Deep-Dive Look Bible Links
- [[Characters - Bean Heads, Plum Ink & Stick Limbs]]
- [[Outlines - Screen-Space Depth & Normal InkPass]]
- [[Lighting - Two-Tone Shaders, Backlit Golden Hour & Contact Blobs]]
- [[Depth & Post - Thin-Lens DOF, Sky Gradients & Mipmap Bloom]]
- [[Color Grade & Procedural Canvas2D Textures]]
