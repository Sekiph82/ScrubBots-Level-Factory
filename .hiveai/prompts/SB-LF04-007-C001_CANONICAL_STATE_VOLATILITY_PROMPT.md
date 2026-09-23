# SB-LF04-007-C001 — Color / Remaining-State Volatility

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-007`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-007-C001_CANONICAL_STATE_VOLATILITY_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-007-C001_CANONICAL_STATE_VOLATILITY_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement SB-LF04-007 as a versioned canonical state-volatility provider.

Use only canonical gameplay state quantities already exposed through accepted authority. Document the exact V1 formula. If the necessary trace is not available without new gameplay emulation, keep production UNAVAILABLE.

Do not use art/image fragmentation as volatility.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
