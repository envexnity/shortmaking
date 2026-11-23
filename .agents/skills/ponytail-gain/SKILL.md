---
name: ponytail-gain
description: >
  Show ponytail's measured benchmark savings (code, tokens, cost, speed) in
  lite, full, or ultra detail. One-shot display, changes nothing.
argument-hint: "[lite|full|ultra|auto]"
license: MIT
---

# Ponytail Gain (Auto-Routed: `lite` | `full` | `ultra`)

One-shot display. Do NOT change mode or write files.

## Situational Auto-Selection
| Situation | Tier | Action |
| :--- | :--- | :--- |
| Inline citation inside another answer / tight token budget | **`lite`** | Read & follow `lite.md` (2-line summary). |
| User asks "what does ponytail save?" / `/ponytail-gain` | **`full`** *(below)* | Display full ASCII scoreboard below. |
| Designing team/agent token-saving stack | **`ultra`** | Read & follow `ultra.md` (adds tier trade-offs + compound input/output token math). |

## Scoreboard (`full`)
Source: Ponytail 5 agentic benchmark (`39 tasks x 5 runs`, Opus 5.5, 18 tasks with hidden safety/correctness checks; geometric mean of per-task medians):

```
  ponytail gain           benchmark · 39 tasks x 5 runs · Opus 5.5

  no-skill        ████████████████████  100%
  Lines of code   █████████···········   47%   ▼ 53%
  Output tokens   ███████████·········   55%   ▼ 45%
  Cost            ███████████████·····   74%   ▼ 26%
  Time            ████████████········   59%   ▼ 41%
  Hidden checks passed   97%  (no-skill 96%)
  Tests where logic needs one   98%  (no-skill 68%)

  This repo:  /ponytail-debt  (deferred shortcuts)
              /ponytail-audit (what's still cuttable)
```

**Honesty boundary:** Benchmark averages only. NEVER fabricate a per-repo savings number ("saved X tokens here")—there is no unbuilt baseline.
