---
name: ponytail-audit
description: >
  Quality audit of a whole repo (lite, full, ultra): bugs, security, scale,
  missing tests, speed, and what to delete/merge/split. Auto-selects lite.md
  (fast 60s triage), full (ranked top <=20 findings), or ultra.md (deep
  architectural surgery & demolition cut-list). One-shot report, changes nothing.
argument-hint: "[lite|full|ultra|auto] [path]"
license: MIT
---

# Ponytail Audit (Auto-Routed: `lite` | `full` | `ultra`)

Audit the repo like the senior developer who just inherited it and will be paged when it breaks.
Order: **correct -> safe -> holds under load -> tested -> fast -> lean.** Changes no code.

## Situational Auto-Selection
| Situation | Tier | Action |
| :--- | :--- | :--- |
| Fast repo onboarding, quick health check, or tight token budget | **`lite`** | Read & follow `lite.md` (entry points + deps + top 5 targets only). |
| Standard repo health check or inherited codebase | **`full`** *(below)* | Follow full ranked audit below (`<=20` findings). |
| Pre-launch security/scale gate, rescuing bloated vibe-coded repo, major rewrite | **`ultra`** | Read & follow `ultra.md` (graph/caller blast-radius + phased cut-list). |

## 1. Map first (`full`)
- Audit named folder/package or whole repo. Use code graph (`graphify`) or entry-point map before reading files.
- Read README, build/deploy config, dependency manifest, entry points (main/routes/handlers/jobs/CLI), and tests.
- State assumed load. Trace critical paths fully (user input, money, auth, writes, background jobs, shared state). On big repos go deep where mistakes cost most and state what you skipped.

## 2. Look for (6 Lenses)
1. **Bug** · 2. **Risk** (security/data loss) · 3. **Scale** (races, N+1, unbounded growth, `O(n^2)`) · 4. **Missing test** · 5. **Speed** · 6. **Lean** (dead code, duplicate helpers, stdlib/native replacements, 1-impl abstractions, mixed-job functions).

## 3. Check & Output
- Concrete failure case required per finding; grep whole tree (including dynamic/string refs) before marking unused. Respect `shortcut:` comments unless ceiling is crossed.
- Start with `What this repo does:` (2-3 sentences) + assumed load.
- Group numbered findings (**Must fix**, **Should fix**, **Nice to have**), max 20 (note count omitted). Each finding has: **What this is**, **Problem**, **Fix**, **If we skip it**.
- End with `Verdict:`, `Lean: -<N> lines, -<M> dependencies possible.`, and `Not checked:`.
