# SB-LF04-002-C001 — Solution Depth / Move Count

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-002`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-002-C001_SOLUTION_DEPTH_AND_MOVE_COUNT_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-002-C001_SOLUTION_DEPTH_AND_MOVE_COUNT_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement a dedicated versioned metric-population function/module for SB-LF04-002.

Consume accepted LevelMetrics + exact SolverEvidenceReport. Validate evidence identity before using it.

Populate only solution_depth and move_count according to the recorded deterministic solution witness. A solved-at-start state may truthfully yield 0/0. Non-solved or non-AVAILABLE evidence must not receive fabricated values.

Do not run another search merely to shorten the path. Do not claim optimality.

Add focused tests and documentation for the witnessed-path semantics.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
