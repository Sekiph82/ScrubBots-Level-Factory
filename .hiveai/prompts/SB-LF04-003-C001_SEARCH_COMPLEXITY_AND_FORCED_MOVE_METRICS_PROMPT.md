# SB-LF04-003-C001 — States / Dead Ends / Branching / Forced Moves

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-003`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-003-C001_SEARCH_COMPLEXITY_AND_FORCED_MOVE_METRICS_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-003-C001_SEARCH_COMPLEXITY_AND_FORCED_MOVE_METRICS_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement SB-LF04-003 as a pure evidence-to-LevelMetrics population step.

Use only accepted SolverMetrics fields. Define branching as mean(branch_counts) over emitted positive branch observations and forced_moves as count(branch_count == 1). Do not inspect board/supply/slots to infer legal moves.

Preserve 002 metrics and all provenance.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
