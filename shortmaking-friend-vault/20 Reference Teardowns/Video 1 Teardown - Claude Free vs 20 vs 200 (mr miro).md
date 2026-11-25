---
title: Video 1 Teardown — Claude Free vs $20 vs $200 (mr miro)
tags:
  - teardown
  - claude
  - economics
  - cartoon-audio-short
  -cartoon-3d-short
area: teardowns
style: 2d-in-3d-toon
status: evergreen
created: 2026-11-15
updated: 2026-11-15
summary: Complete technical breakdown of mr miro's experiment (youtu.be/zGVQt4xoZAM) testing the exact same viral Napoleon vs. Rabbits cartoon prompt across Claude Free, $20 Pro, and $200 Max.
---

# Video 1 Teardown — Claude Free vs $20 vs $200: Same Prompt, Same Viral Cartoon?

- **Creator**: **mr miro** (`@miromotions`)
- **Video URL**: [https://youtu.be/zGVQt4xoZAM](https://youtu.be/zGVQt4xoZAM)
- **Test Story**: *In 1807, Napoleon Bonaparte was defeated by 3,000 domesticated rabbits* (Chief of Staff Berthier accidentally bought tame farm rabbits that swarmed Napoleon looking for cabbages).
- **Core Premise**: Run the **exact same skill (`cartoon-3d-short` / `cartoon-audio-short`), same prompt, and same ElevenLabs voiceover** across all 4 Claude tiers (Free, $20 Pro, $100 Max, $200 Max) to isolate what the subscription tier actually buys you.

---

## 1. Side-by-Side Benchmark Results

| Metric | Free Plan ($0) | Pro Plan ($20/mo) | Max 5× ($100/mo) | Max 20× ($200/mo) |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Surface** | Web Chat (Sonnet, Medium effort) | **Claude Code CLI** (Opus, High effort) | **Claude Code CLI** (Opus/Fable, High effort) | **Claude Code CLI** (Opus/Fable, High effort) |
| **Wall-Clock Build Time** | ~45 mins + 5-hour rate-limit pause | **37 minutes** (continuous) | **1 hr 12 mins** (deep polish loop) | **1 hr 12 mins** (deep polish loop) |
| **Self-Inspection Stills Rendered** | `0` (cannot render video on server) | **`38 test stills`** across 2 polish passes | **`68 test stills`** + 3 full video renders | **`68 test stills`** + 3 full video renders |
| **5-Hour Session Quota Used** | `100%` (hit hard wall at minute 19) | **`19%`** of 5h session | `~14%` of 5h session | `~3.5%` of 5h session |
| **Weekly Quota Used** | N/A | **`4%`** of weekly limit | **`7%`** of weekly limit | **`1.5%`** of weekly limit |
| **Videos / Week Capacity** | `~2–3 shorts/wk` (manual render) | **`~25 shorts/wk`** | **`~14 deeply-polished shorts/wk`** | **`~55–65 deeply-polished shorts/wk`** |

---

## 2. Why Free Failed vs. Why $20 Pro Succeeded

### What Happened on the Free Plan (Sonnet Web Chat)
1. **Cannot Run Local Headless Chromium or FFmpeg**: Because the Free plan runs inside the web chat sandbox, it cannot execute Playwright (`render.mjs`) or Remotion (`npx remotion render`) locally to see what its own frames look like.
2. **Hit the 5-Hour Cap at 19 Minutes**: Writing the Three.js scene (`roman.js` / `world.ts`), character generator (`toon.ts`), and Python audio synthesizer (`audio.py`) exhausted the Free session window at minute 19 before finishing.
3. **Blind Geometry Bugs**: Because Free could not render stills and inspect them:
   - The **carriage sat sideways** on the road.
   - The **rabbit cages were missing bars**.
   - **Zero procedural sound effects** were mixed into the final output.
   - However, because the **Skill (`SKILL.md`)** contained the exact character math (`#241726` plum ink, bean heads, two-tone shaders), the character style itself still looked surprisingly authentic.

### What Happened on the $20 Pro Plan (Claude Code + Opus High Effort)
1. **Autonomous Render-Inspect-Fix Loop**: Running inside **Claude Code** on the local machine, Opus rendered **38 test stills**, looked at the actual PNG frames using vision, and caught its own mistakes without human intervention:
   - *Self-Fix 1*: Noticed a pine tree was blocking Napoleon's face in Shot 2 → moved the tree outside the `>2m` foreground clearance zone.
   - *Self-Fix 2*: Noticed the golden-hour shot looked flat → adjusted the directional light and shadow tint.
2. **Full Procedural Audio Synthesis**: Wrote a custom Python script that synthesized **horse hooves, cage latch clicks, rabbit scurrying, carriage wheels, and a military snare march** synced to `words.json`.
3. **The Verdict on $20 Pro**: At **4% of weekly quota per video (~25 videos/week)**, the $20 Pro plan running in Claude Code (or Antigravity with local shell access) is the **highest-ROI sweet spot** for solo creators.

### What the $100 / $200 Max Plan Added
- Instead of stopping after 2 polish passes (`38 stills`), the Max run executed **68 test stills and 3 full video renders** over `1h 12m`:
  - Built a **custom terrain height function** so hills rolled naturally behind the estate.
  - Added **instanced grass blades, wildflowers, birch trees, and animated cabbage chewing** (`mouth` oscillating with green leaf particles).
  - Fixed a **floating carriage wheel** (`y` offset bug) and **rabbit ear clipping** through Napoleon's bicorn hat on the third inspection pass.

---

## 3. Core Engineering Takeaways from Video 1

> [!IMPORTANT] The Skill Is 80% of the Quality; The Self-Inspection Loop Is the Other 20%
> 1. **Never prompt an LLM to "make an animated video" without a measured Skill.** Even on Free Sonnet, loading `.agents/skills/cartoon-3d-short/SKILL.md` produced the signature bean-head + 3D world look because all the shader and proportion constants were pre-computed.
> 2. **Never let an agent ship a 3D scene blind.** Always force the agent to run `bridge-stills.mjs` or `sheet.py` (`stills.jpg`) and inspect every beat with `read_file` before final render.
> 3. **Keep camera cuts synced to `words.json`, not arbitrary second markers.** In the Napoleon test, cutting on *"Charge!"* (`t = 22.4s`) and *"Three thousand rabbits"* (`t = 14.1s`) is what made the Pro and Max renders feel edited by a human.

---

## 4. Related Vault Notes
- [[Video 2 Teardown - Viral 2D-in-3D Shorts Workflow (Mr omi)]]
- [[Style 1 - 2D-in-3D Toon World (Remotion + Three.js)]]
- [[Style 2 - Standalone 2D-in-3D Kit (Playwright + Three.js, No Remotion)]]
- [[The 12-Agent Look-Match & Sandbox Merge Architecture]]
