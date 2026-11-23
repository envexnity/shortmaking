# Ponytail Audit — `lite` Mode (60-Second Triage Scan)

**When active:** Repo onboarding, quick health check, or token-capped session. Do NOT read every file.

## Fast Map (Minimal Token Budget)
1. Read only: `README.md`, dependency manifest (`package.json`/`pyproject.toml`/`Cargo.toml`), directory tree (depth 2), and 1-2 primary entry points.
2. Check 4 high-signal targets: obvious security/secret leaks, bloated/redundant dependencies, glaring architectural duplication, and missing smoke tests.

## Output Format
- `Repo summary:` 2 sentences + assumed load.
- **Top 5 Highest-Impact Findings** (numbered, 2 lines each: `file:line` — problem -> smallest fix).
- `Quick Lean Estimate:` top deletable deps/modules.
- `Not checked:` explicit list of unread areas. Changes no code.
