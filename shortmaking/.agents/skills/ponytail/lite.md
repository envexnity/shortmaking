# Ponytail — `lite` Mode (Low-Friction Pragmatism)

**When active:** Explicit clear spec, creative/UI/visual polish, rapid prototype, or tiny `<25`-line surgical tweak where challenging scope would waste turns.

## Rules
1. **Build exactly what the user asked** — no unsolicited debate, no scope pushback.
2. **Still avoid bloat:** reuse existing helpers/stdlib/installed deps instead of adding new packages or unused abstractions.
3. **Finish cleanly:** update broken callers/tests if touched; run a quick check on non-trivial logic.
4. **1-line footer:** End your reply with one short line naming any simpler/smaller alternative (if one exists) and anything not checked—let the user decide whether to simplify later.

**Never cut:** trust-boundary validation, data-loss error handling, security, accessibility, explicit user requirements.
