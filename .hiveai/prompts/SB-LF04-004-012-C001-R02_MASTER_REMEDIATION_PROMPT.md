# SB-LF04-004,005,006,007,010,012-C001-R02 — M04 Master Remediation Prompt

Document role: CODEX MASTER REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

## Authorization

Remediate only:

`SB-LF04-004 -> 005 -> 006 -> 007 -> 010 -> 012`

PASS/CLOSED and not to be reopened except minimum compatibility:
- SB-LF04-001
- SB-LF04-002
- SB-LF04-003
- SB-LF04-008
- SB-LF04-009
- SB-LF04-011

R02 index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF04-004-012-C001-R02_REMEDIATION_INDEX.md

R01 re-audit summary:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-004-012-C001-R01_STRICT_REAUDIT_SUMMARY.md

## Core rule

Do not create a fake “verified” canonical receipt.

Current production canonical providers for dependency depth, slot trace, counterfactual bait/deadlock and ordered volatility trace are **not available**.

Therefore M04 V1 must truthfully keep those four production metrics UNAVAILABLE.

Fixture calculators remain useful for contract/unit tests but are not production authority.

## Shared trust-boundary remediation

The generic `verified_canonical_evidence()` design is not accepted because it can mint trust from a caller-authored mapping.

Remove or hard-disable any generic caller-facing path from dictionary/strings/boolean -> VERIFIED_CANONICAL.

A future concrete provider may own receipt issuance only after actual canonical execution.

Do not implement a fake positive provider merely to satisfy tests.

## Provenance remediation

SB-LF04-010 must not accept optional metric producer strings as proof.

Any future optional production metric requires a producer binding created from the actual verified provider result/evidence.

With current 004–007 providers unavailable, optional production metrics must not be provenance-encodable.

## Desktop / worktree hygiene

Canonical project:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not create Desktop sibling worktrees.

Isolation:
- prefer `%TEMP%\ScrubBots-Level-Factory\<task-or-verify>`;
- Desktop fallback only under canonical project `.codex-worktrees\...`;
- remove temporary worktrees when safe;
- durable logs only under repo `.hiveai/codex-logs/`.

## Governance

- Do not edit root TASKS.md.
- Do not create/edit audit files.
- Each R02 task gets its own builder log, implementation commit and terminal log-only commit.
- No gameplay-rule clone.
- No network/provider credits for tests.
- No source/art/LevelData mutation.
- No board-size/color-count difficulty inference.
- Do not weaken 008/009 result integrity.

## Execution

For each task:
1. sync current origin/main;
2. read exact R01 re-audit + R02 prompt;
3. create R02 builder log before edits;
4. implement bounded fix;
5. run focused + affected M04/M03 tests;
6. run full pytest, compileall, Godot, diff-check, TASKS no-diff;
7. commit/push implementation + task log;
8. finalize log + terminal log-only commit;
9. continue.

## Final master log

After all six tasks create:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-C001-R02_MASTER_REMEDIATION_CODEX_LOG.md

Record full URLs, implementation SHAs, terminal log SHAs, focused/full results, provider availability truth, skips, TASKS zero diff and worktree cleanup status.

Final batch-wide gates:
- all M04;
- retained M03;
- production/difficulty;
- full pytest zero failures;
- compileall PASS;
- Godot headless PASS;
- canonical bridge tests where configured;
- git diff --check;
- TASKS zero diff.

Commit/push master log and STOP for independent ChatGPT re-audit.

## Final response

Return only:
1. full GitHub URL of the R02 master remediation log;
2. final master-log commit SHA;
3. six full GitHub URLs for R02 task builder logs.
