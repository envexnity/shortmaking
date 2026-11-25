---
title: Post-Publish Retention Postmortem Template
tags:
  - template
  - analytics
  - retention
  - postmortem
  - growth
  - ab-testing
area: templates
style: all
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Standardized 48-hour and 7-day analytics autopsy template for diagnosing retention curve drop-offs, scoring hook performance, and deciding whether to clone a winner into a 5-part series or remake the opening 3 seconds.
---

# Retention Postmortem — `[VIDEO TITLE]`

- **Video Folder**: `videos/[slug]/`
- **Style / Track**: `[Track 1–7 / Non-3D Style]`
- **Duration**: `[__._ s]` · **Word Rate**: `[__._ wps]` · **Publish Time (UTC / EST / WIB)**: `[YYYY-MM-DD HH:MM]`
- **A/B Variable Tested**: `[e.g., Paradox Hook vs. "In This World" / 1.1s Cut Cadence / Fish Audio Stage Tags]`

---

## 1. Core Performance Scorecard (`48h` & `7d` Snapshots)

| Platform | Views (`48h`) | Views (`7d`) | `0–3 s` Viewed vs. Swiped (Target `≥76%`) | Avg. % Viewed / APV (Target `≥95%`) | Likes / Comments / Shares Ratio | Outcome Tier (`Flop / Baseline / Outlier ≥3×`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **YouTube Shorts** | | | `%` | `%` | | |
| **TikTok** | | | `%` | `%` | | |
| **Instagram Reels** | | | `%` | `%` | | |

---

## 2. Retention Graph Autopsy (Match to [[05 Editing Rhythm, Pre-Vis Animatics & Retention Graph Forensics]])

- **Primary Curve Shape**: `[ ] 0–3s Cliff` · `[ ] 5–10s Second-Hook Slump` · `[ ] Mid-Video Ski Slope` · `[ ] Premature Drop-Off` · `[ ] Flat Plateau + Replay Spike (WINNER)`
- **Exact Biggest Drop Timestamp (`t = __._ s`)**:
  - *What was on screen at `t`?*: `...`
  - *What was being spoken at `t`?*: `...`
  - *Root cause (dead air / slow exposition / unclear visual / early reveal / weak SFX)*: `...`
- **Highest Replay / Comment Spike Timestamp (`t = __._ s`)**:
  - *What triggered the rewatch or comments?*: `...`
  - *Top recurring audience comment theme*: `...`

---

## 3. Action Decision (Pick Exactly ONE)

- [ ] **CLONE WINNER (`≥3×` median + `≥78%` Viewed + `≥95%` APV)**: Immediately add `3–5` sequels using this exact hook structure & visual format to [[Idea Bank.base]]!
- [ ] **RE-HOOK & RE-RELEASE (`APV ≥ 92%` BUT `Viewed < 70%`)**: Body worked, opening failed. Re-cut ONLY `0.0–3.0 s` (new Frame-0 visual anomaly + tighter 10-word Paradox Hook + new title) and schedule for `+30 days`.
- [ ] **FIX PACING RULE (`Viewed ≥ 75%` BUT `APV < 82%`)**: Hook worked, middle sagged. Identify the exact sluggish beat above and tighten cut cadence (`≤1.4 s`) + `"You see,"` visual payoff on the next script.
- [ ] **RETIRE CONCEPT (`Viewed < 65%` AND `APV < 75%`)**: Topic or angle lacked curiosity gap. Log one clear lesson below and move on.

---

## 4. One Permanent Craft Rule Extracted for Next Upload
> **Rule to Carry Forward**: `[Write 1 concrete, testable change for the very next video — never vague advice like "make it better".]`
