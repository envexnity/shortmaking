# Ponytail Gain — `ultra` Mode (Tier Trade-offs & Compound Stack ROI)

Display the full ASCII scoreboard from `SKILL.md`, then add:

## Why Cost Drops Less (-26%) Than Output Tokens (-45%)
Ponytail primarily cuts **code written and output tokens**. Input tokens (system prompts, file reads, verbose shell logs, uncompacted chat history) make up 60-85% of agent bills.

## Tier Trade-off Guide
| Tier | Token Overhead | Best Savings Lever | Risk if Misused |
| :--- | :--- | :--- | :--- |
| **`lite`** | Lowest | Keeps diffs lean without extra negotiation turns | Won't stop an over-scoped request |
| **`full`** | Low | `-45%` output tokens + `-53%` LOC with higher test rate (`98%`) | Balanced default |
| **`ultra`** | Extra 1 turn upfront (if pushing back) | Prevents building entire unnecessary features/deps (`-80%`+ avoided work) | Annoying on already-clear tiny tweaks |

## Compounding Ponytail With Input-Side Savings (Zero Quality Loss)
Pair Ponytail (lean code + concise replies) with: **Prompt Cache prefix stability** (`50-90%` cached input discount) + **Graphify / `rg` / `repomix --compress`** (stop full-file reads) + **CLI log filtering (`rtk` / head-tail error slicing)** + **Model-tier routing** (`Pro/Opus` plans -> `Flash/Haiku` executes).
