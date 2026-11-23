---
name: roblox-game-context
description: |
  Load the user's actual Roblox game context by reading their Rojo project files
  (default.project.json, src/, ReplicatedStorage, ServerScriptService, etc.) and
  build a project-aware prompt for any Roblox feature / system / script request.
  Use this skill whenever the user asks for help with a specific Roblox game and
  the workspace contains a Rojo project. Triggers on phrases like "add [X] to my
  game", "make a [system] for this Roblox game", "I'm building a [tycoon / obby /
  simulator]", or any Roblox dev request where the answer depends on what the user
  is actually building. Do NOT use this for generic Roblox theory questions,
  standalone scripts unrelated to a project, non-Roblox work, or pure prompt-engineering
  theory — for prompt structure (≤150 words, outcome-not-implementation) defer to
  `roblox-prompt-engineer`; this skill is the project-context half of that workflow.
---

# Roblox Game Context

The point of this skill: turn "I want to add X to my game" requests into project-aware
suggestions instead of generic Roblox tutorials. The model reads the user's actual
Rojo project, infers the game type, the existing systems, the code style, and the
tech stack, and uses that to ground every suggestion in the user's codebase.

This skill produces **internal context** (a working-memory profile) plus an
optional one-line confirmation. It does NOT dump a project summary to the user
unless that helps them catch a wrong inference.

## When this skill helps

- The user is asking for a feature / system / script in their game
- The workspace has a Rojo project (or looks like one)
- The suggestion would change based on what game it is (tycoon vs obby vs simulator)

Skip this skill if the user is asking a generic Roblox question, hasn't pointed
at a project, or the workspace has no Rojo files.

## Inputs to collect

If the workspace is empty, doesn't have a Rojo project, or has multiple Rojo
projects, ask the user **before** guessing. Don't pretend to know the project.

- Which Rojo project to use (if multiple found)
- Confirmation of the inferred game type / genre (only ask if it's genuinely
  ambiguous — don't ask when the evidence is clear)
- **Ambiguous feature terms.** If the user uses a term that could mean several
  different things in Roblox — "VIP" (game pass? dev product? profile flag?),
  "save data" (ProfileService? raw DataStoreService? session-locked?),
  "admin" (CMS? chat tag? permissions table?) — ask once before assuming.
  Tycoons default to GamePass, but the cost of asking is one short question
  and the cost of being wrong is a rewrite.

## Procedure

1. **Locate the Rojo project file.**
   - Look for `default.project.json` at the workspace root.
   - If not at root, search one or two levels up with `Glob` (`**/default.project.json`,
     `**/*.project.json`).
   - Read it. Note the `name` (working title) and the service → path mappings
     (`ReplicatedStorage` → `src/ReplicatedStorage`, etc.).
   - **Cross-check against the README.** The `default.project.json` is the
     source of truth for folder layout. If the README describes folders
     differently (e.g. it says `src/server` but the project file says
     `src/ServerScriptService`), note the discrepancy and surface it in
     follow-ups — the user can fix the doc and the next contributor won't be
     misled.
   - If no project file exists, stop and tell the user this isn't a Rojo project.
     Don't guess wildly.

2. **Map the project tree.**
   - Use `Glob` (`src/**/*.lua`, `src/**/*.luau`, `Packages/*.lua`) to list the
     relevant code paths. Skip the project's own `sourcemap.json` and `.git`.
   - Cap the listing — if it's huge (1000+ files), sample the README and
     top-level `src/` structure first.
   - Note where each major Roblox service lives (ServerScriptService, ReplicatedStorage,
     StarterPlayerScripts, etc.) and what folders exist under each.

3. **Read the high-signal files first.**
   - `README.md`, `DESIGN.md`, or any design doc at the project root. Pay
     particular attention to any "Not yet built" / "TODO" / "Future" /
     "Roadmap" section — lines there are a strong signal the user is filling a
     known gap, and confirming the request fits that gap is worth a line in
     the response.
   - `wally.toml` / `wally.lock` — reveals libraries (Knit, ProfileService, Roact,
     Fusion, etc.) → big signal for architecture style.
   - Top-level `Config.lua` / `GameConfig.lua` / shared constants.
   - The largest 2–3 scripts under `ServerScriptService` — these usually define
     core systems (combat loop, currency, data save, plot assignment).
   - One representative ModuleScript under `ReplicatedStorage` (or wherever
     shared modules live) — confirms naming and style conventions.
   - Any small type file (`GameTypes.d.lua`, `types.lua`, `types.d.lua`) — even
     10 lines tells you whether the project is strict-typed, which decides
     whether new fields need to be added to type aliases for `--!strict` to
     stay green.
   - On Windows, use PowerShell `Get-Content` with `-Encoding UTF8` to read `.lua`
     / `.luau` files. Prefer the `Read` tool for anything you'll inspect line by
     line; PowerShell only for quick file listing and counting.

4. **Infer the project profile.** Build a tight ≤200-word internal profile:
   - **Game type / genre** — tycoon, obby, simulator, RPG, fighting, social,
     horror, etc. Cite evidence ("saw `Dropper` class + `Currency` value" vs
     "saw `Checkpoint` part + `Stage` value").
   - **Core systems present** — currency / leaderstats, data saving, plot
     assignment, combat, inventory, shop, GUI, questing, anti-cheat.
   - **Tech stack** — plain Roblox, Knit, ProfileService, Roact / Fusion UI,
     ECS frameworks. Wally dependencies and folder layout give this away.
   - **Conventions** — naming style (`PascalCase` vs `camelCase` for instances,
     `snake_case` vs `PascalCase` for modules), folder layout (`src/server/`,
     `src/client/`, `src/shared/`), and any local style cues (do they use
     strict typing, services via `Knit.GetService`, etc.).
   - **What is missing** — note systems the user might want but haven't built
     yet, so the model doesn't suggest a duplicate.

5. **Use the context, don't show it.** Apply the profile to the user's request:
   - Anchor suggestions to existing systems (extend `Currency`, don't reinvent
     leaderstats).
   - Match conventions (camelCase scripts → use camelCase in suggestions).
   - Match tech stack (don't suggest a Knit pattern in a non-Knit project, or
     vice versa).
   - When the suggestion involves an external-service call (GamePass ownership,
     dev product grant, HTTP request, etc.), check the user's existing code
     for the call style. If the call is rate-limited (`UserOwnsGamePassAsync`,
     `UserOwnsAssetAsync`, `GetProductInfo`, `HttpService:RequestAsync`),
     include a per-player / per-request cache in the suggestion and
     invalidate on `PlayerRemoving` or cache expiry. A tycoon can easily
     trigger rate limits with a "buy" call per second per player.
   - When the user wants a Roblox prompt for an external AI service, fold the
     project context into the prompt naturally (e.g., "I'm building a tycoon
     called Pixel Tycoon using Knit..."). This pairs with
     `roblox-prompt-engineer` — that skill teaches prompt shape, this skill
     supplies the project facts.

6. **Confirm with one line.** Before diving in, acknowledge the inferred game
   in a single short sentence. Pick the form that fits the user's request:

   - **If the user already specified what they want** (e.g. *"add a VIP
     dropper"*) → use a confirming form that names the project and echoes the
     request back as you understood it, so they can correct any wrong
     inference:
     > "Got it — Pixel Tycoon, a tycoon with Knit, ProfileService, and 5
     > dropper tiers. Adding a VIP dropper that fits your existing
     > `DropperTiers` + `BuyDropper` pattern."

   - **If the user is vague** (e.g. *"I want to build something"*) → use a
     question form that confirms the inferred game and asks what's next:
     > "Got it — `Pixel Tycoon`, a tycoon with currency, droppers, and a
     > data store. What do you want to add?"

   This is the one place the profile becomes visible to the user. Keep it
   short; full context lives in your head, not in the chat.

## Output contract

- **Internal:** a working-memory profile (≤200 words) the model uses to ground
  every subsequent suggestion in this turn.
- **External:** one short acknowledgement line stating the inferred game +
  its core systems, so the user can correct wrong inferences.
- When the user's request produces a Roblox prompt (e.g., for Lemonade AI),
  the prompt embeds the project context — game name, existing systems,
  tech stack, conventions — without re-listing them as a separate dump.

## Failure handling

- **No Rojo project found** → ask the user. Don't pretend to know the project.
  If they say "I'm not using Rojo, just help me design from scratch", drop
  the skill and answer directly.
- **Project file is minimal** (only `name` and no service mappings) → check
  the directory itself; some projects use a flat layout. Read whatever's
  there and infer from the file list.
- **Project is huge** (1000+ files, deep folder tree) → don't read everything.
  Sample the README, `wally.toml` if present, the 2–3 biggest scripts, and
  stop. Say what you inferred and what you didn't read.
- **Multiple Rojo projects in workspace** → ask the user which one. Don't
  guess between, say, a tycoon and a fighting game.
- **Game type is ambiguous** → state your best guess + the evidence, then
  ask the user to confirm. Example: "Looks like a tycoon based on the
  `Dropper` class and `Currency` value, but I could be wrong — is that right?"
- **Project uses non-Rojo layout** (legacy `.rbxl` file, no project.json)
  → skill doesn't apply. Tell the user this isn't a Rojo project and offer
  to either help them set up Rojo or work without project context.
- **Read fails on a file** (encoding, size, permissions) → skip that file,
  note it in the confirmation line ("skipped one file I couldn't read"), and
  proceed with what you have.

## Examples

### Example 1 — Tycoon with currency

Workspace:
- `default.project.json` → `name: "Pixel Tycoon"`, `ReplicatedStorage` → `src/ReplicatedStorage`,
  `ServerScriptService` → `src/server`
- `src/server/Dropper.lua` — drops coins every 2s on `Touched`
- `src/server/leaderstats.lua` — sets up `Cash` leaderstat from `DataStoreService`
- `src/shared/Config.lua` — game balance constants
- `wally.toml` lists `knit` and `profileservice`

User: *"Add a VIP dropper to my game"*

Skill does:
- Reads project, identifies a tycoon with Knit + ProfileService.
- Notes existing `Dropper.lua` pattern, `Cash` leaderstat, shared config.
- Suggests: extend the existing `Dropper` module, add a `vipOnly: boolean` to its
  config, gate spawning on a `VIP` BoolValue in the plot, route earnings to the
  existing `Cash` leaderstat through the existing ProfileService save pipeline.
- Confirms: "Got it — Pixel Tycoon, a tycoon with Knit, ProfileService, and
  currency. Adding a VIP dropper that follows your existing Dropper pattern."

### Example 2 — Obby with stages

Workspace:
- `default.project.json` → `name: "Tower of Pain"`
- `src/server/` mostly empty
- `src/ReplicatedStorage/Stage.lua` — `IntValue` tracking current stage
- `wally.toml` — no frameworks, plain Roblox

User: *"How do I add checkpoints to my obby?"*

Skill does:
- Reads project, identifies an obby (no real systems, just stage tracking).
- Notes existing `Stage` value and plain-Roblox style (no Knit).
- Suggests: `Touched`-based checkpoint parts that increment the existing
  `Stage` value, with a `BindableEvent` to respawn the player at the latest
  checkpoint. Uses only `Workspace` + `ReplicatedStorage` — no new frameworks.

## Notes on combo with `roblox-prompt-engineer`

When the user wants a prompt to feed Lemonade AI / Ropilot AI:

1. This skill supplies the **project facts** (game name, type, existing systems,
   tech stack).
2. `roblox-prompt-engineer` supplies the **prompt shape** (≤150 words, lead
   with player action, strip the engineering, etc.).

The two are complementary halves of a project-aware Roblox prompt. If both
seem relevant, load both — they don't conflict.

## Windows (win32) platform notes

When the workspace is on Windows and you need shell commands:

- File listing: `Get-ChildItem -Path <dir> -Recurse -Filter *.lua` instead of
  `find ... -name "*.lua"`.
- Reading files: prefer the `Read` tool for `.lua` / `.luau`. If you must use
  PowerShell, pass `-Encoding UTF8` to `Get-Content` (PowerShell 5.1 silently
  corrupts UTF-8 without it).
- Slashes in paths: Rojo's `default.project.json` uses forward slashes and
  works on both platforms. Don't rewrite them.
- The `Read`, `Glob`, and `Grep` tools work the same on Windows as elsewhere —
  prefer them over raw `Bash` for content operations.
