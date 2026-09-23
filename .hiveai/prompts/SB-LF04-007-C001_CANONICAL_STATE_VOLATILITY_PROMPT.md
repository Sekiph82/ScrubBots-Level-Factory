# SB-LF04-007-C001 — Canonical State Volatility

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-007

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-007-C001_CANONICAL_STATE_VOLATILITY_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-007-C001_CANONICAL_STATE_VOLATILITY_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Add one versioned gameplay-state volatility diagnostic only if ordered canonical trace quantities are available. Do not use pixel/art fragmentation. Recommended V1: a closed normalized signature from canonical remaining-active-cell count, supply remaining count, occupied-slot count or similarly already-exposed canonical quantities; transition delta is normalized absolute change; volatility is mean transition delta in [0,1]. Exact fields/normalizers/formula must be versioned. If trace data is unavailable without gameplay emulation, production remains UNAVAILABLE. Tests: stable trace=0, changing trace, bounds, one-state absent, malformed/unavailable and determinism.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
