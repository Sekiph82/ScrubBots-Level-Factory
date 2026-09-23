# SB-LF04-002-C001 — Solution Depth / Move Count

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-002

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-002-C001_SOLUTION_DEPTH_AND_MOVE_COUNT_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-002-C001_SOLUTION_DEPTH_AND_MOVE_COUNT_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Populate only LevelMetrics.solution_depth and move_count from the exact accepted SolverEvidenceReport bound by schema/version/digest. For AVAILABLE+SOLVED, move_count is the number of canonical LegalMove selections in the recorded witness path and solution_depth is the edge depth of that same witness. Do not call the path shortest/optimal/minimal. Solved-at-start may be 0/0. PROVEN_UNSOLVABLE, INCONCLUSIVE, UNAVAILABLE, ERROR, or missing witness evidence must leave both fields absent, never fabricated zero. Preserve all unrelated metrics and provenance. Pure deterministic transformation only; no new gameplay call, no wall-clock data, no source mutation. Tests: solved witness, solved-at-start, non-solved dispositions, evidence mismatch, deterministic repeat, prior metric preservation.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
