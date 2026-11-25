---
name: context-diet
description: >
  Lossless context compression and session handoff generator. Use when a
  conversation exceeds ~15 turns, after completing a verified milestone, or when
  slimming bloated AGENTS.md / CLAUDE.md / markdown docs without losing a single
  invariant, file path, or technical threshold.
license: MIT
---

# Context Diet (Lossless Compression & Handoff Capsules)

## Mode A — Session Handoff (`HANDOFF.md`, `< 400` tokens)
When finishing a slice or resetting a long thread, capture ONLY:
1. **Done & Verified:** `file:line` + exact passing check/command.
2. **Locked Decisions & Invariants:** choices already made so the next agent never re-debates them.
3. **Next Exact Step:** concrete numbered action(s) + exact target file paths.
4. **Open Risks / `shortcut:` Limits:** anything deferred.

Drop: superseded plans, resolved stack traces, raw search outputs, and polite filler.

## Mode B — Lossless Rule / Doc Slimming (`AGENTS.md`, `SKILL.md`)
When compressing an always-loaded instruction file:
- Preserve **100%** of file paths, CLI commands, exact numbers/thresholds, version pins, and hard safety invariants.
- Replace long narrative explanations with compact tables or 1-line imperatives.
- Move deep reference catalogs out of `AGENTS.md` into linked notes loaded on demand (progressive disclosure).
- Target `< 1,500` tokens for root `AGENTS.md` and `< 800` tokens for individual `SKILL.md` files.
