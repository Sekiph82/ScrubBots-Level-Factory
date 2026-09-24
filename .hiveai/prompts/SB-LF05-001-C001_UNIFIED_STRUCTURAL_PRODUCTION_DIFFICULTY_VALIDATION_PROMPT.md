# SB-LF05-001-C001 — Unified Structural / Production / Difficulty Validation

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-001`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-001-C001_UNIFIED_STRUCTURAL_PRODUCTION_DIFFICULTY_VALIDATION_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-001-C001_UNIFIED_STRUCTURAL_PRODUCTION_DIFFICULTY_VALIDATION_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

Compose one versioned M05 QA entry point over already accepted authorities. It must not invent a parallel validator.

Required stages:
1. exact Level Data V1 source identity;
2. structural validity against current main-game LevelValidator semantics;
3. production legality against current main-game ProductionLevelValidator semantics;
4. Factory production-envelope/palette lineage consistency where already accepted;
5. Difficulty V1 analysis from accepted M04 LevelMetrics/ChallengeScore/Lane artifacts.

Use a capability-gated external main-game validation provider or equivalent exact-source execution against a clean exact-SHA Scrubbots checkout. Do not port LevelValidator/ProductionLevelValidator logic into Python.

The current production truth is width/height 20..59 independently, rectangular legal, difficulty not derived from dimensions or used-color count. Do not resurrect retired class-size or class-color bands.

Return a closed stage-by-stage disposition model, not a single bool. Structural/production/difficulty evidence must each carry exact authority/version/digest.

Tests: structurally invalid; TEST/unknown production difficulty; legal rectangular board; same legal dimensions under different descriptive classes; M04 analysis mismatch; authority/source drift; capability unavailable; deterministic serialization.

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
