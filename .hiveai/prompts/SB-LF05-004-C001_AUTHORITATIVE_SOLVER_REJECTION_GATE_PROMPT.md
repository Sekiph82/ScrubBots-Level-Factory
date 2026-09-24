# SB-LF05-004-C001 — Authoritative Solver Rejection Gate

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task:
`SB-LF05-004`

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-004-C001_AUTHORITATIVE_SOLVER_REJECTION_GATE_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF05-004-C001_AUTHORITATIVE_SOLVER_REJECTION_GATE_CODEX_LOG.md

Do not edit root TASKS.md.

Read first:
- root TASKS.md, AGENTS.md, GOVERNANCE.md;
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md
- https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB-LF04-M04_FINAL_CLOSURE_SUMMARY.md
- retained SB-LF05-006 and SB-LF05-009 evidence/contracts;
- exact task criteria;
- all earlier M05 task implementations in this batch.

## Mission

Add a QA solver gate that consumes accepted M03 solver evidence only.

Rules:
- PROVEN_UNSOLVABLE from exact authoritative solver evidence => REJECT.
- SOLVED => solver gate PASS.
- INCONCLUSIVE/UNKNOWN_BOUND => never label UNSOLVABLE and never reject under the proven-unsolvable reason.
- UNAVAILABLE/ERROR => separate truthful dispositions.
- evidence authority/source/request/budget identity mismatch => ERROR/fail closed.

Do not run a second solver or infer unsolvability from dead ends, Challenge Score, WFC, visual structure or timeout.

The gate must preserve exact solver evidence digest and deterministic budget identity.

Tests: solved, proven-unsolvable, unknown-bound/inconclusive, operational timeout wrapper, unavailable, wrong authority/evidence, deterministic report.

Implement only this task plus minimal compatibility plumbing. Do not preempt later M05 tasks.

Create the task builder log before product edits. Run every required gate. Publish implementation/tests/docs + builder log, then a terminal log-only commit. Continue only under the M05 master batch.
