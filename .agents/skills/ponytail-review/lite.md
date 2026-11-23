# Ponytail Review — `lite` Mode (Rapid Triage Pass)

**When active:** Diff `<40` lines, quick hotfix, UI/CSS/copy tweak, or mid-iteration sanity check. Save tokens—skip prose ceremonies.

## Scope
- Read the diff + grep callers ONLY if a function signature or return shape changed.
- Check only high-ROI failure modes: **Bug, Security/Data-loss Risk, Broken Caller, Obvious Dead Code / Extra Dep**.

## Output Format (Ultra-Compact)
- `Change:` 1 sentence.
- Numbered bullets (`<=5` max): `<n>. [Must/Should] <file:line> — <concrete failure> -> <1-line fix>`
- `Verdict: Ship.` or `Verdict: Fix <nums>.` (plus `Not checked:` if any).

No 4-paragraph templates, no style nits, changes no code.
