# SB-LF05-005-C001 — INCONCLUSIVE vs UNSOLVABLE QA Semantics

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-005`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-005-C001_INCONCLUSIVE_VS_UNSOLVABLE_QA_SEMANTICS_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-005-C001_INCONCLUSIVE_VS_UNSOLVABLE_QA_SEMANTICS_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

Define the closed QA outcome semantics that keep solver uncertainty distinct from proof.

At minimum distinguish:
- ACCEPTABLE_SOLVER_PROOF / SOLVED;
- REJECT_PROVEN_UNSOLVABLE;
- INCONCLUSIVE_REVIEW_OR_RETRY_REQUIRED;
- UNAVAILABLE;
- ERROR.

An INCONCLUSIVE candidate may be queued for retry/review according to later policy, but it must not be counted as a proven-unsolvable rejection.

QA rejection statistics/reasons must preserve this distinction.

Wall-clock timeout remains operational-only and must not become canonical unsolvability.

Tests must prove no code path maps UNKNOWN_BOUND/INCONCLUSIVE/timeout-before-result to PROVEN_UNSOLVABLE.

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
