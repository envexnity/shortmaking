---
name: ponytail-help
description: >
  Quick reference for all 6 ponytail skills, 3 tiers (lite, full, ultra), and
  situational auto-routing. One-shot display, changes nothing.
argument-hint: "[lite|full|ultra|auto]"
license: MIT
---

# Ponytail Help (Auto-Routed: `lite` | `full` | `ultra`)

One-shot display. Do NOT change mode or write files.

## Situational Auto-Selection
- Tight budget / quick command reminder -> `lite.md`
- Standard human help card -> `full` *(below)*
- Full agent auto-routing matrix & vault onboarding -> `ultra.md`

## Levels (Available on ALL 6 Ponytail Skills)
| Level | Trigger | Behavior |
| :--- | :--- | :--- |
| **Lite** | `/ponytail lite` (or `<skill> lite`) | Minimum friction & lowest token output; skips pushback/deep prose. |
| **Full** | `/ponytail` *(default)* | Smallest complete change / full 6-lens review / grouped ledger. |
| **Ultra** | `/ponytail ultra` (or `<skill> ultra`) | Challenges scope before building / adversarial review / live ceiling-breach check. |
| **Auto** | `/ponytail auto` | Agent automatically selects `lite`, `full`, or `ultra` per task using `ROUTER.md`. |

## All 6 Skills
- **`ponytail`** — Lazy senior-dev coding (`lite` | `full` | `ultra`)
- **`ponytail-review`** — Diff / PR / commit quality & lean review (`lite` | `full` | `ultra`)
- **`ponytail-audit`** — Whole-repo quality & bloat audit (`lite` | `full` | `ultra`)
- **`ponytail-debt`** — Harvest `shortcut:` comments into a debt ledger (`lite` | `full` | `ultra`)
- **`ponytail-gain`** — Measured benchmark savings (`lite` | `full` | `ultra`)
- **`ponytail-help`** — This card (`lite` | `full` | `ultra`)

Deactivate: `"stop ponytail"`, `"normal mode"`, or `/ponytail off`.
Upstream repo: https://github.com/DietrichGebert/ponytail
