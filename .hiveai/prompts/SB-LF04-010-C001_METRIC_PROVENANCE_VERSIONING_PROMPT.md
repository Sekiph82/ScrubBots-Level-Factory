# SB-LF04-010-C001 — Metric Provenance / Versioning

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-010`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-010-C001_METRIC_PROVENANCE_VERSIONING_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-010-C001_METRIC_PROVENANCE_VERSIONING_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement SB-LF04-010 as the canonical provenance/versioning envelope for M04.

Bind every derived artifact to its exact upstream digest and policy/provider version. Reject cross-wired LevelMetrics, ChallengeScore and lane results.

Keep optional 004-007 diagnostics explicitly unavailable rather than synthesizing versions or values.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
