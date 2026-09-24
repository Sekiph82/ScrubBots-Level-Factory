# SB-LF05-007-C001 — Machine-Readable QA Report

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-007`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-007-C001_MACHINE_READABLE_QA_REPORT_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-007-C001_MACHINE_READABLE_QA_REPORT_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

Create a closed immutable versioned QA report that composes accepted M05 stages and retained SB-LF05-006 actionable reasons / SB-LF05-009 recognizability evidence.

Report must bind:
- exact source/LevelData/logical-art identities;
- main-game validation authority/result identities;
- production contract facts;
- M03 solver disposition/evidence digest;
- M04 DifficultyAnalysis/score/lane digest where available;
- semantic recognizability assessment/review evidence;
- actionable rejection/retry reasons with stable codes;
- overall QA disposition.

Overall disposition must be derived from stage truth, not caller-supplied independently.

Structural diagnostics must never fabricate recognizability. UNREVIEWED recognizability must not become semantic ACCEPT.

Closed JSON parser, canonical bytes/digest, no timestamps/paths/secrets/operational timeout in canonical identity.

Tests: accepted case, structural reject, proven-unsolvable reject, solver inconclusive, semantic reject, semantic unreviewed, missing evidence, tamper/cross-lineage, unknown fields, deterministic round-trip.

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
