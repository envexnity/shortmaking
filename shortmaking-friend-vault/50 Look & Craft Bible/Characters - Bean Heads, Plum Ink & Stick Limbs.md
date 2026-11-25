---
title: Characters — Bean Heads, Plum Ink & Stick Limbs
tags:
  - look-bible
  - characters
  - canvas2d
  - toon
area: look-bible
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Exact measured anatomy, superellipse bean-head equations, #241726 plum variable-width stroke math, expressions, and 4-frame blink cycles from the 20-short reference study.
---

# Characters — Bean Heads, Plum Ink & Stick Limbs (`toon.ts`)

> [!IMPORTANT] Source Code & Measured Report
> - **Implementation**: `90 Templates & Starter Kits/cartoon-3d-short-kit/bridge/toon.ts` & `cast.ts`
> - **Full Raw Report**: `.agents/skills/cartoon-3d-short/references/reports/characters.md`

Every character in the 2D-in-3D Toon style is a **flat `600×1000` Canvas2D texture mapped onto a `1.32m × 2.20m` (`2.15m` world height) vertical card** standing inside the 3D scene (`soles at y = 975` so feet touch `y = 0`).

---

## 1. Adult vs. Child Proportions (Measured in Head-Heights `HH`)

| Body Segment | Adult (`3.5 HH` Total) | Child (`2.8 HH` Total) | Canvas / Pen Construction |
| :--- | :--- | :--- | :--- |
| **Head (`1.0 HH`)** | `rx = 115, ry = 108` (`H/W = 0.94`) | `rx = 115, ry = 110` (`H/W = 0.96`, larger relative to body) | Asymmetric superellipse bean (`nTop = 1.75`, `nBot = 2.30`, `egg = -0.12`, `asym = +0.08`) |
| **Torso (`1.1 HH`)** | Rounded trapezoid / bean (`wTop = 96`, `wBot = 118`, `h = 235`) | Shorter bean (`h = 165`) | Filled with muted costume color + right/bottom crescent shadow (`alpha = 0.14`) |
| **Stick Legs (`1.4 HH`)** | Single-stroke black/plum lines (`w = 5.8u`, `len = 290px`) | Shorter stick legs (`len = 195px`) | Two parallel/striding strokes + simple horizontal foot ticks (`18px`) |
| **Arms & Hands** | Single-stroke Bezier (`w = 5.5u`) + **solid ink-dot hand (`r = 5.5u`)** | Same (`r = 5.0u`) | **Zero fingers** unless holding a close-up hero prop; hand is a solid `#241726` circle |

---

## 2. The Superellipse Bean-Head Equation

Standard circles (`arc()`) or ellipses (`ellipse()`) look robotic and screamed "AI-generated" in blind tests. The reference shorts use a **squashed superellipse with a heavier jaw (`egg = -0.12`) and slight 3/4 cheek bulge (`asym = +0.08`)**:

```typescript
// Superellipse bean contour (toon.ts)
// nTop = 1.75 (rounder cranium), nBot = 2.30 (flatter/squarer jaw)
for (let i = 0; i <= N; i++) {
  const a = (i / N) * Math.PI * 2;
  const ca = Math.cos(a), sa = Math.sin(a);
  const n = sa < 0 ? 1.75 : 2.30;
  let x = Math.sign(ca) * Math.pow(Math.abs(ca), 2 / n) * rx;
  let y = Math.sign(sa) * Math.pow(Math.abs(sa), 2 / n) * ry;
  // Widen lower jaw & push right cheek out for 3/4 turn:
  x *= 1 - (-0.12) * (y / ry);
  if (x > 0) x *= 1 + 0.08 * Math.sin((y / ry + 1) * Math.PI * 0.5);
}
```

---

## 3. Variable-Width Plum Ink (`#241726`) — The `Pen` Class

- **Never use pure `#000000` on characters**: The measured outline colour across all 20 reference shorts is **`#241726` (dark warm plum/charcoal)**.
- **3:1 Thick-to-Thin Calligraphic Weighting**: The `Pen` class samples each Bezier path into ribbon quads and modulates width by the surface normal's dot product with a `64°` shadow-side vector:
  - **Lit top-left edge**: `0.58 × baseWidth` (`~2.5 px`)
  - **Shadowed bottom-right jaw & under-chin**: `1.38 × baseWidth` (`~6.1 px`)
- **Soft Crescent Self-Shading**: Every head and torso receives a multiply-blended crescent shadow (`#241726` at `alpha = 0.13`) along the right-hand and lower-jaw contour.

---

## 4. Facial Features, Blinks & Acting Rules

| Feature | Exact Measured Spec | Anti-Slop Rule |
| :--- | :--- | :--- |
| **Eye Placement** | `0.45` down from head crown; horizontal spacing **`0.26 × headW`** (`±30px` shifted `+12px` toward facing direction) | Never place eyes at `0.5` width apart (looks wall-eyed). |
| **Default Eye (`'lidded'`)** | Solid `#241726` pupil disc (`r = 9.5`) clipped/topped by a horizontal upper eyelid stroke (`w = 4.2`) + skin-colored mask above | **Zero white sclera in neutral/lidded state; zero white catchlight dots; zero pink cheek blush.** |
| **Other Eye States** | `'dot'` (surprised/alert), `'wide'` (white sclera + small pupil for terror), `'happy'` (`^` arcs), `'dead'` (`X X`), `'wink'` | Trigger `'wide'` **2 frames before** the spoken shock word. |
| **5 Mouth Shapes** | `'line'` (default deadpan), `'smirk'`, `'frown'`, `'o'` (whistle/shock), `'open'` (rounded D-mouth filled `#3a1c24` with `#d4625a` tongue arc) | During speech, alternate `'line'` ↔ `'open'`/`'o'` at **`10 Hz`** gated by VO envelope. |
| **Blink Cycle (`4 frames`)** | Occurs every **`0.5–2.3s` (median `1.2s`)** + on every expression swap: `[0.5, 1.0, 1.0, 0.5]` lid closure over 4 frames at 30fps | Never leave eyes unblinking for `>70 frames`. |
