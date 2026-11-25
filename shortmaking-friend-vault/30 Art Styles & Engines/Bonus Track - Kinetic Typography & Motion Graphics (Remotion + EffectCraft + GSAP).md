---
title: Bonus Track — Kinetic Typography & Motion Graphics (Remotion + EffectCraft + GSAP)
tags:
  - engine
  - remotion
  - effectcraft
  - after-effects
  - gsap
  - vectorcraft
  - figcraft
  - designcraft
  - motion-graphics
  - typography
area: engines
style: motion-graphics
status: evergreen
created: 2026-11-15
updated: 2026-11-21
summary: Complete production engineering bible for kinetic typography, data cards, animated maps, and editorial motion graphics using Remotion, EffectCraft MCP, GSAP, VectorCraft, FigCraft, and DesignCraft — with exact spring physics, easing curves, layer stacks, and deterministic render recipes.
---

# Bonus Track — Kinetic Typography & Motion Graphics (`Remotion` + `EffectCraft` + `GSAP`)

> [!NOTE] Installed MCPs & Vendored Skills
> - **EffectCraft MCPs**: `effectcraft` and `effectcraft-live` (`run_script`, `add_keyframe`, `add_effect`, `set_property`, `render_frame`, `command_batch`)
> - **2D Design & Vector MCPs**: `vectorcraft` (SVG paths/shapes/icons), `figcraft` (UI cards & layouts), `designcraft` (editorial typography/print spreads)
> - **After Effects & EffectCraft Skill**: `.agents/skills/after-effects-automation/SKILL.md`
> - **13 Remotion Skills**: `.agents/skills/remotion-best-practices`, `remotion-captions`, `remotion-maps`, `remotion-markup`, `remotion-multimedia`, `remotion-render`, `remotion-saas`, `remotion-studio`, etc.
> - **7 GSAP Skills**: `.agents/skills/gsap-core`, `gsap-timeline`, `gsap-plugins`, `gsap-react`, `gsap-scrolltrigger`, `gsap-performance`, `gsap-utils`

Even inside 3D or 2D-in-3D shorts, **kinetic typography, map callouts, glowing data cards, and animated word-by-word captions** boost `0–3 s` hook retention by `15–25%`. For standalone non-3D shorts (*Vox*, *MagnatesMedia*, *Kurzgesagt*, *Apple Keynote*, *UI Storytime*), this stack is a complete zero-3D production studio.

---

## 1. The 5-Layer Motion Graphics Composition Stack

Amateur motion graphics look like PowerPoint slides because they drop flat text directly onto a solid color. Every pro motion-graphics frame uses **5 stacked layers**:

| Layer (Bottom → Top) | Visual Role | Exact Craft Settings |
| :--- | :--- | :--- |
| **1. Living Backdrop** | Atmosphere & depth | Deep radial gradient (`#0B1020 → #18223A`) or warm paper texture (`#F5F0E6`) with slow `0.15%/f` zoom drift + faint `8%` dot/blueprint grid moving at `0.3×` parallax. |
| **2. Context / Support Plate** | Framing & B-roll | Archival photo, blurred UI panel, or vector map darkened `-25%` brightness & `-30%` saturation whenever hero text sits on top. |
| **3. Hero Kinetic Subject** | Primary visual focus | Oversized headline, icon, chart, or UI card entering on a **snappy overshoot curve** (`scale 0.85 → 1.06 → 1.0`), never linear fade-in. |
| **4. Micro-Accents & Callouts** | Eye guidance & juice | `2–4f` animated underline/highlighter sweep, ticking numeric counter, subtle particle sparks, or floating cursor/pointer. |
| **5. Optical Finish Pass** | Cohesive film feel | `2–3%` monochrome film grain (`12 fps` boil), soft radial vignette (`18%`), subtle halation/glow on highlight accents, and `3–4f` chromatic aberration (`4–6 px`) on bass hits. |

---

## 2. Exact Spring Physics & Easing Curve Library

**Golden Law**: **Never use `linear` or default `ease` on UI/typography entrances.** Motion should feel physical—fast departure, controlled overshoot, crisp settle.

### A. Remotion `spring()` Presets (`30 fps`)
| Feel / Use Case | `damping` | `stiffness` | `mass` | Overshoot Behavior |
| :--- | :---: | :---: | :---: | :--- |
| **Snappy Subtitle / Word Pop** | `14` | `260` | `0.6` | Crisp `~8%` pop-overshoot, settles in `6–8f` |
| **Hero Hook Title Slam** | `12` | `220` | `0.8` | Punchy `~12%` bounce, pairs with `7f` screen kick |
| **Editorial Card / Map Panel Slide** | `22` | `180` | `0.9` | Critically damped sleek glide, zero rubbery wobble |
| **Comedic Icon / Emoji Boing** | `8` | `240` | `0.7` | Playful elastic oscillation (`~22%` overshoot) |
| **Camera Whip / Zoom-Out Reveal** | `26` | `160` | `1.0` | Fast launch, silky exponential deceleration |

### B. GSAP & EffectCraft / After Effects Equivalent Curves
- **GSAP Snappy Entrance**: `ease: "back.out(1.7)"` (`0.22–0.32 s`) for words/badges; `ease: "expo.out"` (`0.35–0.55 s`) for camera zooms and card slides; `ease: "power4.inOut"` (`0.28–0.40 s`) for whip transitions.
- **EffectCraft / AE Bezier Law**: Never use default `33%` Easy Ease. Set outgoing velocity influence to **`75%–85%`** (`KeyframeEase(0, 82)`) and stagger sibling elements by **`2–4 frames` (`66–133 ms`)** so layouts ripple onto screen instead of popping in unison.

---

## 3. Remotion 13-Skill Production Patterns (React + TypeScript)

1. **Always load `.agents/skills/remotion-best-practices/SKILL.md` first**:
   - **Never use CSS `transition`, CSS `@keyframes`, or `requestAnimationFrame`**. Every single visual property must be a pure deterministic function of `useCurrentFrame()` and `spring()` / `interpolate()`.
   - Isolate every visual beat inside `<Sequence from={startFrame} durationInFrames={dur}>`.
2. **Word-Level Subtitles (`.agents/skills/remotion-captions/SKILL.md`)**:
   - Feed `words.json` into `@remotion/captions` (`createTikTokStyleCaptions({ pages, combineTokensWithinMilliseconds: 900 })`).
   - Follow [[04 Next-Generation Retention, Subtitles & Audio Spec]]: **`2–4` words** inside a tightly fitted `rgba(8,8,10,0.90)` rounded pill (`border-radius: 16px`, `56–64 px` bold geometric sans, `#FFFFFF` base + `#FFE600` active-word pop at `y = 1280–1420 px`).
3. **Animated Maps, Routes & Evolving SVG Paths (`.agents/skills/remotion-maps/SKILL.md`)**:
   - Use `@remotion/paths` (`evolvePath(progress, d)`) to draw glowing travel lines, borders, arrows, and hand-drawn circles in real time.
   - Pair every map route draw with a soft chalk/pencil or subtle UI tick SFX and a `1.0 → 1.18` continuous camera push into the destination pin.
4. **Disk-Safe Rendering (Law 24)**:
   - Always redirect `$env:TMPDIR` to a scratch directory and purge `remotion-*` temp bundles before multi-render loops.

---

## 4. ArtCraft 2D MCP Pipeline (`VectorCraft` → `FigCraft` / `DesignCraft` → `EffectCraft`)

Build 100% original, crisp non-3D visual assets locally without relying on generic stock packs:
1. **Custom Vector Icons & Illustrations (`vectorcraft` MCP)**:
   - Generate clean layered SVGs (`draw_shape`, `draw_path`, `pathfinder`, `set_paint`, `export`) with named sub-paths so individual parts (e.g., rocket flame, arrow head, eyes, clock hands) animate independently.
2. **Screen-Native UI Cards & Dashboards (`figcraft` MCP)**:
   - Author pixel-crisp notification popups, fake chat threads, bank counters, and stat cards (`create_node`, `set_properties`, `export` at `@2x` PNG or SVG) sized `1.8×` larger than real phone UI for instant readability in `9:16`.
3. **Editorial Magazine & Archival Layouts (`designcraft` MCP)**:
   - Create realistic newspaper front pages, classified dossiers, and pull-quote cards (`new_document`, `set_story_text`, `place_image`, `export_png`) for *Vox* / *MagnatesMedia* collage beats.
4. **2.5D Compositing & Camera Animation (`effectcraft` / `effectcraft-live` MCP)**:
   - Load `.agents/skills/after-effects-automation/SKILL.md`.
   - Parent the 3D Camera to a **3D Controller Null** (`separateDimensions = true`) and combine `Position Z` push-ins with subtle `Rotation Z` (`±1.5–4°` Dutch tilt).
   - Add `Noise (2.5%)`, `Posterize Time (12 fps)` on paper/collage layers only, and subtle glow/halation on accent callouts.

---

## 5. Deterministic GSAP + Playwright Frame Capture (`.agents/skills/gsap-timeline`)

When authoring complex SVG morphs (`Flip`, `SplitText`, `CustomEase`, `DrawSVG`) or HTML/Canvas2D kinetic pieces:
```javascript
// 1. Build a single master timeline paused at t = 0
const tl = gsap.timeline({ paused: true });
tl.from(".hook-word", { y: 40, opacity: 0, scale: 0.85, stagger: 0.08, duration: 0.28, ease: "back.out(1.8)" }, 0.0);
tl.to(".camera-stage", { scale: 1.14, rotation: -1.5, duration: 2.2, ease: "none" }, 0.0);

// 2. Expose deterministic frame seeker for Playwright headless capture
window.__renderFrame = (timeSec) => {
  tl.seek(timeSec, false);
};
```
Render frame-by-frame at `30 fps` via Playwright → FFmpeg (`-crf 15 -pix_fmt yuv420p -colorspace bt709`) for **zero dropped frames, zero screen-recording artifacts, and exact millisecond audio sync**.

---

## 6. Hybrid AI-Plate + Clean Vector Text Rule

When mixing painterly or photographic AI B-roll plates with motion graphics (see [[Video 7 Teardown - 3D Motion Graphics With Claude & Google Flow (AIpreneur)]]):
- **Lock 1 anchor style image** before generating any batch of background plates.
- **Never bake text inside an AI image/video generator**—it produces garbled glyphs and soft edges. Always composite kinetic typography, charts, arrows, and subtitles cleanly on top in Remotion, EffectCraft, or GSAP.
- Transition between plates using **paper rips, directional whip blurs, or ink mattes** instead of slow crossfades to black.

## Related Vault Guides
- [[Non-3D Visual Styles Encyclopedia (2D Vector, Storytime Animatics, Documentary Collage, 8-Bit & ASCII Horror)]]
- [[Color Psychology, Typography Pairing & Frame-0 Thumbnail Engineering]]
- [[04 Next-Generation Retention, Subtitles & Audio Spec]]
- [[05 Editing Rhythm, Pre-Vis Animatics & Retention Graph Forensics]]
