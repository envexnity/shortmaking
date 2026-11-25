# Ponytail Help — `ultra` Mode (Complete Reference + Situational Auto-Router)

Display the standard card from `SKILL.md` AND the full situational auto-selection matrix from `../ponytail/ROUTER.md`, plus:

## Escalation & De-Escalation Triggers
- **Auto-escalate `lite -> full`** if a "tiny tweak" touches `>2` files, changes a public signature, or introduces branching/parsing/money/auth logic.
- **Auto-escalate `full -> ultra`** if the request proposes adding a new library/service/abstraction layer, touches auth/billing/migrations, or the repo already shows heavy duplication.
- **Auto-de-escalate `ultra -> lite`** when the user explicitly confirms scope ("just build it as asked") or during pure creative/visual iteration (UI layout, copy, animation timing).
