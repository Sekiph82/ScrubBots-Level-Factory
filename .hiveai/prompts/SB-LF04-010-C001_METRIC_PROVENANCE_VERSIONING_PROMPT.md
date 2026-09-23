# SB-LF04-010-C001 — Metric Provenance / Versioning

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch: main

Task: SB-LF04-010

Audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF04-010-C001_METRIC_PROVENANCE_VERSIONING_AUDIT_CRITERIA.md

Builder log:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LF04-010-C001_METRIC_PROVENANCE_VERSIONING_CODEX_LOG.md

Do not edit root TASKS.md.

Read root TASKS.md, AGENTS.md, GOVERNANCE.md, M03 final closure, SB-LF04-001 LevelMetrics implementation/audit, every preceding M04 task in this batch, and the exact audit criteria.

## Mission

Create a closed immutable DifficultyAnalysis provenance envelope binding exact LevelData/source SHA, canonical gameplay authority, SolverEvidence identity/digest, LevelMetrics schema/version/digest, each populated metric provider/policy version, ChallengeScore digest/version if present, lane mapping digest/version if present, disposition/reason and exact component availability. Reject mixed lineage such as score from metrics A plus lane result from score B. No elapsed time, timeout seconds, local paths, machine IDs or UI state in canonical provenance. Optional unavailable diagnostics remain explicitly unavailable. Tests: valid round trip, every cross-binding mismatch, unknown fields/version, deterministic bytes and no operational telemetry.

Do not implement later M04 tasks except minimal compatibility plumbing. Do not use network/provider credits for tests. Do not create a second gameplay solver. Do not mutate art/LevelData/gameplay source.

Create the task builder log before product/test edits. Run all required gates. Publish implementation/tests/docs + task log, then a terminal log-only commit. Continue only under the M04 master batch.
