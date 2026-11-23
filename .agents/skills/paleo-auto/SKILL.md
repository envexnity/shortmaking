---
name: paleo-auto
description: >
  Zero-touch automatic token-saving orchestrator (MIT, mocasus/paleo v2.5.0).
  Auto-detects long sessions (>15 turns), bulky tool output (>2k tokens), or
  high context pressure (>60%) and activates safe defaults without manual toggles.
version: 2.5.0
license: MIT
---

# paleo-auto

Zero-touch session token guard. Never overrides explicit user skill choices and never auto-forces `ultra` or hard-strict modes unless requested.

## Auto-Detection Triggers
| Condition | Action |
| :--- | :--- |
| Fresh session (first 2 turns) | Baseline terse delivery (`full` — drop filler, keep code/facts exact) |
| Session length `>15` turns | Activate `paleo-trim-context` (summarize stale tool outputs, keep task state) |
| Single tool output `>2,000` est. tokens | Filter/trim subsequent noisy commands (`shell_trim.py` / quiet flags) |
| Context approaching `>60%` capacity | Prepare lossless `HANDOFF.md` (`context-diet`) at next verified milestone |
| Expensive frontier model (`Pro`/`Opus`) | Delegate noisy discovery/boilerplate to `Flash`/`Haiku` subagents |

Report activation in 1 non-intrusive line. Deactivate: `"disable paleo-auto"` / `"stop auto"`.
