# Ponytail Situational Auto-Router (All 6 Skills x 3 Tiers)

Select the **skill** by intent, then select the **tier (`lite` / `full` / `ultra`)** by task risk, ambiguity, and bloat signals. Never guess blindly—match the first row that fits.

## 1. Choose the Skill

| User Intent / Situation | Skill Folder |
| :--- | :--- |
| Writing, fixing, refactoring, scripting, picking dependencies | `ponytail` |
| Reviewing a diff, PR, commit, or recent edits | `ponytail-review` |
| Auditing a whole repo, module, or finding bloat | `ponytail-audit` |
| Listing or checking `shortcut:` / `ponytail:` debt markers | `ponytail-debt` |
| Showing benchmark savings / ROI of ponytail | `ponytail-gain` |
| Explaining commands, levels, or routing rules | `ponytail-help` |

## 2. Choose the Tier (`lite` vs `full` vs `ultra`)

| Skill | Use **`lite.md`** when... | Use **`SKILL.md` (`full` — default)** when... | Use **`ultra.md`** when... |
| :--- | :--- | :--- | :--- |
| **`ponytail`** | User gave an exact, explicit spec; creative/UI/art polish; rapid throwaway prototype; tiny `<25`-line surgical tweak where pushing back wastes turns. | Standard feature, bug fix, refactor, script, or dependency choice where minimal complete diff + 1 test/check is ideal. | Request is vague/over-scoped; user asks for heavy framework/abstraction/microservice; bloated vibe-coded repo; token-critical budget; "cut bloat / do we even need this?". |
| **`ponytail-review`** | Tiny `<40`-line diff, hotfix, copy/CSS tweak, or mid-iteration sanity check (need fast `<=5`-bullet ship/fix verdict). | Standard PR, feature branch, or multi-file commit needing connected-caller & 6-lens review. | Auth/payment/crypto/data-migration PR, production release gate, or large AI-generated diff suspected of over-engineering/hidden races. |
| **`ponytail-audit`** | Fast 60-second repo onboarding, quick health triage, or tight token budget (entry points + deps + top 5 issues only). | Full repo health check or inherited codebase review (ranked top <=20 findings). | Pre-launch security/scale gate, rescuing a sprawling bloated repo, or full architectural demolition & dependency cut-list. |
| **`ponytail-debt`** | Quick pre-commit or sprint sanity check (count + `file:line` list only, zero `git blame`). | Release prep or backlog grooming (full ceiling + upgrade trigger + `no-trigger` rot flags). | Scaling milestone, incident prevention, or quarterly debt paydown (adds `git blame` age + live check of whether current scale already crossed any ceiling). |
| **`ponytail-gain`** | Inline 2-line citation inside another reply (saves output tokens). | User asks "what does ponytail save?" (full ASCII benchmark scoreboard). | Optimizing team/agent workflows (adds `lite`/`full`/`ultra` trade-offs + compound savings with input-side token tools). |
| **`ponytail-help`** | Fast command memory jog (`<=120` tokens). | Human quick reference card. | Agent self-routing or onboarding a new vault (includes full situational decision matrix). |

## 3. Hard Safety Invariants (NEVER Cut in ANY Tier)
Validation at trust boundaries · Error handling preventing data loss · Security & auth checks · Accessibility · Real hardware/render calibration · Explicit user requirements.
