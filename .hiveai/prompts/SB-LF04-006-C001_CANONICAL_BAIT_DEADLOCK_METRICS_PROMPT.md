# SB-LF04-006-C001 — Canonical Bait / Deadlock Metrics

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-006`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-006-C001_CANONICAL_BAIT_DEADLOCK_METRICS_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-006-C001_CANONICAL_BAIT_DEADLOCK_METRICS_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement SB-LF04-006 as canonical counterfactual bait/deadlock analysis.

Use accepted M03 legal-move, transition and solver authority only. Do not use dead_end_count as a synonym.

If exact counterfactual proof cannot be established for production, return UNAVAILABLE and keep LevelMetrics.bait_deadlock absent.

Fixture graphs may prove the calculation contract.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
