---
name: paleo-trim-context
description: >
  Pre-thinking context trimmer (MIT, mocasus/paleo v2.5.0). Distills bulky docs,
  logs, and stale tool observations into key facts + exact source pointers before
  expensive reasoning, keeping ground truth intact.
version: 2.5.0
license: MIT
---

# paleo-trim-context

Keep active context small without losing task state.

## Rules
- **Pre-thinking compression:** Before calling an expensive model or reasoning deeply, distill retrieved docs/dumps into key facts + exact `file:line` pointers.
- **Drop stale noise:** Resolved errors, obsolete file reads, duplicate logs, passing test spam.
- **Keep ground truth:** Latest user instruction, exact file paths, IDs, current plan, open TODOs, locked decisions.
- **Effort pinning:** Trivial step -> low effort, reuse prior conclusions instead of re-deriving.
- **Never guess-drop:** If unsure whether a constraint is still needed, keep it.
