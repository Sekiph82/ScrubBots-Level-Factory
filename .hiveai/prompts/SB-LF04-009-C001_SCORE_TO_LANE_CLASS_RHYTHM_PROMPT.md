# SB-LF04-009-C001 — Score to Lane / Class Rhythm

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-009`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-009-C001_SCORE_TO_LANE_CLASS_RHYTHM_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-009-C001_SCORE_TO_LANE_CLASS_RHYTHM_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement SB-LF04-009 as a versioned score-to-lane mapping.

Use only the Challenge Score V1 numeric result. Thresholds are fixed by the audit criteria.

If descriptive/requested difficulty metadata differs, report the difference neutrally; never mutate art or dimensions to force alignment.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
