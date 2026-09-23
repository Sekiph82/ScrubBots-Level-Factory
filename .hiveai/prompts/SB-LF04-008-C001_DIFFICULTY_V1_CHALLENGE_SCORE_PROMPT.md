# SB-LF04-008-C001 — Difficulty V1 Challenge Score

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-008`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-008-C001_DIFFICULTY_V1_CHALLENGE_SCORE_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-008-C001_DIFFICULTY_V1_CHALLENGE_SCORE_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement Difficulty V1 Challenge Score exactly from the fixed normalization and coefficients in the audit criteria.

Create a versioned policy/result. Score only LevelMetrics with all five required core metrics. Preserve component breakdown and source LevelMetrics digest.

Do not include 004-007 optional diagnostics in V1 score, do not renormalize missing components, and do not use width/height/color-count/class metadata.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
