# SB-LF05-002-C001 — Audited M09 Art-First Round-Trip Reuse

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-002`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-002-C001_AUDITED_M09_ART_FIRST_ROUND_TRIP_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-002-C001_AUDITED_M09_ART_FIRST_ROUND_TRIP_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

Reuse the audited main-game M09 exact-pixel round-trip contract for FINAL LOGICAL LEVEL_ART exports.

Do not rewrite the importer algorithm in Factory.

Required proof:
- one final logical PNG pixel = one logical cell;
- no resize/resample/interpolation;
- exact row-major pixel/palette/cell identity survives PNG -> LevelData -> reconstructed image;
- source logical PNG bytes/pixels are never mutated;
- round-trip evidence binds exact main-game importer/source authority and artifact SHA.

Important: M09 historical difficulty-band behavior is NOT current Difficulty V1 truth. Round-trip reuse must not reintroduce class=dimension or per-class color-count rules. Production legality is owned by SB-LF05-001/003.

A capability-gated main-game M09 round-trip provider is preferred. If capability is absent, report UNAVAILABLE rather than duplicating the algorithm.

Tests: exact round-trip, rectangular logical art, repeated colors/palette ordering, off-path source mutation check, authority drift, capability unavailable, no legacy difficulty inference.

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
