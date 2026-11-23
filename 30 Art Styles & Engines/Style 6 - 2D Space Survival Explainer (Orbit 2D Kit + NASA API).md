---
title: Style 6 — 2D Space Survival Explainer (Orbit 2D Kit + NASA API)
tags:
  - engine
  - orbit
  - 2d-canvas
  - space
  - nasa-api
  - playwright
area: engines
style: orbit-2d-space
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Engineering and visual look-dev guide for Track 6 (orbit-space-video / orbit-2d-space-kit) — 2D Canvas + Playwright renderer for Space Survival explainers with tiny astronaut, animated gauges, blueprint X-rays, dry humor receipts, and real NASA photos.
---

# Style 6 — 2D Space Survival Explainer (`orbit-space-video` / Orbit 2D Kit)

> [!NOTE] Skill & Starter Kit
> - **Teardown Reference**: [[Video 8 Teardown - Orbit 2D Space Survival (Money Mastery Hub)]]
> - **Skill Path**: `.agents/skills/orbit-space-video/SKILL.md`
> - **Starter Kit Path**: `90 Templates & Starter Kits/orbit-2d-space-kit/`

Track 6 is the dedicated 2D explainer engine built for **Orbit Oddities** space-time and planetary survival videos (`1920×1080` widescreen YouTube by default, or adaptable to `1080×1920` Shorts). It combines **pure deterministic HTML5 Canvas 2D vector art**, **animated instrument overlays**, and **real public-domain NASA/JPL photography** without React/Webpack overhead.

---

## 1. Visual Design System & Color Palette

| Token | Hex Value | Usage |
| :--- | :--- | :--- |
| `spaceTop` / `spaceBot` | `#04060e` → `#0c1328` | Deep cosmic backdrop with radial falloff |
| `marsLight` / `marsMid` / `marsDark` | `#d87643` / `#9c4322` / `#3b160a` | 2D illuminated planet body & shaded craters |
| `ridgeDay` (4 layers) | `#994825`, `#713016`, `#4a1c0b`, `#220a03` | Parallax Martian day horizon ridges |
| `ridgeCold` (4 layers) | `#685a6e`, `#493d51`, `#2e2434`, `#16101b` | Parallax Martian night / polar freeze ridges |
| `dustBand` | `rgba(218, 145, 96, 0.24)` | Horizontal dusty twilight band behind foreground peaks |
| `spotlightBg` / `spotlightCenter` | `#241b02` → `#ffd84a` | Full-screen radial spotlight for `KILLER #N` cards |
| `blueprintBg` / `gridLine` | `#050914` / `rgba(45, 82, 138, 0.28)` | Technical X-ray / medical breakdown background |
| `xrayGreen` | `#4ade80` | Neon rounded vector body outline & internal hotspots |
| `alertRed` | `#ef4444` | `YOU` tag, curved pointer arrow, warning banners, callout lines |
| `highlightYellow` | `#f5c842` | Keyword accent in impact captions & `CARBONATED` border stamp |
| `cardBg` | `#1c1a20` (`border rgba(255,255,255,0.12)`) | Pressure gauge cards, metric counters, credit badges |

### Typography Hierarchy
- **Display Condensed (`Impact, "Arial Narrow", "Bahnschrift Condensed", sans-serif`)**: Planet titles (`MARS` `116px`), spotlight titles (`THE THIN AIR` `156px`), bottom impact lines (`64px`), gauge numerals (`68px`), temperatures (`96px`).
- **UI Sans (`"Segoe UI", Inter, system-ui, sans-serif`)**: Micro-labels, pills (`AIR PRESSURE (EARTH = 1,013)`), subheads (`4TH PLANET FROM THE SUN`).
- **Receipt / Credits (`Consolas, "Courier New", monospace`)**: Thermal paper receipts (`MARS SODA CO.`), institutional NASA credits (`NASA/JPL-Caltech/University of Arizona`), status tags.

---

## 2. The 2D Astronaut Rig & Camera Laws

### Tiny Astronaut Proportions
Whether floating in orbit (`0.42–0.85×` scale) or walking along ridge layer 2 (`0.72×` scale):
1. **Helmet**: White rounded circle (`#f8fafc`) with subtle grey rim shading, dark curved visor (`#1e293b` → `#0f172a`) with a warm amber reflection streak (`#d97706`).
2. **Backpack & Torso**: Slightly shaded off-white PLSS life-support pack (`#cbd5e1`) behind the torso with a tiny red mission stripe (`#ef4444`).
3. **Articulated Limbs**: Short rounded boots & gloves (`#e2e8f0` / `#94a3b8`) driven by smooth sine walk phase (`Math.sin(t * 4.5)`) on surfaces or slow zero-g float (`Math.sin(t * 1.4)`) in space.
4. **Headlamp Beam**: Conical linear gradient emanating forward from the helmet (`rgba(255, 248, 220, 0.26)` fading to `0`), subtly flickering (`1 + 0.04 * sin(t * 9)`) so even quiet beats pass motion-variance QA cleanly.

### Zero Frozen Frames Guarantee
Every Orbit scene evaluates `ctx.scale(zoom, zoom)` + gentle parallax drift (`1.0 → 1.035` push-in or slow horizontal pan) plus drifting dust/star motes as pure functions of continuous time `t`. This ensures `mean frame diff > 0.3` and **`0` frozen spans `≥12f`** in `short_qa.py`.

---

## 3. NASA Image API Pipeline (`fetch_nasa.py`)

NASA's public Image & Video Library requires **no API key**:
```text
GET https://images-api.nasa.gov/search?q=Phoenix+lander+scoop+soil+Mars&media_type=image
```
1. Run `python fetch_nasa.py` (with `ssl._create_unverified_context()` fallback if OS CA store rejects TLS on Windows).
2. Download the best-resolution JPEG (`~href` or `collection/items[i].links[0].href` → inspect `asset.json` for `~medium.jpg` / `~large.jpg`).
3. Store local file + exact metadata (`nasa_id`, `center`, `date_created`, `photographer`/`credit`) in `assets/nasa_manifest.json` so every rendered `evidence` slide stamps the true institutional credit (`NASA/JPL-Caltech/...`) and writes a complete `sources.md`.

---

## 4. Kit API (`90 Templates & Starter Kits/orbit-2d-space-kit/`)

In your project's `scenes.js`, set `window.ORBIT_CONFIG` and `window.SCENES = [ ... ]`:
- `type: 'orbit_establish'` — `{ planet, title, subtitle, bottomWhite, bottomYellow, stamp, showYouArrow, astroPos, focusZoom, sunRays }`
- `type: 'planet_compare'` — `{ title, leftPlanet, rightPlanet, captionLeft, captionRight, metricTag }`
- `type: 'killer_card'` — `{ eyebrow, title, statusPill }`
- `type: 'surface_gauge'` — `{ palette: 'day'|'cold', widget: 'gauge'|'thermometer'|'notice'|'delay', ...widgetOpts }`
- `type: 'xray'` — `{ header, calloutLabel, calloutY, targetSpot: 'mouth'|'chest'|'lungs', receipt: { ... } | null, stamps: [...] }`
- `type: 'evidence'` — `{ palette: 'day'|'cold', imgKey, topTag, credit, counters: [{ big, unit, label }, ...] }`
- `type: 'magma_twist'` — `{ title, depthLabel, badgeText, footerLine }`

Render stills QA contact sheet first:
```powershell
node render.js scenes.js --stills stills
```
Then render full `1920×1080 @ 30fps` video and mux normalized audio (`-14 LUFS`, explicit stream map):
```powershell
python make_voice.py --dir .                  # Default: edge-tts en-AU-WilliamNeural (+4%), matching Emu War
node render.js scenes.js --audio audio/mix.wav --out out/final.mp4
```

### Voiceover Defaults & Audio-Only Swap Rule
- **Default Voice System**: `edge-tts` with `en-AU-WilliamNeural` (`rate="+4%"`) — fast, consistent, and identical to *The Great Emu War*. Optional `--engine kokoro --voice orbit_us` is also supported.
- **Never Re-Render on Audio Changes**: If only the voiceover or mix changes, swap audio directly without re-rendering frames:
  ```powershell
  ffmpeg -y -i out/final.mp4 -i audio/mix.wav -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -shortest out/final_swapped.mp4
  ```

> [!IMPORTANT] Next-Generation Retention Upgrade (`2026-11-16`)
> For all future Shorts rendered with this kit, follow **[[04 Next-Generation Retention, Subtitles & Audio Spec]]**: replace bottom double-headlines/extra HUD text with **oversized `8sb2R11FeVw` black-pill subtitles**, cut every `0.9–1.5 s` with rapid camera moves, and use tracks from the curated music pool **only when fitting** the scene mood, paired with `nbwQWTR0SV4` / CC0 SFX.
