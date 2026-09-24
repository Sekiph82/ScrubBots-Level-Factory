# SB-LF04-004..012-C001-R01 — M04 Master Remediation Prompt

Document role: CODEX MASTER REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

## Authorization

Remediate only:

`SB-LF04-004 -> 005 -> 006 -> 007 -> 008 -> 009 -> 010 -> 012`

PASS/CLOSED and not to be reopened except minimal compatibility:
- SB-LF04-001
- SB-LF04-002
- SB-LF04-003
- SB-LF04-011

R01 index:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF04-004-012-C001-R01_REMEDIATION_INDEX.md

C001 audit summary:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-002-012-C001_STRICT_AUDIT_SUMMARY.md

## Governance

- Do not edit root TASKS.md.
- Do not create/edit audit files.
- Each R01 task gets a new builder log, implementation commit and terminal log-only commit.
- Preserve accepted 001/002/003/011 behavior.
- No gameplay-rule clone.
- No network/provider credits merely for tests.
- No board-size/color-count difficulty inference.
- Do not mutate art, LevelData or canonical gameplay checkout.
- Do not hide failures with skip/xfail/deselection outside pre-existing capability contracts.

## Desktop / worktree hygiene

Canonical project:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Do not create Desktop sibling worktrees.

If isolation is required:
1. prefer `%TEMP%\ScrubBots-Level-Factory\<task-or-verify>`;
2. remove it after use when safe;
3. Desktop fallback only inside
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\.codex-worktrees\<task-or-verify>`;
4. durable logs only in repo `.hiveai/codex-logs/`.

## Critical remediation themes

### 004–007
Fixture calculations are allowed, but fixture/caller evidence must never cross into production as VERIFIED_CANONICAL. Current production semantics/trace may truthfully remain UNAVAILABLE.

Use an explicit verifiable provider/evidence boundary. A copied provider id/version or caller boolean is not trust.

### 008
ChallengeScoreResult must be internally consistent with exact DIFFICULTY_V1 coefficients/contributions/score.

### 009
LaneMappingResult must be internally consistent with SCORE_LANE_V1 thresholds and requested-class comparison.

### 010
No generic auto-provenance. Exact producer identity is mandatory for every populated metric. Provenance names are closed to MetricId and availability/provider coverage must match exactly.

### 012
Regression corpus must drive behavior from payloads. Add actual Level Data + art/logical source non-mutation proof and canonical checkout immutability where bridge is exercised.

## Per-task execution

For each task:
1. sync current origin/main;
2. read exact audit + R01 prompt;
3. create R01 builder log before edits;
4. make bounded remediation;
5. run focused + affected predecessor tests;
6. run retained M03/M04 tests;
7. run full pytest, compileall, Godot, diff-check, TASKS no-diff;
8. commit/push implementation/tests/docs + log;
9. finalize log and publish terminal log-only commit;
10. continue.

## Master log

After all eight tasks create:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-C001-R01_MASTER_REMEDIATION_CODEX_LOG.md

Record for each task:
- full builder-log URL;
- implementation SHA;
- terminal log SHA;
- focused/full results;
- provider availability/unavailability truth;
- skips/limitations;
- TASKS zero diff;
- temporary worktree path + cleanup status if used.

Final batch-wide gates:
- all M04 tests;
- retained M03;
- production/difficulty tests;
- full pytest zero failures;
- compileall;
- Godot headless;
- canonical bridge tests where configured;
- git diff --check;
- TASKS zero diff.

Commit/push master log, then STOP for independent ChatGPT re-audit.

## Final response

Return only:
1. full GitHub URL of the R01 master remediation log;
2. final master-log commit SHA;
3. eight full GitHub URLs for R01 task builder logs.
