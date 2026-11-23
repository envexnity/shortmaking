# Ponytail Audit — `ultra` Mode (Architectural Surgery & Demolition Plan)

**When active:** Pre-launch security/scale audit, rescuing an over-engineered or AI-bloated repo, or preparing a major simplification sprint.

## Deep Audit Protocol
1. **Graph & Dependency Mapping:** Query `graphify` (if available) or map all entry points, exports, and dependency imports; identify orphan files, zero-caller exports, circular imports, and single-use wrapper layers.
2. **Critical-Path Adversarial Audit:** Trace auth, billing, persistence, concurrency, and external API trust boundaries end-to-end for concrete failure/exploit cases.
3. **Dependency Audit:** Flag every installed dependency replaceable by stdlib/platform features or `<20` lines of code.
4. **Phased Cut-List:** Rank all findings into:
   - **Phase 1 — Must Fix Now** (bugs, security, data loss, scale cliffs)
   - **Phase 2 — Safe Deletions & Merges** (exact files/exports/deps to delete with zero behavior change, ordered safest-first)
   - **Phase 3 — Structural Simplifications** (collapsing redundant layers/state)

## Output Format
- `What this repo does:` + assumed load + threat surface.
- Up to 25 numbered findings across the 3 phases (concrete case + exact fix + estimated LOC/dep delta).
- End with `Verdict:`, `Total Cuttable: -<N> lines, -<M> files, -<K> dependencies.`, and `Not checked:`. Changes no code.
