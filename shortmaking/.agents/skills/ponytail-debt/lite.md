# Ponytail Debt — `lite` Mode (Instant Count & Pointers)

**When active:** Quick pre-commit check or low-token scan.

## Steps
1. Run `git grep --no-index --exclude-standard -nE '(#|//|/[*]) ?(shortcut|ponytail):'`.
2. Print 1 line per hit: `<file>:<line> — <comment text>` (flag missing triggers with `[no-trigger]`).
3. End with `<N> markers (<M> no-trigger).` Zero `git blame`, zero extra prose.
