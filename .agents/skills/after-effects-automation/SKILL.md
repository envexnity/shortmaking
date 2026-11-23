---
name: after-effects-automation
description: Expert skill for programmatic video editing, motion graphics, kinetic typography, and timeline compositing using Adobe After Effects (ExtendScript / JSX) and the EffectCraft compositor engine.
---

# After Effects & EffectCraft Automation Skill

This skill equips the agent to plan, script, and automate video editing and motion graphics compositions matching Adobe After Effects 2024-2026 standards and the EffectCraft MCP engine.

## 1. Core Architecture & Philosophy

When editing videos and building motion graphics:
- **Zero Pixel Drift:** Structure all visual compositions around standard frame resolutions (1920x1080 for widescreen horizontal, 1080x1920 for 9:16 Shorts/Reels/TikTok).
- **Easing & Interpolation:** Linear keyframes look robotic. Always apply cubic bezier easing (Fast-in/Smooth-out, e.g., Bezier with 75% incoming/outgoing influence) or procedural overshoot expressions:
  ```javascript
  // Elastic Bounce / Overshoot Expression
  freq = 3.0;
  decay = 5.0;
  n = 0;
  if (numKeys > 0){
    n = nearestKey(time).index;
    if (key(n).time > time) n--;
  }
  if (n > 0){
    t = time - key(n).time;
    amp = (velocityAtTime(key(n).time - .001)) / 100;
    w = freq * Math.PI * 2;
    value + (amp * (Math.sin(t * w) / Math.exp(decay * t))) / 2;
  } else {
    value;
  }
  ```
- **Hierarchical Layering:**
  1. **Top Tier:** Adjustment Layers (Color Grade, Film Grain, Global Lens Blur, Chromatic Aberration).
  2. **High Tier:** HUD, Overlays, Counters, Subtitles, Kinetic Text, Callouts.
  3. **Mid Tier:** Cutout memes, character avatars, floating stickers, arrows, spotlight vignettes.
  4. **Base Tier:** Main video footage / gameplay tracks with speed ramps, snap zooms, and screen shakes.
  5. **Background:** Ambient motion gradients, radial starbursts, or dark scrims.

---

## 2. Gaming & Retention Editing Styles ("Noob to Pro")

For high-retention gaming videos (e.g., Roblox Anime Last Stand, Minecraft, Fortnite):
- **Hook Cut (0:00 - 0:05):** Tease the final Godly unit / max level / insane victory with quick cuts (< 0.6s per cut), high-contrast text ("YOU WON'T BELIEVE WHAT HAPPENED..."), and an instant bass drop.
- **Dynamic Snap Zooms:** Apply 115% to 140% scale snap punches onto character faces or critical game moments over 4 to 8 frames, followed by an eased return.
- **Screen Shake (Impacts/Crits):**
  ```javascript
  // Directional Screen Shake Expression
  intensity = 35;
  speed = 40;
  wiggle(speed, intensity) * (1 - ease(time, inPoint, inPoint + 0.3, 0, 1));
  ```
- **Kinetic Text & Pop Subtitles:**
  - Font: Bold, high-impact sans-serif or comic display (Impact, Montserrat Black, Lilita One, Luckiest Guy).
  - Fill: Vibrant yellow (`#FFE600`), neon green (`#00FFA3`), or pure white with heavy dark stroke (8px - 14px `#111111`) and colored drop shadow.
  - Scale pop: Frame 0 (0%) -> Frame 4 (118% overshoot) -> Frame 7 (100%).

---

## 3. Working with EffectCraft MCP

EffectCraft is an After Effects-compatible compositor engine. Always leverage its commands:
1. **Initialize Comp:**
   `command_run { id: "comp.new", params: { name: "Main", width: 1920, height: 1080, fps: 60.0, duration: 30.0 } }`
2. **Add Solid / Background:**
   `command_run { id: "layer.newSolid", params: { name: "BG_Dark", color: [0.05, 0.05, 0.08, 1.0], width: 1920, height: 1080 } }`
3. **Add Kinetic Text:**
   `command_run { id: "layer.newText", params: { text: "NOOB TO PRO", fontSize: 120 } }`
4. **Animate Properties & Keyframes:**
   - Query layer IDs via `get_comp`.
   - Set keyframes with `add_keyframe { layer_id, prop_path: "transform/scale", time: 0.0, value: [0, 0, 100] }`.
   - Add target keyframe: `add_keyframe { layer_id, prop_path: "transform/scale", time: 0.25, value: [100, 100, 100] }`.
5. **Apply Effects:**
   `add_effect { layer_id, effect_id: "glow" }` or `effect.apply`.
6. **Inspect and Verify:**
   Call `render_preview` or `render_frame` to inspect frame output visually.
