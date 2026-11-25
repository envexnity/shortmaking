# Ponytail Debt — `ultra` Mode (Age + Live Ceiling-Breach Audit)

**When active:** Scaling milestone, production readiness review, or quarterly tech-debt paydown.

## Steps
1. Run the shortcut grep across the repo.
2. For each marker, run `git blame -L<line>,<line>` to capture **author & age**.
3. **Live Ceiling Check:** Inspect current repo config, data sizes, user/concurrency assumptions, or usage counts against each marker's stated `ceiling`. Classify each marker as:
   - **`BREACHED` (Upgrade Now):** Current usage/scale already exceeds or approaches the stated ceiling.
   - **`ROTTING` (`no-trigger` or `>180` days untouched):** Missing trigger or stale deferral needing review.
   - **`HEALTHY`:** Safely below ceiling.
4. Output grouped by severity (`BREACHED` -> `ROTTING` -> `HEALTHY`), with exact smallest upgrade path for every `BREACHED` item. Reads only unless asked to write `PONYTAIL-DEBT.md`.
