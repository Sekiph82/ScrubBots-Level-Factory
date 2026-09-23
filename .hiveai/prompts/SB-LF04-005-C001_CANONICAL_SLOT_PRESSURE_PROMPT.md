# SB-LF04-005-C001 — Canonical Slot Pressure

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-005

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-005-C001_CANONICAL_SLOT_PRESSURE_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-005-C001_CANONICAL_SLOT_PRESSURE_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Slot pressure must use canonical gameplay slot-state observations only. Recommended V1 if canonical trace snapshots are safely available: per-state occupancy ratio = occupied canonical slots / canonical capacity, slot_pressure = maximum observed ratio, finite [0,1]. If trace snapshots cannot be retrieved without gameplay emulation, production remains UNAVAILABLE and slot_pressure absent. Never infer from art/colors. Tests cover empty/partial/full occupancy, deterministic max, malformed capacity/state, authority mismatch and unavailable behavior.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
