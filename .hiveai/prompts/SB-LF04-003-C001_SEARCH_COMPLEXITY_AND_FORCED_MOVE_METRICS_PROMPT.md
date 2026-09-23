# SB-LF04-003-C001 — States / Dead Ends / Branching / Forced Moves

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-003

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-003-C001_SEARCH_COMPLEXITY_AND_FORCED_MOVE_METRICS_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-003-C001_SEARCH_COMPLEXITY_AND_FORCED_MOVE_METRICS_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Populate states_visited=SolverMetrics.visited_count, dead_ends=dead_end_count, branching=deterministic arithmetic mean of observed branch_counts, and forced_moves=count(branch_count==1). If no branch observation exists, branching stays absent rather than zero. Use only accepted SolverMetrics; never reconstruct legal actions from CompactSolverState. Preserve 002 metrics and provenance. Tests must cover known branch tuples, forced branches, no branches, evidence mismatch, determinism and preservation.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
