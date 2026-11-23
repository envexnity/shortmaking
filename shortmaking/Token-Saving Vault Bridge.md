---
title: Token-Saving Vault Bridge (7-Layer Zero-Quality-Loss Stack)
tags:
  - tokens
  - optimization
  - ponytail
  - token-guard
  - context-engineering
area: mcps-skills
style: all
status: evergreen
created: 2026-11-21
updated: 2026-11-21
summary: Cross-vault bridge to C:\Users\AFADAZIO\Obsidian\Token-Saving-Vault — 10 installed token-saving skills (6x3 Ponytail auto-routed suite, token-guard, context-diet, paleo-auto, paleo-trim-context), CLI audit/trim utilities, and verified -47% to -64.3% A/B benchmark savings at 100% quality.
---

# Token-Saving Vault Bridge (`65–88%` Compound Savings, `0%` Quality Loss)

> [!IMPORTANT] Connected Master Vault & Runnable Scripts
> - **Master Token-Saving Vault**: `C:\Users\AFADAZIO\Obsidian\Token-Saving-Vault\00 Home.md`
> - **Token Bloat Auditor**: `python "C:\Users\AFADAZIO\Obsidian\Token-Saving-Vault\scripts\token_audit.py" .`
> - **Windows CLI Output Filter**: `python "C:\Users\AFADAZIO\Obsidian\Token-Saving-Vault\scripts\shell_trim.py" -- <command>`
> - **Local Installed Skills (`.agents/skills/`)**: `ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help` *(each with `lite.md`, `SKILL.md` [`full`], `ultra.md` + `ROUTER.md`)*, `token-guard`, `context-diet`, `paleo-auto`, `paleo-trim-context`.

---

## 1. Verified Live A/B Subagent Benchmark Results (Same Model, `100%` Pass Rate)

| Benchmark Tier | Hidden Checks Passed | Observation Tokens | Cumulative Multi-Turn Input Tokens | Total Billed Tokens | Net New LOC Written |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Standard 6-File Repo (`744` LOC, 12 Checks)** | **`12/12` (`100%`)** both | **`-46.3%`** (`6,818` vs `12,701`) | **`-46.4%`** (`52,206` vs `97,425`) | **`-47.0%`** (`48,424` saved) | **`-69.6%`** (`+45` vs `+148` LOC) |
| **Very Hard 13-File Systems Repo (`3,184` LOC, 20 Adversarial & 16-Thread Checks)** | **`20/20` (`100%`)** both | **`-75.6%`** (`10,098` vs `41,367`) | **`-65.6%`** (`90,618` vs `263,100`) | **`-64.3%`** (`174,762` saved — **`2.80×` cheaper!**) | **`-53.8%`** (`+114` vs `+247` LOC) |

---

## 2. The 7-Layer Zero-Quality-Loss Checklist (Enforced by `token-guard`)

1. **Prompt Cache Prefix Stability (`50–90%` input discount)**: Keep system prompt, `AGENTS.md`, and tool schemas static and append-only during an active task; never inject per-second timestamps at Token 0 or rewrite early turns mid-slice.
2. **4-Step Discovery Ladder (`~70%` fewer read tokens)**: `graphify` -> `npx repomix --compress` (Tree-sitter skeleton) -> `rg -n` -> surgical `read_file(StartLine, EndLine)`. Never read full files or static data tables to inspect one function.
3. **Filtered CLI & Tool Output (`60–90%` smaller logs)**: Use quiet flags (`pytest -q --tb=short`, `git status -sb`, `ffmpeg -loglevel error`) or pipe through `shell_trim.py` / `rtk`. Never `read_file` raw `.mp4`, `.info.json`, lockfiles, or minified bundles.
4. **Subagent Isolation & Milestone Handoffs**: Offload noisy multi-file searches to `flash` / `research` subagents returning `<=250`-word `file:line` summaries; write a `<400`-token `HANDOFF.md` (`context-diet`) at verified commit boundaries.
5. **Multi-Tier Model & Effort Routing (`~0.46×` cost)**: Use `Pro`/`Opus` (`high` effort) for greenfield architecture, subtle bugs, and security reviews; use `Flash`/`Haiku` (`low`/`medium` effort) for discovery, boilerplate, and parallel fan-outs.
6. **Ponytail 6×3 Situational Auto-Router (`-53%` LOC, `-45%` output tokens)**: Auto-select `lite.md` (explicit small specs / creative polish), `SKILL.md` (`full` default), or `ultra.md` (vague/over-scoped requests, bloated repos, security PRs) via `.agents/skills/ponytail/ROUTER.md`.
7. **Surgical Diffs & Terse Delivery (`Caveman` / `Paleo`)**: Use `edit_file` chunks instead of full-file rewrites, batch independent tool calls in parallel in the same turn, and compress conversational prose while keeping code, paths, errors, and creative deliverables 100% intact.
