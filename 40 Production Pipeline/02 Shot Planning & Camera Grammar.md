---
title: 02 Shot Planning & Camera Grammar
tags:
  - pipeline
  - camera
  - motion
  - animation
  - storyboarding
area: pipeline
style: all
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Exact measured camera motion laws from the 32,000-frame reference study—hard cuts vs. 18-40f smootherstep glides, 0.15-0.35%/f hold creeps, and 7-frame sign-flipping impact kicks.
---

# 02 Shot Planning & Camera Grammar (`story.ts` / `motion.js`)

> [!IMPORTANT] Source Code & Measured Report
> - **Implementations**: `90 Templates & Starter Kits/cartoon-3d-short-kit/bridge/story.ts` & `cartoon-audio-short-kit/engine/motion.js`
> - **Full Raw Report**: `.agents/skills/cartoon-3d-short/references/reports/motion.md`

Across the 20 reference shorts (`~32,000 frames`), camera movement is **never linear, never static, and never driven by random Perlin noise**. It obeys four mathematical primitives: **`cut`**, **`glide`**, **`push`**, and **`kick`**.

---

## 1. Shot Duration & Cut Cadence

- **Average Shot Length**: **`2.8 – 4.2 seconds` (`84 – 126 frames` at 30fps)**.
- **Fast Montage / Escalation**: **`1.2 – 2.0 seconds` (`36 – 60 frames`)** during rapid-fire jokes or `"Luckily / Unluckily"` reversals.
- **The 30-Degree / 40% Scale Rule**:
  - When making a **Hard Cut** (`1 frame`), the new camera MUST differ by **`≥ 30°` in azimuth** OR **`≥ 40%` in subject distance** (e.g., Wide `[0, 3.2, 14]` → Medium Close-Up `[-1.2, 1.65, 3.8]`).
  - If two framing positions are close (`< 2.5m` apart in the same zone), connect them with a **Smootherstep Glide (`18–40 frames`)** instead of a hard cut.

---

## 2. The 4 Camera Motion Primitives (`motion.js`)

### Primitive 1: `smootherstep(u)` Glides (`18–40 frames`)
Standard cubic `smoothstep` has non-zero second derivatives at `u = 0` and `u = 1`, which produces a visible jerk when a pan starts or stops. Always use Ken Perlin's **quintic `smootherstep`** (`6u^5 - 15u^4 + 10u^3`), whose velocity AND acceleration are zero at both endpoints:

```typescript
export function smootherstep(u: number): number {
  const x = Math.max(0, Math.min(1, u));
  return x * x * x * (x * (x * 6 - 15) + 10);
}
```
- **Speed Cap**: Peak optical flow during a glide must stay **`≤ 25 px/frame` at 720p** (`≤ 38 px/frame` at 1080p) so the viewer's eye never loses the subject.

### Primitive 2: Mandatory Hold Creep — `push(cam, baseCam, u, rate)`
**No camera hold may ever sit static for `≥ 4 frames`.** During every dialogue or reaction hold, the camera creeps slowly toward (or pulls back from) the `lookAt` target along the view ray:
- **Standard Hold Creep**: **`0.15% – 0.35%` of distance per frame** (`~4.5% – 10%` dolly over a 3-second shot).
- **Punch-Word Push**: **`0.60%` per frame** over `12–18 frames` on dramatic reveals (*"You see,"*).

```typescript
export function push(camPos: THREE.Vector3, lookAt: THREE.Vector3, framesElapsed: number, rate = 0.0022) {
  const factor = Math.max(0.65, 1 - framesElapsed * rate);
  camPos.lerpVectors(lookAt, camPos, factor);
}
```

### Primitive 3: 7-Frame Sign-Flipping Impact `KICKS`
When a bolt snaps, a sword strikes, a horse lands on the general, or a gavel slams, **never use random `Math.random()` shake**. The reference shorts use a **deterministic 7-frame alternating-sign damped oscillation** (`±1` sign flip every frame, decaying linearly by `1 - k/7`):

```typescript
// Deterministic 7-frame impact kick (story.ts / motion.js)
export function applyKick(cam: THREE.PerspectiveCamera, frame: number, startFrame: number, ampY = 0.14, ampRoll = 0.022) {
  const k = frame - startFrame;
  if (k < 0 || k >= 7) return;
  const decay = 1 - k / 7;
  const sign = (k % 2 === 0) ? 1 : -1;
  cam.position.y += sign * ampY * decay;
  cam.rotation.z += sign * ampRoll * decay;
}
```

### Primitive 4: Walk & March Bobbing (`walkPose`)
- When characters walk or march across a 3D set, their vertical bounce is a rectified sine wave (`Math.abs(Math.sin(phase)) * 0.06m`) at **`2.0 – 2.4 steps/sec`** (`118–140 BPM`), with leg stride alternating in opposite phase and body tilt (`±0.035 rad`).
