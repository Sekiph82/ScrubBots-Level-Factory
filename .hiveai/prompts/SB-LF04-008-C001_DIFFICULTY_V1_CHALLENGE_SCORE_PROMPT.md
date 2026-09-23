# SB-LF04-008-C001 — Difficulty V1 Challenge Score

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-008

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-008-C001_DIFFICULTY_V1_CHALLENGE_SCORE_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-008-C001_DIFFICULTY_V1_CHALLENGE_SCORE_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Implement deterministic engineering-policy Challenge Score V1 in [0,100] using ONLY guaranteed core metrics from 002/003: move_count, states_visited, dead_ends, branching, forced_moves. Optional 004-007 diagnostics are NOT in V1 and must not be treated as zero. Fixed normalizers: move=clamp(log1p(move_count)/log1p(64),0,1); states=clamp(log1p(states_visited)/log1p(10000),0,1); dead_end=clamp(dead_ends/max(states_visited,1),0,1); branching=clamp(branching/4.0,0,1); forced_relief=clamp(forced_moves/max(states_visited,1),0,1); forced_component=1-forced_relief. Coefficients: move .25, states .25, dead_end .15, branching .15, forced .20. score=100*weighted sum. All five required metrics must exist; do not renormalize weights. Create versioned policy/result with source LevelMetrics digest and component breakdown. No width/height/color/class in formula. Tests use hand-calculated values, bounds, missing metrics, zero-state edge, metadata independence and determinism.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
