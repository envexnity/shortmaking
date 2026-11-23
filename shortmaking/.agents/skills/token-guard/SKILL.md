---
name: token-guard
description: >
  Master 7-layer zero-quality-loss token optimizer. Enforces graph/grep/slice
  reads, parallel tool batching, filtered CLI output, surgical diffs, prefix
  stability, model-tier delegation, and situational Ponytail/Caveman tiering
  without ever compromising correctness, security, or creative quality.
license: MIT
---

# Token Guard (Zero-Quality-Loss 7-Layer Protocol)

Maximize signal per token. Never degrade correctness, security, tests, or creative quality—one wrong guess costs `4x` more than one targeted read.

## 1. Input & Tool Hygiene (Biggest Lever)
- **Climb the Discovery Ladder:** `graphify` -> `repomix --compress` / `rg -n` -> `read_file(StartLine, EndLine)`. Never read an 800-line file for 20 lines.
- **Parallelize independent calls:** Batch unrelated reads/searches in 1 turn (eliminates `Nx` prefix re-read tax).
- **Filter verbose stdout:** Use quiet flags (`pytest -q --tb=short`, `git status -sb`, `ffmpeg -loglevel error`) or `shell_trim.py` / `rtk`. Never dump lockfiles, `.mp4`, `.info.json`, or `node_modules`.
- **Isolate exploration:** Delegate noisy multi-file research or web/browser tasks to `flash` / `research` subagents returning `<=250`-word `file:line` summaries.

## 2. Prompt Cache & Session Hygiene
- **Keep prefix append-only** during an active slice (no mid-task rewriting of early context).
- **Compact only at verified milestones** (after commit/pass) or write a `<400`-token `HANDOFF.md` (`context-diet`) before starting a fresh thread.

## 3. Output, Editing & Verification Discipline
- **Surgical diffs only:** Prefer `edit_file` over full-file `write_file(Overwrite=True)`.
- **Artifact-first:** Write long reports/plans to `.md` files once; reply with link + concise highlights (never re-summarize the whole file).
- **Auto-route Ponytail tier** (`ponytail/ROUTER.md`): `lite` for explicit tiny edits/creative polish · `full` default · `ultra` for bloated repos/vague over-scoped requests/security PRs.
- **Compress chatter, never deliverables:** Keep code, diffs, paths, errors, and user-facing creative copy at 100% fidelity.
