---
name: ponytail-debt
description: >
  Harvest every `shortcut:` (and legacy `ponytail:`) comment into a tracked debt
  ledger (lite, full, ultra). Auto-selects lite.md (fast count/list), full
  (grouped ledger + rot flags), or ultra.md (adds git blame age + live ceiling
  breach detection). One-shot report, changes nothing.
argument-hint: "[lite|full|ultra|auto] [marker]"
license: MIT
---

# Ponytail Debt (Auto-Routed: `lite` | `full` | `ultra`)

Every deliberate ponytail shortcut is marked `shortcut: <ceiling>, <upgrade trigger>` (older code may say `ponytail:`). Harvest them so deferrals never silently rot.

## Situational Auto-Selection
| Situation | Tier | Action |
| :--- | :--- | :--- |
| Fast pre-commit or quick count check | **`lite`** | Read & follow `lite.md` (1 grep, compact list, zero blame). |
| Release prep or sprint backlog grooming | **`full`** *(below)* | Full grouped ledger with `no-trigger` rot flags. |
| Scaling milestone, incident prep, or quarterly debt paydown | **`ultra`** | Read & follow `ultra.md` (adds `git blame` age + checks whether current scale already crossed any ceiling). |

## Scan (`full`)
Run (skipping `.git` and `.gitignore`d paths):
`git grep --no-index --exclude-standard -nE '(#|//|/[*]) ?(shortcut|ponytail):'`
*(If the user names a custom marker like `/ponytail-debt TODO`, grep that instead.)*
Skip false positives (e.g., prose about keyboard shortcuts).

## Output (`full`)
Group by file, one row per marker:
`<file>:<line>, <what was simplified>. ceiling: <limit>. upgrade: <trigger>.`
Flag any marker missing an upgrade trigger with `[no-trigger]`.
End with `<N> markers, <M> with no trigger.` (or `No shortcut debt. Clean ledger.`).
Reads only; write `PONYTAIL-DEBT.md` only if asked.
