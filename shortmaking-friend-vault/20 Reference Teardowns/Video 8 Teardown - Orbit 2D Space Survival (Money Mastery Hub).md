---
title: Video 8 Teardown — Orbit 2D Space Survival (Money Mastery Hub)
tags:
  - teardown
  - orbit
  - 2d-animation
  - space
  - nasa-api
  - playwright
area: teardowns
style: orbit-2d-space
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete reverse-engineering of the Orbit 2D Space Survival video skill ("Depth Theory moved to Space") from Money Mastery Hub (youtu.be/ziyWYLrvYaU), including the 4 script laws, 8 visual scene archetypes, NASA Image API pipeline, and 3 QA layout checks.
---

# Video 8 Teardown — Orbit 2D Space Survival (`ziyWYLrvYaU`)

- **Reference Video**: *"Claude Makes Entire Space Videos From One Prompt (GET the FREE SKILL)"* ([youtu.be/ziyWYLrvYaU](https://youtu.be/ziyWYLrvYaU))
- **Creator**: **Money Mastery Hub** (`Orbit Space Video Skill v3`)
- **Demo Video Analysed**: *"What Would Kill You First On Mars?"* (`2:19`, `352 words`, `1920×1080 @ 30fps`, `5` real NASA photos, `1` visual gag per joke)
- **Skill & Starter Kit**: `.agents/skills/orbit-space-video/SKILL.md` and `90 Templates & Starter Kits/orbit-2d-space-kit/`

---

## 1. Core Viral Concept: "Depth Theory Moved to Space"

Inspired by viral oceanographic survival channels (*Depth Theory* — `8.2M+` views on dark abyssal explainers), Orbit transfers the exact psychological formula into outer space:
1. **Radical Scale Contrast**: A tiny white 2D spacesuit (`YOU`, `~36px` tall, sweeping triangular headlamp beam, curved red pointer arrow) drifting beside or above an enormous 2D illustrated cosmic body (planet, moon, or curved planetary horizon).
2. **Calm Escalating Countdown**: Instead of frantic hyper-editing, a dry, composed narrator walks step-by-step through **what kills you first**, punching through golden spotlight transition cards (`KILLER #1: THE THIN AIR`, `KILLER #2: THE COLD`, `KILLER #3: TOXIC DUST`, `KILLER #4: RADIATION`).
3. **Real Space Agency Receipts**: Claims are backed by **live NASA/JPL/ESA numbers** and **real public-domain NASA photos** fetched directly from `https://images-api.nasa.gov/search` and mounted inside tilted white Polaroid evidence frames with red mission tags and institutional credits.

---

## 2. The 4 Orbit Script Laws (Measured Verbatim)

From the video's Step 3 script breakdown (`352 words` ≈ `2:19`, `~2.55–2.8 wps`):

| Law | Mechanism | Example from Mars Reference |
| :--- | :--- | :--- |
| **1. Open on a Rule, Then Break It** | Establish an everyday intuition as `"the rule"`, then shatter it on Sentence 3–4 with a sensory contradiction. | *"Picture this. You're standing on Mars. It's just a cold desert, and deserts don't kill astronauts. **That's the rule.** Then your tongue starts to fizz."* |
| **2. Every Number Gets a Comparison** | Never drop a bare unit (`6 mbar`, `-125°C`, `0.64 mSv`). Always anchor it immediately to a human body threshold or Earth landmark. | `6 mbar` = **under 1% of Earth's `1,013 mbar`** (water boils at **37°C — your body temperature**); `-125°C` = **colder than any night ever recorded in Antarctica**; `0.64 mSv/day` = **6 chest X-rays every day**. |
| **3. A Dry Joke + 1 Picture Per Joke** | Follow every terrifying physical mechanism with deadpan corporate humor paired with a dedicated 2D prop/card. | *"Like soda you never drank"* → **`MARS SODA CO.` itemized receipt** (`SALIVA: $0 / BUBBLES: $0 / AIR PRESSURE: $0 / TOTAL: YOU`) + tilted **`CARBONATED`** stamp; perchlorate soil → **`DOORMAT NOTICE: WIPE FEET please`** staked in the dust. |
| **4. `"What Can You Do?"` — Knock Every Option Down** | In the final act, let the viewer imagine escape routes (*hold breath, dig down, call for help*) and dismantle each with hard physics. | *"Call for help? Your message takes up to **twenty-two minutes** to reach Earth — one way."* |

### Fact-Check Honesty Rule
Every quantitative claim in `sources.md` is verified against **NASA / JPL / ESA** sources before rendering. Any open scientific debate or unconfirmed hypothesis is explicitly flagged on screen instead of stated as fact:
- Confirmed: `6 mbar` pressure, `-60°C` avg / `-125°C` pole temp, `0.64 mSv/day` surface radiation (MSL RAD), `90 sols` planned vs `14.4 years` actual Opportunity lifespan.
- Flagged On Screen: **Alba Mons magma** → badged **`UNPROVEN`**; **liquid water deep underground** → labeled **`POSSIBLE, NOT FOUND`**.

---

## 3. The 8 Visual Scene Archetypes

| Scene Key | Visual Composition | Primary Motion |
| :--- | :--- | :--- |
| **`orbit_establish`** | Deep dark navy starfield (`#04060e`), subtle top-left sun rays, giant 2D layered planet orb or curved horizon arc, tiny 2D astronaut + translucent headlamp cone + bold red `YOU` & curved red arrow, bold condensed title (`MARS · 4TH PLANET FROM THE SUN` or yellow `WHAT KILLS YOU FIRST?`), bottom white+yellow headline (`JUST A COLD DESERT`), optional badge (`THE RULE`). | Slow orbital zoom/drift, gently floating astronaut bob, pulsing headlamp cone. |
| **`planet_compare`** | Side-by-side 2D planets in starfield (e.g., Earth vs. Mars) with diameter/pressure/gravity comparison readouts beneath. | Smooth lateral parallax pan + subtle scale pulse. |
| **`killer_card`** | Full-screen golden-yellow radial spotlight oval (`#ffd84a` → `#2a1f04` corners), small bold black header (`KILLER #1`), giant condensed black impact title (`THE THIN AIR`, `THE COLD`), optional green status pill (`SUIT: PATCHED`). | Snappy spring scale pop + subtle spotlight vignette drift (`push()`). |
| **`surface_gauge`** | 4–5 wavy layered 2D planetary terrain ridges (warm rust `#b85d35 → #240d05` or icy violet `#6b5b73 → #16111a`) with dusty atmospheric horizon stripe, walking/standing tiny astronaut, and an animated HUD instrument: dark **Pressure Gauge Card** (`AIR PRESSURE (EARTH = 1,013)` needle sweeping down to `6 mbar`), glowing cyan **Thermometer** (`-60°C` / `-125°C`), **`DOORMAT NOTICE`** prop, or **`22 MIN DELAY`** radio arc. | Multi-layer parallax ridge scroll, animated gauge needle / mercury column, subtle dust motes. |
| **`xray`** | Dark navy blueprint grid (`#060913` + `#121f38` grid lines), bold white top header (`REMEMBER THAT FIZZ?` / `CHEST X-RAY ×6`), neon-green (`#4ade80`) rounded torso+head diagram with glowing internal hotspot and red pointer line to dark pill badge (`SALIVA: BOILING` / `0.64 mSv / DAY`). | Subtle blueprint zoom creep, pulsing glow hotspot, callout line draw-in. |
| **`receipt`** (overlay or right panel) | Jagged-edge paper thermal receipt (`MARS SODA CO.`) with dotted prices (`$0`) and `TOTAL: YOU` in red, stamped with a tilted bold bordered badge (`CARBONATED`). | Slide-up entrance + rubber-stamp scale slam on beat word. |
| **`evidence`** | 2D planetary ridge backdrop with a slightly tilted white-bordered **real NASA/JPL photograph**, red top location pill (`PHOENIX LANDER · 2008 · MARTIAN SOIL IN ITS SCOOP`), bottom-left dark credit badge (`NASA/JPL-Caltech/...`), and optional upper-left stacked dark metric counters (`90 days BUILT TO LAST` / `14.4 years ACTUALLY LASTED`). | Gentle photo float/tilt + staggered metric card slide-in. |
| **`magma_twist`** | Subsurface layered Martian crust cross-section with glowing molten chamber (`8–11 KM DOWN`), tiny surface astronaut silhouette above, and explicit amber/red verification pill (`UNPROVEN · POSSIBLE, NOT FOUND`). | Heat shimmer pulse in magma chamber + slow pan down through rock strata. |

---

## 4. The 3 Mandatory Orbit Stills QA Checks

Before encoding the final MP4, the reference workflow renders a full test grid (`stills/sheet.jpg`) and explicitly checks for 3 layout/data bugs:
1. **`GAUGE ROUNDS TO 1%` Trap**: When atmospheric pressure is `<1%` of Earth's (`6 / 1013 = 0.59%`), naive integer rounding displays `1%` or `0%`. Always display exact decimal (`0.6%`) or sub-1% text (`<1% · 6 mbar`).
2. **`TEMPS OVERLAP` Trap**: Putting average (`-60°C`) and pole extreme (`-125°C`) side-by-side or too close horizontally causes the big condensed numerals to clip into each other. Give them clean spacing (`>=140px` horizontally or stacked vertically with `>=110px` spacing).
3. **`COUNTER HITS PHOTO TAG` Trap**: In the NASA Opportunity rover slide, placing comparison counters (`90 days` / `14.4 years`) too low on the left collides with the bottom-left `NASA/JPL-Caltech` photo credit tag (`y ≈ 940`). Keep left-column counter cards in the upper half (`y = 200..540`).
