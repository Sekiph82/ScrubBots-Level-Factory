# SB-LF04-005-C001 — Canonical Slot Pressure

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-005`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-005-C001_CANONICAL_SLOT_PRESSURE_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-005-C001_CANONICAL_SLOT_PRESSURE_CODEX_LOG.md`

Do not edit root `TASKS.md`.

Read first:
- root TASKS, AGENTS, GOVERNANCE;
- `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- SB-LF04-001 LevelMetrics implementation/audit;
- every previously completed M04 task in this batch;
- exact task audit criteria above.

Implement SB-LF04-005 with a canonical slot-pressure provider.

Prefer exact canonical state/trace evidence from the accepted bridge if available. V1 slot_pressure is maximum occupied-slot ratio across the observed canonical trace, capacity bound to canonical ProofState semantics.

If canonical snapshots are not safely available, keep production UNAVAILABLE rather than porting slot rules into Python.

Global scope guards:
- no second gameplay solver;
- no WFC-as-difficulty truth;
- no board-size/color-count difficulty inference;
- no source/art mutation;
- no network/provider credits for tests;
- no later-task implementation beyond compatibility plumbing.

Run all criteria-required gates, record exact counts, publish implementation + task builder log, then terminal log-only commit. Continue only when invoked by the M04 master batch.
