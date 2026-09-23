# SB-LF04-009-C001 — Score to Lane / Class Rhythm

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-009

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-009-C001_SCORE_TO_LANE_CLASS_RHYTHM_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-009-C001_SCORE_TO_LANE_CLASS_RHYTHM_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Map AVAILABLE Difficulty V1 score by score only: EASY [0,25), MEDIUM [25,50), HARD [50,75), VERY_HARD [75,100]. Define exact boundaries and reject out-of-range scores. Predicted class is analysis output and must not rewrite requested difficulty metadata, board dimensions, colors, art or LevelData. Carry source ChallengeScore digest/version and mapping policy version. Optional comparison to descriptive/requested class is neutral match/mismatch only. Tests cover every threshold edge, same score on different sizes/colors, deterministic serialization and non-mutation.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
