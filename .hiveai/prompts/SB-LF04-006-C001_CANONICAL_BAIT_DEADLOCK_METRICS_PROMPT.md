# SB-LF04-006-C001 — Canonical Bait / Deadlock Metrics

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-006

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-006-C001_CANONICAL_BAIT_DEADLOCK_METRICS_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-006-C001_CANONICAL_BAIT_DEADLOCK_METRICS_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Bait/deadlock requires canonical counterfactual proof. Never equate search dead_end_count with bait. Recommended exact V1 when executable: canonical legal moves -> canonical transition for each -> canonical solver child classification; proven_deadlock_move_count counts only children proven PROVEN_UNSOLVABLE; bait_deadlock ratio = proven_deadlock_move_count/legal_move_count. UNKNOWN_BOUND or INCONCLUSIVE children cannot be counted as proven deadlocks and prevent an EXACT claim when exactness is required. Use M03 providers/bridge only. If unavailable, leave absent. Tests: 0, partial, all deadlock, inconclusive child, unavailable, repeat determinism and authority binding.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
