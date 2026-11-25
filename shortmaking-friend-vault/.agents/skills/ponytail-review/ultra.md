# Ponytail Review — `ultra` Mode (Adversarial Gate & Deletion Hunt)

**When active:** Auth/payments/crypto/data migrations, pre-production release PRs, or large AI-generated diffs suspected of hidden bugs or bloat.

## Deep Verification Steps
1. **Adversarial flow trace:** Trace every untrusted input to sink (DB, shell, HTML, filesystem, network). Actively try to construct a concrete exploit, race condition, partial-write corruption, or empty/max-bound crash.
2. **Blast-radius grep:** Check EVERY caller, test, migration, env var, and serialization schema touched directly or transitively.
3. **Ruthless Lean & Deletion Pass:** Hunt for every unnecessary abstraction, wrapper, new dependency, redundant state copy, defensive dead branch, and copy-pasted block. Compute an explicit **Deletion Plan** (`-N` lines, `-M` deps).
4. **Test-quality audit:** Reject mocked-out tautology tests; verify at least one real integration/edge-case test fails if the core logic breaks.

## Output Format
- `What this change does:` + assumed load & threat model (2-3 sentences).
- Numbered **Must fix** / **Should fix** / **Deletion & Simplification Plan** (each with concrete case, exact smallest patch, and blast radius).
- End with `Verdict:`, `Lean: -<N> lines, -<M> deps cuttable.`, and explicit `Not checked:`. Changes no code.
