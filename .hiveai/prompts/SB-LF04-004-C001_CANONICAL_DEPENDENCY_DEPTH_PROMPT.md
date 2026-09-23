# SB-LF04-004-C001 — Canonical Dependency Depth

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-004

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-004-C001_CANONICAL_DEPENDENCY_DEPTH_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-004-C001_CANONICAL_DEPENDENCY_DEPTH_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Dependency depth is legal only from an explicit canonical dependency-semantics provider bound to accepted ScrubBots gameplay authority. M03 path depth is not dependency depth. Do not infer dependency from colors, adjacency, WFC, move order, dimensions or heuristics. Define a versioned provider/result with AVAILABLE/UNAVAILABLE/ERROR and exact authority/state/evidence binding. If no canonical dependency semantics are executable in current main-game authority, production must truthfully remain UNAVAILABLE and LevelMetrics.dependency_depth absent. Fixture-only providers may validate the contract but cannot become production authority.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
