---
name: ponytail-review
description: >
  Quality review of a change (lite, full, ultra): logic correctness, safety,
  real load, tests, speed, and lean code. Auto-selects lite.md (<40-line diffs),
  full (standard PRs), or ultra.md (high-risk/auth/money/large AI diffs).
  Use for "review this", "code review", "review PR", /ponytail-review.
argument-hint: "[lite|full|ultra|auto] [target]"
license: MIT
---

# Ponytail Review (Auto-Routed: `lite` | `full` | `ultra`)

Review a change like the senior developer who will be paged when it breaks.
Priority order: **correct -> safe -> holds under load -> tested -> fast -> lean.**
Lists findings; changes no code.

## Situational Auto-Selection
| Situation | Tier | Action |
| :--- | :--- | :--- |
| Tiny `<40`-line diff, hotfix, CSS/copy tweak, fast mid-iteration check | **`lite`** | Read & follow `lite.md` (`<=5` terse bullets + Ship/Fix verdict). |
| Standard PR, feature branch, or multi-file commit | **`full`** *(below)* | Follow full 6-lens review below. |
| Auth/money/security/data-migration PR, production release, or large/bloated AI diff | **`ultra`** | Read & follow `ultra.md` (adversarial trace + deletion plan). |

## 1. Understand first (`full`)
- Review named target (uncommitted/staged, branch, PR, files); default to uncommitted changes or last commit.
- Read the diff AND connected code: callers of changed functions, callees, tests, README.
- Trace real data flow (input -> storage -> output) and state the expected load assumed.

## 2. Look for (6 Lenses)
1. **Bug:** wrong result, crash, missed edge case (empty, zero, last item, rounding, TZ), broken caller, patch in one caller leaving shared code broken.
2. **Risk:** injection, weak randomness, secrets, missing trust-boundary validation, swallowed errors, unsafe write order/no transaction.
3. **Scale:** check-then-write races, duplicated per-process work, unbounded memory, N+1 queries, `O(n^2)` on big input.
4. **Missing test:** risky new logic with no failing-when-broken test (1 good test, not coverage vanity).
5. **Speed:** real slowdowns (hot-loop redundant work).
6. **Lean:** delete dead code/unused flags; reuse existing repo helper (name path); use stdlib/native; cut 1-impl abstractions; merge near-copies; split multi-job functions by job (never by line count).

## 3. Verify & Report
- Every finding requires a concrete failure case ("input X -> wrong result Y"). Confirm callers/deadness by grep. Respect `shortcut:` comments unless current load crossed their ceiling. No style nitpicks.
- Plain English. Start with `What this change does:` (2-3 sentences).
- Group numbered findings into **Must fix**, **Should fix**, **Nice to have** (skip empty groups). Each finding has: **What this is**, **Problem**, **Fix** (smallest working fix), **If we skip it**.
- End with `Verdict: Ship.` or `Verdict: fix <nums> first.`, `Lean: -<N> lines possible.`, and `Not checked:` (1 line if relevant).
